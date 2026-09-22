# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
"""
Define EC connector functionality mixin for model runners.
"""

from collections.abc import Generator
from contextlib import AbstractContextManager, contextmanager, nullcontext
from typing import TYPE_CHECKING

import torch

from vllm.distributed.ec_transfer import get_ec_transfer, has_ec_transfer
from vllm.distributed.ec_transfer.ec_connector.base import ECConnectorBase
from vllm.logger import init_logger
from vllm.v1.outputs import ECConnectorOutput

if TYPE_CHECKING:
    from vllm.v1.core.sched.output import SchedulerOutput

logger = init_logger(__name__)


def _ec_tp_size() -> int:
    """TP world size; 1 when the distributed group is not initialized."""
    try:
        from vllm.distributed import get_tensor_model_parallel_world_size

        return get_tensor_model_parallel_world_size()
    except Exception:  # noqa: BLE001
        return 1


def _ec_tp_rank() -> int:
    try:
        from vllm.distributed import get_tensor_model_parallel_rank

        return get_tensor_model_parallel_rank()
    except Exception:  # noqa: BLE001
        return 0


# Marker key inside the broadcast payload telling ranks to use the
# connector's own per-rank load path (rank0 store fetch failed).
_EC_FALLBACK_KEY = "__ec_fallback__"


def _ec_load_via_rank0_broadcast(
    ec_connector: ECConnectorBase,
    encoder_cache: dict[str, torch.Tensor],
    **kwargs,
) -> bool:
    """Rank0-pull + TP-broadcast load path for EC consumer caches.

    Returns True when handled (TP > 1 and the connector opted in via
    broadcast_loads), False when the caller should use the connector's
    per-rank start_load_caches (TP == 1, shared-memory connector, or
    rank0 fetch failed and the fallback marker was broadcast).

    Encoder output is TP-invariant (merger RowParallel all-reduce gives
    every rank the full tensor), so one store GET + one NCCL broadcast
    replaces N per-rank GETs. Uses the TP group's broadcast_object
    (pickle over the group) — no custom size/payload protocol.
    """
    tp_size = _ec_tp_size()
    if tp_size <= 1 or not ec_connector.broadcast_loads:
        return False

    from vllm.distributed import get_tp_group

    rank = _ec_tp_rank()
    payload = None

    if rank == 0:
        private_cache: dict[str, torch.Tensor] = {}
        try:
            ec_connector.start_load_caches(private_cache, **kwargs)
        except Exception as e:  # noqa: BLE001 — degrade, never kill the engine
            logger.warning(
                "EC rank0 broadcast load failed, falling back to per-rank: %r", e
            )
            payload = {_EC_FALLBACK_KEY: True}
        else:
            payload = {
                mm_hash: {
                    "dtype": str(t.dtype).removeprefix("torch."),
                    "shape": tuple(t.shape),
                    "bytes": t.detach()
                    .to("cpu")
                    .contiguous()
                    .view(torch.uint8)
                    .numpy()
                    .tobytes(),
                }
                for mm_hash, t in private_cache.items()
            }

    received = get_tp_group().broadcast_object(payload, src=0)
    if received.get(_EC_FALLBACK_KEY):
        return False

    device = str(
        getattr(ec_connector, "device", None)
        or kwargs.get("device")
        or f"cuda:{torch.cuda.current_device()}"
    )
    for mm_hash, item in received.items():
        if mm_hash in encoder_cache:
            continue
        t = torch.frombuffer(
            bytearray(item["bytes"]), dtype=getattr(torch, item["dtype"])
        )
        encoder_cache[mm_hash] = t.reshape(item["shape"]).to(device)
        logger.info(
            "EC broadcast load mm_hash=%s bytes=%d", mm_hash, len(item["bytes"])
        )
    return True


# Defined as a EC connector functionality mixin for ModelRunner (GPU, TPU)
class ECConnectorModelRunnerMixin:
    @staticmethod
    def maybe_save_ec_to_connector(
        encoder_cache: dict[str, torch.Tensor],
        mm_hash: str,
        **kwargs,
    ):
        if not has_ec_transfer():
            logger.debug("Not have ec transfer please check")
            return
        connector = get_ec_transfer()
        connector.save_caches(encoder_cache=encoder_cache, mm_hash=mm_hash, **kwargs)

    @staticmethod
    def maybe_get_ec_connector_output(
        scheduler_output: "SchedulerOutput",
        encoder_cache: dict[str, torch.Tensor],
        **kwargs,
    ) -> AbstractContextManager[ECConnectorOutput | None]:
        return (
            ECConnectorModelRunnerMixin._get_ec_connector_output(
                scheduler_output, encoder_cache, **kwargs
            )
            if has_ec_transfer()
            else nullcontext()
        )

    # This context manager must be used within an active forward context.
    # It encapsulates the entire EC connector lifecycle within execute_model
    @staticmethod
    @contextmanager
    def _get_ec_connector_output(
        scheduler_output: "SchedulerOutput",
        encoder_cache: dict[str, torch.Tensor],
        **kwargs,
    ) -> Generator[ECConnectorOutput, None, None]:
        output = ECConnectorOutput()

        ec_connector = get_ec_transfer()
        assert isinstance(ec_connector, ECConnectorBase)
        assert scheduler_output.ec_connector_metadata is not None
        ec_connector.bind_connector_metadata(scheduler_output.ec_connector_metadata)

        # Load caches for consumer or both roles.
        # vit-artifact rank0-pull broadcast: encoder output is TP-invariant
        # (merger RowParallel all-reduce gives every rank the full tensor),
        # so only TP rank 0 fetches from the store and bytes are broadcast
        # over the TP group — one GET per image instead of one per rank.
        if ec_connector.is_consumer and not _ec_load_via_rank0_broadcast(
            ec_connector, encoder_cache, **kwargs
        ):
            ec_connector.start_load_caches(encoder_cache, **kwargs)

        # vit-artifact E store-verify resave (VIT_ARTIFACT_E_VERIFY_STORE=1):
        # L1-hit items whose artifact was missing from the store — re-upload
        # the L1-resident tensor (idempotent: uploader's store.has() decides).
        resave = getattr(scheduler_output.ec_connector_metadata, "resave", None)
        if resave:
            for mm_hash, grid in resave.items():
                if mm_hash not in encoder_cache:
                    logger.warning(
                        "vit-artifact resave mm_hash=%s skipped — tensor not "
                        "in worker encoder cache",
                        mm_hash,
                    )
                    continue
                ec_connector.save_caches(
                    encoder_cache=encoder_cache, mm_hash=mm_hash, grid_thw=grid
                )

        try:
            yield output
        finally:
            output.finished_sending, output.finished_recving = (
                ec_connector.get_finished(scheduler_output.finished_req_ids)
            )

            ec_connector.clear_connector_metadata()
