# SPDX-License-Identifier: Apache-2.0
"""vit-artifact no-image synthesis helpers (design §5.2.1/§5.2.2, plan C).

The chat front-end hook lives in chat_utils.parse_image (sync) and
_image_with_uuid_async (async — the one OpenAI chat actually uses); this
module holds the predicates, the h128 bridge, and the placeholder-image
construction that lets the PD processor run without fetching the image.

Placeholder rationale (handoff §6.8.3.1): the engine's processor-cache
check (processor.py _get_cache_missing_items) raises on data=None for
items its cache doesn't hold. A black image constructed at the EXACT
grid recorded in the artifact manifest passes that check and produces
identical token counts / placeholder expansion / mrope positions — only
the pixel values differ, and those are never consumed: the scheduler
routes artifact hits to external_load (never into the encoder batch), so
the worker's real embedding is the only writer of encoder_cache.

Grid math (verified against Qwen3-VL processor, transformers 4.57):
  grid unit = patch (16px); H = t*h*16, W = t*w*16.
  Forward-construction only — NEVER reverse-guess from num_mm_tokens
  (aspect ratio drives mrope positions).
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

_PATCH_SIZE = 16

# mm_hash -> grid tuple cached across requests: manifest lookups are
# synchronous oss2 calls; the async parser must not re-issue them per
# request (residual #2, handoff §6.8.3.1). Misses (grid=None) are NOT
# memoized — an artifact that appears later (E just committed) must be
# picked up without a PD restart; the retry cost is one store GET per
# request until then, and those requests fail at has_cache_item anyway.
_GRID_MEMO: dict[str, tuple[int, ...]] = {}


def synth_enabled() -> bool:
    return os.getenv("VLLM_VIT_SYNTH", "0") == "1"


def url_key_enabled() -> bool:
    """E-side URL-key mode: fetch the image as usual, but key the encoder
    cache by h128(url) instead of the engine content hash — the same key
    the PD synthesis path computes, so both sides land on one cache key
    with no uuid field in the request at all."""
    return os.getenv("VIT_ARTIFACT_URL_KEY", "0") == "1"


def synth_uuid(url: str) -> str | None:
    """h128(normalized URL) via the vit-artifact package.

    Returns None for non-URL media (data:/file:) — those keep the
    engine's content hash and miss semantics (fallback form, by design).
    Also None when the vit-artifact package is not installed: the
    frontend then keeps plain fetch semantics (upstream default).
    """
    if not (url.startswith(("http://", "https://", "oss://"))):
        return None
    try:
        from vit_artifact import mm_hash_from_url
    except ImportError:
        return None
    return mm_hash_from_url(url)


def _manifest_grid(mm_hash: str) -> tuple[int, ...] | None:
    """Look up grid_thw from the artifact manifest (memoized on hit).

    check_identity=False: the frontend process has no engine config,
    so the model/dtype defense cannot be evaluated here — the full
    defense runs later in the consumer's has_cache_item (gate 3).
    """
    if mm_hash in _GRID_MEMO:
        return _GRID_MEMO[mm_hash]
    grid: tuple[int, ...] | None = None
    try:
        from vit_artifact import open_store

        store = open_store(os.environ["VIT_ARTIFACT_URI"])
        manifest = store.get_ready_manifest(mm_hash, check_identity=False)
        if manifest is not None and manifest.grid_thw is not None:
            grid = tuple(int(x) for x in manifest.grid_thw)
    except Exception as e:  # noqa: BLE001 — placeholder is best-effort
        logger.warning(
            "vit-artifact synth: manifest lookup failed for %s: %r", mm_hash, e
        )
    if grid is not None:
        _GRID_MEMO[mm_hash] = grid
    return grid


def synth_placeholder(url: str):
    """Black PIL image at the manifest grid, or None when unavailable.

    Forward-construction: H = t*h*16, W = t*w*16. The image is only a
    shape carrier — the processor produces correct token counts and mrope
    from the grid, and the real embedding comes from the artifact store.
    """
    mm_hash = synth_uuid(url)
    if mm_hash is None:
        return None
    grid = _manifest_grid(mm_hash)
    if grid is None or len(grid) != 3:
        # Old artifact (pre-0.2.3, no grid) or lookup failure: no
        # placeholder possible; caller falls back to fetching the image.
        return None
    t, h, w = grid
    height, width = t * h * _PATCH_SIZE, t * w * _PATCH_SIZE
    from PIL import Image

    return Image.new("RGB", (width, height))
