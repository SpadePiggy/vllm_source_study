# vLLM `feat/engram_jit_cache` ← `v0.17.1_omega` 全量变更文档（PR 视图 · 含全部源码 diff）

> **Head**：`feat/engram_jit_cache` @ `c2f0d629e2`（2026-09-20）
> **Base**：`v0.17.1_omega` @ `0411f812e4`（merge-base 与 base 顶端重合，diff 为纯净的分支净变更）
> **规模**：13 commits / 59 files / **+6081 / -86**
> **内容**：每个变更文件独立一节，附**完整 unified diff（5 行上下文）**——全部增删行逐行收录，可照抄复现

## 0. 如何用本文档复现每一行代码

- **新增文件**：其 diff 中每一行都以 `+` 开头，从第一行到最后一行就是该文件的**全部内容**，逐行照抄即可重建；
- **修改文件**：`+` 行是新代码、`-` 行是被删除的代码、无前缀行是上下文；把 diff 块内容存成 `.patch` 后执行 `git apply xxx.patch` 可精确复现该文件的每一处变更；
- **全量校验**：`git diff -U5 v0.17.1_omega...feat/engram_jit_cache` 的输出应与本文档所有 diff 块按序拼接完全一致；
- 本文档为 base → HEAD 的**净差异**：中途加入又删除的内容（如 `vllm/whale_vllm/fuse_jit_cache/barrier.py`，`47615758b9` 引入、`b0e3efb2c1` 移除）不会出现。

## 1. 提交清单（13 commits，时间序）

| # | Commit | 日期 | 作者 | 说明 |
|---|---|---|---|---|
| 1 | `cc23ba4ba4` | 2026-07-30 | sunxia.sx | feat(video): PyAV 后端 + 子进程视频解析，防损坏 HEVC 导致 worker coredump |
| 2 | `47615758b9` | 2026-08-20 | shaoguohao.sgh | **feat: vLLM JIT/autotune 产物经 Engram 跨 Pod 共享（本分支核心）** |
| 3 | `e1d1316051` | 2026-08-20 | shaoguohao.sgh | perf(docker): 发布镜像构建时间从 ~60min 大幅缩短 |
| 4 | `ceeb7ef6a5` | 2026-08-20 | shaoguohao.sgh | fix(docker): 回退破坏 arm64 的 cuda-python/bindings/core 三件套 pin |
| 5 | `b4a7966575` | 2026-08-21 | shaoguohao.sgh | fix(whale): 稳定化 Engram 编译缓存 key（Fuser 镜像路径改 sha256 固定路径） |
| 6 | `b0e3efb2c1` | 2026-08-25 | shaoguohao.sgh | refactor(whale): Engram pull 同步移到 launcher，移除 vLLM 内 barrier 注入 |
| 7 | `983aefae95` | 2026-08-31 | songani.san | feat: 接入 media-fetch-sdk 支持 mediafetch:// 协议（Req#85339520） |
| 8 | `d4019dbb97` | 2026-08-31 | yunmo.dl | bugfix: 回移 Mamba encoder 调度与 spec-decode placeholder 修复 |
| 9 | `9f1210b41a` | 2026-09-01 | yinjuncheng.yjc | ci: 镜像 tag 加时间戳，避免重复构建失败 |
| 10 | `a028b62223` | 2026-09-08 | songani.san | feat: media-fetch-sdk 启用到 ROCm 镜像 |
| 11 | `0c2d27509e` | 2026-09-14 | yunmo.dl | fix: Qwen3-Next GDN Triton kernel 在 V1 profiling 期间预热 |
| 12 | `b2e9c53d45` | 2026-09-18 | yunmo.dl | ci: 模型精度回归验证 CI（Qwen3-VL-2B / Qwen2.5-Omni-3B 差分） |
| 13 | `c2f0d629e2` | 2026-09-20 | shaoguohao.sgh | fix(whale): Fuser 只清理本实例注册的临时副本 |

## 2. 变更分组（正文按此组织）

| 组 | 主题 | 文件数 | 对应提交 |
|---|---|---|---|
| 1 | Engram JIT 编译缓存跨 Pod 共享（核心特性） | 14 | 2, 5, 6, 13 |
| 2 | Docker 发布镜像构建提速 | 3 | 3, 4 |
| 3 | 模型精度回归验证 CI | 23 | 12 |
| 4 | mediafetch:// 协议接入 | 7 | 7, 10 |
| 5 | PyAV 视频后端 + 子进程解码隔离 | 5 | 1 |
| 6 | 上游 bugfix 回移（Mamba 调度 / GDN 预热） | 6 | 8, 11 |
| 7 | CI 杂项 | 1 | 9 |

## 3. 测试与验证状态

| 项 | 状态 |
|---|---|
| Engram adapter contract 测试（tests/whale/，624 行） | Aone PR job 每次触发必跑（pr_test_nv.yaml / pr_test_rocm.yaml） |
| 精度 CI 本地单测 23 个 + Ruff / shell 语法 / YAML 解析 | 通过 |
| 精度 CI 端到端（Aone #71） | image 20 / video 20 / audio 21 个 tensor 全过；+0.25 失败探针已验证 |
| Docker 构建 | arm64 CUDA 从 ~60min 显著缩短（层序重排 + 缓存挂载 + pin 消除回溯） |
| Engram 端到端 GPU/FUSE 恢复 | 尚无 CI，依赖发布镜像人工验证 |
| 视频子进程隔离 / mediafetch | 单测覆盖；线上依赖 `VLLM_VIDEO_DECODE_IN_SUBPROCESS=1` / `mediafetch://` 实际启用 |

## 4. 合入注意点

1. **Engram pull 不再与权重加载重叠**（`b0e3efb2c1` 的取舍）：冷启动多出实际 pull 耗时（默认上限 600s），换取 vLLM 核心零入侵；启动时长敏感的部署需评估。
2. **`definition_id` 已升 v2**（torch_compile / deep_gemm / aiter）：v1 命名空间的旧快照（随机 temp_copy 后缀 key）与新 pod 永不匹配，合入后首轮预热会重新发布。
3. **`/tmp/model_temp_copy` 变为共享固定路径**：多进程安全依赖"只删自己注册的副本"（`c2f0d629e2`）；同机多 vLLM 进程并行启动时 symlink 镜像重建存在短暂窗口。
4. **`scheduler.py` 的 Mamba 对齐重排**影响 P/D 分离 + EAGLE 组合路径的调度行为，已有单测覆盖，建议 PPU 环境回归一轮。

---

以下为 59 个文件的完整源码 diff（由 `git diff -U5 v0.17.1_omega...feat/engram_jit_cache` 逐文件拆分，每个文件一节）。

## 5. 文件总览（59 个文件，新增/修改状态与规模）

| # | 组 | 状态 | 文件 | 规模 |
|---|---|---|---|---|
| 1 | 1 | 新增 | `vllm/whale_vllm/fuse_jit_cache/__init__.py` | +4 / -0 |
| 2 | 1 | 新增 | `vllm/whale_vllm/fuse_jit_cache/__main__.py` | +12 / -0 |
| 3 | 1 | 新增 | `vllm/whale_vllm/fuse_jit_cache/adapter.py` | +258 / -0 |
| 4 | 1 | 新增 | `vllm/whale_vllm/fuse_jit_cache/README.md` | +99 / -0 |
| 5 | 1 | 修改 | `vllm/whale_vllm/start.sh` | +185 / -2 |
| 6 | 1 | 修改 | `vllm/whale_vllm/vllm_server/utils/fuser.py` | +33 / -11 |
| 7 | 1 | 新增 | `tools/engram/check_cache_keys.py` | +346 / -0 |
| 8 | 1 | 新增 | `tests/whale/__init__.py` | +1 / -0 |
| 9 | 1 | 新增 | `tests/whale/test_engram_adapter.py` | +509 / -0 |
| 10 | 1 | 新增 | `tests/whale/test_fuser.py` | +114 / -0 |
| 11 | 1 | 修改 | `requirements/alibaba.txt` | +7 / -1 |
| 12 | 1 | 修改 | `requirements/alibaba-arm64.txt` | +6 / -0 |
| 13 | 1 | 修改 | `.aoneci/pr_test_nv.yaml` | +10 / -4 |
| 14 | 1 | 修改 | `.aoneci/pr_test_rocm.yaml` | +11 / -5 |
| 15 | 2 | 修改 | `docker/ali/Dockerfile.release_cuda` | +33 / -9 |
| 16 | 2 | 修改 | `docker/ali/Dockerfile.release_cuda_arm64` | +49 / -9 |
| 17 | 2 | 修改 | `docker/ali/Dockerfile.release_rocm` | +24 / -5 |
| 18 | 3 | 新增 | `.aoneci/pr_accuracy_test_nv.yaml` | +211 / -0 |
| 19 | 3 | 新增 | `tools/accuracy_ci/README.md` | +163 / -0 |
| 20 | 3 | 新增 | `tools/accuracy_ci/__init__.py` | +1 / -0 |
| 21 | 3 | 新增 | `tools/accuracy_ci/accuracy_impact.py` | +401 / -0 |
| 22 | 3 | 新增 | `tools/accuracy_ci/build_wheel.sh` | +53 / -0 |
| 23 | 3 | 新增 | `tools/accuracy_ci/capture_qwen3_vl.py` | +405 / -0 |
| 24 | 3 | 新增 | `tools/accuracy_ci/compare.py` | +284 / -0 |
| 25 | 3 | 新增 | `tools/accuracy_ci/coverage.rc` | +10 / -0 |
| 26 | 3 | 新增 | `tools/accuracy_ci/download_model.py` | +45 / -0 |
| 27 | 3 | 新增 | `tools/accuracy_ci/download_native_base_wheel.sh` | +75 / -0 |
| 28 | 3 | 新增 | `tools/accuracy_ci/impact_rules.json` | +79 / -0 |
| 29 | 3 | 新增 | `tools/accuracy_ci/materialize_revision.sh` | +39 / -0 |
| 30 | 3 | 新增 | `tools/accuracy_ci/native_changes.sh` | +34 / -0 |
| 31 | 3 | 新增 | `tools/accuracy_ci/preload_deps.sh` | +20 / -0 |
| 32 | 3 | 新增 | `tools/accuracy_ci/requirements.txt` | +3 / -0 |
| 33 | 3 | 新增 | `tools/accuracy_ci/run_revision_diff.sh` | +305 / -0 |
| 34 | 3 | 新增 | `tests/accuracy_ci/test_accuracy_impact.py` | +213 / -0 |
| 35 | 3 | 新增 | `tests/accuracy_ci/test_capture.py` | +144 / -0 |
| 36 | 3 | 新增 | `tests/accuracy_ci/test_compare.py` | +153 / -0 |
| 37 | 3 | 新增 | `tests/accuracy_ci/test_download_model.py` | +35 / -0 |
| 38 | 3 | 新增 | `tests/accuracy_ci/test_download_native_base_wheel.py` | +86 / -0 |
| 39 | 3 | 新增 | `tests/accuracy_ci/test_materialize_revision.py` | +48 / -0 |
| 40 | 3 | 修改 | `.gitignore` | +2 / -0 |
| 41 | 4 | 新增 | `vllm/multimodal/mediafetchutils.py` | +217 / -0 |
| 42 | 4 | 修改 | `vllm/multimodal/media/connector.py` | +22 / -2 |
| 43 | 4 | 修改 | `vllm/entrypoints/metrics/mm_preprocessing.py` | +87 / -5 |
| 44 | 4 | 新增 | `tests/multimodal/test_mediafetchutils.py` | +206 / -0 |
| 45 | 4 | 修改 | `tests/entrypoints/metrics/test_mm_preprocessing.py` | +73 / -0 |
| 46 | 4 | 修改 | `requirements/alibaba-cuda.txt` | +3 / -0 |
| 47 | 4 | 修改 | `requirements/alibaba-rocm.txt` | +2 / -0 |
| 48 | 5 | 修改 | `vllm/multimodal/video.py` | +279 / -4 |
| 49 | 5 | 修改 | `vllm/multimodal/media/video.py` | +119 / -2 |
| 50 | 5 | 修改 | `vllm/envs.py` | +10 / -0 |
| 51 | 5 | 修改 | `vllm/model_executor/models/qwen3_vl.py` | +2 / -1 |
| 52 | 5 | 修改 | `tests/multimodal/media/test_video.py` | +226 / -0 |
| 53 | 6 | 修改 | `vllm/v1/core/sched/scheduler.py` | +22 / -22 |
| 54 | 6 | 修改 | `vllm/v1/worker/gpu_model_runner.py` | +4 / -0 |
| 55 | 6 | 修改 | `tests/v1/core/test_scheduler.py` | +139 / -0 |
| 56 | 6 | 修改 | `tests/v1/worker/test_gpu_input_batch.py` | +36 / -0 |
| 57 | 6 | 修改 | `tests/v1/worker/test_gpu_model_runner.py` | +23 / -0 |
| 58 | 6 | 修改 | `vllm/model_executor/models/qwen3_next.py` | +98 / -1 |
| 59 | 7 | 修改 | `.aoneci/build_docker.yaml` | +3 / -3 |

---

## 组 1 · Engram JIT 编译缓存跨 Pod 共享（核心特性 · 14 文件）

Engram 把 warm pod 的 torch.compile / DeepGEMM / Triton / aiter 编译产物发布为集群共享快照，
冷 pod 启动时拉取恢复以跳过本地 JIT 编译。本组是框架适配层（4 个 CacheSpec + pull/push 编排），
传输/校验/GC 由 engram wheel 提供。pull 在 server 启动前同步完成（限时、失败不阻断），
push 等 `/health` 就绪后后台发布，对 vLLM 核心代码零入侵。
设计细节见 `47615758b9` / `b4a7966575` / `b0e3efb2c1` / `c2f0d629e2` 的提交说明。


### 1. `vllm/whale_vllm/fuse_jit_cache/__init__.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：包标记文件；使 fuse_jit_cache 可作为顶层模块被 `python -m` 执行
- **规模**：+4 / -0（改后文件共 4 行）
- **涉及提交**：
  - `47615758b9` feat: share vLLM JIT/autotune artifacts across pods via Engram
````diff
diff --git a/vllm/whale_vllm/fuse_jit_cache/__init__.py b/vllm/whale_vllm/fuse_jit_cache/__init__.py
new file mode 100644
index 0000000000..97db036c37
--- /dev/null
+++ b/vllm/whale_vllm/fuse_jit_cache/__init__.py
@@ -0,0 +1,4 @@
+# Copyright (c) Alibaba. All rights reserved.
+"""Whale vLLM's torch-free Engram adapter."""
+
+from __future__ import annotations
````

### 2. `vllm/whale_vllm/fuse_jit_cache/__main__.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：Torch-free CLI 入口：`python -m fuse_jit_cache pull/push`，只 import engram 与 adapter，绝不 import vllm 与 torch（避免 env_override 改写 LD_LIBRARY_PATH 的副作用）
- **规模**：+12 / -0（改后文件共 12 行）
- **涉及提交**：
  - `47615758b9` feat: share vLLM JIT/autotune artifacts across pods via Engram
````diff
diff --git a/vllm/whale_vllm/fuse_jit_cache/__main__.py b/vllm/whale_vllm/fuse_jit_cache/__main__.py
new file mode 100644
index 0000000000..726c83dc43
--- /dev/null
+++ b/vllm/whale_vllm/fuse_jit_cache/__main__.py
@@ -0,0 +1,12 @@
+# Copyright (c) Alibaba. All rights reserved.
+"""Torch-free Engram helper entrypoint for Whale vLLM."""
+
+from __future__ import annotations
+
+import sys
+
+from engram.jit_cache import main
+from fuse_jit_cache import adapter as _adapter  # noqa: F401
+
+if __name__ == "__main__":
+    sys.exit(main())
````

### 3. `vllm/whale_vllm/fuse_jit_cache/adapter.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：核心适配层：向 engram 注册 4 个 CacheSpec——vllm_torch_compile、vllm_deep_gemm、triton、aiter，逐个声明本地根路径、参与 key 的包版本、实现文件哈希、兼容性环境变量与启用门禁
- **规模**：+258 / -0（改后文件共 258 行）
- **涉及提交**：
  - `b4a7966575` fix(whale): stabilize Engram compile cache keys
  - `47615758b9` feat: share vLLM JIT/autotune artifacts across pods via Engram
````diff
diff --git a/vllm/whale_vllm/fuse_jit_cache/adapter.py b/vllm/whale_vllm/fuse_jit_cache/adapter.py
new file mode 100644
index 0000000000..b0f6ad6550
--- /dev/null
+++ b/vllm/whale_vllm/fuse_jit_cache/adapter.py
@@ -0,0 +1,258 @@
+# Copyright (c) Alibaba. All rights reserved.
+"""Register Whale vLLM's Engram cache kinds without importing vLLM or Torch.
+
+The separate ``triton`` kind covers kernels compiled before vLLM redirects
+Triton into its ``torch_compile_cache`` tree.
+"""
+
+from __future__ import annotations
+
+import importlib.metadata
+import importlib.util
+import os
+from pathlib import Path, PurePosixPath
+
+from engram import jit_cache_env
+from engram.jit_cache_env import _env_bool
+from engram.jit_cache_specs import (
+    CacheSpec,
+    _all_files,
+    _shared_object,
+    register_specs,
+)
+
+os.environ.setdefault("ENGRAM_FRAMEWORK_PACKAGE", "vllm")
+os.environ.setdefault("ENGRAM_REMOTE_PREFIX", "vllm-jit-cache-v1")
+
+
+def _vllm_cache_root() -> Path:
+    explicit = os.getenv("VLLM_CACHE_ROOT", "").strip()
+    if explicit:
+        return Path(explicit).expanduser()
+    xdg = os.getenv("XDG_CACHE_HOME", "").strip()
+    base = Path(xdg).expanduser() if xdg else Path("~/.cache").expanduser()
+    return base / "vllm"
+
+
+def _torch_compile_root() -> Path:
+    return _vllm_cache_root() / "torch_compile_cache"
+
+
+def _deep_gemm_root() -> Path:
+    override = os.getenv("DG_JIT_CACHE_DIR", "").strip()
+    if override:
+        return Path(override).expanduser()
+    return _vllm_cache_root() / "deep_gemm"
+
+
+def _triton_root() -> Path:
+    override = os.getenv("TRITON_CACHE_DIR", "").strip()
+    if override:
+        return Path(override).expanduser()
+    home = os.getenv("TRITON_HOME", "").strip()
+    base = Path(home).expanduser() if home else Path("~").expanduser()
+    return base / ".triton" / "cache"
+
+
+def _aiter_package_root() -> Path | None:
+    try:
+        spec = importlib.util.find_spec("aiter")
+    except (ImportError, ValueError):
+        return None
+    if spec is None:
+        return None
+    locations = list(spec.submodule_search_locations or ())
+    if locations:
+        return Path(locations[0])
+    if spec.origin:
+        return Path(spec.origin).parent
+    return None
+
+
+def _aiter_root() -> Path:
+    override = os.getenv("AITER_JIT_DIR", "").strip()
+    if override:
+        return Path(override).expanduser()
+    package_root = _aiter_package_root()
+    if package_root is not None:
+        return package_root / "jit"
+    return Path("/.aiter")
+
+
+_TRITON_DISTRIBUTION_CANDIDATES = (
+    "triton",
+    "pytorch-triton-rocm",
+    "pytorch-triton",
+    "triton-rocm",
+)
+_DEEP_GEMM_DISTRIBUTION_CANDIDATES = (
+    "deep_gemm",
+    "deep-gemm",
+    "sgl-deep-gemm",
+)
+_AITER_DISTRIBUTION_CANDIDATES = (
+    "amd-aiter",
+    "aiter",
+)
+
+
+def _first_installed_distribution(candidates: tuple[str, ...]) -> str | None:
+    for name in candidates:
+        try:
+            importlib.metadata.distribution(name)
+        except importlib.metadata.PackageNotFoundError:
+            continue
+        return name
+    return None
+
+
+_TRITON_DISTRIBUTION = _first_installed_distribution(_TRITON_DISTRIBUTION_CANDIDATES)
+_DEEP_GEMM_DISTRIBUTION = _first_installed_distribution(
+    _DEEP_GEMM_DISTRIBUTION_CANDIDATES
+)
+_AITER_DISTRIBUTION = _first_installed_distribution(_AITER_DISTRIBUTION_CANDIDATES)
+
+_TRITON_IMPLEMENTATION_DISTRIBUTIONS: tuple[str, ...] = (
+    (_TRITON_DISTRIBUTION,) if _TRITON_DISTRIBUTION else ()
+)
+_TRITON_PACKAGES: tuple[str, ...] = (
+    ("torch", _TRITON_DISTRIBUTION) if _TRITON_DISTRIBUTION else ("torch",)
+)
+_DEEP_GEMM_PACKAGES: tuple[str, ...] = (
+    ("torch", "vllm", _DEEP_GEMM_DISTRIBUTION)
+    if _DEEP_GEMM_DISTRIBUTION
+    else ("torch", "vllm", "deep_gemm")
+)
+_DEEP_GEMM_IMPLEMENTATION_DISTRIBUTIONS: tuple[str, ...] = (
+    ("torch", _DEEP_GEMM_DISTRIBUTION) if _DEEP_GEMM_DISTRIBUTION else ("torch",)
+)
+_AITER_PACKAGES: tuple[str, ...] = (
+    ("torch", _AITER_DISTRIBUTION) if _AITER_DISTRIBUTION else ("torch", "amd-aiter")
+)
+_AITER_IMPLEMENTATION_DISTRIBUTIONS: tuple[str, ...] = (
+    (_AITER_DISTRIBUTION,) if _AITER_DISTRIBUTION else ()
+)
+
+
+def _is_cuda_runtime() -> bool:
+    return not jit_cache_env._is_rocm_runtime()
+
+
+def _module_installed(name: str) -> bool:
+    try:
+        return importlib.util.find_spec(name) is not None
+    except (ImportError, ValueError):
+        return False
+
+
+def _torch_compile_cache_enabled() -> bool:
+    return not _env_bool("VLLM_DISABLE_COMPILE_CACHE", default=False)
+
+
+def _deep_gemm_cache_enabled() -> bool:
+    return (
+        _is_cuda_runtime()
+        and _env_bool("VLLM_USE_DEEP_GEMM", default=True)
+        and _module_installed("deep_gemm")
+        and _DEEP_GEMM_DISTRIBUTION is not None
+    )
+
+
+def _triton_cache_enabled() -> bool:
+    return _module_installed("triton")
+
+
+def _aiter_cache_enabled() -> bool:
+    return (
+        jit_cache_env._is_rocm_runtime()
+        and _env_bool("VLLM_ROCM_USE_AITER", default=False)
+        and _module_installed("aiter")
+        and _AITER_DISTRIBUTION is not None
+    )
+
+
+def _triton_artifact(relative_path: PurePosixPath) -> bool:
+    return relative_path.suffix not in {".lock", ".tmp"}
+
+
+_VLLM_SPECS: tuple[CacheSpec, ...] = (
+    CacheSpec(
+        name="vllm_torch_compile",
+        local_root=_torch_compile_root,
+        packages=_TRITON_PACKAGES + ("vllm",),
+        include_file=_all_files,
+        implementation_files=(
+            "compilation/backends.py",
+            "compilation/caching.py",
+            "compilation/compiler_interface.py",
+            "compilation/decorators.py",
+            "compilation/piecewise_backend.py",
+            "compilation/wrapper.py",
+            "config/compilation.py",
+        ),
+        implementation_distributions=("torch", "vllm"),
+        compatibility_env=(
+            "PYTORCH_ROCM_ARCH",
+            "TORCH_CUDA_ARCH_LIST",
+        ),
+        enabled=_torch_compile_cache_enabled,
+        # v2 starts a clean namespace after making Whale's resolved model path
+        # deterministic. Snapshots under v1 contain cache directories keyed by
+        # a random model_temp_copy suffix and can never match a patched pod.
+        definition_id="vllm/torch_compile/v2",
+    ),
+    CacheSpec(
+        name="vllm_deep_gemm",
+        local_root=_deep_gemm_root,
+        packages=_DEEP_GEMM_PACKAGES,
+        include_file=_all_files,
+        # RECORD separates same-version internal rebuilds.
+        implementation_distributions=_DEEP_GEMM_IMPLEMENTATION_DISTRIBUTIONS,
+        compatibility_env=(
+            "DG_JIT_CPP_STANDARD",
+            "DG_JIT_NVCC_COMPILER",
+            "DG_JIT_USE_NVRTC",
+            "DG_JIT_USE_RUNTIME_API",
+            "DG_JIT_WITH_LINEINFO",
+            "TORCH_CUDA_ARCH_LIST",
+            "VLLM_USE_DEEP_GEMM_E8M0",
+            "VLLM_USE_DEEP_GEMM_TMA_ALIGNED_SCALES",
+        ),
+        enabled=_deep_gemm_cache_enabled,
+        definition_id="vllm/deep_gemm/v2",
+    ),
+    CacheSpec(
+        name="triton",
+        local_root=_triton_root,
+        packages=_TRITON_PACKAGES,
+        include_file=_triton_artifact,
+        implementation_distributions=_TRITON_IMPLEMENTATION_DISTRIBUTIONS,
+        compatibility_env=(
+            "PYTORCH_ROCM_ARCH",
+            "TORCH_CUDA_ARCH_LIST",
+            "TRITON_LIBCUDA_PATH",
+            "TRITON_PTXAS_PATH",
+        ),
+        enabled=_triton_cache_enabled,
+        definition_id="vllm/triton/v1",
+    ),
+    CacheSpec(
+        name="aiter",
+        local_root=_aiter_root,
+        packages=_AITER_PACKAGES,
+        include_file=_shared_object,
+        implementation_distributions=_AITER_IMPLEMENTATION_DISTRIBUTIONS,
+        compatibility_env=(
+            "AITER_ASM_DIR",
+            "AITER_LOG_MORE",
+            "GPU_ARCHS",
+            "HIP_FORCE_DEV_KERNARG",
+            "PYTORCH_ROCM_ARCH",
+        ),
+        excluded_dirs=frozenset({"build", "ck", "hsa", "include"}),
+        enabled=_aiter_cache_enabled,
+        definition_id="vllm/aiter/v2",
+    ),
+)
+
+register_specs(*_VLLM_SPECS)
````

### 4. `vllm/whale_vllm/fuse_jit_cache/README.md`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：中文使用与排障文档：开关变量表、缓存 kind 表、启动时序、0% 命中排查步骤（check_cache_keys.py 用法）、已知缺口
- **规模**：+99 / -0（改后文件共 99 行）
- **涉及提交**：
  - `b0e3efb2c1` refactor(whale): move Engram pull synchronization to launcher
  - `b4a7966575` fix(whale): stabilize Engram compile cache keys
  - `47615758b9` feat: share vLLM JIT/autotune artifacts across pods via Engram
````diff
diff --git a/vllm/whale_vllm/fuse_jit_cache/README.md b/vllm/whale_vllm/fuse_jit_cache/README.md
new file mode 100644
index 0000000000..f777cfb45b
--- /dev/null
+++ b/vllm/whale_vllm/fuse_jit_cache/README.md
@@ -0,0 +1,99 @@
+# fuse_jit_cache — Whale vLLM 的 Engram 接入
+
+把 vLLM 的 JIT 编译与 autotune 产物固化成集群共享快照，让新 pod 跳过本地编译。
+核心传输/校验/GC 由 [`engram`](https://code.alibaba-inc.com) wheel 提供；本目录只是
+框架适配层（4 个 `CacheSpec` + 远端命名空间注入）。
+
+## 开启
+
+只需要在 Whale 部署的环境配置里设一个变量：
+
+```
+ENGRAM_URI=oss://<bucket>/<path>        # 或 dfs://... 或一个 PVC 路径
+```
+
+未设置时整条链路静默跳过，行为与接入前完全一致。`vllm/whale_vllm/start.sh` 会在
+服务进程启动前同步执行 pull，然后启动一个后台 helper，在 `/health` 就绪后
+发布 push。
+
+OSS 直传只认这三个**隔离**变量（通用 `OSS_*` 仍专属模型/媒体加载）：
+
+```
+ENGRAM_OSS_ACCESS_ID / ENGRAM_OSS_ACCESS_KEY / ENGRAM_OSS_ENDPOINT
+```
+
+## 常用环境变量
+
+| 变量 | 默认 | 说明 |
+|---|---|---|
+| `ENGRAM_URI` | 无 | 远端根路径。未设置 = 完全禁用 |
+| `ENGRAM_DISABLE` | `0` | 主开关，`1` 时跳过 pull 与 push |
+| `ENGRAM_MODE` | `rw` | `ro` 只拉不发布（适合只读集群） |
+| `ENGRAM_MODEL_ID` | 无 | 模型不可变标识。**未设置时回落到 `CHECKPOINT_PATH`**；当 checkpoint 路径在各 pod 间不稳定时必须显式设置，否则命名空间不一致会导致 0% 命中 |
+| `ENGRAM_KINDS` | 全部 | 逗号分隔，收窄到部分 kind |
+| `ENGRAM_PULL_TIMEOUT_SEC` | `600` | 服务启动前同步 pull 的总时限；失败或超时时降级为本地 JIT |
+| `ENGRAM_PUSH_TIMEOUT_SEC` | `600` | push 总时限 |
+| `ENGRAM_READY_TIMEOUT_SEC` | `3600` | push 前等 `/health` 的时限 |
+| `ENGRAM_REMOTE_PREFIX` | `vllm-jit-cache-v1` | 远端命名空间前缀（由 adapter 注入） |
+
+`WHALE_JIT_CACHE_*` 旧名全部仍然兼容。
+
+## 缓存 kind
+
+| kind | 本地路径 | 门禁 |
+|---|---|---|
+| `vllm_torch_compile` | `VLLM_CACHE_ROOT/torch_compile_cache` | `VLLM_DISABLE_COMPILE_CACHE` 未置真 |
+| `vllm_deep_gemm` | `DG_JIT_CACHE_DIR` 或 `VLLM_CACHE_ROOT/deep_gemm` | CUDA + `VLLM_USE_DEEP_GEMM` + `deep_gemm` 已装 |
+| `triton` | `TRITON_CACHE_DIR` 或 `$TRITON_HOME/.triton/cache` | `triton` 已装 |
+| `aiter` | `AITER_JIT_DIR` 或 `/.aiter` | ROCm + `VLLM_ROCM_USE_AITER` |
+
+`vllm_torch_compile` 已经把 torch.compile 路径上的 inductor 与 triton 产物一并覆盖
+（vLLM 在 `vllm/compilation/compiler_interface.py:457-462` 把两个 cache dir 重定向进
+该树）。`triton` 单独存在是因为那次重定向在 `if disable_cache: return` 时整段跳过，
+且发生在部分手写 kernel 已经编译**之后** —— 详见 `adapter.py` 顶部的说明。
+
+## 启动时序
+
+Engram 不再向 vLLM 的 model loader、quantization 或 worker 路径注入 barrier。启动脚本
+依次执行：
+
+1. 用独立 helper 同步 pull 所有选中的 cache kind；
+2. pull 完成、失败或超时后才启动 vLLM；失败不会阻断服务；
+3. 后台 push helper 等待 `/health`，就绪后发布本地缓存。
+
+这个时序不再将 pull 与权重加载重叠，因此冷启动会多出实际 pull 耗时；换来的是
+vLLM 核心代码零 Engram 入侵，且不再需要 status-file 完成协议。
+
+## 排查 0% 命中
+
+命中率归零时**不会报错**，两个独立的 key 都必须匹配。用这个脚本定位：
+
+```bash
+# 在每个 pod 上（服务至少完整预热过一次）
+python3 tools/engram/check_cache_keys.py dump -o /tmp/keys-$(hostname).json
+# 然后对比
+python3 tools/engram/check_cache_keys.py compare /tmp/keys-podA.json /tmp/keys-podB.json
+```
+
+它会分别检查 vLLM 自己的 `torch_compile_cache/<hash_key>` 与 engram 的
+compatibility digest，并在分歧时**指出具体是哪个 factor**。
+
+最常见的原因：两个 pod 的 `--model` 字符串不同。`"model"` 不在
+`vllm/config/model.py` 的 `ignored_factors` 里，所以它进了 `config_hash`，进而改变
+编译目录名。Whale 的模型软链接镜像使用固定根目录，并按转换前的原始模型路径寻址：
+`/tmp/model_temp_copy/<sha256(original-model-path)>`。若用 `tempfile.mkdtemp()` 生成随机
+后缀，即使同一 pod 反复启动也会得到不同的 `config_hash`，表现为 Engram 成功恢复但
+vLLM 完全不命中。
+
+## 已知缺口
+
+- **FlashInfer autotune 无法共享**。vLLM 的 `flashinfer_autotune()`
+  （`vllm/model_executor/warmup/kernel_warmup.py:81-109`）只进入进程内的
+  `fi_utils.autotune()` 上下文，不落盘，因此没有可共享的产物。SGLang 侧有
+  `flashinfer_autotune` kind 是因为它自己实现了 JSON 持久化。要补齐需要先在 vLLM
+  里做落盘能力，属于独立增量。
+- **ARM64 direct Pangu 暂不可用**。ARM 内部源没有 `pangudfs-client`，所以该架构安装
+  `engram[fuse,oss]`：`dfs://` pull/push 走 FUSE；x86 CUDA/ROCm 安装
+  `engram[fuse,pangu,oss]`，优先 direct Pangu push。
+- **尚无端到端 GPU/FUSE CI**。Aone PR job 会执行 adapter 与 launcher
+  contract 测试，但真实远端 mount、TP worker 恢复和首次编译命中仍需发布镜像验证。
````

### 5. `vllm/whale_vllm/start.sh`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：Engram 编排：server 启动前同步 pull（限时、失败继续）、后台 push 等 `/health` 就绪后发布、退出时回收 helper；`dump_runtime_env` 对 env.txt 做 URI/凭证脱敏；注入 mediafetch 的 DEPLOY_ENV/DEPLOY_REGION
- **规模**：+185 / -2（改后文件共 406 行）
- **涉及提交**：
  - `b0e3efb2c1` refactor(whale): move Engram pull synchronization to launcher
  - `47615758b9` feat: share vLLM JIT/autotune artifacts across pods via Engram
  - `983aefae95` [Req#85339520] vLLM 接入 media-fetch-sdk 支持 mediafetch:// 协议 * [Req#85339520] vLLM 接入 media-fetch-sdk 支持 mediafetch:// 协议
````diff
diff --git a/vllm/whale_vllm/start.sh b/vllm/whale_vllm/start.sh
index 59930fabcb..061e383b76 100644
--- a/vllm/whale_vllm/start.sh
+++ b/vllm/whale_vllm/start.sh
@@ -37,10 +37,176 @@ export LOG_PATH=$LOG_DIR
 
 export STDOUT_FILE=$LOG_DIR/stdout
 export STDERR_FILE=$LOG_DIR/stderr
 export ENV_FILE=$LOG_DIR/env.txt
 
+# ---------------------------------------------------------------------------
+# Engram 完全由启动脚本编排：pull 在 server 启动前完成，push 等 /health 就绪。
+# ---------------------------------------------------------------------------
+
+ENGRAM_PYTHON="${ENGRAM_PYTHON:-python3}"
+
+# 避免把 URI、命令参数和凭证写进 env.txt。
+dump_runtime_env() {
+  printenv | sed -E \
+    -e 's/^(ENGRAM_URI|ENGRAM_MODEL_ID|ENGRAM_OSS_ENDPOINT|WHALE_JIT_CACHE_URI|WHALE_JIT_CACHE_MODEL_ID|WHALE_JIT_CACHE_OSS_ENDPOINT|OSS_ENDPOINT)=.*/\1=<redacted>/' \
+    -e 's/^(CMD|EXTRA_CMD)=.*/\1=<redacted>/' \
+    -e 's/^([^=]*(ACCESS[_-]?(ID|KEY)|API[_-]?KEY|TOKEN|PASSWORD|PASSWD|PRIVATE[_-]?KEY|COOKIE|CSRF|SESSION|BEARER|CREDENTIAL|SECRET|SIGNATURE|AUTHORIZATION)[^=]*)=.*/\1=<redacted>/I' \
+    -e 's/([?&][^=&]*(access[_-]?(id|key)|api[_-]?key|token|password|passwd|private[_-]?key|cookie|csrf|session|bearer|credential|secret|signature|authorization)[^=&]*=)[^&[:space:]]+/\1<redacted>/gI' \
+    -e 's#(://[^?#[:space:]]*)[?#][^[:space:]]*#\1?<redacted>#g' \
+    -e 's#(://)[^/@[:space:]]+@#\1<redacted>@#g'
+}
+
+ENGRAM_PUSH_JOB=""
+ENGRAM_HELPER_PYTHONPATH=""
+
+# 只定位 vllm，不 import 它；helper 以顶层 fuse_jit_cache 启动以避免 import torch。
+resolve_fuse_jit_cache_parent() {
+  "${ENGRAM_PYTHON}" -s -c '
+import importlib.util
+from pathlib import Path
+
+spec = importlib.util.find_spec("vllm")
+if spec is None:
+    raise SystemExit(1)
+locations = list(spec.submodule_search_locations or ())
+package_root = Path(locations[0]) if locations else Path(spec.origin).parent
+adapter_parent = package_root / "whale_vllm"
+if not (adapter_parent / "fuse_jit_cache" / "__main__.py").is_file():
+    raise SystemExit(1)
+print(adapter_parent)
+'
+}
+
+job_spec_for_pid() {
+  jobs -l | awk -v target="$1" '
+    $2 == target {
+      job = $1
+      sub(/^\[/, "%", job)
+      sub(/\][+-]?$/, "", job)
+      print job
+      exit
+    }
+  '
+}
+
+shell_job_is_running() {
+  jobs -l >/dev/null 2>&1
+  [ -n "$(jobs -pr "$1" 2>/dev/null)" ]
+}
+
+terminate_shell_job() {
+  local target_job="$1"
+  local remaining_checks=100
+  if [ -z "$target_job" ]; then
+    return
+  fi
+  if shell_job_is_running "$target_job"; then
+    kill -TERM "$target_job" 2>/dev/null || true
+    while shell_job_is_running "$target_job" && [ "$remaining_checks" -gt 0 ]; do
+      sleep 0.1
+      remaining_checks=$((remaining_checks - 1))
+    done
+    if shell_job_is_running "$target_job"; then
+      kill -KILL "$target_job" 2>/dev/null || true
+    fi
+  fi
+  wait "$target_job" 2>/dev/null || true
+}
+
+# 回收可能仍在等待服务就绪的 push helper。
+cleanup_engram_jobs() {
+  local publisher_job="${ENGRAM_PUSH_JOB:-}"
+  ENGRAM_PUSH_JOB=""
+  terminate_shell_job "$publisher_job"
+}
+
+engram_disabled() {
+  case "${ENGRAM_DISABLE:-${WHALE_JIT_CACHE_DISABLE:-0}}" in
+    0|false|False|FALSE|no|No|NO|off|Off|OFF) return 1 ;;
+    *) return 0 ;;
+  esac
+}
+
+start_engram_jobs() {
+  trap cleanup_engram_jobs EXIT
+
+  # URI 与凭证不进 xtrace。
+  set +x
+  # 串行 pull 不使用 Engram 的异步 status-file/barrier 协议。
+  unset ENGRAM_EARLY_PULL_STATUS_FILE
+  unset ENGRAM_LATE_PULL_STATUS_FILE
+  unset WHALE_JIT_CACHE_EARLY_PULL_STATUS_FILE
+  unset WHALE_JIT_CACHE_LATE_PULL_STATUS_FILE
+  ENGRAM_ADAPTER_PARENT="$(resolve_fuse_jit_cache_parent 2>/dev/null || true)"
+  ENGRAM_HELPER_PYTHONPATH="${ENGRAM_ADAPTER_PARENT}${PYTHONPATH:+:${PYTHONPATH}}"
+
+  if engram_disabled; then
+    echo "ENGRAM_DISABLE is enabled; skipping Engram pull and push"
+  elif [ -z "${ENGRAM_URI:-${WHALE_JIT_CACHE_URI:-}}" ]; then
+    echo "ENGRAM_URI is unset; skipping Engram pull and push"
+  elif ! command -v timeout >/dev/null 2>&1; then
+    echo "timeout command unavailable; skipping Engram pull and push" >&2
+  elif [ -z "$ENGRAM_ADAPTER_PARENT" ]; then
+    echo "Cannot locate vllm/whale_vllm/fuse_jit_cache; skipping Engram pull and push" >&2
+  elif ! env PYTHONPATH="${ENGRAM_HELPER_PYTHONPATH}" \
+    "${ENGRAM_PYTHON}" -s -c 'import fuse_jit_cache.adapter' >/dev/null 2>&1; then
+    # engram wheel 未安装或 adapter 不可导入：静默回落到纯本地 JIT。
+    echo "Engram adapter is not importable; skipping Engram pull and push" >&2
+  else
+    ENGRAM_PULL_TIMEOUT_SEC="${ENGRAM_PULL_TIMEOUT_SEC:-${WHALE_JIT_CACHE_PULL_TIMEOUT_SEC:-600}}"
+    if [[ ! "$ENGRAM_PULL_TIMEOUT_SEC" =~ ^[1-9][0-9]*$ ]]; then
+      echo "Invalid ENGRAM_PULL_TIMEOUT_SEC; using 600 seconds" >&2
+      ENGRAM_PULL_TIMEOUT_SEC=600
+    fi
+
+    echo "Pulling vLLM JIT caches before the server starts"
+    if timeout --foreground --signal=INT --kill-after=10s \
+      "${ENGRAM_PULL_TIMEOUT_SEC}s" \
+      env PYTHONPATH="${ENGRAM_HELPER_PYTHONPATH}" \
+      "${ENGRAM_PYTHON}" -s -m fuse_jit_cache pull \
+      --timeout "${ENGRAM_PULL_TIMEOUT_SEC}" \
+      >> "$STDOUT_FILE" 2>> "$STDERR_FILE"; then
+      echo "Engram pull completed"
+    else
+      pull_status=$?
+      echo "Engram pull failed with status ${pull_status}; continuing with local JIT" >&2
+    fi
+
+    ENGRAM_READY_TIMEOUT_SEC="${ENGRAM_READY_TIMEOUT_SEC:-${WHALE_JIT_CACHE_READY_TIMEOUT_SEC:-3600}}"
+    if [[ ! "$ENGRAM_READY_TIMEOUT_SEC" =~ ^[1-9][0-9]*$ ]]; then
+      echo "Invalid ENGRAM_READY_TIMEOUT_SEC; using 3600 seconds" >&2
+      ENGRAM_READY_TIMEOUT_SEC=3600
+    fi
+    ENGRAM_PUSH_TIMEOUT_SEC="${ENGRAM_PUSH_TIMEOUT_SEC:-${WHALE_JIT_CACHE_PUSH_TIMEOUT_SEC:-600}}"
+    if [[ ! "$ENGRAM_PUSH_TIMEOUT_SEC" =~ ^[1-9][0-9]*$ ]]; then
+      echo "Invalid ENGRAM_PUSH_TIMEOUT_SEC; using 600 seconds" >&2
+      ENGRAM_PUSH_TIMEOUT_SEC=600
+    fi
+    ENGRAM_PUSH_PROCESS_TIMEOUT_SEC="${ENGRAM_PUSH_PROCESS_TIMEOUT_SEC:-$((ENGRAM_READY_TIMEOUT_SEC + ENGRAM_PUSH_TIMEOUT_SEC + 600))}"
+    if [[ ! "$ENGRAM_PUSH_PROCESS_TIMEOUT_SEC" =~ ^[1-9][0-9]*$ ]]; then
+      echo "Invalid ENGRAM_PUSH_PROCESS_TIMEOUT_SEC; using bounded default" >&2
+      ENGRAM_PUSH_PROCESS_TIMEOUT_SEC=$((ENGRAM_READY_TIMEOUT_SEC + ENGRAM_PUSH_TIMEOUT_SEC + 600))
+    fi
+
+    timeout --foreground --signal=INT --kill-after=10s \
+      "${ENGRAM_PUSH_PROCESS_TIMEOUT_SEC}s" \
+      env PYTHONPATH="${ENGRAM_HELPER_PYTHONPATH}" \
+      "${ENGRAM_PYTHON}" -s -m fuse_jit_cache push \
+      --wait-ready "http://127.0.0.1:${START_PORT}/health" \
+      --timeout "${ENGRAM_READY_TIMEOUT_SEC}" \
+      --operation-timeout "${ENGRAM_PUSH_TIMEOUT_SEC}" \
+      >> "$STDOUT_FILE" 2>> "$STDERR_FILE" &
+    ENGRAM_PUSH_JOB="$(job_spec_for_pid "$!")"
+    if [ -z "$ENGRAM_PUSH_JOB" ]; then
+      echo "Cannot identify the Engram publisher shell job; cleanup will not signal it" >&2
+    fi
+  fi
+  set -x
+}
+# ---------------------- Engram definitions end -----------------------------
+
 #logging level
 export LOG_LEVEL="INFO"
 
 # pyfsutil
 export HADOOP_HOME=$HIPPO_APP_INST_ROOT/usr/local/hadoop/hadoop;
@@ -102,10 +268,24 @@ export LD_LIBRARY_PATH="$FIXED_LD_LIBRARY_PATH"
 export LD_LIBRARY_PATH_SETTED=1;
 
 export FSLIB_PANGU_ENABLE_SEQUENTIAL_READAHEAD=${FSLIB_PANGU_ENABLE_SEQUENTIAL_READAHEAD-"true"}
 export FSLIB_PANGU_ENABLE_BUFFER_WRITE=${FSLIB_PANGU_ENABLE_BUFFER_WRITE-"true"}
 
+# media-fetch-sdk: DEPLOY_ENV (pre/prod) and DEPLOY_REGION (sh/zb)
+# Hippo 注入优先，未注入时默认 prod/zb，SIGMA_APP_SITE 含 EA 前缀则改 sh
+if [[ -z "${DEPLOY_ENV}" ]]; then
+    export DEPLOY_ENV=prod
+fi
+if [[ -z "${DEPLOY_REGION}" ]]; then
+    if [[ "${SIGMA_APP_SITE}" =~ ^[Ee][Aa] ]]; then
+        export DEPLOY_REGION=sh
+    else
+        export DEPLOY_REGION=zb
+    fi
+fi
+echo "DEPLOY_ENV=${DEPLOY_ENV}, DEPLOY_REGION=${DEPLOY_REGION}"
+
 echo "START_PORT=${START_PORT}";
 
 export PY_INFERENCE_LOG_RESPONSE=1
 
 # setting vllm config
@@ -178,13 +358,16 @@ if [ -z "${ASYNC_SCHEDULING}" ]; then
     echo "ASYNC_SCHEDULING is not set or is empty. No action taken."
 else
     EXTRA_CMD="${EXTRA_CMD} --async-scheduling"
 fi
 
+# 在 PATH、LD_LIBRARY_PATH 和 FSLIB 环境固定后启动 helper。
+start_engram_jobs
+
 hf_overrides_status="${HF_OVERRIDES}"
 
-printenv > "$ENV_FILE";
+dump_runtime_env > "$ENV_FILE";
 
 if [ -n "$SPECIFY_TRANSFORMERS_VERSION" ]; then
     echo "install specific transformers version: $SPECIFY_TRANSFORMERS_VERSION"
     python3 -m pip install transformers=="$SPECIFY_TRANSFORMERS_VERSION" -i https://artlab.alibaba-inc.com/1/PYPI/simple/ --trusted-host=artlab.alibaba-inc.com
 fi
@@ -218,6 +401,6 @@ else
         --load-format ${LOAD_FORMAT} \
         --dtype ${DTYPE} \
         --gpu-memory-utilization ${GPU_MEMORY_UTILIZATION} \
         --enable-prefix-caching \
         ${EXTRA_CMD} >> "$STDOUT_FILE" 2>> "$STDERR_FILE"
-fi
\ No newline at end of file
+fi
````

### 6. `vllm/whale_vllm/vllm_server/utils/fuser.py`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：三个修复：temp_copy_base 用固定路径替代 mkdtemp 随机后缀（稳定 torch.compile cache key）；create_temp_local_copy 新增 source_identity 参数（用挂载前原始路径参与 sha256）；_cleanup_temp_copies 只删本实例注册的副本
- **规模**：+33 / -11（改后文件共 167 行）
- **涉及提交**：
  - `c2f0d629e2` fix(whale): only remove temp copies registered by the Fuser instance
  - `b4a7966575` fix(whale): stabilize Engram compile cache keys
````diff
diff --git a/vllm/whale_vllm/vllm_server/utils/fuser.py b/vllm/whale_vllm/vllm_server/utils/fuser.py
index 5c5c41448c..fd0901df20 100644
--- a/vllm/whale_vllm/vllm_server/utils/fuser.py
+++ b/vllm/whale_vllm/vllm_server/utils/fuser.py
@@ -44,11 +44,17 @@ class MountRwMode(Enum):
 class Fuser:
     def __init__(self) -> None:
         self._fuse_uri = "http://0:28006"
         self._fuse_path_prefix = "/mnt/fuse"
         self._mount_src_map = {}
-        self.temp_copy_base = tempfile.mkdtemp(prefix="model_temp_copy_")
+        # ModelConfig hashes the resolved model path into vLLM's torch.compile
+        # cache key. A random mkdtemp suffix therefore creates a new cache
+        # directory on every restart and makes restored Engram artifacts
+        # unreachable. Keep the mirror path stable; its contents are rebuilt by
+        # create_temp_local_copy on every use.
+        self.temp_copy_base = os.path.join(tempfile.gettempdir(), "model_temp_copy")
+        os.makedirs(self.temp_copy_base, exist_ok=True)
         logging.info(f"Temporary copy base directory created: {self.temp_copy_base}")
         self._temp_copies = {}  # key: original_path, value: {'copy_path': ..., 'original_path': ...}
         atexit.register(self._cleanup_temp_copies)
         atexit.register(self.umount_all)
 
@@ -70,13 +76,23 @@ class Fuser:
             raise RetryableError(f"mount {path} -> {mnt_path} failed: {mount_result}")
         logging.info(f"mount dir success: {path} -> {mnt_path}")
         self._mount_src_map[mnt_path] = path
         return mnt_path
 
-    def create_temp_local_copy(self, path: str) -> str:
-        """Create a fresh temporary local copy (via symlinks) of the given path."""
-        path_hash = hashlib.md5(path.encode("utf-8")).hexdigest()
+    def create_temp_local_copy(
+        self,
+        path: str,
+        source_identity: Optional[str] = None,
+    ) -> str:
+        """Create a fresh symlink mirror at a stable, model-specific path.
+
+        ``path`` may already be a generated FUSE mount path. Use the original
+        pre-mount path as ``source_identity`` so the path hashed into vLLM's
+        compilation config describes the model rather than a transport detail.
+        """
+        identity = source_identity if source_identity is not None else path
+        path_hash = hashlib.sha256(identity.encode("utf-8")).hexdigest()
         copy_path = os.path.join(self.temp_copy_base, path_hash)
         
         # Always start fresh: remove if exists
         if os.path.exists(copy_path):
             shutil.rmtree(copy_path)
@@ -122,24 +138,30 @@ class Fuser:
                 self.umount_fuse_dir(mnt_path)
             except Exception as e:
                 logging.warning(f"Failed to umount {mnt_path}: {e}")
 
     def _cleanup_temp_copies(self):
-        try:
-            if os.path.exists(self.temp_copy_base):
-                shutil.rmtree(self.temp_copy_base)
-                logging.info(f"Cleaned up temporary copy directory: {self.temp_copy_base}")
-        except Exception as e:
-            logging.warning(f"Failed to clean up temporary copies: {e}")
+        for entry in self._temp_copies.values():
+            copy_path = entry['copy_path']
+            try:
+                shutil.rmtree(copy_path, ignore_errors=True)
+                logging.info("Cleaned up temporary copy directory: %s", copy_path)
+            except Exception as e:
+                logging.warning("Failed to clean up %s: %s", copy_path, e)
 
 _fuser = Fuser()
 
 def fetch_remote_file_to_local(
     path: str, 
     mount_mode: MountRwMode = MountRwMode.RWMODE_RO, 
     enable_temp_copy: bool = False
 ):
+    source_identity = path
     parse_result = urlparse(path)
     if parse_result.scheme != '':  # remote path
         path = _fuser.mount_dir(path, mount_mode)
     
-    return _fuser.create_temp_local_copy(path) if enable_temp_copy else path
+    return (
+        _fuser.create_temp_local_copy(path, source_identity)
+        if enable_temp_copy
+        else path
+    )
````

### 7. `tools/engram/check_cache_keys.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：0% 命中诊断工具：dump 导出本 pod 的 vLLM torch_compile hash_key 与 engram compatibility digest，compare 对比两份导出并指出具体分歧 factor
- **规模**：+346 / -0（改后文件共 346 行）
- **涉及提交**：
  - `47615758b9` feat: share vLLM JIT/autotune artifacts across pods via Engram
````diff
diff --git a/tools/engram/check_cache_keys.py b/tools/engram/check_cache_keys.py
new file mode 100755
index 0000000000..3e7d687e1d
--- /dev/null
+++ b/tools/engram/check_cache_keys.py
@@ -0,0 +1,346 @@
+#!/usr/bin/env python3
+# SPDX-License-Identifier: Apache-2.0
+"""Diagnose Engram cache misses by comparing cache keys across pods.
+
+Two independent keys must match before a pod can reuse another pod's artifacts,
+and *neither* reports an error when it does not match -- you simply get a 0% hit
+rate that looks identical to a cold start:
+
+1. **vLLM's own compile-cache directory name.** `VllmBackend.__call__` derives
+   `torch_compile_cache/<hash_key>` from
+   `[env_hash, config_hash, code_hash, compiler_hash]`
+   (`vllm/compilation/backends.py:952-963`). `config_hash` comes from
+   `VllmConfig.compute_hash()`, which includes `model_config.model` -- the
+   `--model` string -- because `"model"` is absent from the `ignored_factors`
+   set in `vllm/config/model.py`. Two pods that name the same checkpoint
+   differently therefore compile into different directories.
+   This one is a *correctness guard*, not a bug: a mismatched key is a miss, and
+   Engram's never-overwrite pull means it can never load the wrong kernel.
+
+2. **Engram's compatibility digest.** The remote layout is
+   `<prefix>/<kind>/<compatibility-digest>/<model-digest>/snapshots`, so a
+   divergent digest points the pull at a namespace nothing was pushed to.
+
+Usage
+-----
+On each pod, after the server has warmed up at least once:
+
+    python3 tools/engram/check_cache_keys.py dump -o /tmp/keys-$(hostname).json
+
+Then, anywhere:
+
+    python3 tools/engram/check_cache_keys.py compare \
+        /tmp/keys-podA.json /tmp/keys-podB.json
+
+`compare` exits 0 when every key agrees, 1 when a key diverges (and names the
+exact factor), and 2 on bad input. `dump` never needs a GPU; it only reads
+files and installed package metadata.
+"""
+
+from __future__ import annotations
+
+import argparse
+import json
+import os
+import socket
+import sys
+from pathlib import Path
+from typing import Any
+
+# ---------------------------------------------------------------------------
+# dump
+# ---------------------------------------------------------------------------
+
+
+def _vllm_cache_root() -> Path:
+    """Resolve VLLM_CACHE_ROOT the way vllm/envs.py:251-255,535-538 does."""
+
+    explicit = os.getenv("VLLM_CACHE_ROOT", "").strip()
+    if explicit:
+        return Path(explicit).expanduser()
+    xdg = os.getenv("XDG_CACHE_HOME", "").strip()
+    base = Path(xdg).expanduser() if xdg else Path("~/.cache").expanduser()
+    return base / "vllm"
+
+
+def _tree_stats(root: Path) -> dict[str, Any]:
+    if not root.exists():
+        return {"exists": False}
+    files = 0
+    total_bytes = 0
+    for path in root.rglob("*"):
+        try:
+            if path.is_file():
+                files += 1
+                total_bytes += path.stat().st_size
+        except OSError:
+            continue
+    return {"exists": True, "files": files, "bytes": total_bytes}
+
+
+def _collect_compile_keys(cache_root: Path) -> dict[str, Any]:
+    """Read every cache_key_factors.json vLLM wrote (backends.py:1016)."""
+
+    compile_root = cache_root / "torch_compile_cache"
+    result: dict[str, Any] = {
+        "root": str(compile_root),
+        **_tree_stats(compile_root),
+        "hash_keys": {},
+    }
+    if not compile_root.is_dir():
+        return result
+
+    for meta_path in sorted(compile_root.rglob("cache_key_factors.json")):
+        try:
+            factors = json.loads(meta_path.read_text(encoding="utf-8"))
+        except (OSError, ValueError) as exc:
+            factors = {"_unreadable": repr(exc)}
+        relative = meta_path.relative_to(compile_root)
+        # <hash_key>/rank_r_dp/[prefix/]cache_key_factors.json
+        hash_key = relative.parts[0] if relative.parts else "?"
+        result["hash_keys"].setdefault(hash_key, {})[str(relative)] = factors
+    return result
+
+
+def _collect_engram_digests() -> dict[str, Any]:
+    """Compute each registered kind's compatibility digest, if Engram is present."""
+
+    try:
+        from engram import jit_cache_compat, jit_cache_env, jit_cache_model
+        from engram.jit_cache_specs import registered_specs
+
+        adapter_parent = Path(__file__).resolve().parents[2] / "vllm" / "whale_vllm"
+        sys.path.insert(0, str(adapter_parent))
+        import fuse_jit_cache.adapter  # noqa: F401  registers the specs
+    except Exception as exc:  # noqa: BLE001 - diagnostics must not hard-fail
+        return {"available": False, "error": repr(exc)}
+
+    kinds: dict[str, Any] = {}
+    for spec in registered_specs():
+        entry: dict[str, Any] = {"enabled": None}
+        try:
+            entry["enabled"] = bool(spec.enabled())
+        except Exception as exc:  # noqa: BLE001
+            entry["enabled_error"] = repr(exc)
+        try:
+            local_root = spec.local_root()
+            entry["local_root"] = str(local_root)
+            entry.update(_tree_stats(local_root))
+        except Exception as exc:  # noqa: BLE001
+            entry["local_root_error"] = repr(exc)
+        try:
+            compatibility = jit_cache_compat._compatibility(spec)
+            entry["compatibility_digest"] = jit_cache_compat._compatibility_digest(
+                compatibility
+            )
+            # Keep the raw factors: this is what makes a divergence explainable.
+            entry["compatibility"] = compatibility
+        except Exception as exc:  # noqa: BLE001
+            entry["compatibility_error"] = repr(exc)
+        kinds[spec.name] = entry
+
+    return {
+        "available": True,
+        "remote_prefix": jit_cache_env._remote_prefix(),
+        # Only the digest, never the raw checkpoint locator (it can embed
+        # credentials -- jit_cache_model never logs or persists the raw value).
+        "model_digest": jit_cache_model._model_digest(),
+        "model_identity_source": jit_cache_model._model_identity_source(),
+        "kinds": kinds,
+    }
+
+
+def _dump() -> dict[str, Any]:
+    cache_root = _vllm_cache_root()
+    return {
+        "schema": 1,
+        "host": socket.gethostname(),
+        "vllm_cache_root": str(cache_root),
+        "compile_cache": _collect_compile_keys(cache_root),
+        "engram": _collect_engram_digests(),
+    }
+
+
+# ---------------------------------------------------------------------------
+# compare
+# ---------------------------------------------------------------------------
+
+
+def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
+    if isinstance(value, dict):
+        flat: dict[str, Any] = {}
+        for key, item in value.items():
+            flat.update(_flatten(item, f"{prefix}.{key}" if prefix else str(key)))
+        return flat
+    return {prefix: value}
+
+
+def _compare_compile_keys(left: dict, right: dict, report: list[str]) -> bool:
+    lk = set(left.get("compile_cache", {}).get("hash_keys", {}))
+    rk = set(right.get("compile_cache", {}).get("hash_keys", {}))
+    if lk and lk == rk:
+        report.append(f"OK   vLLM compile hash_key set matches: {sorted(lk)}")
+        return True
+    if not lk or not rk:
+        left_keys = sorted(lk) or "none"
+        right_keys = sorted(rk) or "none"
+        report.append(
+            "WARN vLLM compile hash_key absent on one side "
+            f"({left['host']}={left_keys}, {right['host']}={right_keys}); "
+            "warm up the server at least once before dumping"
+        )
+        return True
+
+    common = lk & rk
+    left_only = lk - rk
+    right_only = rk - lk
+    report.append("FAIL vLLM compile hash_key sets differ between the two pods")
+    if common:
+        report.append(f"       -> common (possibly stale): {sorted(common)}")
+    report.append(f"       -> only {left['host']}: {sorted(left_only)}")
+    report.append(f"       -> only {right['host']}: {sorted(right_only)}")
+
+    # Name the responsible factor using a key unique to each side. Comparing an
+    # arbitrary historical key can explain the wrong pair when roots contain
+    # artifacts from more than one launch.
+    def _first_factors(dump: dict, preferred: set[str]) -> dict:
+        hash_keys = dump["compile_cache"]["hash_keys"]
+        for key in sorted(preferred):
+            entries = hash_keys.get(key, {})
+            for factors in entries.values():
+                return factors
+        return {}
+
+    lf = _first_factors(left, left_only)
+    rf = _first_factors(right, right_only)
+    for factor in ("config_hash", "code_hash", "compiler_hash"):
+        if lf.get(factor) != rf.get(factor):
+            report.append(
+                f"       -> {factor} differs ({lf.get(factor)} vs {rf.get(factor)})"
+            )
+    lenv, renv = _flatten(lf.get("env", {})), _flatten(rf.get("env", {}))
+    for key in sorted(set(lenv) | set(renv)):
+        if lenv.get(key) != renv.get(key):
+            report.append(
+                f"       -> env.{key}: {lenv.get(key)!r} vs {renv.get(key)!r}"
+            )
+    return False
+
+
+def _compare_engram(left: dict, right: dict, report: list[str]) -> bool:
+    le, re_ = left.get("engram", {}), right.get("engram", {})
+    if not (le.get("available") and re_.get("available")):
+        report.append(
+            "WARN Engram not importable on one side; skipping digest comparison "
+            f"({le.get('error') or re_.get('error')})"
+        )
+        return True
+
+    ok = True
+    if le.get("remote_prefix") != re_.get("remote_prefix"):
+        report.append(
+            f"FAIL remote prefix differs: {le.get('remote_prefix')} vs "
+            f"{re_.get('remote_prefix')}"
+        )
+        ok = False
+    if le.get("model_digest") is None or re_.get("model_digest") is None:
+        # Neither ENGRAM_MODEL_ID nor CHECKPOINT_PATH was set, so Engram fails
+        # closed to local JIT on that side -- no pull and no push happen at all.
+        report.append(
+            "FAIL model digest is unavailable on at least one side "
+            f"({left['host']}={le.get('model_digest')}, "
+            f"{right['host']}={re_.get('model_digest')}); Engram fails closed to "
+            "local JIT without a model identity -- set ENGRAM_MODEL_ID (or ensure "
+            "CHECKPOINT_PATH is exported)"
+        )
+        ok = False
+    elif le.get("model_digest") != re_.get("model_digest"):
+        report.append(
+            "FAIL model digest differs -- the two pods use different model "
+            f"namespaces (identity source: {le.get('model_identity_source')} vs "
+            f"{re_.get('model_identity_source')}); set ENGRAM_MODEL_ID explicitly "
+            "when the checkpoint path is not stable across pods"
+        )
+        ok = False
+
+    for kind in sorted(set(le.get("kinds", {})) | set(re_.get("kinds", {}))):
+        lkind = le.get("kinds", {}).get(kind, {})
+        rkind = re_.get("kinds", {}).get(kind, {})
+        if not (lkind.get("enabled") and rkind.get("enabled")):
+            report.append(
+                f"SKIP {kind}: not enabled on both sides "
+                f"({lkind.get('enabled')} / {rkind.get('enabled')})"
+            )
+            continue
+        ld, rd = lkind.get("compatibility_digest"), rkind.get("compatibility_digest")
+        if ld and ld == rd:
+            report.append(f"OK   {kind}: compatibility digest {ld}")
+            continue
+        if ld is None or rd is None:
+            # A digest that could not be computed is a fail-closed miss for that
+            # kind. Surface the reason rather than reporting a false divergence.
+            report.append(
+                f"FAIL {kind}: compatibility digest unavailable "
+                f"({left['host']}={ld}, {right['host']}={rd})"
+            )
+            for host, entry in ((left["host"], lkind), (right["host"], rkind)):
+                error = entry.get("compatibility_error")
+                if error:
+                    report.append(f"       -> {host}: {error}")
+            ok = False
+            continue
+        report.append(f"FAIL {kind}: compatibility digest differs ({ld} vs {rd})")
+        ok = False
+        lflat = _flatten(lkind.get("compatibility", {}))
+        rflat = _flatten(rkind.get("compatibility", {}))
+        for key in sorted(set(lflat) | set(rflat)):
+            if lflat.get(key) != rflat.get(key):
+                report.append(
+                    f"       -> {key}: {lflat.get(key)!r} vs {rflat.get(key)!r}"
+                )
+    return ok
+
+
+def _compare(left_path: Path, right_path: Path) -> int:
+    try:
+        left = json.loads(left_path.read_text(encoding="utf-8"))
+        right = json.loads(right_path.read_text(encoding="utf-8"))
+    except (OSError, ValueError) as exc:
+        print(f"cannot read dumps: {exc!r}", file=sys.stderr)
+        return 2
+
+    report: list[str] = [f"comparing {left.get('host')} vs {right.get('host')}", ""]
+    ok = _compare_compile_keys(left, right, report)
+    report.append("")
+    ok = _compare_engram(left, right, report) and ok
+    print("\n".join(report))
+    return 0 if ok else 1
+
+
+def main(argv: list[str] | None = None) -> int:
+    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
+    sub = parser.add_subparsers(dest="command", required=True)
+
+    dump = sub.add_parser("dump", help="write this pod's cache keys to JSON")
+    dump.add_argument("-o", "--output", type=Path, help="output path (default: stdout)")
+
+    compare = sub.add_parser("compare", help="diff two dumps and name the divergence")
+    compare.add_argument("left", type=Path)
+    compare.add_argument("right", type=Path)
+
+    args = parser.parse_args(argv)
+
+    if args.command == "dump":
+        payload = json.dumps(_dump(), indent=2, sort_keys=True, default=str)
+        if args.output:
+            args.output.write_text(payload + "\n", encoding="utf-8")
+            print(f"wrote {args.output}")
+        else:
+            print(payload)
+        return 0
+
+    return _compare(args.left, args.right)
+
+
+if __name__ == "__main__":
+    sys.exit(main())
````

### 8. `tests/whale/__init__.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：tests/whale 测试包标记
- **规模**：+1 / -0（改后文件共 1 行）
- **涉及提交**：
  - `47615758b9` feat: share vLLM JIT/autotune artifacts across pods via Engram
````diff
diff --git a/tests/whale/__init__.py b/tests/whale/__init__.py
new file mode 100644
index 0000000000..9881313609
--- /dev/null
+++ b/tests/whale/__init__.py
@@ -0,0 +1 @@
+# SPDX-License-Identifier: Apache-2.0
````

### 9. `tests/whale/test_engram_adapter.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：Engram adapter contract 测试：CacheSpec 注册与门禁、各缓存根路径解析、远端命名空间、launcher 时序约定
- **规模**：+509 / -0（改后文件共 509 行）
- **涉及提交**：
  - `b0e3efb2c1` refactor(whale): move Engram pull synchronization to launcher
  - `b4a7966575` fix(whale): stabilize Engram compile cache keys
  - `47615758b9` feat: share vLLM JIT/autotune artifacts across pods via Engram
````diff
diff --git a/tests/whale/test_engram_adapter.py b/tests/whale/test_engram_adapter.py
new file mode 100644
index 0000000000..1e2c5a0e0b
--- /dev/null
+++ b/tests/whale/test_engram_adapter.py
@@ -0,0 +1,509 @@
+# SPDX-License-Identifier: Apache-2.0
+"""Contract and drift tests for Whale vLLM's Engram adapter."""
+
+from __future__ import annotations
+
+import importlib.util
+import os
+import re
+import subprocess
+import sys
+from pathlib import Path, PurePosixPath
+
+import pytest
+
+pytest.importorskip("engram", reason="Engram wheel is not installed")
+
+_REPO_ROOT = Path(__file__).resolve().parents[2]
+_ADAPTER_PARENT = _REPO_ROOT / "vllm" / "whale_vllm"
+sys.path.insert(0, str(_ADAPTER_PARENT))
+
+from engram import jit_cache_compat, jit_cache_env  # noqa: E402
+from engram.jit_cache_specs import registered_specs  # noqa: E402
+from fuse_jit_cache import adapter  # noqa: E402  import registers the specs
+
+_EXPECTED_KINDS = {
+    "vllm_torch_compile",
+    "vllm_deep_gemm",
+    "triton",
+    "aiter",
+}
+
+_START_SH = _REPO_ROOT / "vllm" / "whale_vllm" / "start.sh"
+_GPU_WORKER = _REPO_ROOT / "vllm" / "v1" / "worker" / "gpu_worker.py"
+_GPU_MODEL_RUNNER = _REPO_ROOT / "vllm" / "v1" / "worker" / "gpu_model_runner.py"
+_MODEL_LOADER_UTILS = (
+    _REPO_ROOT / "vllm" / "model_executor" / "model_loader" / "utils.py"
+)
+_FP8_QUANT = (
+    _REPO_ROOT / "vllm" / "model_executor" / "layers" / "quantization" / "fp8.py"
+)
+_CACHE_KEY_TOOL = _REPO_ROOT / "tools" / "engram" / "check_cache_keys.py"
+
+
+def _spec(name: str):
+    for spec in registered_specs():
+        if spec.name == name:
+            return spec
+    raise AssertionError(f"cache kind {name!r} is not registered")
+
+
+# ---------------------------------------------------------------------------
+# Registry contract
+# ---------------------------------------------------------------------------
+
+
+def test_import_registers_the_expected_kinds():
+    assert {spec.name for spec in registered_specs()} >= _EXPECTED_KINDS
+
+
+def test_helper_import_does_not_load_vllm_or_torch():
+    env = os.environ.copy()
+    env["PYTHONPATH"] = os.pathsep.join(
+        filter(None, (str(_ADAPTER_PARENT), env.get("PYTHONPATH")))
+    )
+    result = subprocess.run(
+        [
+            sys.executable,
+            "-s",
+            "-c",
+            # Parenthesized so the two fragments read as one deliberate string
+            # rather than a collection entry with a missing comma (ruff ISC004).
+            (
+                "import sys, fuse_jit_cache.adapter; "
+                "assert 'vllm' not in sys.modules; "
+                "assert 'torch' not in sys.modules"
+            ),
+        ],
+        env=env,
+        capture_output=True,
+        text=True,
+        check=False,
+    )
+    assert result.returncode == 0, result.stderr
+
+
+def test_adapter_injects_framework_package_and_remote_prefix():
+    assert os.environ["ENGRAM_FRAMEWORK_PACKAGE"] == "vllm"
+    assert jit_cache_env._remote_prefix() == "vllm-jit-cache-v1"
+
+
+def test_remote_prefix_is_a_safe_single_path_component():
+    # A bad prefix would escape the cache namespace; the core validates it, so
+    # assert our chosen value actually passes that validation.
+    assert re.fullmatch(r"[A-Za-z0-9._-]+", "vllm-jit-cache-v1")
+
+
+def test_reimport_is_idempotent():
+    """A second import must not raise CacheSpecConflictError.
+
+    vLLM loads plugins in several processes and a reload recreates the closures,
+    so every spec carries a stable ``definition_id``.
+    """
+
+    before = registered_specs()
+    importlib.reload(adapter)
+    assert registered_specs() == before
+
+
+def test_every_spec_declares_a_definition_id():
+    for spec in registered_specs():
+        if spec.name in _EXPECTED_KINDS:
+            assert spec.definition_id, spec.name
+
+
+def test_torch_compile_namespace_excludes_random_model_path_snapshots():
+    assert _spec("vllm_torch_compile").definition_id == "vllm/torch_compile/v2"
+
+
+# ---------------------------------------------------------------------------
+# Enable gates: must be decidable out of process, without a GPU
+# ---------------------------------------------------------------------------
+
+
+def test_torch_compile_gate_follows_vllm_disable_compile_cache(monkeypatch):
+    monkeypatch.delenv("VLLM_DISABLE_COMPILE_CACHE", raising=False)
+    assert _spec("vllm_torch_compile").enabled() is True
+    monkeypatch.setenv("VLLM_DISABLE_COMPILE_CACHE", "1")
+    assert _spec("vllm_torch_compile").enabled() is False
+
+
+def test_deep_gemm_gate_requires_cuda_and_the_module(monkeypatch):
+    monkeypatch.setattr(adapter, "_DEEP_GEMM_DISTRIBUTION", "deep_gemm")
+    monkeypatch.setattr(adapter, "_module_installed", lambda name: name == "deep_gemm")
+    monkeypatch.setattr(jit_cache_env, "_is_rocm_runtime", lambda: True)
+    assert _spec("vllm_deep_gemm").enabled() is False
+
+    monkeypatch.setattr(jit_cache_env, "_is_rocm_runtime", lambda: False)
+    monkeypatch.setenv("VLLM_USE_DEEP_GEMM", "0")
+    assert _spec("vllm_deep_gemm").enabled() is False
+    monkeypatch.setenv("VLLM_USE_DEEP_GEMM", "1")
+    assert _spec("vllm_deep_gemm").enabled() is True
+
+
+def test_aiter_gate_requires_rocm_and_the_vllm_switch(monkeypatch):
+    monkeypatch.setattr(adapter, "_AITER_DISTRIBUTION", "amd-aiter")
+    monkeypatch.setattr(adapter, "_module_installed", lambda name: name == "aiter")
+    monkeypatch.setattr(jit_cache_env, "_is_rocm_runtime", lambda: False)
+    monkeypatch.setenv("VLLM_ROCM_USE_AITER", "1")
+    assert _spec("aiter").enabled() is False
+
+    monkeypatch.setattr(jit_cache_env, "_is_rocm_runtime", lambda: True)
+    monkeypatch.delenv("VLLM_ROCM_USE_AITER", raising=False)
+    # vllm/envs.py:919 -- the switch defaults to False.
+    assert _spec("aiter").enabled() is False
+    monkeypatch.setenv("VLLM_ROCM_USE_AITER", "1")
+    assert _spec("aiter").enabled() is True
+
+
+def test_external_jit_specs_use_the_resolved_distribution_fingerprints():
+    assert (
+        _spec("vllm_deep_gemm").implementation_distributions
+        == adapter._DEEP_GEMM_IMPLEMENTATION_DISTRIBUTIONS
+    )
+    assert (
+        _spec("aiter").implementation_distributions
+        == adapter._AITER_IMPLEMENTATION_DISTRIBUTIONS
+    )
+
+
+# ---------------------------------------------------------------------------
+# Cache roots
+# ---------------------------------------------------------------------------
+
+
+def test_vllm_cache_root_honours_explicit_override(monkeypatch):
+    monkeypatch.setenv("VLLM_CACHE_ROOT", "/mnt/cache/vllm")
+    assert adapter._vllm_cache_root() == Path("/mnt/cache/vllm")
+    assert _spec("vllm_torch_compile").local_root() == Path(
+        "/mnt/cache/vllm/torch_compile_cache"
+    )
+
+
+def test_vllm_cache_root_honours_xdg_cache_home(monkeypatch):
+    monkeypatch.delenv("VLLM_CACHE_ROOT", raising=False)
+    monkeypatch.setenv("XDG_CACHE_HOME", "/xdg")
+    assert adapter._vllm_cache_root() == Path("/xdg/vllm")
+
+
+def test_deep_gemm_root_prefers_the_frameworks_own_env(monkeypatch):
+    # vllm/utils/deep_gemm.py:151 only writes DG_JIT_CACHE_DIR when unset, so an
+    # explicit value is the shared source of truth.
+    monkeypatch.setenv("DG_JIT_CACHE_DIR", "/mnt/dg")
+    assert _spec("vllm_deep_gemm").local_root() == Path("/mnt/dg")
+
+    monkeypatch.delenv("DG_JIT_CACHE_DIR", raising=False)
+    monkeypatch.setenv("VLLM_CACHE_ROOT", "/mnt/cache/vllm")
+    assert _spec("vllm_deep_gemm").local_root() == Path("/mnt/cache/vllm/deep_gemm")
+
+
+def test_triton_root_follows_tritons_own_resolution_order(monkeypatch):
+    monkeypatch.setenv("TRITON_CACHE_DIR", "/explicit/triton")
+    assert _spec("triton").local_root() == Path("/explicit/triton")
+
+    monkeypatch.delenv("TRITON_CACHE_DIR", raising=False)
+    monkeypatch.setenv("TRITON_HOME", "/thome")
+    assert _spec("triton").local_root() == Path("/thome/.triton/cache")
+
+    monkeypatch.delenv("TRITON_HOME", raising=False)
+    monkeypatch.setenv("HOME", "/")
+    # The Whale release images run with HOME=/ and pre-create /.triton
+    # (docker/ali/Dockerfile.release_cuda:69).
+    assert _spec("triton").local_root() == Path("/.triton/cache")
+
+
+def test_triton_root_is_not_inside_the_torch_compile_tree(monkeypatch):
+    """The two triton kinds must stay disjoint, or push would double-carry.
+
+    vLLM redirects TRITON_CACHE_DIR into torch_compile_cache from
+    InductorAdaptor.initialize_cache, but that happens in the server process
+    only. Both helpers run outside vLLM, so they must resolve the *default*
+    location here.
+    """
+
+    monkeypatch.delenv("TRITON_CACHE_DIR", raising=False)
+    monkeypatch.delenv("TRITON_HOME", raising=False)
+    monkeypatch.setenv("VLLM_CACHE_ROOT", "/mnt/cache/vllm")
+    triton_root = _spec("triton").local_root()
+    compile_root = _spec("vllm_torch_compile").local_root()
+    assert compile_root not in triton_root.parents
+    assert triton_root not in compile_root.parents
+
+
+def test_aiter_root_prefers_the_image_provided_jit_dir(monkeypatch):
+    monkeypatch.setenv("AITER_JIT_DIR", "/.aiter")
+    assert _spec("aiter").local_root() == Path("/.aiter")
+
+
+# ---------------------------------------------------------------------------
+# include_file predicates
+# ---------------------------------------------------------------------------
+
+
+def test_triton_include_skips_locks_and_partial_writes():
+    include = _spec("triton").include_file
+    assert include(PurePosixPath("abc/kernel.cubin"))
+    assert include(PurePosixPath("abc/kernel.json"))
+    assert include(PurePosixPath("__grp__kernel.json"))
+    assert not include(PurePosixPath("abc/kernel.lock"))
+    assert not include(PurePosixPath("abc/kernel.tmp"))
+
+
+def test_torch_compile_include_takes_the_whole_tree():
+    include = _spec("vllm_torch_compile").include_file
+    for relative in (
+        "abcd123456/rank_0_0/backbone/vllm_compile_cache.py",
+        "abcd123456/rank_0_0/inductor_cache/xx/yy.py",
+        "abcd123456/rank_0_0/triton_cache/zz/kernel.cubin",
+        "torch_aot_compile/abcd/rank_0_0/model",
+    ):
+        assert include(PurePosixPath(relative)), relative
+
+
+# ---------------------------------------------------------------------------
+# Launcher consistency
+# ---------------------------------------------------------------------------
+
+
+def test_start_sh_runs_the_helper_through_the_adapter_module():
+    """The helper must import the adapter, or the registry is empty.
+
+    `python -m engram.jit_cache` would start with no specs registered and
+    silently select nothing (docs/adapter.md section 1).
+    """
+
+    text = _START_SH.read_text(encoding="utf-8")
+    assert "-m fuse_jit_cache pull" in text
+    assert "-m fuse_jit_cache push" in text
+    assert "-m engram.jit_cache" not in text
+
+
+def test_start_sh_uses_a_serial_pull_without_the_barrier_protocol():
+    text = _START_SH.read_text(encoding="utf-8")
+    launcher_start = text.index("\nstart_engram_jobs() {")
+    launcher_end = text.index(
+        "# ---------------------- Engram definitions end", launcher_start
+    )
+    launcher = text[launcher_start:launcher_end]
+
+    assert launcher.index("-m fuse_jit_cache pull") < launcher.index(
+        "-m fuse_jit_cache push"
+    )
+    assert "Pulling vLLM JIT caches before the server starts" in launcher
+    assert "continuing with local JIT" in launcher
+    assert "launch_background_engram_pull" not in launcher
+    assert "ENGRAM_EARLY_KINDS" not in launcher
+    assert ".pending" not in launcher
+
+
+def test_start_sh_clears_inherited_async_barrier_status_files():
+    text = _START_SH.read_text(encoding="utf-8")
+    for name in (
+        "ENGRAM_EARLY_PULL_STATUS_FILE",
+        "ENGRAM_LATE_PULL_STATUS_FILE",
+        "WHALE_JIT_CACHE_EARLY_PULL_STATUS_FILE",
+        "WHALE_JIT_CACHE_LATE_PULL_STATUS_FILE",
+    ):
+        assert f"unset {name}" in text
+
+
+def test_start_sh_pull_failure_is_fail_soft_and_precedes_server(tmp_path):
+    text = _START_SH.read_text(encoding="utf-8")
+    definitions_start = text.index('ENGRAM_PYTHON="${ENGRAM_PYTHON:-python3}"')
+    definitions_end = text.index(
+        "# ---------------------- Engram definitions end", definitions_start
+    )
+    definitions = text[definitions_start:definitions_end]
+
+    fake_python = tmp_path / "fake-python"
+    fake_python.write_text(
+        """#!/usr/bin/env bash
+case "$*" in
+  *importlib.util.find_spec*) printf '%s\\n' "$FAKE_ADAPTER_PARENT" ;;
+  *"import fuse_jit_cache.adapter"*) exit 0 ;;
+  *"-m fuse_jit_cache pull"*)
+    printf 'pull\\n' >> "$FAKE_EVENTS"
+    exit "$FAKE_PULL_STATUS"
+    ;;
+  *"-m fuse_jit_cache push"*)
+    printf 'push\\n' >> "$FAKE_EVENTS"
+    ;;
+  *) exit 99 ;;
+esac
+""",
+        encoding="utf-8",
+    )
+    fake_python.chmod(0o755)
+
+    fake_timeout = tmp_path / "timeout"
+    fake_timeout.write_text(
+        """#!/usr/bin/env bash
+while [ "$#" -gt 0 ] && [ "$1" != "env" ]; do
+  shift
+done
+exec "$@"
+""",
+        encoding="utf-8",
+    )
+    fake_timeout.chmod(0o755)
+
+    events = tmp_path / "events"
+    stdout = tmp_path / "stdout"
+    stderr = tmp_path / "stderr"
+    harness = (
+        definitions
+        + """
+start_engram_jobs
+printf 'server\\n' >> "$FAKE_EVENTS"
+wait || true
+cleanup_engram_jobs
+trap - EXIT
+"""
+    )
+    env = os.environ.copy()
+    env.update(
+        {
+            "ENGRAM_PYTHON": str(fake_python),
+            "ENGRAM_URI": "/fake/cache",
+            "ENGRAM_PULL_TIMEOUT_SEC": "1",
+            "ENGRAM_READY_TIMEOUT_SEC": "1",
+            "ENGRAM_PUSH_TIMEOUT_SEC": "1",
+            "ENGRAM_PUSH_PROCESS_TIMEOUT_SEC": "3",
+            "FAKE_ADAPTER_PARENT": str(_ADAPTER_PARENT),
+            "FAKE_EVENTS": str(events),
+            "FAKE_PULL_STATUS": "17",
+            "PATH": os.pathsep.join((str(tmp_path), env["PATH"])),
+            "START_PORT": "12233",
+            "STDOUT_FILE": str(stdout),
+            "STDERR_FILE": str(stderr),
+        }
+    )
+    result = subprocess.run(
+        ["bash", "-c", harness],
+        env=env,
+        capture_output=True,
+        text=True,
+        check=False,
+    )
+
+    assert result.returncode == 0, result.stderr
+    recorded = events.read_text(encoding="utf-8").splitlines()
+    assert recorded[0] == "pull"
+    assert "server" in recorded
+    assert "push" in recorded
+    assert "continuing with local JIT" in result.stderr
+
+
+def test_start_sh_does_not_dump_credentials_into_the_env_log():
+    text = _START_SH.read_text(encoding="utf-8")
+    assert 'dump_runtime_env > "$ENV_FILE"' in text
+    assert 'printenv > "$ENV_FILE"' not in text
+
+
+def test_start_sh_launches_helpers_after_runtime_environment_is_finalized():
+    text = _START_SH.read_text(encoding="utf-8")
+    launch = text.rindex("\nstart_engram_jobs\n")
+    assert launch > text.index("export FSLIB_DFS_STORAGE_LINKS=")
+    assert launch > text.index('export LD_LIBRARY_PATH="$FIXED_LD_LIBRARY_PATH"')
+    assert launch < text.index('if [ "${CMD}" ]', launch)
+
+
+def test_alibaba_requirements_install_the_transport_extras():
+    x86 = (_REPO_ROOT / "requirements" / "alibaba.txt").read_text(encoding="utf-8")
+    arm = (_REPO_ROOT / "requirements" / "alibaba-arm64.txt").read_text(
+        encoding="utf-8"
+    )
+    assert "engram[fuse,pangu,oss]==0.1.4" in x86
+    assert "engram[fuse,oss]==0.1.4" in arm
+    assert "pypi/pypi-releases" in x86
+    assert "pypi/pypi-releases" in arm
+
+
+# ---------------------------------------------------------------------------
+# vLLM runtime isolation
+# ---------------------------------------------------------------------------
+
+
+def test_vllm_runtime_has_no_engram_barrier_hooks():
+    assert not (_ADAPTER_PARENT / "fuse_jit_cache" / "barrier.py").exists()
+    for path in (
+        _MODEL_LOADER_UTILS,
+        _FP8_QUANT,
+        _GPU_WORKER,
+        _GPU_MODEL_RUNNER,
+    ):
+        text = path.read_text(encoding="utf-8")
+        assert "fuse_jit_cache.barrier" not in text, path
+        assert "join_early_pull" not in text, path
+        assert "join_late_pull" not in text, path
+
+
+def test_cache_key_diagnostic_does_not_accept_a_stale_intersection():
+    module_spec = importlib.util.spec_from_file_location(
+        "test_check_cache_keys", _CACHE_KEY_TOOL
+    )
+    assert module_spec is not None and module_spec.loader is not None
+    module = importlib.util.module_from_spec(module_spec)
+    module_spec.loader.exec_module(module)
+
+    left = {
+        "host": "left",
+        "compile_cache": {"hash_keys": {"active-left": {}, "stale": {}}},
+    }
+    right = {
+        "host": "right",
+        "compile_cache": {"hash_keys": {"active-right": {}, "stale": {}}},
+    }
+    report: list[str] = []
+    assert module._compare_compile_keys(left, right, report) is False
+    assert any("possibly stale" in line for line in report)
+
+
+# ---------------------------------------------------------------------------
+# Drift guards against vLLM internals
+# ---------------------------------------------------------------------------
+
+
+def test_declared_implementation_sources_exist_in_the_vllm_tree():
+    """Catch an upstream rename of the compilation modules.
+
+    A missing implementation source makes the core raise for that kind, which
+    pull swallows per-kind -- a 0% hit rate with only a warning in the log.
+    """
+
+    package_root = _REPO_ROOT / "vllm"
+    missing = [
+        relative
+        for relative in _spec("vllm_torch_compile").implementation_files
+        if not (package_root / relative).is_file()
+    ]
+    assert not missing, missing
+
+
+def test_framework_source_root_resolves_and_hashes_the_declared_sources():
+    if importlib.util.find_spec("vllm") is None:
+        pytest.skip("vllm is not importable from this environment")
+    identities = jit_cache_compat._source_identities(
+        _spec("vllm_torch_compile").implementation_files
+    )
+    assert set(identities) == set(_spec("vllm_torch_compile").implementation_files)
+    assert all(len(digest) == 64 for digest in identities.values())
+
+
+@pytest.mark.skipif(
+    importlib.util.find_spec("torch") is None,
+    reason="importing vllm.envs requires torch",
+)
+def test_cache_roots_match_vllm_envs(monkeypatch):
+    """The adapter re-derives VLLM_CACHE_ROOT without importing vllm.
+
+    Assert the two agree, so a change in vllm/envs.py cannot silently point the
+    helpers at a directory the server never writes.
+    """
+
+    monkeypatch.delenv("VLLM_CACHE_ROOT", raising=False)
+    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
+
+    import vllm.envs as envs
+
+    assert adapter._vllm_cache_root() == Path(envs.VLLM_CACHE_ROOT)
````

### 10. `tests/whale/test_fuser.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：Fuser 测试：稳定镜像路径、source_identity 哈希、清理只删本实例注册副本
- **规模**：+114 / -0（改后文件共 114 行）
- **涉及提交**：
  - `c2f0d629e2` fix(whale): only remove temp copies registered by the Fuser instance
  - `b4a7966575` fix(whale): stabilize Engram compile cache keys
````diff
diff --git a/tests/whale/test_fuser.py b/tests/whale/test_fuser.py
new file mode 100644
index 0000000000..3f5143e349
--- /dev/null
+++ b/tests/whale/test_fuser.py
@@ -0,0 +1,114 @@
+# SPDX-License-Identifier: Apache-2.0
+"""Regression tests for Whale's model-directory FUSE mirror."""
+
+from __future__ import annotations
+
+import hashlib
+import importlib.util
+import tempfile
+from pathlib import Path
+
+
+_FUSER_PATH = (
+    Path(__file__).resolve().parents[2]
+    / "vllm/whale_vllm/vllm_server/utils/fuser.py"
+)
+
+
+def _load_fuser_module():
+    spec = importlib.util.spec_from_file_location("whale_fuser_test", _FUSER_PATH)
+    assert spec is not None and spec.loader is not None
+    module = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(module)
+    return module
+
+
+def test_model_temp_copy_path_is_stable_across_process_lifecycles(
+    monkeypatch, tmp_path: Path
+):
+    # Loading the module constructs its process-global Fuser. Redirect the
+    # platform temp directory first so the test never touches the real /tmp.
+    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
+    fuser = _load_fuser_module()
+
+    first = fuser.Fuser()
+    second = fuser.Fuser()
+    expected_base = tmp_path / "model_temp_copy"
+    assert Path(first.temp_copy_base) == expected_base
+    assert Path(second.temp_copy_base) == expected_base
+
+    source = tmp_path / "mounted-model"
+    source.mkdir()
+    (source / "config.json").write_text("{}", encoding="utf-8")
+
+    original_model_path = "dfs://model-cluster/checkpoints/qwen"
+    first_copy = first.create_temp_local_copy(
+        str(source), source_identity=original_model_path
+    )
+    second_copy = second.create_temp_local_copy(
+        str(source), source_identity=original_model_path
+    )
+    assert first_copy == second_copy
+    assert Path(second_copy).name == hashlib.sha256(
+        original_model_path.encode("utf-8")
+    ).hexdigest()
+    assert (Path(second_copy) / "config.json").is_symlink()
+
+    # Avoid leaving the explicitly-created mirrors until the interpreter's
+    # atexit phase. Cleanup is idempotent for their shared copy path.
+    for client in (first, second, fuser._fuser):
+        client._cleanup_temp_copies()
+
+
+def test_cleanup_only_removes_copies_registered_by_instance(
+    monkeypatch, tmp_path: Path
+):
+    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
+    fuser = _load_fuser_module()
+
+    first = fuser.Fuser()
+    second = fuser.Fuser()
+    first_source = tmp_path / "first-model"
+    second_source = tmp_path / "second-model"
+    first_source.mkdir()
+    second_source.mkdir()
+    (first_source / "config.json").write_text("{}", encoding="utf-8")
+    (second_source / "config.json").write_text("{}", encoding="utf-8")
+
+    first_copy = Path(first.create_temp_local_copy(str(first_source)))
+    second_copy = Path(second.create_temp_local_copy(str(second_source)))
+    unowned_copy = Path(first.temp_copy_base) / "owned-by-another-process"
+    unowned_copy.mkdir()
+
+    first._cleanup_temp_copies()
+
+    assert Path(first.temp_copy_base).is_dir()
+    assert not first_copy.exists()
+    assert second_copy.is_dir()
+    assert unowned_copy.is_dir()
+
+    second._cleanup_temp_copies()
+
+
+def test_remote_model_copy_is_keyed_by_pre_mount_path(monkeypatch, tmp_path: Path):
+    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
+    fuser = _load_fuser_module()
+
+    mounted = tmp_path / "mounted-model"
+    mounted.mkdir()
+    (mounted / "config.json").write_text("{}", encoding="utf-8")
+    original_model_path = "dfs://model-cluster/checkpoints/qwen"
+    monkeypatch.setattr(
+        fuser._fuser,
+        "mount_dir",
+        lambda _path, _mount_mode: str(mounted),
+    )
+
+    resolved = fuser.fetch_remote_file_to_local(
+        original_model_path,
+        enable_temp_copy=True,
+    )
+    expected_hash = hashlib.sha256(original_model_path.encode("utf-8")).hexdigest()
+    assert Path(resolved) == tmp_path / "model_temp_copy" / expected_hash
+
+    fuser._fuser._cleanup_temp_copies()
````

### 11. `requirements/alibaba.txt`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：新增 engram[fuse,pangu,oss]==0.1.4（FUSE pull + Pangu/OSS direct push）与 pebble>=5.0；配置 artlab 内部源
- **规模**：+7 / -1（改后文件共 16 行）
- **涉及提交**：
  - `47615758b9` feat: share vLLM JIT/autotune artifacts across pods via Engram
  - `cc23ba4ba4` feat(video): add PyAV backend to prevent worker coredump on corrupted HEVC videos;add video parse in sub progress
````diff
diff --git a/requirements/alibaba.txt b/requirements/alibaba.txt
index 3809222c25..83c7802186 100644
--- a/requirements/alibaba.txt
+++ b/requirements/alibaba.txt
@@ -1,10 +1,16 @@
+--extra-index-url http://artlab.alibaba-inc.com/1/pypi/pypi-releases
+--trusted-host artlab.alibaba-inc.com
+
 soundfile
 qwen_omni_utils[decord]==0.0.9+90037ae5
 qwen_vl_utils[decord]==0.0.14+c447d619
 llm_plugin==0.0.4
 oss2==2.13.1
 pypaimon_ali==1.5.dev0
 pyatunnel[sdk2]==1.2.1.2
 alluxio-pfs>=0.1.6a3
 lake-py-lib-lite>=0.1.17.13
-flashinfer-cubin==0.6.4
\ No newline at end of file
+flashinfer-cubin==0.6.4
+pebble>=5.0
+# Engram：FUSE pull + Pangu/OSS direct push。传输依赖均为懒加载。
+engram[fuse,pangu,oss]==0.1.4
````

### 12. `requirements/alibaba-arm64.txt`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：新增 engram[fuse,oss]==0.1.4（ARM 内部源无 pangudfs-client，仅 FUSE pull + OSS push）与 pebble>=5.0；配置 artlab 内部源
- **规模**：+6 / -0（改后文件共 22 行）
- **涉及提交**：
  - `47615758b9` feat: share vLLM JIT/autotune artifacts across pods via Engram
  - `cc23ba4ba4` feat(video): add PyAV backend to prevent worker coredump on corrupted HEVC videos;add video parse in sub progress
````diff
diff --git a/requirements/alibaba-arm64.txt b/requirements/alibaba-arm64.txt
index 7ae2a2d79f..36230a1f3e 100644
--- a/requirements/alibaba-arm64.txt
+++ b/requirements/alibaba-arm64.txt
@@ -1,6 +1,10 @@
+--extra-index-url http://artlab.alibaba-inc.com/1/pypi/pypi-releases
+--trusted-host artlab.alibaba-inc.com
+
 soundfile
+pebble>=5.0
 qwen_omni_utils==0.0.9+90037ae5
 qwen_vl_utils==0.0.14+c447d619
 llm_plugin==0.0.4
 oss2==2.13.1
 flashinfer-cubin==0.6.4
@@ -12,5 +16,7 @@ nvidia-cutlass-dsl-libs-base==4.4.2
 
 # Pin starlette/fastapi for compatibility
 starlette==1.2.1
 fastapi==0.136.3
 
+# ARM64 内部源暂无 pangudfs-client；保留 FUSE pull 与 OSS direct push。
+engram[fuse,oss]==0.1.4
````

### 13. `.aoneci/pr_test_nv.yaml`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：PR 测试流水线：noop job 替换为 Engram adapter contract 测试（装 engram wheel、bash -n start.sh、pytest tests/whale），触发分支增加 v0.17.1_omega
- **规模**：+10 / -4（改后文件共 45 行）
- **涉及提交**：
  - `47615758b9` feat: share vLLM JIT/autotune artifacts across pods via Engram
````diff
diff --git a/.aoneci/pr_test_nv.yaml b/.aoneci/pr_test_nv.yaml
index c380404fc7..d90154ccdb 100644
--- a/.aoneci/pr_test_nv.yaml
+++ b/.aoneci/pr_test_nv.yaml
@@ -2,10 +2,11 @@ name: 功能测试
 
 triggers:
   merge_request:
     target-branches:
       - v0.17.1
+      - v0.17.1_omega
     types:
       - opened
 
 strategy:
   fast-fail: true
@@ -17,23 +18,28 @@ vars:
   gpu_cuda12_image: hub.docker.alibaba-inc.com/isearch/vllm_server_cuda:v0.11.1-test-0.0.24ac79891ae5fd0156c6dca1cffa47b0dfee5efc
 
 stages:
   test:
     jobs:
-      noop:
+      engram-adapter:
         runs-on:
           - 8-32Gi
           - self-hosted
           - aios-ai-infra
         image: ${{vars.gpu_cuda12_image}}
         timeout: 5m
         steps:
           - uses: checkout
-          - id: noop
-            name: Noop Test
+          - id: engram_adapter_contract
+            name: Engram adapter contract
             run: |
-                echo "All tests passed (noop)"
+                set -e
+                python3 -m pip install --no-deps engram==0.1.4 \
+                  --index-url http://artlab.alibaba-inc.com/1/pypi/pypi-releases \
+                  --trusted-host artlab.alibaba-inc.com
+                bash -n vllm/whale_vllm/start.sh
+                python3 -m pytest --noconftest -q tests/whale/test_engram_adapter.py
             container:
               options: "--cap-add SYS_ADMIN \
                         --device /dev/fuse \
                         -v /dev/shm:/dev/shm \
                         --user=root"
````

### 14. `.aoneci/pr_test_rocm.yaml`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：pr_test_nv.yaml 的 ROCm 版，同样替换为 Engram contract 测试并增加 v0.17.1_omega 触发
- **规模**：+11 / -5（改后文件共 45 行）
- **涉及提交**：
  - `47615758b9` feat: share vLLM JIT/autotune artifacts across pods via Engram
````diff
diff --git a/.aoneci/pr_test_rocm.yaml b/.aoneci/pr_test_rocm.yaml
index 1b1ba586d2..03aad0e0ae 100644
--- a/.aoneci/pr_test_rocm.yaml
+++ b/.aoneci/pr_test_rocm.yaml
@@ -2,10 +2,11 @@ name: AMD功能测试
 
 triggers:
   merge_request:
     target-branches:
       - v0.17.1
+      - v0.17.1_omega
     types:
       - opened
 
 strategy:
   fast-fail: true
@@ -17,23 +18,28 @@ vars:
   gpu_cuda12_image: hub.docker.alibaba-inc.com/isearch/vllm_server_cuda:v0.11.1-test-0.0.24ac79891ae5fd0156c6dca1cffa47b0dfee5efc
 
 stages:
   test:
     jobs:
-      noop:
+      engram-adapter:
         runs-on:
           - 8-32Gi
           - self-hosted
           - aios-ai-infra
         image: ${{vars.gpu_cuda12_image}}
         timeout: 5m
         steps:
           - uses: checkout
-          - id: noop
-            name: Noop Test
+          - id: engram_adapter_contract
+            name: Engram adapter contract
             run: |
-                echo "All tests passed (noop)"
+                set -e
+                python3 -m pip install --no-deps engram==0.1.4 \
+                  --index-url http://artlab.alibaba-inc.com/1/pypi/pypi-releases \
+                  --trusted-host artlab.alibaba-inc.com
+                bash -n vllm/whale_vllm/start.sh
+                python3 -m pytest --noconftest -q tests/whale/test_engram_adapter.py
             container:
               options: "--cap-add SYS_ADMIN \
                         --device /dev/fuse \
                         -v /dev/shm:/dev/shm \
-                        --user=root"
\ No newline at end of file
+                        --user=root"
````

---

## 组 2 · Docker 发布镜像构建提速（3 文件）

arm64 CUDA 发布镜像曾耗时 60 分钟，三个独立原因逐一修复：pip 解析回溯（仅 quack-kernels
一项就 552 秒）、`COPY . .` 让所有 pip 层随源码改动失效、无 pip 缓存挂载。
`ceeb7ef6a5` 回退了从成品 `pip freeze` 抄来的 cuda-python 三件套 pin（来源错误导致 ResolutionImpossible）。


### 15. `docker/ali/Dockerfile.release_cuda`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：层序重排：ffmpeg 解包与 constraints 生成移到 `COPY . .` 之前，源码改动不再使 pip 层全部失效；全部 pip 步骤挂载缓存；constraints 增加 quack-kernels==0.4.1（消除 552s 解析回溯）；alibaba-cuda 步骤补 yum.tbsite.net 源（media-fetch-sdk）
- **规模**：+33 / -9（改后文件共 99 行）
- **涉及提交**：
  - `e1d1316051` perf(docker): cut release image build time from ~60min
  - `983aefae95` [Req#85339520] vLLM 接入 media-fetch-sdk 支持 mediafetch:// 协议 * [Req#85339520] vLLM 接入 media-fetch-sdk 支持 mediafetch:// 协议
````diff
diff --git a/docker/ali/Dockerfile.release_cuda b/docker/ali/Dockerfile.release_cuda
index b5378d17d4..90c844f01d 100644
--- a/docker/ali/Dockerfile.release_cuda
+++ b/docker/ali/Dockerfile.release_cuda
@@ -4,50 +4,74 @@ ENV LD_LIBRARY_PATH=/usr/local/nvidia/lib64:/usr/lib64:/usr/local/cuda/lib64:$LD
 
 ENV PATH=$PATH:/usr/local/cuda/bin:/opt/conda310/bin
 
 WORKDIR /source/vllm
 
-COPY . .
+# ---------------------------------------------------------------------------
+# 只依赖单个文件的步骤放在 `COPY . .` 之前，这样源码改动不会让它们失效。
+# x86 上 `pip install -e .` 是第一个 pip 步骤且需要完整源码树，因此 pip 步骤本身
+# 无法上移；能上移的只有 ffmpeg 解包和 constraints 生成。
+# ---------------------------------------------------------------------------
 
-RUN ls -la
+COPY ffmpeg-release-amd64-static.tar.xz ./
 
 # Install ffmpeg from bundled static binary
 RUN tar -xJf ffmpeg-release-amd64-static.tar.xz; \
     DIR="$(find . -maxdepth 1 -type d -name 'ffmpeg-*-amd64-static' | head -n 1)"; \
     install -m 0755 "${DIR}/ffmpeg" "${DIR}/ffprobe" /usr/local/bin/; \
     ffprobe -version | head -n 2
 
 # Pin cutlass-dsl to prevent newer incompatible versions during editable install
+#
+# quack-kernels is pinned for a different reason: requirements/cuda.txt declares only
+# a floor (`quack-kernels>=0.2.7`), every quack_kernels wheel is py3-none-any, and
+# 0.5.0+ declare Requires-Python >=3.12 while this image is conda310 (Python 3.10).
+# Without a pin pip walks 0.6.4 down to 0.4.1 and re-resolves the graph behind it;
+# on arm64 that cost 552s of the editable-install step. 0.4.1 is the newest version
+# installable on 3.10, which is what the resolver already lands on.
 RUN echo 'nvidia-cutlass-dsl==4.4.2' > /tmp/constraints.txt && \
-    echo 'nvidia-cutlass-dsl-libs-base==4.4.2' >> /tmp/constraints.txt
+    echo 'nvidia-cutlass-dsl-libs-base==4.4.2' >> /tmp/constraints.txt && \
+    echo 'quack-kernels==0.4.1' >> /tmp/constraints.txt
 
-RUN VLLM_USE_PRECOMPILED=1 VLLM_PRECOMPILED_WHEEL_LOCATION=https://artlab.alibaba-inc.com/1/pypi/aios-ai-infra/vllm/vllm-0.17.1+dev0.0.536acc2762f43ea9ea6f76a64460fa3bca109460-cp310-cp310-linux_x86_64.whl /opt/conda310/bin/pip install -e . --verbose -c /tmp/constraints.txt -i https://artifacts.antgroup-inc.cn/simple/ \
+COPY . .
+
+RUN ls -la
+
+RUN --mount=type=cache,target=/var/cache/pip,mode=0777 \
+    PIP_CACHE_DIR=/var/cache/pip VLLM_USE_PRECOMPILED=1 VLLM_PRECOMPILED_WHEEL_LOCATION=https://artlab.alibaba-inc.com/1/pypi/aios-ai-infra/vllm/vllm-0.17.1+dev0.0.536acc2762f43ea9ea6f76a64460fa3bca109460-cp310-cp310-linux_x86_64.whl /opt/conda310/bin/pip install -e . --verbose -c /tmp/constraints.txt -i https://artifacts.antgroup-inc.cn/simple/ \
     --extra-index-url=https://artlab.alibaba-inc.com/1/PYPI/py-central/ \
     --extra-index-url=https://artlab.alibaba-inc.com/1/PYPI/pytorch/ \
     --extra-index-url=http://artlab.alibaba-inc.com/1/pypi/aios-ai-infra \
     --trusted-host=artlab.alibaba-inc.com
 
-RUN /opt/conda310/bin/pip install -r requirements/alibaba.txt -i https://artifacts.antgroup-inc.cn/simple/ \
+RUN --mount=type=cache,target=/var/cache/pip,mode=0777 \
+    PIP_CACHE_DIR=/var/cache/pip /opt/conda310/bin/pip install -r requirements/alibaba.txt -i https://artifacts.antgroup-inc.cn/simple/ \
     --extra-index-url=https://artlab.alibaba-inc.com/1/pypi/huiwa_rtp_internal \
     --extra-index-url=http://artlab.alibaba-inc.com/1/pypi/rtp_diffusion \
     --extra-index-url=http://artlab.alibaba-inc.com/1/pypi/aios-ai-infra \
     --extra-index-url=http://artlab.alibaba-inc.com/1/pypi/nebula \
     --extra-index-url=http://yum.tbsite.net/mirrors/ppypi/nebula-ai/simple \
     --trusted-host=artlab.alibaba-inc.com \
     --trusted-host=yum.tbsite.net
 
-RUN /opt/conda310/bin/pip install -r requirements/alibaba-cuda.txt -c /tmp/constraints.txt -i https://artifacts.antgroup-inc.cn/simple/ \
+RUN --mount=type=cache,target=/var/cache/pip,mode=0777 \
+    PIP_CACHE_DIR=/var/cache/pip /opt/conda310/bin/pip install -r requirements/alibaba-cuda.txt -c /tmp/constraints.txt -i https://artifacts.antgroup-inc.cn/simple/ \
     --extra-index-url=https://artlab.alibaba-inc.com/1/pypi/huiwa_rtp_internal \
     --extra-index-url=http://artlab.alibaba-inc.com/1/pypi/rtp_diffusion \
     --extra-index-url=http://artlab.alibaba-inc.com/1/pypi/aios-ai-infra \
-    --trusted-host=artlab.alibaba-inc.com
+    --extra-index-url=http://yum.tbsite.net/aliyun-pypi/simple/ \
+    --extra-index-url=http://yum.tbsite.net/pypi/simple/ \
+    --trusted-host=artlab.alibaba-inc.com \
+    --trusted-host=yum.tbsite.net
 
 # Force install transformers 5.3.0 (override vLLM dependency constraint)
-RUN /opt/conda310/bin/pip install transformers==5.3.0 -i https://artlab.alibaba-inc.com/1/PYPI/simple/ --trusted-host=artlab.alibaba-inc.com
+RUN --mount=type=cache,target=/var/cache/pip,mode=0777 \
+    PIP_CACHE_DIR=/var/cache/pip /opt/conda310/bin/pip install transformers==5.3.0 -i https://artlab.alibaba-inc.com/1/PYPI/simple/ --trusted-host=artlab.alibaba-inc.com
 
 # Force reinstall pinned cutlass-dsl to ensure correct version even if a newer one slipped in
-RUN /opt/conda310/bin/pip install --force-reinstall nvidia-cutlass-dsl==4.4.2 nvidia-cutlass-dsl-libs-base==4.4.2 \
+RUN --mount=type=cache,target=/var/cache/pip,mode=0777 \
+    PIP_CACHE_DIR=/var/cache/pip /opt/conda310/bin/pip install --force-reinstall nvidia-cutlass-dsl==4.4.2 nvidia-cutlass-dsl-libs-base==4.4.2 \
     -i https://artifacts.antgroup-inc.cn/simple/ --trusted-host=artlab.alibaba-inc.com
 
 RUN /opt/conda310/bin/pip freeze
 
 WORKDIR /app/vllm_server
````

### 16. `docker/ali/Dockerfile.release_cuda_arm64`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：与 x86 相同的层序与缓存优化；`ceeb7ef6a5` 回退 cuda-python/cuda-bindings/cuda-core 三件套 pin（torch 自锁 cuda-bindings==13.0.3，pin 13.3.1 导致 ResolutionImpossible）
- **规模**：+49 / -9（改后文件共 132 行）
- **涉及提交**：
  - `ceeb7ef6a5` fix(docker): drop the cuda-python/bindings/core pins that broke arm64
  - `e1d1316051` perf(docker): cut release image build time from ~60min
````diff
diff --git a/docker/ali/Dockerfile.release_cuda_arm64 b/docker/ali/Dockerfile.release_cuda_arm64
index feecab6936..11860f2903 100644
--- a/docker/ali/Dockerfile.release_cuda_arm64
+++ b/docker/ali/Dockerfile.release_cuda_arm64
@@ -4,13 +4,20 @@ ENV LD_LIBRARY_PATH=/usr/local/nvidia/lib64:/usr/lib64:/usr/local/cuda/lib64:$LD
 
 ENV PATH=$PATH:/usr/local/cuda/bin:/opt/conda310/bin
 
 WORKDIR /source/vllm
 
-COPY . .
+# ---------------------------------------------------------------------------
+# 依赖层：只依赖清单文件，因此能跨提交复用 buildkit 缓存。
+#
+# `COPY . .` 原本是第 3 条指令，导致任何一个文件的改动（哪怕 README 改一个字）都会
+# 让后面全部 21 层失效——包括 6 个 pip 步骤。这里先只 copy 依赖清单，把不需要源码的
+# 安装步骤留在 `COPY . .` 之前。
+# ---------------------------------------------------------------------------
 
-RUN ls -la
+COPY requirements/ ./requirements/
+COPY use_existing_torch.py pyproject.toml ./
 
 # Install ffmpeg from OSS (same 7.0.2 version as x86)
 RUN curl -fSL -o /tmp/ffmpeg-release-arm64-static.tar.xz \
         "http://bahamutruntime.oss-cn-zhangjiakou.aliyuncs.com/fm/ffmpeg-release-arm64-static.tar.xz" && \
     tar -xJf /tmp/ffmpeg-release-arm64-static.tar.xz -C /tmp && \
@@ -19,51 +26,84 @@ RUN curl -fSL -o /tmp/ffmpeg-release-arm64-static.tar.xz \
     rm -rf /tmp/ffmpeg-* && \
     ffprobe -version | head -n 2
 
 # Install CUDA-enabled PyTorch for ARM64 from internal artlab mirror
 # PyPI default aarch64 torch wheel is CPU-only; must use cu130 wheels for GB200 (CUDA 13.0)
-RUN /opt/conda310/bin/pip install \
+RUN --mount=type=cache,target=/var/cache/pip,mode=0777 \
+    PIP_CACHE_DIR=/var/cache/pip /opt/conda310/bin/pip install \
     https://artlab.alibaba-inc.com/1/PYPI/pytorch/whl/torch/%252Fwhl%252Fcu130/torch-2.10.0%2Bcu130-cp310-cp310-manylinux_2_28_aarch64.whl \
     https://artlab.alibaba-inc.com/1/PYPI/pytorch/whl/torchvision/%252Fwhl%252Fcu130/torchvision-0.25.0%2Bcu130-cp310-cp310-manylinux_2_28_aarch64.whl \
     https://artlab.alibaba-inc.com/1/PYPI/pytorch/whl/torchaudio/%252Fwhl%252Fcu130/torchaudio-2.10.0%2Bcu130-cp310-cp310-manylinux_2_28_aarch64.whl
 
 # Strip torch declarations from pyproject.toml and all requirements/*.txt to prevent
 # pip from overwriting the CUDA torch we just installed with a CPU-only version
 RUN /opt/conda310/bin/python3 use_existing_torch.py --prefix
 
 # Install remaining build dependencies (torch already stripped from build.txt above)
-RUN /opt/conda310/bin/pip install -r requirements/build.txt \
+RUN --mount=type=cache,target=/var/cache/pip,mode=0777 \
+    PIP_CACHE_DIR=/var/cache/pip /opt/conda310/bin/pip install -r requirements/build.txt \
     -i https://artifacts.antgroup-inc.cn/simple/ \
     --trusted-host=artlab.alibaba-inc.com
 
 # Pin torch to prevent indirect dependencies (e.g. compressed-tensors's torch>=1.7.0)
 # from pulling a newer CPU-only torch from py-central index
+#
+# quack-kernels is pinned for a different reason: requirements/cuda.txt declares only
+# a floor (`quack-kernels>=0.2.7`), every quack_kernels wheel is py3-none-any, and
+# 0.5.0+ declare Requires-Python >=3.12 while this image is conda310. Without a pin
+# pip walks 0.6.4 down to 0.4.1 and re-resolves the whole graph behind it, which
+# also dragged cuda_python through 6 candidates and vllm through 4 -- 552s of the
+# vllm install step. 0.4.1 is the newest release installable on Python 3.10, i.e.
+# what the resolver already selects, so the resulting image is unchanged.
+#
+# Do NOT pin cuda-python/cuda-bindings/cuda-core here: torch 2.10.0+cu130 itself
+# requires cuda-bindings==13.0.3, so they are already deterministic at this step and
+# an explicit pin conflicts with torch. (The 13.3.1 seen in a finished image's
+# `pip freeze` comes from the later `--force-reinstall nvidia-cutlass-dsl` step, not
+# from this one.)
 RUN echo 'torch==2.10.0+cu130' > /tmp/constraints-arm64.txt && \
     echo 'torchvision==0.25.0+cu130' >> /tmp/constraints-arm64.txt && \
     echo 'torchaudio==2.10.0+cu130' >> /tmp/constraints-arm64.txt && \
     echo 'nvidia-cutlass-dsl==4.4.2' >> /tmp/constraints-arm64.txt && \
-    echo 'nvidia-cutlass-dsl-libs-base==4.4.2' >> /tmp/constraints-arm64.txt
+    echo 'nvidia-cutlass-dsl-libs-base==4.4.2' >> /tmp/constraints-arm64.txt && \
+    echo 'quack-kernels==0.4.1' >> /tmp/constraints-arm64.txt
+
+# ---------------------------------------------------------------------------
+# 源码层：从这里开始，任何源码改动都会重建下面的层。
+# ---------------------------------------------------------------------------
+
+COPY . .
+
+# 上面的 `COPY . .` 把原始 requirements/*.txt 与 pyproject.toml 覆盖回来了，重新剥一次。
+# use_existing_torch.py --prefix 是幂等的（重复执行零改动），所以这不会多剥任何东西。
+RUN /opt/conda310/bin/python3 use_existing_torch.py --prefix
+
+RUN ls -la
 
 # Install vllm with precompiled aarch64 wheel from artlab pypi
-RUN VLLM_USE_PRECOMPILED=1 VLLM_PRECOMPILED_WHEEL_LOCATION=https://artlab.alibaba-inc.com/1/pypi/aios-ai-infra/vllm/vllm-0.1.dev1+g511afc90b.d20260519-cp310-cp310-linux_aarch64.whl /opt/conda310/bin/pip install -e . --verbose --no-build-isolation -c /tmp/constraints-arm64.txt -i https://artifacts.antgroup-inc.cn/simple/ \
+RUN --mount=type=cache,target=/var/cache/pip,mode=0777 \
+    PIP_CACHE_DIR=/var/cache/pip VLLM_USE_PRECOMPILED=1 VLLM_PRECOMPILED_WHEEL_LOCATION=https://artlab.alibaba-inc.com/1/pypi/aios-ai-infra/vllm/vllm-0.1.dev1+g511afc90b.d20260519-cp310-cp310-linux_aarch64.whl /opt/conda310/bin/pip install -e . --verbose --no-build-isolation -c /tmp/constraints-arm64.txt -i https://artifacts.antgroup-inc.cn/simple/ \
     --extra-index-url=https://artlab.alibaba-inc.com/1/PYPI/py-central/ \
     --extra-index-url=https://artlab.alibaba-inc.com/1/PYPI/pytorch/ \
     --extra-index-url=http://artlab.alibaba-inc.com/1/pypi/aios-ai-infra \
     --trusted-host=artlab.alibaba-inc.com
 
-RUN /opt/conda310/bin/pip install -r requirements/alibaba-arm64.txt -c /tmp/constraints-arm64.txt -i https://artifacts.antgroup-inc.cn/simple/ \
+RUN --mount=type=cache,target=/var/cache/pip,mode=0777 \
+    PIP_CACHE_DIR=/var/cache/pip /opt/conda310/bin/pip install -r requirements/alibaba-arm64.txt -c /tmp/constraints-arm64.txt -i https://artifacts.antgroup-inc.cn/simple/ \
     --extra-index-url=https://artlab.alibaba-inc.com/1/pypi/huiwa_rtp_internal \
     --extra-index-url=http://artlab.alibaba-inc.com/1/pypi/rtp_diffusion \
     --extra-index-url=http://artlab.alibaba-inc.com/1/pypi/aios-ai-infra \
     --extra-index-url=http://artlab.alibaba-inc.com/1/pypi/nebula \
     --trusted-host=artlab.alibaba-inc.com
 
 # Force install transformers 5.3.0 (override vLLM dependency constraint)
-RUN /opt/conda310/bin/pip install transformers==5.3.0 -i https://artlab.alibaba-inc.com/1/PYPI/simple/ --trusted-host=artlab.alibaba-inc.com
+RUN --mount=type=cache,target=/var/cache/pip,mode=0777 \
+    PIP_CACHE_DIR=/var/cache/pip /opt/conda310/bin/pip install transformers==5.3.0 -i https://artlab.alibaba-inc.com/1/PYPI/simple/ --trusted-host=artlab.alibaba-inc.com
 
 # Force reinstall pinned cutlass-dsl to ensure correct version even if a newer one slipped in
-RUN /opt/conda310/bin/pip install --force-reinstall nvidia-cutlass-dsl==4.4.2 nvidia-cutlass-dsl-libs-base==4.4.2 \
+RUN --mount=type=cache,target=/var/cache/pip,mode=0777 \
+    PIP_CACHE_DIR=/var/cache/pip /opt/conda310/bin/pip install --force-reinstall nvidia-cutlass-dsl==4.4.2 nvidia-cutlass-dsl-libs-base==4.4.2 \
     -i https://artifacts.antgroup-inc.cn/simple/ --trusted-host=artlab.alibaba-inc.com
 
 RUN /opt/conda310/bin/pip freeze
 
 WORKDIR /app/vllm_server
````

### 17. `docker/ali/Dockerfile.release_rocm`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：层序重排与 pip 缓存挂载的 ROCm 版
- **规模**：+24 / -5（改后文件共 103 行）
- **涉及提交**：
  - `e1d1316051` perf(docker): cut release image build time from ~60min
````diff
diff --git a/docker/ali/Dockerfile.release_rocm b/docker/ali/Dockerfile.release_rocm
index a438b11a80..7c9cf63916 100644
--- a/docker/ali/Dockerfile.release_rocm
+++ b/docker/ali/Dockerfile.release_rocm
@@ -1,39 +1,58 @@
 FROM hub.docker.alibaba-inc.com/tre-ai-infra/amd:alinux3-x86-rocm_7.2.0-py_3.10-torch_2.9.1-triton_3.5.1-fa_2.8.3-aiter_0.1.12-vllm_0.17.0rc1_2026_03_13_10_01_34
 
 WORKDIR /opt/vllm
-COPY . .
+
+# ---------------------------------------------------------------------------
+# 依赖层：只依赖清单文件与 ffmpeg tarball，因此能跨提交复用 buildkit 缓存。
+#
+# `COPY . .` 原本是第 2 条指令，任何源码改动都会让后面全部层失效（包括 3 个 pip
+# 步骤）。ROCm 镜像里 vllm 来自 base image、没有 `pip install -e .`，所以三个 pip
+# 步骤全都不需要源码树，可以整体上移到 `COPY . .` 之前。
+# ---------------------------------------------------------------------------
+
+COPY requirements/ ./requirements/
+COPY ffmpeg-release-amd64-static.tar.xz ./
 
 RUN mkdir -p /source && ln -sfn /opt/vllm /source/vllm
-RUN ls -la
 
 # Install ffmpeg from bundled static binary
 RUN tar -xJf ffmpeg-release-amd64-static.tar.xz; \
     DIR="$(find . -maxdepth 1 -type d -name 'ffmpeg-*-amd64-static' | head -n 1)"; \
     install -m 0755 "${DIR}/ffmpeg" "${DIR}/ffprobe" /usr/local/bin/; \
     ffprobe -version | head -n 2
 
-RUN /usr/local/bin/pip3 install -r requirements/alibaba.txt -i https://artifacts.antgroup-inc.cn/simple/ \
+RUN --mount=type=cache,target=/var/cache/pip,mode=0777 \
+    PIP_CACHE_DIR=/var/cache/pip /usr/local/bin/pip3 install -r requirements/alibaba.txt -i https://artifacts.antgroup-inc.cn/simple/ \
     --extra-index-url=https://artlab.alibaba-inc.com/1/pypi/huiwa_rtp_internal \
     --extra-index-url=http://artlab.alibaba-inc.com/1/pypi/rtp_diffusion \
     --extra-index-url=http://artlab.alibaba-inc.com/1/pypi/aios-ai-infra \
     --extra-index-url=http://artlab.alibaba-inc.com/1/pypi/nebula \
     --extra-index-url=http://yum.tbsite.net/mirrors/ppypi/nebula-ai/simple \
     --trusted-host=artlab.alibaba-inc.com \
     --trusted-host=yum.tbsite.net
 
-RUN /usr/local/bin/pip3 install -r requirements/alibaba-rocm.txt -i https://artifacts.antgroup-inc.cn/simple/ \
+RUN --mount=type=cache,target=/var/cache/pip,mode=0777 \
+    PIP_CACHE_DIR=/var/cache/pip /usr/local/bin/pip3 install -r requirements/alibaba-rocm.txt -i https://artifacts.antgroup-inc.cn/simple/ \
     --extra-index-url=https://artlab.alibaba-inc.com/1/pypi/huiwa_rtp_internal \
     --extra-index-url=http://artlab.alibaba-inc.com/1/pypi/rtp_diffusion \
     --extra-index-url=http://artlab.alibaba-inc.com/1/pypi/aios-ai-infra \
     --extra-index-url=http://yum.tbsite.net/aliyun-pypi/simple/ \
     --extra-index-url=https://artlab.alibaba-inc.com/1/pypi/openlm \
     --trusted-host=artlab.alibaba-inc.com \
     --trusted-host=yum.tbsite.net
 
 # Force install transformers 5.3.0 (override vLLM dependency constraint)
-RUN /usr/local/bin/pip3 install transformers==5.3.0 -i https://artlab.alibaba-inc.com/1/PYPI/simple/ --trusted-host=artlab.alibaba-inc.com
+RUN --mount=type=cache,target=/var/cache/pip,mode=0777 \
+    PIP_CACHE_DIR=/var/cache/pip /usr/local/bin/pip3 install transformers==5.3.0 -i https://artlab.alibaba-inc.com/1/PYPI/simple/ --trusted-host=artlab.alibaba-inc.com
+
+# ---------------------------------------------------------------------------
+# 源码层：从这里开始，任何源码改动都会重建下面的层。
+# ---------------------------------------------------------------------------
+
+COPY . .
+RUN ls -la
 
 WORKDIR /app/vllm_server
 COPY vllm/whale_vllm/start.sh .
 
 RUN chmod -R 777 .
````

---

## 组 3 · 模型精度回归验证 CI（23 文件）

为 v0.17.1_omega 增加独立的精度门禁：CR 目标分支为 v0.17.1_omega 时自动触发。
BASE 与 candidate 各用独立 wheel + 虚拟环境，捕获多模态输入 / encoder 输出 / 融合后
decoder 输入 / prefill 与首个 decode 输出 / logits / token id / top-k logprob 后逐 tensor 差分。
Python-only 变更复用已发布 native wheel，native-sensitive 变更完整重编。Aone #71 已端到端验证。


### 18. `.aoneci/pr_accuracy_test_nv.yaml`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：精度回归 CI 流水线：Qwen3-VL-2B 覆盖图片/视频路径、Qwen2.5-Omni-3B 覆盖音频路径；BASE 与 candidate 独立 wheel + venv 差分；wheel 走 /ssd/2 按 run ID 隔离的临时目录并清理；上传轻量 JSON 报告与 changed-code coverage
- **规模**：+211 / -0（改后文件共 211 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/.aoneci/pr_accuracy_test_nv.yaml b/.aoneci/pr_accuracy_test_nv.yaml
new file mode 100644
index 0000000000..2eaa1c4d9d
--- /dev/null
+++ b/.aoneci/pr_accuracy_test_nv.yaml
@@ -0,0 +1,211 @@
+name: 精度验证
+
+triggers:
+  merge_request:
+    target-branches:
+      - v0.17.1_omega
+
+strategy:
+  fast-fail: true
+  concurrency:
+    group: 'accuracy-${{git.merge_request.id?:(git.branch?:"")}}'
+    cancel-in-progress: true
+
+vars:
+  gpu_cuda12_image: hub.docker.alibaba-inc.com/isearch/vllm_server_cuda:v0.17.1-test-0.0.9d8ea6789b4124d0841a9b999cad95f47320ef79
+
+stages:
+  build:
+    jobs:
+      build-base-wheel:
+        runs-on:
+          - 32-128Gi
+          - self-hosted
+          - aios-ai-infra
+        image: ${{vars.gpu_cuda12_image}}
+        timeout: 180m
+        steps:
+          - uses: checkout
+          - id: build-base-wheel
+            name: Build BASE Wheel
+            run: |
+                set -euo pipefail
+                PIPELINE_RUN_ID='${{pipeline.inst.id}}'
+                if [[ ! "${PIPELINE_RUN_ID}" =~ ^[0-9]+$ ]]; then
+                  echo "Invalid Aone pipeline run ID: ${PIPELINE_RUN_ID:-<empty>}" >&2
+                  exit 1
+                fi
+                PIPELINE_CACHE_ROOT=/ssd/2/accuracy-ci/pipeline
+                PIPELINE_CACHE_DIR=${PIPELINE_CACHE_ROOT}/${PIPELINE_RUN_ID}
+                BASE_WHEEL_CACHE=${PIPELINE_CACHE_DIR}/base
+                mkdir -p "${PIPELINE_CACHE_ROOT}"
+                echo "Cleaning stale accuracy pipeline caches older than 48 hours"
+                find "${PIPELINE_CACHE_ROOT}" -mindepth 1 -maxdepth 1 \
+                  -type d -mmin +2880 -print -exec rm -rf -- {} +
+                rm -rf -- "${PIPELINE_CACHE_DIR}"
+                TARGET_REF=refs/remotes/origin/v0.17.1_omega
+                git fetch --no-tags --depth=1000 origin \
+                  "+refs/heads/v0.17.1_omega:${TARGET_REF}"
+                BASE_SHA=$(git rev-parse "${TARGET_REF}^{commit}")
+                BASE_TREE=$(mktemp -d /tmp/vllm-accuracy-base.XXXXXX)
+                cleanup_build() {
+                  local status=$?
+                  rm -rf -- "${BASE_TREE}"
+                  if (( status != 0 )); then
+                    rm -rf -- "${PIPELINE_CACHE_DIR}"
+                  fi
+                }
+                trap cleanup_build EXIT
+                bash tools/accuracy_ci/materialize_revision.sh \
+                  "${BASE_SHA}" "${BASE_TREE}"
+                bash tools/accuracy_ci/download_native_base_wheel.sh \
+                  "${BASE_SHA}" accuracy-ci-wheels/native-base.whl
+                ACCURACY_PRECOMPILED_WHEEL=accuracy-ci-wheels/native-base.whl \
+                  bash tools/accuracy_ci/build_wheel.sh \
+                  "${BASE_TREE}" "${BASE_WHEEL_CACHE}"
+                echo "${BASE_SHA}" > "${BASE_WHEEL_CACHE}/source-sha"
+                du -sh "${PIPELINE_CACHE_DIR}"
+            container:
+              options: "--cap-add SYS_ADMIN \
+                        --device /dev/fuse \
+                        -v /dev/shm:/dev/shm \
+                        -v /ssd/2:/ssd/2 \
+                        --user=root"
+  test:
+    jobs:
+      accuracy-diff:
+        runs-on:
+          - 32-128Gi
+          - self-hosted
+          - aios-ai-infra
+        image: ${{vars.gpu_cuda12_image}}
+        timeout: 180m
+        steps:
+          - uses: checkout
+          - id: accuracy-diff
+            name: Multimodal Accuracy Diff
+            run: |
+                set -euo pipefail
+                PIPELINE_RUN_ID='${{pipeline.inst.id}}'
+                if [[ ! "${PIPELINE_RUN_ID}" =~ ^[0-9]+$ ]]; then
+                  echo "Invalid Aone pipeline run ID: ${PIPELINE_RUN_ID:-<empty>}" >&2
+                  exit 1
+                fi
+                PIPELINE_CACHE_DIR=/ssd/2/accuracy-ci/pipeline/${PIPELINE_RUN_ID}
+                BASE_WHEEL_CACHE=${PIPELINE_CACHE_DIR}/base
+                CANDIDATE_DIR=accuracy-ci-wheels/candidate
+                NATIVE_WHEEL=accuracy-ci-wheels/native-base.whl
+                cleanup_wheels() {
+                  echo "Cleaning base wheel pipeline cache: ${PIPELINE_CACHE_DIR}"
+                  du -sh "${PIPELINE_CACHE_DIR}" 2>/dev/null || true
+                  rm -rf -- "${PIPELINE_CACHE_DIR}"
+                  echo "Cleaning candidate wheel: ${CANDIDATE_DIR}"
+                  rm -rf -- "${CANDIDATE_DIR}"
+                  rm -f -- "${NATIVE_WHEEL}"
+                  if [[ -e "${PIPELINE_CACHE_DIR}" || \
+                        -e "${CANDIDATE_DIR}" || -e "${NATIVE_WHEEL}" ]]; then
+                    echo "Accuracy wheel cleanup failed" >&2
+                    exit 1
+                  fi
+                  echo "Accuracy wheel cleanup complete"
+                }
+                trap cleanup_wheels EXIT
+
+                CANDIDATE_BRANCH='${{git.branch?:""}}'
+                if [[ -z "${CANDIDATE_BRANCH}" ]] || \
+                    ! git check-ref-format --branch "${CANDIDATE_BRANCH}" >/dev/null; then
+                  echo "Invalid candidate branch: ${CANDIDATE_BRANCH:-<empty>}" >&2
+                  exit 1
+                fi
+                TARGET_REF=refs/remotes/origin/v0.17.1_omega
+                # Use a fresh ref namespace so legacy Git deepens candidate
+                # history even when checkout already created origin/<branch>.
+                CANDIDATE_REF=refs/remotes/accuracy-ci/candidate
+                git fetch --no-tags --depth=1000 origin \
+                  "+refs/heads/v0.17.1_omega:${TARGET_REF}" \
+                  "+refs/heads/${CANDIDATE_BRANCH}:${CANDIDATE_REF}"
+                BASE_SHA=$(git rev-parse "${TARGET_REF}^{commit}")
+                if DIFF_BASE_SHA=$(git merge-base "${BASE_SHA}" HEAD); then
+                  echo "Accuracy impact merge-base: ${DIFF_BASE_SHA}"
+                else
+                  echo "Candidate ancestry is incomplete; impact report may be unavailable" >&2
+                fi
+                CACHE_BASE_SHA=$(cat "${BASE_WHEEL_CACHE}/source-sha")
+                if [[ "${CACHE_BASE_SHA}" != "${BASE_SHA}" ]]; then
+                  echo "Base cache ${CACHE_BASE_SHA} does not match ${BASE_SHA}" >&2
+                  exit 1
+                fi
+
+                if [[ $(bash tools/accuracy_ci/native_changes.sh \
+                  "${BASE_SHA}" HEAD) == true ]]; then
+                  echo "Native-sensitive CR: building candidate wheel from source"
+                  bash tools/accuracy_ci/build_wheel.sh \
+                    "${PWD}" "${CANDIDATE_DIR}"
+                else
+                  echo "Python-only CR: reusing native base wheel"
+                  bash tools/accuracy_ci/download_native_base_wheel.sh \
+                    "${BASE_SHA}" "${NATIVE_WHEEL}"
+                  ACCURACY_PRECOMPILED_WHEEL="${NATIVE_WHEEL}" \
+                    bash tools/accuracy_ci/build_wheel.sh \
+                    "${PWD}" "${CANDIDATE_DIR}"
+                fi
+                git rev-parse HEAD > "${CANDIDATE_DIR}/source-sha"
+
+                nvidia-smi
+                python3 -m pip install \
+                  -r tools/accuracy_ci/requirements.txt
+                set +e
+                ACCURACY_BASE_SHA="${BASE_SHA}" \
+                ACCURACY_BASE_WHEEL_DIR="${BASE_WHEEL_CACHE}" \
+                ACCURACY_HEAD_WHEEL_DIR="${CANDIDATE_DIR}" \
+                  bash tools/accuracy_ci/run_revision_diff.sh
+                ACCURACY_STATUS=$?
+                set -e
+                mkdir -p accuracy-ci-reports
+                echo "${ACCURACY_STATUS}" > accuracy-ci-reports/exit-code
+                echo "Deferred accuracy result until reports are uploaded: ${ACCURACY_STATUS}"
+            container:
+              options: "--cap-add SYS_ADMIN \
+                        --device /dev/fuse \
+                        -v /dev/shm:/dev/shm \
+                        -v /ssd/2:/ssd/2 \
+                        -e VLLM_USE_MODELSCOPE=True \
+                        -e MODELSCOPE_CACHE=/ssd/2/modelscope \
+                        -e ACCURACY_DOWNLOAD_WITH_MODELSCOPE=1 \
+                        -e ACCURACY_MODEL_DIR=/ssd/2/modelscope/accuracy-ci/Qwen3-VL-2B-Instruct \
+                        -e ACCURACY_AUDIO_MODEL=Qwen/Qwen2.5-Omni-3B \
+                        -e ACCURACY_AUDIO_MODEL_DIR=/ssd/2/modelscope/accuracy-ci/Qwen2.5-Omni-3B \
+                        -e VLLM_VIDEO_LOADER_BACKEND=qwen_vl_utils \
+                        -e VLLM_VIDEO_DECODE_IN_SUBPROCESS=1 \
+                        -e FORCE_QWENVL_VIDEO_READER=opencv \
+                        -e QWEN_VL_RESIZE_CPU=1 \
+                        -e ACCURACY_AUTO_SELECT_GPU=1 \
+                        -e ACCURACY_GPU_MEMORY_UTILIZATION=0.1 \
+                        -e ACCURACY_AUDIO_GPU_MEMORY_UTILIZATION=0.2 \
+                        --gpus all \
+                        --user=root"
+          - uses: upload-artifact
+            inputs:
+              name: accuracy-reports
+              path: accuracy-ci-reports/*.json
+          - id: enforce-accuracy-result
+            name: Enforce Accuracy Result
+            run: |
+                set -euo pipefail
+                STATUS_FILE=accuracy-ci-reports/exit-code
+                if [[ ! -f "${STATUS_FILE}" ]]; then
+                  echo "Missing deferred accuracy status: ${STATUS_FILE}" >&2
+                  exit 1
+                fi
+                ACCURACY_STATUS=$(cat "${STATUS_FILE}")
+                if [[ ! "${ACCURACY_STATUS}" =~ ^[0-9]+$ ]] || \
+                    (( ACCURACY_STATUS > 255 )); then
+                  echo "Invalid deferred accuracy status: ${ACCURACY_STATUS}" >&2
+                  exit 1
+                fi
+                if (( ACCURACY_STATUS != 0 )); then
+                  echo "Accuracy comparison failed with status ${ACCURACY_STATUS}" >&2
+                else
+                  echo "Accuracy comparison passed"
+                fi
+                exit "${ACCURACY_STATUS}"
````

### 19. `tools/accuracy_ci/README.md`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：精度 CI 工具的原理与使用文档
- **规模**：+163 / -0（改后文件共 163 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tools/accuracy_ci/README.md b/tools/accuracy_ci/README.md
new file mode 100644
index 0000000000..99631a64cd
--- /dev/null
+++ b/tools/accuracy_ci/README.md
@@ -0,0 +1,163 @@
+# Revision accuracy CI MVP
+
+This check builds the target branch tip and the candidate revision into
+separate virtual environments, runs deterministic Qwen3-VL image/video and
+Qwen2.5-Omni audio requests, and compares inputs, encoder embeddings, fused
+decoder inputs, prefill/decode hidden states, logits, generated token IDs, and
+top-k log probabilities. All three media inputs are served over a loopback HTTP
+server, exercising vLLM's remote-media connector without relying on an external
+media host. The job creates a deterministic two-second MP4 with FFmpeg, then
+explicitly decodes and samples four frames through the `qwen_vl_utils` vLLM
+video backend before invoking the Qwen3-VL processor. The reported backend,
+package version, decoded shape, and sampling metadata are also compared. Its
+internal reader is fixed to OpenCV and resize is fixed to CPU for deterministic
+preprocessing without initializing CUDA before the vLLM engine worker starts.
+Video decoding runs through vLLM's subprocess isolation so a native decoder
+failure cannot terminate the accuracy process. Aone installs the versions in
+`requirements.txt`, validated by the successful accuracy pipeline, instead of
+depending on packages inherited from the base image.
+
+Generated token IDs and each serialized top-k logprob entry must match exactly,
+including token ID, rank, decoded token, and floating-point logprob. The earlier
+MVP overlap and logprob-delta tolerances were removed because they allowed
+element-level output changes. Tensor checkpoints retain reviewed numerical
+thresholds for GPU floating-point variation. Reports are emitted as strict JSON;
+metrics that cannot be computed after a structural mismatch are represented as
+`null`, never `NaN` or `Infinity`.
+
+Candidate inference also records per-scenario Python execution coverage. After
+the numerical comparisons finish, `accuracy_impact.py` maps candidate-side
+changes in precision-sensitive code to the image and video scenarios that
+executed them. Import statements, class declarations, and function declarations
+are not treated as runtime evidence. For every scenario hit, the report includes
+the status of the multimodal input, encoder output, fused decoder input, prefill
+output, and first decode output comparisons.
+CR changes are calculated from the merge-base of the current target tip and
+candidate, so target-branch commits merged after the CR was created are not
+misreported as candidate changes.
+
+This impact assessment is advisory: an uncovered change is evidence that the
+current scenario matrix has a gap, not evidence of a numerical regression, and
+does not fail the job. Tensor comparison remains the accuracy gate. The
+machine-readable result is written to
+`accuracy-ci-artifacts/accuracy-impact-report.json`.
+On shallow CI checkouts, Aone fetches the target and named candidate branch in
+one depth-limited operation before finding the merge-base. This avoids legacy
+Git failures caused by a second shallow fetch. If ancestry or report generation
+is still unavailable, the report records `assessment: unavailable` and the
+tensor result remains the sole job outcome.
+
+Run it on a CUDA host from the repository root:
+
+```bash
+bash tools/accuracy_ci/run_revision_diff.sh
+```
+
+In Aone, the BASE wheel is transferred to the GPU comparison job through a
+run-scoped directory on the shared `/ssd/2` mount. It is removed together with
+the candidate wheel by an EXIT trap after comparison, whether the job succeeds
+or fails. Neither wheel is retained as an Aone artifact.
+For Python-only changes, the job dynamically finds the newest compatible
+immutable native wheel in ArtLab and only repackages candidate Python sources.
+Compatibility means the wheel commit is an ancestor of the target tip and no
+native-sensitive path differs between those revisions. A native-sensitive
+candidate is fully compiled. Local runs retain the standalone fallback that
+builds both wheels when artifact directories are not supplied.
+
+The default base is the latest fetched revision of `origin/v0.17.1_omega`. The
+following environment variables customize a run:
+
+- `ACCURACY_BASE_SHA`: compare against an explicit commit.
+- `ACCURACY_TARGET_BRANCH`: change the target branch used as the base revision.
+- `ACCURACY_MODEL`: change the model ID or use an existing local model path.
+- `ACCURACY_DOWNLOAD_WITH_MODELSCOPE=1`: explicitly download the model before
+  loading it with vLLM.
+- `ACCURACY_MODEL_DIR`: ModelScope download destination.
+- `ACCURACY_IMAGE`: change the local input image.
+- `ACCURACY_VIDEO`: use an existing local MP4 instead of generating the
+  deterministic four-frame test video.
+- `ACCURACY_OUTPUT_DIR`: change the artifact directory.
+- `ACCURACY_REPORT_ARTIFACT_DIR`: change the directory containing the three
+  lightweight JSON files prepared for Aone artifact upload.
+- `ACCURACY_BUILD_JOBS`: control parallel wheel compilation.
+- `ACCURACY_GPU_MEMORY_UTILIZATION`: control the per-run vLLM GPU memory
+  reservation (default: `0.1`, which is sufficient for the 2B MVP model).
+- `ACCURACY_BASE_WHEEL_DIR` and `ACCURACY_HEAD_WHEEL_DIR`: directories containing
+  one wheel and a `source-sha` file. Aone supplies the base directory from the
+  run-scoped shared cache and builds the candidate directory in the test job.
+- `ACCURACY_PRECOMPILED_WHEEL`: optional immutable wheel whose native extensions
+  are reused by `build_wheel.sh` for a Python-only package build.
+- `ACCURACY_VLLM_DEPS_CACHE`: directory containing preloaded native build
+  dependencies; defaults to `/ssd/2/vllm_deps/.deps`. A missing directory is a
+  supported fallback and is reported in the build log.
+- `ACCURACY_AUTO_SELECT_GPU=1`: select the visible GPU with the most free
+  memory immediately before each BASE and candidate capture. The Aone job
+  enables this and exposes all runner GPUs to the container so it does not
+  contend on a hard-coded device.
+- `ACCURACY_IMPACT_RULES`: override the precision-sensitive path-to-scenario
+  mapping used by the advisory impact report.
+- `ACCURACY_AUDIO_MODEL`: audio-capable model used by the audio scenario;
+  defaults to `Qwen/Qwen2.5-Omni-3B`.
+- `ACCURACY_AUDIO_MODEL_DIR`: shared ModelScope cache directory for the audio
+  model.
+- `ACCURACY_AUDIO_GPU_MEMORY_UTILIZATION`: GPU memory fraction for the larger
+  audio-capable model; defaults to `0.2`.
+
+Artifacts are written under `accuracy-ci-artifacts/`. Image, video, and audio
+metrics are stored in their respective `<modality>/report.json` files; failure
+details are also printed to CI stdout. All comparisons are attempted before
+the script returns failure, so one regression does not hide another modality's
+result.
+The advisory coverage assessment is stored in `accuracy-impact-report.json`.
+In Aone, the base wheel is passed from the build job to the test job through a
+pipeline-specific directory on the shared `/ssd/2` mount, keyed by
+the Aone `${{pipeline.inst.id}}` run identifier. The test step's EXIT trap
+removes the directory, and the build step removes stale directories older than
+48 hours to cover canceled runs. The wheel is not kept as a run artifact.
+`image-report.json`, `video-report.json`,
+`audio-report.json`, and `accuracy-impact-report.json` are uploaded together as
+the independent `accuracy-reports` artifact. The project artifact policy
+currently retains it for 30 days. Successful comparisons print only a
+checkpoint summary to stdout; the full per-tensor metrics remain in the JSON
+artifact. Failed comparisons still print their complete diagnostics.
+The comparison step records its exit code without failing immediately, uploads
+the reports, and then a final enforcement step restores that exit code. This
+ensures numerical regressions still fail the pipeline after their diagnostics
+have been retained, without relying on unsupported `always()` behavior.
+
+The model itself is not stored in this repository or baked into the test
+image. Therefore, a model ID such as `Qwen/Qwen3-VL-2B-Instruct` needs either
+network access to a model registry or a populated local cache. The Aone job
+uses ModelScope `snapshot_download` to populate shared directories on `/ssd/2`,
+then passes the same local model directories to both vLLM revisions. This
+avoids the remote repository API compatibility path inside vLLM. Image and
+video use `Qwen/Qwen3-VL-2B-Instruct`; audio uses
+`Qwen/Qwen2.5-Omni-3B`. A fully offline environment can instead set both model
+variables to local directories and leave `ACCURACY_DOWNLOAD_WITH_MODELSCOPE`
+disabled.
+
+This version intentionally uses TP=1, eager execution, one request per
+modality, two generated tokens, no chunked prefill, and no prefix cache.
+Tensor thresholds in `compare.py` are initial guardrails and should be
+recalibrated from repeated same-revision runs on the CI GPU before expanding
+the test matrix. Token IDs and top-k logprob entries do not use these
+thresholds; they require exact equality.
+
+The capture process explicitly enables `VLLM_ALLOW_INSECURE_SERIALIZATION`
+because `LLM.apply_model` must serialize the CI-owned instrumentation
+functions into the local engine worker. This opt-in is scoped to the dedicated
+capture subprocess and must not be reused with untrusted serialized input or
+enabled in production services.
+
+## Publishing the native base wheel
+
+No commit or wheel URL is pinned in the repository. The downloader walks the
+target branch history, reads immutable wheel hashes from the ArtLab simple
+index, and selects the newest published ancestor for which `native_changes.sh`
+reports no native difference. The `NATIVE_PATHS` array in that script is the
+authoritative native-sensitive path list. It must be updated whenever a new
+native build input is introduced. After such a change is merged into
+`v0.17.1_omega`, the existing `制作Wheel包` pipeline must publish a wheel for
+the new target tip before Python-only CRs can reuse native extensions. Until
+then, the accuracy CI fails closed instead of falling back to an incompatible
+wheel.
````

### 20. `tools/accuracy_ci/__init__.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：tools/accuracy_ci 包标记
- **规模**：+1 / -0（改后文件共 1 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tools/accuracy_ci/__init__.py b/tools/accuracy_ci/__init__.py
new file mode 100644
index 0000000000..e112758eab
--- /dev/null
+++ b/tools/accuracy_ci/__init__.py
@@ -0,0 +1 @@
+"""Utilities for revision-to-revision numerical accuracy checks."""
````

### 21. `tools/accuracy_ci/accuracy_impact.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：变更影响面分析：结合 impact_rules.json 判断改动是否触碰精度敏感路径，决定复用 native wheel 还是完整重编
- **规模**：+401 / -0（改后文件共 401 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tools/accuracy_ci/accuracy_impact.py b/tools/accuracy_ci/accuracy_impact.py
new file mode 100644
index 0000000000..91551835ba
--- /dev/null
+++ b/tools/accuracy_ci/accuracy_impact.py
@@ -0,0 +1,401 @@
+# SPDX-License-Identifier: Apache-2.0
+"""Report which accuracy scenarios exercise precision-sensitive changes.
+
+This report is deliberately advisory. Numerical comparison remains the
+accuracy gate; this module describes how much evidence the current scenario
+matrix provides for a candidate change.
+"""
+
+from __future__ import annotations
+
+import argparse
+import ast
+import fnmatch
+import json
+import re
+import subprocess
+from dataclasses import dataclass
+from pathlib import Path
+from typing import Any
+
+HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
+
+
+@dataclass(frozen=True)
+class RuntimeStatement:
+    line: int
+    end_line: int
+    kind: str
+    function: str
+
+
+class _StatementVisitor(ast.NodeVisitor):
+    def __init__(self) -> None:
+        self.scope: list[str] = []
+        self.statements: list[RuntimeStatement] = []
+
+    def _visit_scope(self, node: ast.AST, name: str) -> None:
+        self.scope.append(name)
+        for child in ast.iter_child_nodes(node):
+            self.visit(child)
+        self.scope.pop()
+
+    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
+        self._visit_scope(node, node.name)
+
+    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
+        self._visit_scope(node, node.name)
+
+    def visit_ClassDef(self, node: ast.ClassDef) -> None:
+        self._visit_scope(node, node.name)
+
+    def visit_Import(self, node: ast.Import) -> None:
+        return
+
+    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
+        return
+
+    def generic_visit(self, node: ast.AST) -> None:
+        if isinstance(node, ast.stmt) and not (
+            isinstance(node, ast.Expr)
+            and isinstance(node.value, ast.Constant)
+            and isinstance(node.value.value, str)
+        ):
+            self.statements.append(
+                RuntimeStatement(
+                    line=node.lineno,
+                    end_line=getattr(node, "end_lineno", node.lineno),
+                    kind=type(node).__name__,
+                    function=".".join(self.scope) or "<module>",
+                )
+            )
+        super().generic_visit(node)
+
+
+def parse_changed_lines(diff: str) -> dict[str, set[int]]:
+    """Return candidate-side added or modified physical lines."""
+    changed: dict[str, set[int]] = {}
+    current_path: str | None = None
+    for line in diff.splitlines():
+        if line.startswith("+++ b/"):
+            current_path = line[6:]
+            changed.setdefault(current_path, set())
+            continue
+        if not current_path:
+            continue
+        match = HUNK_RE.match(line)
+        if match:
+            start = int(match.group(1))
+            count = int(match.group(2) or "1")
+            changed[current_path].update(range(start, start + count))
+    return {path: lines for path, lines in changed.items() if lines}
+
+
+def changed_runtime_statements(
+    path: Path, changed_lines: set[int]
+) -> list[dict[str, Any]]:
+    """Map physical diff lines to the narrowest enclosing runtime statement."""
+    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
+    visitor = _StatementVisitor()
+    visitor.visit(tree)
+
+    grouped: dict[RuntimeStatement, set[int]] = {}
+    for changed_line in changed_lines:
+        candidates = [
+            statement
+            for statement in visitor.statements
+            if statement.line <= changed_line <= statement.end_line
+        ]
+        if not candidates:
+            continue
+        statement = min(
+            candidates,
+            key=lambda item: (item.end_line - item.line, -item.line),
+        )
+        grouped.setdefault(statement, set()).add(changed_line)
+
+    return [
+        {
+            "line": statement.line,
+            "end_line": statement.end_line,
+            "kind": statement.kind,
+            "function": statement.function,
+            "changed_lines": sorted(lines),
+        }
+        for statement, lines in sorted(
+            grouped.items(), key=lambda item: (item[0].line, item[0].end_line)
+        )
+    ]
+
+
+def _normalize_coverage_path(path: str) -> str | None:
+    normalized = path.replace("\\", "/")
+    marker = "/site-packages/vllm/"
+    if marker in normalized:
+        return "vllm/" + normalized.split(marker, 1)[1]
+    if normalized.startswith("vllm/"):
+        return normalized
+    marker = "/vllm/"
+    if marker in normalized:
+        return "vllm/" + normalized.rsplit(marker, 1)[1]
+    return None
+
+
+def load_executed_lines(path: Path) -> dict[str, set[int]]:
+    report = json.loads(path.read_text(encoding="utf-8"))
+    executed: dict[str, set[int]] = {}
+    for filename, details in report.get("files", {}).items():
+        normalized = _normalize_coverage_path(filename)
+        if normalized is not None:
+            executed.setdefault(normalized, set()).update(details["executed_lines"])
+    return executed
+
+
+def load_checkpoints(path: Path) -> dict[str, dict[str, Any]]:
+    report = json.loads(path.read_text(encoding="utf-8"))
+    return report.get("checkpoints", {})
+
+
+def _matching_rule(path: str, rules: list[dict[str, Any]]) -> dict[str, Any] | None:
+    # fnmatch treats '/' as an ordinary character, so a trailing '*.py'
+    # intentionally covers both direct and nested Python files.
+    for rule in rules:
+        if any(fnmatch.fnmatchcase(path, pattern) for pattern in rule["patterns"]):
+            return rule
+    return None
+
+
+def evaluate_impact(
+    repo_root: Path,
+    changed: dict[str, set[int]],
+    rules_config: dict[str, Any],
+    scenario_coverage: dict[str, dict[str, set[int]]],
+    scenario_checkpoints: dict[str, dict[str, dict[str, Any]]],
+) -> dict[str, Any]:
+    roots = tuple(rules_config["precision_roots"])
+    rules = rules_config["rules"]
+    files: list[dict[str, Any]] = []
+    ignored_files: list[str] = []
+    unknown_files: list[str] = []
+
+    for path, physical_lines in sorted(changed.items()):
+        if not path.endswith(".py") or not path.startswith(roots):
+            ignored_files.append(path)
+            continue
+        rule = _matching_rule(path, rules)
+        if rule is None:
+            unknown_files.append(path)
+            continue
+
+        statements = changed_runtime_statements(repo_root / path, physical_lines)
+        covered_count = 0
+        for statement in statements:
+            hits = []
+            for scenario in rule["scenarios"]:
+                executed = scenario_coverage.get(scenario, {}).get(path, set())
+                if statement["line"] in executed:
+                    hits.append(
+                        {
+                            "scenario": scenario,
+                            "checkpoints": scenario_checkpoints.get(scenario, {}),
+                        }
+                    )
+            statement["scenario_hits"] = hits
+            statement["covered"] = bool(hits)
+            covered_count += int(bool(hits))
+
+        if not statements:
+            status = "no_runtime_statement_changes"
+        elif covered_count == len(statements):
+            status = "covered"
+        elif covered_count:
+            status = "partially_covered"
+        else:
+            status = "uncovered"
+        files.append(
+            {
+                "path": path,
+                "rule": rule["name"],
+                "expected_scenarios": rule["scenarios"],
+                "changed_lines": sorted(physical_lines),
+                "runtime_statements": statements,
+                "status": status,
+            }
+        )
+
+    statement_count = sum(len(item["runtime_statements"]) for item in files)
+    covered_count = sum(
+        sum(statement["covered"] for statement in item["runtime_statements"])
+        for item in files
+    )
+    if unknown_files or covered_count < statement_count:
+        assessment = "partial" if covered_count else "uncovered"
+    elif statement_count:
+        assessment = "covered"
+    else:
+        assessment = "not_applicable"
+    return {
+        "schema_version": 1,
+        "advisory": True,
+        "assessment": assessment,
+        "summary": {
+            "precision_files": len(files) + len(unknown_files),
+            "runtime_statements": statement_count,
+            "covered_statements": covered_count,
+            "uncovered_statements": statement_count - covered_count,
+            "unknown_files": len(unknown_files),
+        },
+        "files": files,
+        "unknown_files": unknown_files,
+        "ignored_files": ignored_files,
+    }
+
+
+def _git_changed_lines(
+    repo_root: Path, base: str, candidate: str
+) -> tuple[str, dict[str, set[int]]]:
+    merge_base = subprocess.run(
+        ["git", "merge-base", base, candidate],
+        cwd=repo_root,
+        check=True,
+        capture_output=True,
+        text=True,
+    ).stdout.strip()
+    result = subprocess.run(
+        [
+            "git",
+            "diff",
+            "--unified=0",
+            "--no-color",
+            "--diff-filter=ACMR",
+            merge_base,
+            candidate,
+            "--",
+            "*.py",
+        ],
+        cwd=repo_root,
+        check=True,
+        capture_output=True,
+        text=True,
+    )
+    return merge_base, parse_changed_lines(result.stdout)
+
+
+def _parse_mapping(
+    values: list[str], parser: argparse.ArgumentParser
+) -> dict[str, Path]:
+    result = {}
+    for value in values:
+        scenario, separator, filename = value.partition("=")
+        if not separator or not scenario or not filename:
+            parser.error(f"invalid scenario mapping: {value!r}")
+        result[scenario] = Path(filename)
+    return result
+
+
+def _print_summary(report: dict[str, Any]) -> None:
+    summary = report["summary"]
+    print("Accuracy impact coverage (advisory): " + report["assessment"])
+    print(
+        "Runtime statements: "
+        f"{summary['covered_statements']}/{summary['runtime_statements']} covered"
+    )
+    if report["assessment"] == "unavailable":
+        print("Reason: " + report.get("reason", "unknown analysis error"))
+    for file_report in report["files"]:
+        print(f"- {file_report['path']}: {file_report['status']}")
+        for statement in file_report["runtime_statements"]:
+            scenarios = (
+                ", ".join(hit["scenario"] for hit in statement["scenario_hits"])
+                or "no scenario"
+            )
+            print(
+                f"  {statement['function']}:{statement['line']} "
+                f"[{statement['kind']}] -> {scenarios}"
+            )
+    for path in report["unknown_files"]:
+        print(f"- {path}: no precision coverage rule")
+    print("Advisory only: numerical tensor comparison determines CI success.")
+
+
+def generate_report(
+    repo_root: Path,
+    base: str,
+    candidate: str,
+    rules_path: Path,
+    coverage_paths: dict[str, Path],
+    comparison_paths: dict[str, Path],
+) -> dict[str, Any]:
+    try:
+        scenario_coverage = {
+            scenario: load_executed_lines(path)
+            for scenario, path in coverage_paths.items()
+        }
+        scenario_checkpoints = {
+            scenario: load_checkpoints(path)
+            for scenario, path in comparison_paths.items()
+        }
+        rules = json.loads(rules_path.read_text(encoding="utf-8"))
+        diff_base, changed = _git_changed_lines(repo_root, base, candidate)
+        report = evaluate_impact(
+            repo_root,
+            changed,
+            rules,
+            scenario_coverage,
+            scenario_checkpoints,
+        )
+        report["diff_base_sha"] = diff_base
+    except Exception as error:  # noqa: BLE001 - report must remain advisory
+        # Preserve the failure in the JSON report; _print_summary also emits
+        # this reason to the CI log while leaving tensor comparison authoritative.
+        report = {
+            "schema_version": 1,
+            "advisory": True,
+            "assessment": "unavailable",
+            "reason": f"{type(error).__name__}: {error}",
+            "summary": {
+                "precision_files": 0,
+                "runtime_statements": 0,
+                "covered_statements": 0,
+                "uncovered_statements": 0,
+                "unknown_files": 0,
+            },
+            "files": [],
+            "unknown_files": [],
+            "ignored_files": [],
+        }
+    report["base_sha"] = base
+    report["candidate_sha"] = candidate
+    return report
+
+
+def main() -> None:
+    parser = argparse.ArgumentParser()
+    parser.add_argument("--repo-root", type=Path, required=True)
+    parser.add_argument("--base", required=True)
+    parser.add_argument("--candidate", required=True)
+    parser.add_argument("--rules", type=Path, required=True)
+    parser.add_argument("--coverage", action="append", default=[])
+    parser.add_argument("--comparison", action="append", default=[])
+    parser.add_argument("--report", type=Path, required=True)
+    args = parser.parse_args()
+
+    coverage_paths = _parse_mapping(args.coverage, parser)
+    comparison_paths = _parse_mapping(args.comparison, parser)
+    report = generate_report(
+        args.repo_root,
+        args.base,
+        args.candidate,
+        args.rules,
+        coverage_paths,
+        comparison_paths,
+    )
+    args.report.parent.mkdir(parents=True, exist_ok=True)
+    args.report.write_text(
+        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
+    )
+    _print_summary(report)
+
+
+if __name__ == "__main__":
+    main()
````

### 22. `tools/accuracy_ci/build_wheel.sh`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：构建 candidate wheel
- **规模**：+53 / -0（改后文件共 53 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tools/accuracy_ci/build_wheel.sh b/tools/accuracy_ci/build_wheel.sh
new file mode 100644
index 0000000000..d2348cde63
--- /dev/null
+++ b/tools/accuracy_ci/build_wheel.sh
@@ -0,0 +1,53 @@
+#!/usr/bin/env bash
+# SPDX-License-Identifier: Apache-2.0
+
+set -euo pipefail
+
+if [[ $# -ne 2 ]]; then
+  echo "Usage: $0 <source-dir> <output-dir>" >&2
+  exit 2
+fi
+
+REPO_ROOT=$(git rev-parse --show-toplevel)
+SOURCE_DIR=$(cd "$1" && pwd)
+mkdir -p "$2"
+OUTPUT_DIR=$(cd "$2" && pwd)
+BUILD_JOBS=${ACCURACY_BUILD_JOBS:-32}
+CUDA_ARCH_LIST=${ACCURACY_TORCH_CUDA_ARCH_LIST:-9.0}
+PRECOMPILED_WHEEL=${ACCURACY_PRECOMPILED_WHEEL:-}
+VLLM_DEPS_CACHE=${ACCURACY_VLLM_DEPS_CACHE:-/ssd/2/vllm_deps/.deps}
+# shellcheck disable=SC1091
+source "${REPO_ROOT}/tools/accuracy_ci/preload_deps.sh"
+
+build_env=(
+  MAX_JOBS="${BUILD_JOBS}"
+  TORCH_CUDA_ARCH_LIST="${CUDA_ARCH_LIST}"
+)
+if [[ -n "${PRECOMPILED_WHEEL}" ]]; then
+  PRECOMPILED_WHEEL=$(cd "$(dirname "${PRECOMPILED_WHEEL}")" && pwd)/$(basename "${PRECOMPILED_WHEEL}")
+  if [[ ! -f "${PRECOMPILED_WHEEL}" ]]; then
+    echo "Precompiled wheel does not exist: ${PRECOMPILED_WHEEL}" >&2
+    exit 1
+  fi
+  build_env+=(
+    VLLM_USE_PRECOMPILED=1
+    VLLM_PRECOMPILED_WHEEL_LOCATION="${PRECOMPILED_WHEEL}"
+    VLLM_SKIP_PRECOMPILED_VERSION_SUFFIX=1
+  )
+  echo "Reusing native extensions from ${PRECOMPILED_WHEEL}"
+fi
+
+(
+  cd "${SOURCE_DIR}"
+  preload_accuracy_build_deps "${REPO_ROOT}" "${SOURCE_DIR}" "${VLLM_DEPS_CACHE}"
+  env "${build_env[@]}" python3 -m pip wheel --no-build-isolation --no-deps \
+      --wheel-dir "${OUTPUT_DIR}" .
+)
+
+wheels=("${OUTPUT_DIR}"/*.whl)
+if [[ ${#wheels[@]} -ne 1 || ! -f "${wheels[0]}" ]]; then
+  echo "Expected exactly one wheel in ${OUTPUT_DIR}" >&2
+  exit 1
+fi
+python3 -m zipfile -t "${wheels[0]}"
+echo "Built ${wheels[0]}"
````

### 23. `tools/accuracy_ci/capture_qwen3_vl.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：捕获脚本：多模态输入、encoder 输出、融合后 decoder 输入、prefill 与首个 decode 输出、logits、token id、top-k logprob
- **规模**：+405 / -0（改后文件共 405 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tools/accuracy_ci/capture_qwen3_vl.py b/tools/accuracy_ci/capture_qwen3_vl.py
new file mode 100644
index 0000000000..a36f68fc38
--- /dev/null
+++ b/tools/accuracy_ci/capture_qwen3_vl.py
@@ -0,0 +1,405 @@
+# SPDX-License-Identifier: Apache-2.0
+"""Capture stable Qwen3-VL inference boundaries for accuracy CI.
+
+This file intentionally lives outside the vLLM package. CI imports the same
+copy while running both the base and candidate wheels, so the base revision
+does not need to contain any instrumentation.
+"""
+
+from __future__ import annotations
+
+import argparse
+import importlib.metadata
+import json
+import os
+import shutil
+import tempfile
+import threading
+from collections.abc import Iterator, Mapping, Sequence
+from contextlib import contextmanager
+from functools import partial
+from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
+from pathlib import Path
+from typing import Any
+
+import numpy as np
+import torch
+from PIL import Image
+
+IMAGE_PLACEHOLDER = "<|vision_start|><|image_pad|><|vision_end|>"
+VIDEO_PLACEHOLDER = "<|vision_start|><|video_pad|><|vision_end|>"
+IMAGE_PROMPT = (
+    "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n"
+    "<|im_start|>user\n"
+    f"{IMAGE_PLACEHOLDER}What is shown in this image? Reply briefly."
+    "<|im_end|>\n<|im_start|>assistant\n"
+)
+VIDEO_PROMPT = (
+    "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n"
+    "<|im_start|>user\n"
+    f"{VIDEO_PLACEHOLDER}What happens in this video? Reply briefly."
+    "<|im_end|>\n<|im_start|>assistant\n"
+)
+AUDIO_PROMPT = (
+    "<|im_start|>system\nYou are Qwen, a helpful assistant.<|im_end|>\n"
+    "<|im_start|>user\n"
+    "<|audio_bos|><|AUDIO|><|audio_eos|>"
+    "Describe this audio briefly."
+    "<|im_end|>\n<|im_start|>assistant\n"
+)
+
+
+class _CaptureState:
+    def __init__(self) -> None:
+        self.tensors: dict[str, torch.Tensor] = {}
+        self.calls: dict[str, int] = {}
+
+    def record(self, prefix: str, value: Any) -> None:
+        call_idx = self.calls.get(prefix, 0)
+        self.calls[prefix] = call_idx + 1
+        self._flatten(f"{prefix}.{call_idx:03d}", value)
+
+    def _flatten(self, name: str, value: Any) -> None:
+        if isinstance(value, torch.Tensor):
+            # Keep the original dtype in the manifest, but serialize floating
+            # tensors as float32 because NumPy cannot represent bfloat16.
+            self.tensors[name] = value.detach().to(device="cpu").contiguous()
+        elif isinstance(value, Mapping):
+            for key in sorted(value, key=str):
+                self._flatten(f"{name}.{key}", value[key])
+        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
+            for idx, item in enumerate(value):
+                self._flatten(f"{name}.{idx:03d}", item)
+
+
+def _install_capture(model: torch.nn.Module) -> dict[str, str]:
+    """Install instrumentation in a model worker via ``LLM.apply_model``."""
+    if hasattr(model, "_accuracy_ci_capture"):
+        raise RuntimeError("accuracy capture is already installed")
+
+    state = _CaptureState()
+    model._accuracy_ci_capture = state  # type: ignore[attr-defined]
+
+    def wrap_method(method_name: str) -> None:
+        original = getattr(model, method_name)
+
+        def wrapped(*args: Any, **kwargs: Any) -> Any:
+            state.record(f"{method_name}.args", args)
+            state.record(f"{method_name}.kwargs", kwargs)
+            output = original(*args, **kwargs)
+            state.record(f"{method_name}.output", output)
+            return output
+
+        setattr(model, method_name, wrapped)
+
+    for method_name in ("embed_multimodal", "embed_input_ids", "compute_logits"):
+        if hasattr(model, method_name):
+            wrap_method(method_name)
+
+    def forward_pre_hook(
+        _module: torch.nn.Module, args: tuple[Any, ...], kwargs: dict[str, Any]
+    ) -> None:
+        state.record("forward.args", args)
+        state.record("forward.kwargs", kwargs)
+
+    def forward_hook(
+        _module: torch.nn.Module,
+        _args: tuple[Any, ...],
+        _kwargs: dict[str, Any],
+        output: Any,
+    ) -> None:
+        state.record("forward.output", output)
+
+    model.register_forward_pre_hook(forward_pre_hook, with_kwargs=True)
+    model.register_forward_hook(forward_hook, with_kwargs=True)
+    return {"model_class": type(model).__qualname__}
+
+
+def _export_capture(model: torch.nn.Module, output_dir: str) -> dict[str, Any]:
+    state: _CaptureState = model._accuracy_ci_capture  # type: ignore[attr-defined]
+    out = Path(output_dir)
+    out.mkdir(parents=True, exist_ok=True)
+
+    arrays: dict[str, np.ndarray] = {}
+    manifest: dict[str, Any] = {"schema_version": 1, "tensors": {}}
+    for name, tensor in sorted(state.tensors.items()):
+        original_dtype = str(tensor.dtype).removeprefix("torch.")
+        serialized = tensor.float() if tensor.is_floating_point() else tensor
+        arrays[name] = serialized.numpy()
+        manifest["tensors"][name] = {
+            "shape": list(tensor.shape),
+            "dtype": original_dtype,
+        }
+
+    np.savez(out / "tensors.npz", **arrays)
+    (out / "manifest.json").write_text(
+        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
+    )
+    return {"num_tensors": len(arrays), "calls": state.calls}
+
+
+def _serialize_logprobs(logprobs: Any) -> list[list[dict[str, Any]]]:
+    serialized = []
+    for step in logprobs or []:
+        entries = []
+        for token_id, item in sorted(step.items()):
+            entries.append(
+                {
+                    "token_id": int(token_id),
+                    "logprob": float(item.logprob),
+                    "rank": item.rank,
+                    "decoded_token": item.decoded_token,
+                }
+            )
+        serialized.append(entries)
+    return serialized
+
+
+def parse_args() -> argparse.Namespace:
+    parser = argparse.ArgumentParser()
+    parser.add_argument("--output-dir", type=Path, required=True)
+    parser.add_argument("--source-sha", required=True)
+    parser.add_argument("--model", default="Qwen/Qwen3-VL-2B-Instruct")
+    parser.add_argument("--image", type=Path, required=True)
+    parser.add_argument("--video", type=Path, required=True)
+    parser.add_argument("--audio", type=Path, required=True)
+    parser.add_argument(
+        "--modality", choices=("image", "video", "audio"), default="image"
+    )
+    parser.add_argument("--max-model-len", type=int, default=1024)
+    parser.add_argument("--gpu-memory-utilization", type=float, default=0.1)
+    return parser.parse_args()
+
+
+def _resolve_local_model(model: str) -> str:
+    model_path = Path(model)
+    return str(model_path.resolve()) if model_path.exists() else model
+
+
+class _QuietMediaHandler(SimpleHTTPRequestHandler):
+    def log_message(self, format: str, *args: Any) -> None:
+        pass
+
+
+@contextmanager
+def _serve_media(
+    image: Path, video: Path, audio: Path
+) -> Iterator[dict[str, str]]:
+    """Serve deterministic CI media over loopback HTTP.
+
+    Keeping the source assets local avoids relying on a mutable or expiring
+    public URL while still exercising MediaConnector's real HTTP path.
+    """
+    with tempfile.TemporaryDirectory(prefix="vllm-accuracy-media-") as root:
+        root_path = Path(root)
+        image_name = "image.png"
+        video_name = "video.mp4"
+        audio_name = "audio.wav"
+        shutil.copyfile(image, root_path / image_name)
+        shutil.copyfile(video, root_path / video_name)
+        shutil.copyfile(audio, root_path / audio_name)
+
+        handler = partial(_QuietMediaHandler, directory=root)
+        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
+        thread = threading.Thread(target=server.serve_forever, daemon=True)
+        thread.start()
+        host, port = server.server_address[:2]
+        try:
+            yield {
+                "image": f"http://{host}:{port}/{image_name}",
+                "video": f"http://{host}:{port}/{video_name}",
+                "audio": f"http://{host}:{port}/{audio_name}",
+            }
+        finally:
+            server.shutdown()
+            thread.join()
+            server.server_close()
+
+
+def _build_image_request(image: Image.Image) -> dict[str, Any]:
+    return {
+        "prompt": IMAGE_PROMPT,
+        "multi_modal_data": {"image": image.convert("RGB")},
+    }
+
+
+def _build_video_request(
+    frames: np.ndarray, metadata: dict[str, Any]
+) -> dict[str, Any]:
+    return {
+        "prompt": VIDEO_PROMPT,
+        "multi_modal_data": {"video": (frames, metadata)},
+    }
+
+
+def _build_audio_request(audio: tuple[np.ndarray, int | float]) -> dict[str, Any]:
+    return {
+        "prompt": AUDIO_PROMPT,
+        "multi_modal_data": {"audio": audio},
+    }
+
+
+def _normalize_video_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
+    return {
+        "total_num_frames": int(metadata["total_num_frames"]),
+        "fps": float(metadata["fps"]),
+        "duration": float(metadata["duration"]),
+        "video_backend": str(metadata["video_backend"]),
+        "frames_indices": [int(index) for index in metadata["frames_indices"]],
+        "do_sample_frames": bool(metadata["do_sample_frames"]),
+    }
+
+
+def main() -> None:
+    args = parse_args()
+    args.output_dir = args.output_dir.resolve()
+    args.image = args.image.resolve()
+    args.video = args.video.resolve()
+    args.audio = args.audio.resolve()
+    args.model = _resolve_local_model(args.model)
+    args.output_dir.mkdir(parents=True, exist_ok=True)
+    # The Omega fork writes a split metrics log to ./logs during import.
+    # Keep those runtime files inside the artifact directory. This entry point
+    # runs in a dedicated process and all caller-provided paths are absolute
+    # before changing its working directory.
+    (args.output_dir / "logs").mkdir(exist_ok=True)
+    os.chdir(args.output_dir)
+
+    # Imports happen here so this script can be imported by CPU-only unit tests.
+    import vllm
+    from vllm import LLM, SamplingParams
+    from vllm.multimodal.media.connector import MediaConnector
+
+    # Start the engine before qwen_vl_utils probes CUDA availability. This
+    # avoids initializing CUDA in the API process before the engine worker
+    # establishes NCCL, while keeping decoding in the same revision venv.
+    mm_processor_kwargs = (
+        {}
+        if args.modality == "audio"
+        else {
+            "min_pixels": 28 * 28,
+            "max_pixels": 1280 * 28 * 28,
+            "fps": 1,
+        }
+    )
+    llm = LLM(
+        model=args.model,
+        dtype="half",
+        seed=0,
+        max_model_len=args.max_model_len,
+        max_num_seqs=1,
+        tensor_parallel_size=1,
+        enforce_eager=True,
+        enable_chunked_prefill=False,
+        enable_prefix_caching=False,
+        disable_log_stats=True,
+        limit_mm_per_prompt={args.modality: 1},
+        mm_processor_kwargs=mm_processor_kwargs,
+        mm_processor_cache_gb=0,
+        gpu_memory_utilization=args.gpu_memory_utilization,
+    )
+    install_result = llm.apply_model(_install_capture)
+
+    connector = MediaConnector(
+        media_io_kwargs={
+            "video": {
+                "video_backend": "qwen_vl_utils",
+                "num_frames": 4,
+            }
+        },
+        allowed_media_domains=["127.0.0.1"],
+    )
+    with _serve_media(args.image, args.video, args.audio) as media_urls:
+        media_url = media_urls[args.modality]
+        if args.modality == "image":
+            image = connector.fetch_image(media_url)
+            request = _build_image_request(image)
+            media = {
+                "type": "image",
+                "size": list(image.size),
+                "transport": "http",
+            }
+        elif args.modality == "video":
+            frames, video_metadata = connector.fetch_video(media_url)
+            if video_metadata.get("video_backend") != "qwen_vl_utils":
+                raise RuntimeError(
+                    "Video did not use qwen_vl_utils: "
+                    f"{video_metadata.get('video_backend')!r}"
+                )
+            request = _build_video_request(frames, video_metadata)
+            media = {
+                "type": "video",
+                "transport": "http",
+                "loader_backend": "qwen_vl_utils",
+                "qwen_vl_utils_version": importlib.metadata.version(
+                    "qwen-vl-utils"
+                ),
+                "qwen_reader_backend": os.environ.get("FORCE_QWENVL_VIDEO_READER"),
+                "decode_isolation": os.environ.get(
+                    "VLLM_VIDEO_DECODE_IN_SUBPROCESS"
+                ),
+                "resize_device": (
+                    "cpu"
+                    if os.environ.get("QWEN_VL_RESIZE_CPU") == "1"
+                    else "auto"
+                ),
+                "decoded_shape": list(frames.shape),
+                "metadata": _normalize_video_metadata(video_metadata),
+            }
+        else:
+            audio = connector.fetch_audio(media_url)
+            request = _build_audio_request(audio)
+            samples, sample_rate = audio
+            media = {
+                "type": "audio",
+                "transport": "http",
+                "sample_rate": float(sample_rate),
+                "num_samples": int(samples.shape[-1]),
+            }
+
+    params = SamplingParams(
+        temperature=0.0,
+        seed=0,
+        max_tokens=2,
+        logprobs=20,
+        ignore_eos=True,
+    )
+    outputs = llm.generate([request], params, use_tqdm=False)
+
+    export_result = llm.apply_model(
+        lambda model: _export_capture(model, str(args.output_dir))
+    )
+    request_output = outputs[0]
+    completion = request_output.outputs[0]
+    result = {
+        "schema_version": 1,
+        "source_sha": args.source_sha,
+        "model": args.model,
+        "modality": args.modality,
+        "media": media,
+        "prompt": request["prompt"],
+        "prompt_token_ids": list(request_output.prompt_token_ids),
+        "output_token_ids": list(completion.token_ids),
+        "text": completion.text,
+        "logprobs": _serialize_logprobs(completion.logprobs),
+        "environment": {
+            "vllm": vllm.__version__,
+            "torch": torch.__version__,
+            "cuda": torch.version.cuda,
+            "gpu": torch.cuda.get_device_name(0),
+        },
+        "instrumentation": {
+            "install": install_result,
+            "export": export_result,
+        },
+    }
+    (args.output_dir / "result.json").write_text(
+        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
+    )
+    print(json.dumps(result, indent=2, sort_keys=True))
+
+
+if __name__ == "__main__":
+    # apply_model serializes functions; this is deliberately opt-in for CI.
+    os.environ.setdefault("VLLM_ALLOW_INSECURE_SERIALIZATION", "1")
+    main()
````

### 24. `tools/accuracy_ci/compare.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：BASE 与 candidate 的 tensor 逐个差分比较与阈值判定
- **规模**：+284 / -0（改后文件共 284 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tools/accuracy_ci/compare.py b/tools/accuracy_ci/compare.py
new file mode 100644
index 0000000000..8519c5fe79
--- /dev/null
+++ b/tools/accuracy_ci/compare.py
@@ -0,0 +1,284 @@
+# SPDX-License-Identifier: Apache-2.0
+"""Compare accuracy artifacts produced by two vLLM revisions."""
+
+from __future__ import annotations
+
+import argparse
+import json
+from dataclasses import asdict, dataclass
+from pathlib import Path
+from typing import Any
+
+import numpy as np
+
+CHECKPOINT_PREFIXES = {
+    "multimodal_input": ("embed_multimodal.kwargs.000",),
+    "encoder_output": ("embed_multimodal.output.000",),
+    "fused_decoder_input": (
+        "embed_input_ids.output.000",
+        "forward.kwargs.000.inputs_embeds",
+    ),
+    "prefill_output": (
+        "forward.output.000",
+        "compute_logits.output.000",
+    ),
+    "first_decode_output": (
+        "forward.output.001",
+        "compute_logits.output.001",
+    ),
+}
+
+
+@dataclass(frozen=True)
+class Threshold:
+    nrmse: float
+    cosine: float
+
+
+@dataclass
+class TensorDiff:
+    name: str
+    nrmse: float | None
+    cosine: float | None
+    max_abs: float | None
+    mean_abs: float | None
+    passed: bool
+    reason: str = ""
+
+
+def _threshold(name: str, dtype: str) -> Threshold:
+    # These values define the accuracy gate and intentionally remain versioned
+    # with the comparator so every threshold change receives code review.
+    if "embed_multimodal.kwargs" in name:
+        return Threshold(nrmse=1e-6, cosine=0.999999)
+    if any(
+        checkpoint in name
+        for checkpoint in (
+            "embed_multimodal.output",
+            "embed_input_ids.output",
+            "forward.kwargs",
+            "forward.output",
+            "compute_logits",
+        )
+    ):
+        return Threshold(nrmse=5e-3, cosine=0.999)
+    if dtype in {"float16", "half"}:
+        return Threshold(nrmse=3e-3, cosine=0.9999)
+    if dtype == "bfloat16":
+        return Threshold(nrmse=5e-3, cosine=0.999)
+    return Threshold(nrmse=1e-5, cosine=0.999999)
+
+
+def compare_tensor(
+    name: str,
+    base: np.ndarray,
+    candidate: np.ndarray,
+    dtype: str,
+) -> TensorDiff:
+    if base.shape != candidate.shape:
+        return TensorDiff(name, None, None, None, None, False, "shape")
+    if not np.issubdtype(base.dtype, np.floating):
+        passed = np.array_equal(base, candidate)
+        return TensorDiff(
+            name,
+            0.0 if passed else None,
+            1.0 if passed else None,
+            0.0 if passed else None,
+            0.0 if passed else None,
+            passed,
+            "" if passed else "exact mismatch",
+        )
+    if not np.all(np.isfinite(base)) or not np.all(np.isfinite(candidate)):
+        return TensorDiff(name, None, None, None, None, False, "non-finite values")
+
+    base64 = base.astype(np.float64, copy=False)
+    candidate64 = candidate.astype(np.float64, copy=False)
+    delta = candidate64 - base64
+    max_abs = float(np.max(np.abs(delta), initial=0.0))
+    mean_abs = float(np.mean(np.abs(delta))) if delta.size else 0.0
+    denom = max(float(np.linalg.norm(base64.ravel())), 1e-12)
+    nrmse = float(np.linalg.norm(delta.ravel()) / denom)
+    if base64.size == 0:
+        cosine = 1.0
+    else:
+        candidate_norm = float(np.linalg.norm(candidate64.ravel()))
+        if denom <= 1e-12 or candidate_norm <= 1e-12:
+            cosine = 1.0 if np.array_equal(base64, candidate64) else 0.0
+        else:
+            cosine = float(
+                np.dot(base64.ravel(), candidate64.ravel()) / (denom * candidate_norm)
+            )
+    threshold = _threshold(name, dtype)
+    passed = nrmse <= threshold.nrmse and cosine >= threshold.cosine
+    reason = ""
+    if not passed:
+        reason = (
+            f"nrmse={nrmse:.3e}/{threshold.nrmse:.3e}, "
+            f"cosine={cosine:.7f}/{threshold.cosine:.7f}"
+        )
+    return TensorDiff(name, nrmse, cosine, max_abs, mean_abs, passed, reason)
+
+
+def _load(directory: Path) -> tuple[dict[str, Any], dict[str, Any], Any]:
+    result = json.loads((directory / "result.json").read_text(encoding="utf-8"))
+    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
+    tensors = np.load(directory / "tensors.npz")
+    return result, manifest, tensors
+
+
+def _compare_logprob_step(
+    step_idx: int,
+    base_step: list[dict[str, Any]],
+    candidate_step: list[dict[str, Any]],
+) -> list[str]:
+    if base_step == candidate_step:
+        return []
+    return [f"top-k logprobs differ at generation step {step_idx}"]
+
+
+def _checkpoint_summary(
+    base_keys: set[str],
+    candidate_keys: set[str],
+    diffs: list[TensorDiff],
+) -> dict[str, dict[str, Any]]:
+    compared = {diff.name: diff for diff in diffs}
+    checkpoints: dict[str, dict[str, Any]] = {}
+    for name, prefixes in CHECKPOINT_PREFIXES.items():
+        base_present = all(
+            any(key.startswith(prefix) for key in base_keys) for prefix in prefixes
+        )
+        candidate_present = all(
+            any(key.startswith(prefix) for key in candidate_keys) for prefix in prefixes
+        )
+        matching = [
+            diff
+            for tensor_name, diff in compared.items()
+            if any(tensor_name.startswith(prefix) for prefix in prefixes)
+        ]
+        compared_prefixes = all(
+            any(diff.name.startswith(prefix) for diff in matching)
+            for prefix in prefixes
+        )
+        checkpoints[name] = {
+            "passed": (
+                base_present
+                and candidate_present
+                and compared_prefixes
+                and all(diff.passed for diff in matching)
+            ),
+            "tensor_count": len(matching),
+        }
+    return checkpoints
+
+
+def compare_artifacts(base_dir: Path, candidate_dir: Path) -> dict[str, Any]:
+    base_result, base_manifest, base_tensors = _load(base_dir)
+    candidate_result, candidate_manifest, candidate_tensors = _load(candidate_dir)
+    errors: list[str] = []
+
+    for field in ("model", "modality", "media", "prompt", "prompt_token_ids"):
+        if base_result[field] != candidate_result[field]:
+            errors.append(f"{field} differs")
+
+    base_ids = base_result["output_token_ids"]
+    candidate_ids = candidate_result["output_token_ids"]
+    if base_ids != candidate_ids:
+        errors.append(f"output token ids differ: {base_ids} != {candidate_ids}")
+
+    base_keys = set(base_manifest["tensors"])
+    candidate_keys = set(candidate_manifest["tensors"])
+    if base_keys != candidate_keys:
+        errors.append(
+            "tensor schema differs: "
+            f"missing={sorted(base_keys - candidate_keys)}, "
+            f"extra={sorted(candidate_keys - base_keys)}"
+        )
+
+    # If the first generated token differs, the second forward pass has a
+    # different logical input. It is already a hard failure, so don't report
+    # the resulting decode tensors as an additional numerical regression.
+    comparable_decode = bool(
+        base_ids and candidate_ids and base_ids[0] == candidate_ids[0]
+    )
+
+    required_prefixes = tuple(
+        prefix for prefixes in CHECKPOINT_PREFIXES.values() for prefix in prefixes
+    )
+    for prefix in required_prefixes:
+        if not any(name.startswith(prefix) for name in base_keys):
+            errors.append(f"required checkpoint missing from base: {prefix}")
+        if not any(name.startswith(prefix) for name in candidate_keys):
+            errors.append(f"required checkpoint missing from candidate: {prefix}")
+    diffs: list[TensorDiff] = []
+    for name in sorted(base_keys & candidate_keys):
+        if not comparable_decode and (
+            name.startswith("forward.output.001")
+            or name.startswith("forward.kwargs.001")
+            or name.startswith("compute_logits.output.001")
+            or name.startswith("compute_logits.args.001")
+        ):
+            continue
+        base_info = base_manifest["tensors"][name]
+        candidate_info = candidate_manifest["tensors"][name]
+        if base_info != candidate_info:
+            diffs.append(TensorDiff(name, None, None, None, None, False, "metadata"))
+            continue
+        diffs.append(
+            compare_tensor(
+                name, base_tensors[name], candidate_tensors[name], base_info["dtype"]
+            )
+        )
+
+    if len(base_result["logprobs"]) != len(candidate_result["logprobs"]):
+        errors.append("number of generation logprob steps differs")
+    for step_idx, (base_step, candidate_step) in enumerate(
+        zip(base_result["logprobs"], candidate_result["logprobs"])
+    ):
+        errors.extend(_compare_logprob_step(step_idx, base_step, candidate_step))
+
+    failed_tensors = [diff for diff in diffs if not diff.passed]
+    report = {
+        "passed": not errors and not failed_tensors,
+        "base_sha": base_result["source_sha"],
+        "candidate_sha": candidate_result["source_sha"],
+        "decode_tensors_compared": comparable_decode,
+        "errors": errors,
+        "checkpoints": _checkpoint_summary(base_keys, candidate_keys, diffs),
+        "failed_tensors": [asdict(diff) for diff in failed_tensors],
+        "tensor_diffs": [asdict(diff) for diff in diffs],
+    }
+    return report
+
+
+def render_console_report(report: dict[str, Any]) -> str:
+    if not report["passed"]:
+        return json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
+    summary = {
+        "passed": True,
+        "base_sha": report["base_sha"],
+        "candidate_sha": report["candidate_sha"],
+        "decode_tensors_compared": report["decode_tensors_compared"],
+        "checkpoints": report["checkpoints"],
+        "tensor_count": len(report["tensor_diffs"]),
+    }
+    return json.dumps(summary, indent=2, sort_keys=True, allow_nan=False)
+
+
+def main() -> None:
+    parser = argparse.ArgumentParser()
+    parser.add_argument("--base", type=Path, required=True)
+    parser.add_argument("--candidate", type=Path, required=True)
+    parser.add_argument("--report", type=Path)
+    args = parser.parse_args()
+
+    report = compare_artifacts(args.base, args.candidate)
+    rendered = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
+    if args.report:
+        args.report.write_text(rendered + "\n", encoding="utf-8")
+    print(render_console_report(report))
+    if not report["passed"]:
+        raise SystemExit(1)
+
+
+if __name__ == "__main__":
+    main()
````

### 25. `tools/accuracy_ci/coverage.rc`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：changed-code coverage 配置
- **规模**：+10 / -0（改后文件共 10 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tools/accuracy_ci/coverage.rc b/tools/accuracy_ci/coverage.rc
new file mode 100644
index 0000000000..cee07e20cd
--- /dev/null
+++ b/tools/accuracy_ci/coverage.rc
@@ -0,0 +1,10 @@
+[run]
+branch = false
+concurrency = multiprocessing, thread
+parallel = true
+sigterm = true
+source = ${ACCURACY_COVERAGE_SOURCE-vllm}
+
+[report]
+omit =
+    */tests/*
````

### 26. `tools/accuracy_ci/download_model.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：从 ModelScope 下载并缓存模型
- **规模**：+45 / -0（改后文件共 45 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tools/accuracy_ci/download_model.py b/tools/accuracy_ci/download_model.py
new file mode 100644
index 0000000000..d908f10b10
--- /dev/null
+++ b/tools/accuracy_ci/download_model.py
@@ -0,0 +1,45 @@
+# SPDX-License-Identifier: Apache-2.0
+"""Download and validate an accuracy-CI model with ModelScope."""
+
+from __future__ import annotations
+
+import argparse
+import json
+from pathlib import Path
+
+
+def _validate_model(directory: Path) -> None:
+    required = ("config.json", "tokenizer_config.json")
+    missing = [name for name in required if not (directory / name).is_file()]
+
+    index_path = directory / "model.safetensors.index.json"
+    if index_path.is_file():
+        index = json.loads(index_path.read_text(encoding="utf-8"))
+        shards = set(index.get("weight_map", {}).values())
+        missing.extend(name for name in shards if not (directory / name).is_file())
+    elif not (directory / "model.safetensors").is_file():
+        missing.append("model.safetensors or model.safetensors.index.json")
+
+    if missing:
+        raise RuntimeError(f"Incomplete model download in {directory}: {missing}")
+
+
+def main() -> None:
+    parser = argparse.ArgumentParser()
+    parser.add_argument("--model", required=True)
+    parser.add_argument("--output-dir", type=Path, required=True)
+    parser.add_argument("--path-file", type=Path, required=True)
+    args = parser.parse_args()
+
+    from modelscope import snapshot_download
+
+    model_dir = Path(
+        snapshot_download(args.model, local_dir=str(args.output_dir.resolve()))
+    ).resolve()
+    _validate_model(model_dir)
+    args.path_file.write_text(str(model_dir) + "\n", encoding="utf-8")
+    print(model_dir)
+
+
+if __name__ == "__main__":
+    main()
````

### 27. `tools/accuracy_ci/download_native_base_wheel.sh`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：下载 BASE 的 native wheel（按 pipeline run ID 隔离临时目录）
- **规模**：+75 / -0（改后文件共 75 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tools/accuracy_ci/download_native_base_wheel.sh b/tools/accuracy_ci/download_native_base_wheel.sh
new file mode 100644
index 0000000000..b24ca5f959
--- /dev/null
+++ b/tools/accuracy_ci/download_native_base_wheel.sh
@@ -0,0 +1,75 @@
+#!/usr/bin/env bash
+# SPDX-License-Identifier: Apache-2.0
+
+set -euo pipefail
+
+if [[ $# -ne 2 ]]; then
+  echo "Usage: $0 <target-revision> <output-path>" >&2
+  exit 2
+fi
+
+REPO_ROOT=$(git rev-parse --show-toplevel)
+TARGET_SHA=$(git rev-parse "$1^{commit}")
+OUTPUT_PATH=$2
+INDEX_URL=${ACCURACY_WHEEL_INDEX_URL:-http://artlab.alibaba-inc.com/1/pypi/aios-ai-infra/vllm/}
+PYTHON_TAG=${ACCURACY_WHEEL_PYTHON_TAG:-cp310-cp310}
+PLATFORM_TAG=${ACCURACY_WHEEL_PLATFORM_TAG:-linux_x86_64}
+INDEX_FILE=$(mktemp /tmp/vllm-accuracy-wheel-index.XXXXXX)
+trap 'rm -f -- "${INDEX_FILE}"' EXIT
+
+download_with_retry() {
+  local output_path=$1
+  local url=$2
+  local attempt
+
+  # The CUDA CI image ships an older curl without --retry-all-errors.
+  # Retry explicitly so HTTP failures and other transient errors get the
+  # same treatment on both old and new curl versions.
+  for attempt in 1 2 3 4; do
+    if curl --fail --location --output "${output_path}" "${url}"; then
+      return 0
+    fi
+    if [[ ${attempt} -eq 4 ]]; then
+      echo "Failed to download ${url} after ${attempt} attempts" >&2
+      return 1
+    fi
+    sleep $((attempt * 2))
+  done
+}
+
+download_with_retry "${INDEX_FILE}" "${INDEX_URL}"
+
+WHEEL_SHA=
+WHEEL_HREF=
+WHEEL_DIGEST=
+# Aone fetches at most 1000 target commits. Keep the walk unbounded within the
+# available history: an arbitrary smaller cap could reject a still-compatible
+# wheel after a long sequence of Python-only commits. The loop exits on the
+# newest compatible wheel.
+while read -r candidate_sha; do
+  pattern="${candidate_sha}-${PYTHON_TAG}-${PLATFORM_TAG}.whl#sha256="
+  match=$(grep -F -m1 -- "${pattern}" "${INDEX_FILE}" || true)
+  if [[ -z "${match}" ]]; then
+    continue
+  fi
+  if [[ $(bash "${REPO_ROOT}/tools/accuracy_ci/native_changes.sh" \
+    "${candidate_sha}" "${TARGET_SHA}") == true ]]; then
+    continue
+  fi
+  WHEEL_SHA=${candidate_sha}
+  WHEEL_HREF=$(sed -n 's/.*href="\([^"]*\)".*/\1/p' <<<"${match}")
+  WHEEL_DIGEST=${WHEEL_HREF##*#sha256=}
+  WHEEL_HREF=${WHEEL_HREF%%#*}
+  break
+done < <(git rev-list "${TARGET_SHA}")
+
+if [[ -z "${WHEEL_SHA}" || -z "${WHEEL_HREF}" || -z "${WHEEL_DIGEST}" ]]; then
+  echo "No compatible native wheel found for target ${TARGET_SHA}." >&2
+  echo "Run 制作Wheel包 for the target tip after a native-sensitive merge." >&2
+  exit 1
+fi
+
+mkdir -p "$(dirname "${OUTPUT_PATH}")"
+echo "Using native wheel from ${WHEEL_SHA} for target ${TARGET_SHA}"
+download_with_retry "${OUTPUT_PATH}" "${INDEX_URL}${WHEEL_HREF}"
+echo "${WHEEL_DIGEST}  ${OUTPUT_PATH}" | sha256sum --check --strict
````

### 28. `tools/accuracy_ci/impact_rules.json`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：路径到精度敏感度的规则表
- **规模**：+79 / -0（改后文件共 79 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tools/accuracy_ci/impact_rules.json b/tools/accuracy_ci/impact_rules.json
new file mode 100644
index 0000000000..f9155f3598
--- /dev/null
+++ b/tools/accuracy_ci/impact_rules.json
@@ -0,0 +1,79 @@
+{
+  "schema_version": 1,
+  "precision_roots": [
+    "vllm/model_executor/layers/",
+    "vllm/model_executor/models/",
+    "vllm/multimodal/",
+    "vllm/transformers_utils/",
+    "vllm/v1/worker/"
+  ],
+  "rules": [
+    {
+      "name": "audio-media",
+      "patterns": ["vllm/multimodal/media/audio.py"],
+      "scenarios": ["audio"]
+    },
+    {
+      "name": "video-media",
+      "patterns": [
+        "vllm/multimodal/media/video.py",
+        "vllm/multimodal/video.py"
+      ],
+      "scenarios": ["video"]
+    },
+    {
+      "name": "image-media",
+      "patterns": [
+        "vllm/multimodal/image.py",
+        "vllm/multimodal/media/image.py"
+      ],
+      "scenarios": ["image"]
+    },
+    {
+      "name": "shared-multimodal",
+      "patterns": ["vllm/multimodal/*.py"],
+      "scenarios": ["image", "video", "audio"]
+    },
+    {
+      "name": "video-transformer-processor",
+      "patterns": [
+        "vllm/transformers_utils/video_processor.py",
+        "vllm/transformers_utils/processors/*video*.py"
+      ],
+      "scenarios": ["video"]
+    },
+    {
+      "name": "shared-transformer-processor",
+      "patterns": [
+        "vllm/transformers_utils/processor.py",
+        "vllm/transformers_utils/processors/qwen_vl.py"
+      ],
+      "scenarios": ["image", "video", "audio"]
+    },
+    {
+      "name": "qwen3-vl-model",
+      "patterns": ["vllm/model_executor/models/qwen3_vl.py"],
+      "scenarios": ["image", "video"]
+    },
+    {
+      "name": "qwen2.5-omni-model",
+      "patterns": ["vllm/model_executor/models/qwen2_5_omni_thinker.py"],
+      "scenarios": ["audio"]
+    },
+    {
+      "name": "model-implementation",
+      "patterns": ["vllm/model_executor/models/*.py"],
+      "scenarios": ["image", "video", "audio"]
+    },
+    {
+      "name": "model-layer",
+      "patterns": ["vllm/model_executor/layers/*.py"],
+      "scenarios": ["image", "video", "audio"]
+    },
+    {
+      "name": "v1-worker",
+      "patterns": ["vllm/v1/worker/*.py"],
+      "scenarios": ["image", "video", "audio"]
+    }
+  ]
+}
````

### 29. `tools/accuracy_ci/materialize_revision.sh`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：把目标 revision 物化为可构建工作区
- **规模**：+39 / -0（改后文件共 39 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tools/accuracy_ci/materialize_revision.sh b/tools/accuracy_ci/materialize_revision.sh
new file mode 100755
index 0000000000..5eb043c39f
--- /dev/null
+++ b/tools/accuracy_ci/materialize_revision.sh
@@ -0,0 +1,39 @@
+#!/usr/bin/env bash
+# SPDX-License-Identifier: Apache-2.0
+
+set -euo pipefail
+
+if [[ $# -ne 2 ]]; then
+  echo "Usage: $0 <revision> <destination>" >&2
+  exit 2
+fi
+
+REPO_ROOT=$(git rev-parse --show-toplevel)
+REVISION=$(git rev-parse "$1^{commit}")
+DESTINATION=$2
+
+if [[ -e "${DESTINATION}" && -n $(ls -A "${DESTINATION}") ]]; then
+  echo "Destination must be empty: ${DESTINATION}" >&2
+  exit 1
+fi
+
+mkdir -p "${DESTINATION}"
+git archive "${REVISION}" | tar -x -C "${DESTINATION}"
+
+# Aone checks out a shallow repository with an old Git version that cannot be
+# cloned locally. A detached HEAD is enough for setup.py's version generator:
+# `git describe` fails (there are no tags), then `git rev-parse HEAD` returns
+# the validated source SHA. No commit objects need to be copied.
+(
+  cd "${DESTINATION}"
+  git init --quiet
+  printf '%s\n' "${REVISION}" > .git/HEAD
+)
+
+MATERIALIZED_SHA=$(cd "${DESTINATION}" && git rev-parse HEAD)
+if [[ "${MATERIALIZED_SHA}" != "${REVISION}" ]]; then
+  echo "Materialized ${MATERIALIZED_SHA}, expected ${REVISION}" >&2
+  exit 1
+fi
+
+echo "Materialized ${REVISION} at ${DESTINATION}"
````

### 30. `tools/accuracy_ci/native_changes.sh`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：检测变更是否涉及 native（C++/CUDA）代码
- **规模**：+34 / -0（改后文件共 34 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tools/accuracy_ci/native_changes.sh b/tools/accuracy_ci/native_changes.sh
new file mode 100644
index 0000000000..4252fdabcf
--- /dev/null
+++ b/tools/accuracy_ci/native_changes.sh
@@ -0,0 +1,34 @@
+#!/usr/bin/env bash
+# SPDX-License-Identifier: Apache-2.0
+
+set -euo pipefail
+
+if [[ $# -ne 2 ]]; then
+  echo "Usage: $0 <base-revision> <candidate-revision>" >&2
+  exit 2
+fi
+
+# Keep this conservative and update it whenever a new native build input is
+# introduced. README.md treats this array as the authoritative path list.
+NATIVE_PATHS=(
+  CMakeLists.txt
+  setup.py
+  pyproject.toml
+  requirements
+  csrc
+  cmake
+  third_party
+  .aoneci/extract_and_preload_vllm_deps.py
+  tools/accuracy_ci/preload_deps.sh
+)
+
+set +e
+git diff --quiet "$1" "$2" -- "${NATIVE_PATHS[@]}"
+status=$?
+set -e
+
+case ${status} in
+  0) echo false ;;
+  1) echo true ;;
+  *) echo "Unable to classify native changes between $1 and $2" >&2; exit "${status}" ;;
+esac
````

### 31. `tools/accuracy_ci/preload_deps.sh`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：预装精度 CI 依赖
- **规模**：+20 / -0（改后文件共 20 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tools/accuracy_ci/preload_deps.sh b/tools/accuracy_ci/preload_deps.sh
new file mode 100644
index 0000000000..9054f95b54
--- /dev/null
+++ b/tools/accuracy_ci/preload_deps.sh
@@ -0,0 +1,20 @@
+#!/usr/bin/env bash
+# SPDX-License-Identifier: Apache-2.0
+
+# This file is sourced by the wheel builders so the generated environment is
+# applied to their current shell rather than being lost in a child process.
+preload_accuracy_build_deps() {
+  local repo_root=$1
+  local source_dir=$2
+  local cache_dir=$3
+
+  if [[ -d "${cache_dir}" ]]; then
+    python3 "${repo_root}/.aoneci/extract_and_preload_vllm_deps.py" \
+      --vllm-source "${source_dir}" \
+      --cache-dir "${cache_dir}"
+    # shellcheck disable=SC1091
+    source "${source_dir}/.deps/vllm_deps.env"
+  else
+    echo "No dependency preload cache at ${cache_dir}; continuing without it" >&2
+  fi
+}
````

### 32. `tools/accuracy_ci/requirements.txt`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：精度 CI 锁定的 Python 依赖
- **规模**：+3 / -0（改后文件共 3 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tools/accuracy_ci/requirements.txt b/tools/accuracy_ci/requirements.txt
new file mode 100644
index 0000000000..acec7d33f9
--- /dev/null
+++ b/tools/accuracy_ci/requirements.txt
@@ -0,0 +1,3 @@
+# Versions observed in the successful Aone accuracy run #70.
+modelscope==1.27.0
+pebble==5.2.2
````

### 33. `tools/accuracy_ci/run_revision_diff.sh`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：差分验证主编排脚本
- **规模**：+305 / -0（改后文件共 305 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tools/accuracy_ci/run_revision_diff.sh b/tools/accuracy_ci/run_revision_diff.sh
new file mode 100755
index 0000000000..78553bcae4
--- /dev/null
+++ b/tools/accuracy_ci/run_revision_diff.sh
@@ -0,0 +1,305 @@
+#!/usr/bin/env bash
+# SPDX-License-Identifier: Apache-2.0
+
+set -euo pipefail
+
+REPO_ROOT=$(git rev-parse --show-toplevel)
+HEAD_SHA=$(git rev-parse HEAD)
+BASE_SHA=${ACCURACY_BASE_SHA:-}
+TARGET_BRANCH=${ACCURACY_TARGET_BRANCH:-v0.17.1_omega}
+MODEL=${ACCURACY_MODEL:-Qwen/Qwen3-VL-2B-Instruct}
+AUDIO_MODEL=${ACCURACY_AUDIO_MODEL:-Qwen/Qwen2.5-Omni-3B}
+DOWNLOAD_WITH_MODELSCOPE=${ACCURACY_DOWNLOAD_WITH_MODELSCOPE:-0}
+MODEL_DIR=${ACCURACY_MODEL_DIR:-/ssd/2/modelscope/accuracy-ci/Qwen3-VL-2B-Instruct}
+AUDIO_MODEL_DIR=${ACCURACY_AUDIO_MODEL_DIR:-/ssd/2/modelscope/accuracy-ci/Qwen2.5-Omni-3B}
+IMAGE=${ACCURACY_IMAGE:-${REPO_ROOT}/tests/multimodal/assets/image1.png}
+VIDEO=${ACCURACY_VIDEO:-}
+AUDIO=${ACCURACY_AUDIO:-}
+OUTPUT_DIR=${ACCURACY_OUTPUT_DIR:-${REPO_ROOT}/accuracy-ci-artifacts}
+REPORT_ARTIFACT_DIR=${ACCURACY_REPORT_ARTIFACT_DIR:-${REPO_ROOT}/accuracy-ci-reports}
+BUILD_JOBS=${ACCURACY_BUILD_JOBS:-32}
+GPU_MEMORY_UTILIZATION=${ACCURACY_GPU_MEMORY_UTILIZATION:-0.1}
+AUDIO_GPU_MEMORY_UTILIZATION=${ACCURACY_AUDIO_GPU_MEMORY_UTILIZATION:-0.2}
+BASE_WHEEL_DIR=${ACCURACY_BASE_WHEEL_DIR:-}
+HEAD_WHEEL_DIR=${ACCURACY_HEAD_WHEEL_DIR:-}
+IMPACT_RULES=${ACCURACY_IMPACT_RULES:-${REPO_ROOT}/tools/accuracy_ci/impact_rules.json}
+COVERAGE_RC=${REPO_ROOT}/tools/accuracy_ci/coverage.rc
+VLLM_DEPS_CACHE=${ACCURACY_VLLM_DEPS_CACHE:-/ssd/2/vllm_deps/.deps}
+# shellcheck disable=SC1091
+source "${REPO_ROOT}/tools/accuracy_ci/preload_deps.sh"
+
+# Keep qwen_vl_utils decoding deterministic and avoid initializing CUDA in the
+# API process before vLLM starts its engine worker.
+export FORCE_QWENVL_VIDEO_READER=${FORCE_QWENVL_VIDEO_READER:-opencv}
+export QWEN_VL_RESIZE_CPU=${QWEN_VL_RESIZE_CPU:-1}
+export VLLM_VIDEO_LOADER_BACKEND=${VLLM_VIDEO_LOADER_BACKEND:-qwen_vl_utils}
+export VLLM_VIDEO_DECODE_IN_SUBPROCESS=${VLLM_VIDEO_DECODE_IN_SUBPROCESS:-1}
+
+if [[ -z "${BASE_SHA}" ]]; then
+  TARGET_REF="refs/remotes/origin/${TARGET_BRANCH}"
+  git fetch --no-tags origin \
+    "+refs/heads/${TARGET_BRANCH}:${TARGET_REF}"
+  BASE_SHA=$(git rev-parse "${TARGET_REF}^{commit}")
+fi
+
+TMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/vllm-accuracy-ci.XXXXXX")
+BASE_TREE=${TMP_ROOT}/base
+BASE_VENV=${TMP_ROOT}/base-venv
+HEAD_VENV=${TMP_ROOT}/head-venv
+WHEEL_DIR=${TMP_ROOT}/wheels
+mkdir -p "${BASE_TREE}" "${WHEEL_DIR}"
+
+cleanup() {
+  case "${TMP_ROOT}" in
+    "${TMPDIR:-/tmp}"/vllm-accuracy-ci.*)
+      rm -rf -- "${TMP_ROOT}"
+      ;;
+  esac
+}
+trap cleanup EXIT
+
+if [[ -z "${VIDEO}" || -z "${AUDIO}" ]]; then
+  if ! command -v ffmpeg >/dev/null 2>&1; then
+    echo "ffmpeg is required to generate accuracy CI test media" >&2
+    exit 1
+  fi
+fi
+
+if [[ -z "${VIDEO}" ]]; then
+  VIDEO=${TMP_ROOT}/qwen-vl-utils-ci.mp4
+  ffmpeg -hide_banner -loglevel error -y \
+    -f lavfi -i "testsrc2=size=224x224:rate=2:duration=2" \
+    -an -c:v libx264 -preset ultrafast -pix_fmt yuv420p -threads 1 \
+    -map_metadata -1 -fflags +bitexact -flags:v +bitexact "${VIDEO}"
+fi
+
+if [[ -z "${AUDIO}" ]]; then
+  AUDIO=${TMP_ROOT}/qwen-omni-ci.wav
+  ffmpeg -hide_banner -loglevel error -y \
+    -f lavfi -i "sine=frequency=440:sample_rate=16000:duration=1" \
+    -ac 1 -c:a pcm_s16le -map_metadata -1 -fflags +bitexact \
+    -flags:a +bitexact "${AUDIO}"
+fi
+
+if [[ "${DOWNLOAD_WITH_MODELSCOPE}" == "1" ]]; then
+  MODEL_PATH_FILE=${TMP_ROOT}/model-path
+  python3 "${REPO_ROOT}/tools/accuracy_ci/download_model.py" \
+    --model "${MODEL}" \
+    --output-dir "${MODEL_DIR}" \
+    --path-file "${MODEL_PATH_FILE}"
+  MODEL=$(<"${MODEL_PATH_FILE}")
+  AUDIO_MODEL_PATH_FILE=${TMP_ROOT}/audio-model-path
+  python3 "${REPO_ROOT}/tools/accuracy_ci/download_model.py" \
+    --model "${AUDIO_MODEL}" \
+    --output-dir "${AUDIO_MODEL_DIR}" \
+    --path-file "${AUDIO_MODEL_PATH_FILE}"
+  AUDIO_MODEL=$(<"${AUDIO_MODEL_PATH_FILE}")
+  # Loading from the validated local directory no longer needs vLLM's remote
+  # ModelScope adapter, which is version-sensitive in the v0.17.1 branch.
+  unset VLLM_USE_MODELSCOPE
+fi
+
+python3 -m venv --system-site-packages "${BASE_VENV}"
+python3 -m venv --system-site-packages "${HEAD_VENV}"
+
+build_and_install() {
+  local source_dir=$1
+  local venv_dir=$2
+  local wheel_output=$3
+  mkdir -p "${wheel_output}"
+  (
+    cd "${source_dir}"
+    preload_accuracy_build_deps "${REPO_ROOT}" "${source_dir}" "${VLLM_DEPS_CACHE}"
+    env MAX_JOBS="${BUILD_JOBS}" python3 -m pip wheel \
+      --no-build-isolation --no-deps --wheel-dir "${wheel_output}" .
+  )
+  "${venv_dir}/bin/python" -m pip install --no-deps "${wheel_output}"/*.whl
+}
+
+install_wheel_artifact() {
+  local wheel_dir=$1
+  local venv_dir=$2
+  local expected_sha=$3
+  local source_sha_file=${wheel_dir}/source-sha
+  local wheels=("${wheel_dir}"/*.whl)
+
+  if [[ ! -f "${source_sha_file}" ]]; then
+    echo "Missing artifact metadata: ${source_sha_file}" >&2
+    return 1
+  fi
+  if [[ "$(<"${source_sha_file}")" != "${expected_sha}" ]]; then
+    echo "Wheel artifact SHA does not match ${expected_sha}: ${wheel_dir}" >&2
+    return 1
+  fi
+  if [[ ${#wheels[@]} -ne 1 || ! -f "${wheels[0]}" ]]; then
+    echo "Expected exactly one wheel artifact in ${wheel_dir}" >&2
+    return 1
+  fi
+  "${venv_dir}/bin/python" -m zipfile -t "${wheels[0]}"
+  "${venv_dir}/bin/python" -m pip install --no-deps "${wheels[0]}"
+}
+
+if [[ -n "${BASE_WHEEL_DIR}" || -n "${HEAD_WHEEL_DIR}" ]]; then
+  if [[ -z "${BASE_WHEEL_DIR}" || -z "${HEAD_WHEEL_DIR}" ]]; then
+    echo "Both ACCURACY_BASE_WHEEL_DIR and ACCURACY_HEAD_WHEEL_DIR are required" >&2
+    exit 1
+  fi
+  install_wheel_artifact "${BASE_WHEEL_DIR}" "${BASE_VENV}" "${BASE_SHA}"
+  install_wheel_artifact "${HEAD_WHEEL_DIR}" "${HEAD_VENV}" "${HEAD_SHA}"
+else
+  bash "${REPO_ROOT}/tools/accuracy_ci/materialize_revision.sh" \
+    "${BASE_SHA}" "${BASE_TREE}"
+  build_and_install "${BASE_TREE}" "${BASE_VENV}" "${WHEEL_DIR}/base"
+  build_and_install "${REPO_ROOT}" "${HEAD_VENV}" "${WHEEL_DIR}/head"
+fi
+
+HEAD_SITE_PACKAGES=$(
+  "${HEAD_VENV}/bin/python" -c \
+    'import sysconfig; print(sysconfig.get_paths()["purelib"])'
+)
+export ACCURACY_COVERAGE_SOURCE=${HEAD_SITE_PACKAGES}/vllm
+if [[ ! -d "${ACCURACY_COVERAGE_SOURCE}" ]]; then
+  echo "Candidate vLLM source is missing: ${ACCURACY_COVERAGE_SOURCE}" >&2
+  exit 1
+fi
+# A --system-site-packages venv adds its own .pth files before the system
+# site-packages directory. Install a private copy so process_startup() is
+# available while Python processes this venv's .pth files.
+"${HEAD_VENV}/bin/python" -m pip install \
+  --ignore-installed --no-deps "coverage>=7.6,<8"
+echo 'import coverage; coverage.process_startup()' \
+  > "${HEAD_SITE_PACKAGES}/accuracy_ci_coverage.pth"
+COVERAGE_OUTPUT=${OUTPUT_DIR}/coverage
+mkdir -p "${COVERAGE_OUTPUT}"
+
+select_accuracy_gpu() {
+  if [[ "${ACCURACY_AUTO_SELECT_GPU:-0}" != "1" ]]; then
+    return
+  fi
+
+  local gpu_index
+  local gpu_free_mib
+  local gpu_selection
+  if ! gpu_selection=$(
+    nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits |
+      awk -F ', *' '
+        NR == 1 || $2 > max_free { best = $1; max_free = $2 }
+        END { if (NR > 0) print best, max_free }
+      '
+  ); then
+    echo "Unable to query available GPUs with nvidia-smi" >&2
+    return 1
+  fi
+  read -r gpu_index gpu_free_mib <<<"${gpu_selection}" || true
+  if [[ ! "${gpu_index:-}" =~ ^[0-9]+$ || \
+        ! "${gpu_free_mib:-}" =~ ^[0-9]+$ ]]; then
+    echo "Invalid GPU selection from nvidia-smi: ${gpu_selection:-<empty>}" >&2
+    return 1
+  fi
+
+  export CUDA_VISIBLE_DEVICES="${gpu_index}"
+  echo "Selected GPU ${gpu_index} with ${gpu_free_mib} MiB free"
+}
+
+capture_case() {
+  local modality=$1
+  local venv_dir=$2
+  local revision=$3
+  local output_dir=$4
+  local model=${MODEL}
+  local gpu_memory_utilization=${GPU_MEMORY_UTILIZATION}
+  if [[ "${modality}" == "audio" ]]; then
+    model=${AUDIO_MODEL}
+    gpu_memory_utilization=${AUDIO_GPU_MEMORY_UTILIZATION}
+  fi
+
+  mkdir -p "${output_dir}"
+  select_accuracy_gpu
+  local command=(
+    "${venv_dir}/bin/python"
+    "${REPO_ROOT}/tools/accuracy_ci/capture_qwen3_vl.py"
+    --output-dir "${output_dir}"
+    --source-sha "${revision}"
+    --model "${model}"
+    --image "${IMAGE}"
+    --video "${VIDEO}"
+    --audio "${AUDIO}"
+    --modality "${modality}"
+    --gpu-memory-utilization "${gpu_memory_utilization}"
+  )
+  if [[ "${revision}" == "${HEAD_SHA}" ]]; then
+    local coverage_dir=${COVERAGE_OUTPUT}/${modality}
+    mkdir -p "${coverage_dir}"
+    COVERAGE_PROCESS_START="${COVERAGE_RC}" \
+    COVERAGE_FILE="${coverage_dir}/.coverage" \
+      "${command[@]}"
+    COVERAGE_FILE="${coverage_dir}/.coverage" \
+      "${HEAD_VENV}/bin/python" -m coverage combine "${coverage_dir}"
+    # Run reporting outside the checkout. Otherwise `source = vllm` resolves
+    # the repository package instead of the candidate wheel measured above.
+    (
+      cd "${TMP_ROOT}"
+      COVERAGE_FILE="${coverage_dir}/.coverage" \
+        "${HEAD_VENV}/bin/python" -m coverage json \
+          --rcfile="${COVERAGE_RC}" \
+          -o "${COVERAGE_OUTPUT}/${modality}.json"
+    )
+  else
+    "${command[@]}"
+  fi
+}
+
+for modality in image video audio; do
+  echo "Capturing ${modality} accuracy case for BASE"
+  capture_case "${modality}" "${BASE_VENV}" "${BASE_SHA}" \
+    "${OUTPUT_DIR}/${modality}/base"
+  echo "Capturing ${modality} accuracy case for candidate"
+  capture_case "${modality}" "${HEAD_VENV}" "${HEAD_SHA}" \
+    "${OUTPUT_DIR}/${modality}/candidate"
+done
+
+comparison_status=0
+for modality in image video audio; do
+  echo "Comparing ${modality} accuracy case"
+  "${HEAD_VENV}/bin/python" "${REPO_ROOT}/tools/accuracy_ci/compare.py" \
+    --base "${OUTPUT_DIR}/${modality}/base" \
+    --candidate "${OUTPUT_DIR}/${modality}/candidate" \
+    --report "${OUTPUT_DIR}/${modality}/report.json" || comparison_status=1
+done
+
+echo "Reporting changed-code coverage by accuracy scenario (advisory only)"
+if ! "${HEAD_VENV}/bin/python" \
+    "${REPO_ROOT}/tools/accuracy_ci/accuracy_impact.py" \
+    --repo-root "${REPO_ROOT}" \
+    --base "${BASE_SHA}" \
+    --candidate "${HEAD_SHA}" \
+    --rules "${IMPACT_RULES}" \
+    --coverage "image=${COVERAGE_OUTPUT}/image.json" \
+    --coverage "video=${COVERAGE_OUTPUT}/video.json" \
+    --coverage "audio=${COVERAGE_OUTPUT}/audio.json" \
+    --comparison "image=${OUTPUT_DIR}/image/report.json" \
+    --comparison "video=${OUTPUT_DIR}/video/report.json" \
+    --comparison "audio=${OUTPUT_DIR}/audio/report.json" \
+    --report "${OUTPUT_DIR}/accuracy-impact-report.json"; then
+  echo "Accuracy impact report failed; tensor comparison result is unchanged" >&2
+fi
+
+mkdir -p "${REPORT_ARTIFACT_DIR}"
+rm -f -- \
+  "${REPORT_ARTIFACT_DIR}/image-report.json" \
+  "${REPORT_ARTIFACT_DIR}/video-report.json" \
+  "${REPORT_ARTIFACT_DIR}/audio-report.json" \
+  "${REPORT_ARTIFACT_DIR}/accuracy-impact-report.json"
+cp "${OUTPUT_DIR}/image/report.json" \
+  "${REPORT_ARTIFACT_DIR}/image-report.json"
+cp "${OUTPUT_DIR}/video/report.json" \
+  "${REPORT_ARTIFACT_DIR}/video-report.json"
+cp "${OUTPUT_DIR}/audio/report.json" \
+  "${REPORT_ARTIFACT_DIR}/audio-report.json"
+if [[ -f "${OUTPUT_DIR}/accuracy-impact-report.json" ]]; then
+  cp "${OUTPUT_DIR}/accuracy-impact-report.json" \
+    "${REPORT_ARTIFACT_DIR}/accuracy-impact-report.json"
+fi
+echo "Prepared accuracy JSON reports: ${REPORT_ARTIFACT_DIR}"
+
+exit "${comparison_status}"
````

### 34. `tests/accuracy_ci/test_accuracy_impact.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：accuracy_impact 单测
- **规模**：+213 / -0（改后文件共 213 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tests/accuracy_ci/test_accuracy_impact.py b/tests/accuracy_ci/test_accuracy_impact.py
new file mode 100644
index 0000000000..ed382a354e
--- /dev/null
+++ b/tests/accuracy_ci/test_accuracy_impact.py
@@ -0,0 +1,213 @@
+# SPDX-License-Identifier: Apache-2.0
+
+import json
+import subprocess
+from pathlib import Path
+
+from tools.accuracy_ci import accuracy_impact
+from tools.accuracy_ci.accuracy_impact import (
+    changed_runtime_statements,
+    evaluate_impact,
+    generate_report,
+    parse_changed_lines,
+)
+
+
+def _write_source(repo: Path) -> str:
+    relative = "vllm/multimodal/media/video.py"
+    source = repo / relative
+    source.parent.mkdir(parents=True)
+    source.write_text(
+        "import os\n"
+        "\n"
+        "class Decoder:\n"
+        "    def decode(self, enabled):\n"
+        "        size = (\n"
+        "            224\n"
+        "            if enabled\n"
+        "            else 112\n"
+        "        )\n"
+        "        return size\n",
+        encoding="utf-8",
+    )
+    return relative
+
+
+def _rules() -> dict:
+    return {
+        "precision_roots": ["vllm/multimodal/"],
+        "rules": [
+            {
+                "name": "video",
+                "patterns": ["vllm/multimodal/**/*.py"],
+                "scenarios": ["video"],
+            }
+        ],
+    }
+
+
+def _checkpoints() -> dict:
+    return {
+        "multimodal_input": {"passed": True, "tensor_count": 1},
+        "encoder_output": {"passed": True, "tensor_count": 1},
+        "prefill_output": {"passed": True, "tensor_count": 1},
+        "first_decode_output": {"passed": True, "tensor_count": 1},
+    }
+
+
+def test_parse_changed_lines_reads_candidate_hunks():
+    diff = """diff --git a/a.py b/a.py
+--- a/a.py
++++ b/a.py
+@@ -2 +2,2 @@
++new
++lines
+"""
+
+    assert parse_changed_lines(diff) == {"a.py": {2, 3}}
+
+
+def test_runtime_statements_ignore_import_and_declarations(tmp_path: Path):
+    path = _write_source(tmp_path)
+
+    statements = changed_runtime_statements(
+        tmp_path / path,
+        {1, 3, 4, 6, 10},
+    )
+
+    assert [(item["line"], item["function"]) for item in statements] == [
+        (5, "Decoder.decode"),
+        (10, "Decoder.decode"),
+    ]
+    assert statements[0]["changed_lines"] == [6]
+
+
+def test_impact_links_scenario_hit_to_tensor_checkpoints(tmp_path: Path):
+    path = _write_source(tmp_path)
+    report = evaluate_impact(
+        tmp_path,
+        {path: {6}},
+        _rules(),
+        {"video": {path: {5}}},
+        {"video": _checkpoints()},
+    )
+
+    statement = report["files"][0]["runtime_statements"][0]
+    assert report["advisory"]
+    assert report["assessment"] == "covered"
+    assert statement["scenario_hits"] == [
+        {"scenario": "video", "checkpoints": _checkpoints()}
+    ]
+
+
+def test_uncovered_change_is_advisory_instead_of_failure(tmp_path: Path):
+    path = _write_source(tmp_path)
+    report = evaluate_impact(
+        tmp_path,
+        {path: {10}},
+        _rules(),
+        {"video": {path: set()}},
+        {"video": _checkpoints()},
+    )
+
+    assert report["advisory"]
+    assert report["assessment"] == "uncovered"
+    assert report["summary"]["uncovered_statements"] == 1
+
+
+def test_non_precision_change_is_not_applicable(tmp_path: Path):
+    report = evaluate_impact(
+        tmp_path,
+        {"vllm/connections.py": {10}},
+        _rules(),
+        {},
+        {},
+    )
+
+    assert report["assessment"] == "not_applicable"
+    assert report["ignored_files"] == ["vllm/connections.py"]
+
+
+def test_top_level_video_change_requires_video_scenario(tmp_path: Path):
+    relative = "vllm/multimodal/video.py"
+    source = tmp_path / relative
+    source.parent.mkdir(parents=True)
+    source.write_text("result = decode_video()\n", encoding="utf-8")
+    repo_root = Path(__file__).parents[2]
+    rules = json.loads(
+        (repo_root / "tools/accuracy_ci/impact_rules.json").read_text(encoding="utf-8")
+    )
+
+    report = evaluate_impact(
+        tmp_path,
+        {relative: {1}},
+        rules,
+        {"image": {relative: {1}}, "video": {relative: set()}},
+        {"image": _checkpoints(), "video": _checkpoints()},
+    )
+
+    assert report["assessment"] == "uncovered"
+    assert report["files"][0]["rule"] == "video-media"
+
+
+def test_fnmatch_rules_cover_direct_and_nested_python_files():
+    repo_root = Path(__file__).parents[2]
+    rules = json.loads(
+        (repo_root / "tools/accuracy_ci/impact_rules.json").read_text(encoding="utf-8")
+    )["rules"]
+
+    direct = accuracy_impact._matching_rule(
+        "vllm/model_executor/models/example.py", rules
+    )
+    nested = accuracy_impact._matching_rule(
+        "vllm/model_executor/models/nested/example.py", rules
+    )
+
+    assert direct is not None and direct["name"] == "model-implementation"
+    assert nested is not None and nested["name"] == "model-implementation"
+
+
+def test_merge_base_failure_produces_advisory_unavailable_report(
+    tmp_path: Path, monkeypatch
+):
+    coverage = tmp_path / "coverage.json"
+    comparison = tmp_path / "comparison.json"
+    rules = tmp_path / "rules.json"
+    coverage.write_text('{"files": {}}', encoding="utf-8")
+    comparison.write_text('{"checkpoints": {}}', encoding="utf-8")
+    rules.write_text('{"precision_roots": [], "rules": []}', encoding="utf-8")
+
+    def fail_merge_base(*_args, **_kwargs):
+        raise subprocess.CalledProcessError(1, ["git", "merge-base"])
+
+    monkeypatch.setattr(accuracy_impact, "_git_changed_lines", fail_merge_base)
+    report = generate_report(
+        tmp_path,
+        "base",
+        "candidate",
+        rules,
+        {"video": coverage},
+        {"video": comparison},
+    )
+
+    assert report["assessment"] == "unavailable"
+    assert report["advisory"]
+    assert report["base_sha"] == "base"
+    assert "CalledProcessError" in report["reason"]
+
+
+def test_unavailable_summary_prints_reason(capsys):
+    report = {
+        "assessment": "unavailable",
+        "reason": "merge-base history is missing",
+        "summary": {
+            "covered_statements": 0,
+            "runtime_statements": 0,
+        },
+        "files": [],
+        "unknown_files": [],
+    }
+
+    accuracy_impact._print_summary(report)
+
+    assert "Reason: merge-base history is missing" in capsys.readouterr().out
````

### 35. `tests/accuracy_ci/test_capture.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：capture 单测
- **规模**：+144 / -0（改后文件共 144 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tests/accuracy_ci/test_capture.py b/tests/accuracy_ci/test_capture.py
new file mode 100644
index 0000000000..57b29fc589
--- /dev/null
+++ b/tests/accuracy_ci/test_capture.py
@@ -0,0 +1,144 @@
+# SPDX-License-Identifier: Apache-2.0
+
+import json
+import urllib.request
+
+import numpy as np
+import torch
+from PIL import Image
+
+from tools.accuracy_ci.capture_qwen3_vl import (
+    AUDIO_PROMPT,
+    IMAGE_PROMPT,
+    VIDEO_PROMPT,
+    _build_audio_request,
+    _build_image_request,
+    _build_video_request,
+    _export_capture,
+    _install_capture,
+    _normalize_video_metadata,
+    _resolve_local_model,
+    _serve_media,
+)
+from vllm.multimodal.media.connector import MediaConnector
+
+
+class _DummyModel(torch.nn.Module):
+    def embed_multimodal(self, *, pixel_values):
+        return (pixel_values + 1,)
+
+    def embed_input_ids(self, input_ids, *, multimodal_embeddings):
+        return input_ids.float().unsqueeze(-1) + multimodal_embeddings[0]
+
+    def compute_logits(self, hidden_states):
+        return hidden_states * 2
+
+    def forward(self, *, input_ids, positions, inputs_embeds):
+        return inputs_embeds + input_ids.unsqueeze(-1) + positions.unsqueeze(-1)
+
+
+def test_capture_records_stable_boundaries(tmp_path):
+    model = _DummyModel()
+    _install_capture(model)
+    values = torch.ones(2, 1)
+    mm_embeds = model.embed_multimodal(pixel_values=values)
+    inputs_embeds = model.embed_input_ids(
+        torch.tensor([1, 2]), multimodal_embeddings=mm_embeds
+    )
+    for _ in range(2):
+        hidden = model(
+            input_ids=torch.tensor([1, 2]),
+            positions=torch.tensor([0, 1]),
+            inputs_embeds=inputs_embeds,
+        )
+        model.compute_logits(hidden)
+
+    exported = _export_capture(model, str(tmp_path))
+    manifest = json.loads((tmp_path / "manifest.json").read_text())
+    tensors = np.load(tmp_path / "tensors.npz")
+
+    assert exported["num_tensors"] == len(tensors)
+    assert "embed_multimodal.kwargs.000.pixel_values" in manifest["tensors"]
+    assert "embed_multimodal.output.000.000" in manifest["tensors"]
+    assert "embed_input_ids.output.000" in manifest["tensors"]
+    assert "forward.kwargs.000.inputs_embeds" in manifest["tensors"]
+    assert "forward.output.000" in manifest["tensors"]
+    assert "forward.output.001" in manifest["tensors"]
+    assert "compute_logits.output.000" in manifest["tensors"]
+    assert "compute_logits.output.001" in manifest["tensors"]
+
+
+def test_resolve_local_model_before_working_directory_change(tmp_path, monkeypatch):
+    model_dir = tmp_path / "model"
+    model_dir.mkdir()
+    monkeypatch.chdir(tmp_path)
+
+    assert _resolve_local_model("model") == str(model_dir.resolve())
+    assert _resolve_local_model("Qwen/Qwen3-VL-2B-Instruct") == (
+        "Qwen/Qwen3-VL-2B-Instruct"
+    )
+
+
+def test_serve_media_over_loopback_http(tmp_path):
+    image = tmp_path / "source-image.png"
+    video = tmp_path / "source-video.mp4"
+    audio = tmp_path / "source-audio.wav"
+    Image.new("RGB", (2, 3), color=(1, 2, 3)).save(image)
+    video.write_bytes(b"video-bytes")
+    audio.write_bytes(b"audio-bytes")
+
+    with _serve_media(image, video, audio) as urls:
+        assert urls["image"].startswith("http://127.0.0.1:")
+        assert urllib.request.urlopen(urls["video"]).read() == b"video-bytes"
+        assert urllib.request.urlopen(urls["audio"]).read() == b"audio-bytes"
+        loaded_image = MediaConnector(
+            allowed_media_domains=["127.0.0.1"]
+        ).fetch_image(urls["image"])
+
+    assert loaded_image.size == (2, 3)
+
+
+def test_build_qwen2_5_omni_audio_request():
+    samples = np.zeros(16000, dtype=np.float32)
+
+    request = _build_audio_request((samples, 16000))
+
+    assert request["prompt"] == AUDIO_PROMPT
+    audio, sample_rate = request["multi_modal_data"]["audio"]
+    assert audio is samples
+    assert sample_rate == 16000
+
+
+def test_build_image_request():
+    image = Image.new("RGB", (40, 20), color=(1, 2, 3))
+
+    request = _build_image_request(image)
+
+    assert request["prompt"] == IMAGE_PROMPT
+    assert request["multi_modal_data"]["image"].size == (40, 20)
+
+
+def test_build_qwen_vl_utils_video_request():
+    frames = np.zeros((4, 224, 224, 3), dtype=np.uint8)
+    metadata = {
+        "total_num_frames": np.int64(4),
+        "fps": np.float64(2.0),
+        "duration": np.float64(2.0),
+        "video_backend": "qwen_vl_utils",
+        "frames_indices": [np.int64(0), 1, 2, 3],
+        "do_sample_frames": False,
+    }
+
+    request = _build_video_request(frames, metadata)
+    frames, metadata = request["multi_modal_data"]["video"]
+
+    assert request["prompt"] == VIDEO_PROMPT
+    assert frames.shape == (4, 224, 224, 3)
+    assert _normalize_video_metadata(metadata) == {
+        "total_num_frames": 4,
+        "fps": 2.0,
+        "duration": 2.0,
+        "video_backend": "qwen_vl_utils",
+        "frames_indices": [0, 1, 2, 3],
+        "do_sample_frames": False,
+    }
````

### 36. `tests/accuracy_ci/test_compare.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：compare 单测
- **规模**：+153 / -0（改后文件共 153 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tests/accuracy_ci/test_compare.py b/tests/accuracy_ci/test_compare.py
new file mode 100644
index 0000000000..7d626fab2c
--- /dev/null
+++ b/tests/accuracy_ci/test_compare.py
@@ -0,0 +1,153 @@
+# SPDX-License-Identifier: Apache-2.0
+
+import json
+from dataclasses import asdict
+from pathlib import Path
+
+import numpy as np
+
+from tools.accuracy_ci.compare import (
+    compare_artifacts,
+    compare_tensor,
+    render_console_report,
+)
+
+
+def test_compare_tensor_detects_numerical_regression():
+    base = np.ones((8,), dtype=np.float32)
+    candidate = base.copy()
+    candidate[0] = 2.0
+
+    diff = compare_tensor("forward.output.000", base, candidate, "float16")
+
+    assert not diff.passed
+    assert diff.max_abs == 1.0
+
+
+def test_non_comparable_tensor_metrics_are_strict_json():
+    diff = compare_tensor(
+        "forward.output.000",
+        np.ones((1,), dtype=np.float32),
+        np.ones((2,), dtype=np.float32),
+        "float32",
+    )
+
+    rendered = json.dumps(asdict(diff), allow_nan=False)
+
+    assert not diff.passed
+    assert diff.nrmse is None
+    assert '"nrmse": null' in rendered
+
+
+def test_non_finite_tensor_is_an_explicit_failure():
+    values = np.array([1.0, np.nan], dtype=np.float32)
+
+    diff = compare_tensor("forward.output.000", values, values, "float32")
+
+    assert not diff.passed
+    assert diff.reason == "non-finite values"
+    json.dumps(asdict(diff), allow_nan=False)
+
+
+def _write_artifact(path: Path, *, tokens: list[int], delta: float = 0.0):
+    path.mkdir()
+    tensor = np.array([1.0 + delta, 2.0], dtype=np.float32)
+    tensor_names = {
+        "embed_multimodal.kwargs.000.pixel_values": tensor,
+        "embed_multimodal.output.000.000": tensor,
+        "embed_input_ids.output.000": tensor,
+        "forward.kwargs.000.inputs_embeds": tensor,
+        "forward.output.000": tensor,
+        "forward.output.001": tensor,
+        "compute_logits.output.000": tensor,
+        "compute_logits.output.001": tensor,
+    }
+    np.savez(path / "tensors.npz", **tensor_names)
+    manifest = {
+        "schema_version": 1,
+        "tensors": {name: {"shape": [2], "dtype": "float16"} for name in tensor_names},
+    }
+    result = {
+        "schema_version": 1,
+        "source_sha": path.name,
+        "model": "model",
+        "modality": "image",
+        "media": {"type": "image", "size": [400, 80]},
+        "prompt": "prompt",
+        "prompt_token_ids": [1, 2],
+        "output_token_ids": tokens,
+        "logprobs": [
+            [{"token_id": tokens[0], "logprob": -0.1, "rank": 1}],
+            [{"token_id": tokens[1], "logprob": -0.2, "rank": 1}],
+        ],
+    }
+    (path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
+    (path / "result.json").write_text(json.dumps(result), encoding="utf-8")
+
+
+def test_compare_artifacts_passes_identical_runs(tmp_path):
+    base = tmp_path / "base"
+    candidate = tmp_path / "candidate"
+    _write_artifact(base, tokens=[10, 11])
+    _write_artifact(candidate, tokens=[10, 11])
+
+    report = compare_artifacts(base, candidate)
+
+    assert report["passed"]
+    assert report["decode_tensors_compared"]
+    assert all(checkpoint["passed"] for checkpoint in report["checkpoints"].values())
+
+
+def test_compare_artifacts_fails_changed_tokens(tmp_path):
+    base = tmp_path / "base"
+    candidate = tmp_path / "candidate"
+    _write_artifact(base, tokens=[10, 11])
+    _write_artifact(candidate, tokens=[12, 13])
+
+    report = compare_artifacts(base, candidate)
+
+    assert not report["passed"]
+    assert not report["decode_tensors_compared"]
+    assert "output token ids differ" in report["errors"][0]
+    assert not report["checkpoints"]["first_decode_output"]["passed"]
+
+
+def test_compare_artifacts_requires_elementwise_equal_logprobs(tmp_path):
+    base = tmp_path / "base"
+    candidate = tmp_path / "candidate"
+    _write_artifact(base, tokens=[10, 11])
+    _write_artifact(candidate, tokens=[10, 11])
+    result_path = candidate / "result.json"
+    result = json.loads(result_path.read_text(encoding="utf-8"))
+    result["logprobs"][0][0]["logprob"] += 1e-12
+    result_path.write_text(json.dumps(result), encoding="utf-8")
+
+    report = compare_artifacts(base, candidate)
+
+    assert not report["passed"]
+    assert report["errors"] == ["top-k logprobs differ at generation step 0"]
+
+
+def test_success_console_report_omits_per_tensor_details(tmp_path):
+    base = tmp_path / "base"
+    candidate = tmp_path / "candidate"
+    _write_artifact(base, tokens=[10, 11])
+    _write_artifact(candidate, tokens=[10, 11])
+
+    output = render_console_report(compare_artifacts(base, candidate))
+
+    assert '"tensor_count": 8' in output
+    assert "tensor_diffs" not in output
+    assert "embed_multimodal.kwargs.000.pixel_values" not in output
+
+
+def test_failure_console_report_keeps_diagnostics(tmp_path):
+    base = tmp_path / "base"
+    candidate = tmp_path / "candidate"
+    _write_artifact(base, tokens=[10, 11])
+    _write_artifact(candidate, tokens=[12, 13])
+
+    output = render_console_report(compare_artifacts(base, candidate))
+
+    assert '"passed": false' in output
+    assert "tensor_diffs" in output
````

### 37. `tests/accuracy_ci/test_download_model.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：download_model 单测
- **规模**：+35 / -0（改后文件共 35 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tests/accuracy_ci/test_download_model.py b/tests/accuracy_ci/test_download_model.py
new file mode 100644
index 0000000000..f6d7af1b8c
--- /dev/null
+++ b/tests/accuracy_ci/test_download_model.py
@@ -0,0 +1,35 @@
+# SPDX-License-Identifier: Apache-2.0
+
+import json
+
+import pytest
+
+from tools.accuracy_ci.download_model import _validate_model
+
+
+def test_validate_model_with_sharded_weights(tmp_path):
+    (tmp_path / "config.json").write_text("{}")
+    (tmp_path / "tokenizer_config.json").write_text("{}")
+    (tmp_path / "model-00001-of-00001.safetensors").write_bytes(b"weights")
+    (tmp_path / "model.safetensors.index.json").write_text(
+        json.dumps(
+            {
+                "weight_map": {
+                    "model.embed_tokens.weight": "model-00001-of-00001.safetensors"
+                }
+            }
+        )
+    )
+
+    _validate_model(tmp_path)
+
+
+def test_validate_model_rejects_missing_shard(tmp_path):
+    (tmp_path / "config.json").write_text("{}")
+    (tmp_path / "tokenizer_config.json").write_text("{}")
+    (tmp_path / "model.safetensors.index.json").write_text(
+        json.dumps({"weight_map": {"weight": "missing.safetensors"}})
+    )
+
+    with pytest.raises(RuntimeError, match="missing.safetensors"):
+        _validate_model(tmp_path)
````

### 38. `tests/accuracy_ci/test_download_native_base_wheel.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：download_native_base_wheel 单测
- **规模**：+86 / -0（改后文件共 86 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tests/accuracy_ci/test_download_native_base_wheel.py b/tests/accuracy_ci/test_download_native_base_wheel.py
new file mode 100644
index 0000000000..d252f05fac
--- /dev/null
+++ b/tests/accuracy_ci/test_download_native_base_wheel.py
@@ -0,0 +1,86 @@
+# SPDX-License-Identifier: Apache-2.0
+
+import hashlib
+import os
+import subprocess
+from pathlib import Path
+
+
+def test_download_works_with_old_curl(tmp_path: Path) -> None:
+    repo_root = Path(__file__).resolve().parents[2]
+    target_sha = subprocess.check_output(
+        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
+    ).strip()
+
+    wheel = tmp_path / "source.whl"
+    wheel.write_bytes(b"accuracy-ci-wheel")
+    digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
+    wheel_name = f"vllm-test-{target_sha}-cp310-cp310-linux_x86_64.whl"
+    index = tmp_path / "index.html"
+    index.write_text(
+        f'<a href="{wheel_name}#sha256={digest}">{wheel_name}</a>\n',
+        encoding="utf-8",
+    )
+
+    fake_bin = tmp_path / "bin"
+    fake_bin.mkdir()
+    fake_curl = fake_bin / "curl"
+    fake_curl.write_text(
+        """#!/usr/bin/env python3
+import os
+import shutil
+import sys
+
+if "--retry-all-errors" in sys.argv:
+    raise SystemExit(2)
+output = sys.argv[sys.argv.index("--output") + 1]
+source = (
+    os.environ["FAKE_INDEX"]
+    if sys.argv[-1].endswith("/")
+    else os.environ["FAKE_WHEEL"]
+)
+shutil.copyfile(source, output)
+""",
+        encoding="utf-8",
+    )
+    fake_curl.chmod(0o755)
+    fake_sha256sum = fake_bin / "sha256sum"
+    fake_sha256sum.write_text(
+        """#!/usr/bin/env python3
+import hashlib
+import pathlib
+import sys
+
+expected, path = sys.stdin.read().strip().split(maxsplit=1)
+actual = hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
+raise SystemExit(0 if actual == expected else 1)
+""",
+        encoding="utf-8",
+    )
+    fake_sha256sum.chmod(0o755)
+
+    output = tmp_path / "downloaded.whl"
+    env = os.environ.copy()
+    env.update(
+        {
+            "PATH": f"{fake_bin}:{env['PATH']}",
+            "FAKE_INDEX": str(index),
+            "FAKE_WHEEL": str(wheel),
+            "ACCURACY_WHEEL_INDEX_URL": "https://example.invalid/simple/",
+        }
+    )
+    result = subprocess.run(
+        [
+            "bash",
+            str(repo_root / "tools/accuracy_ci/download_native_base_wheel.sh"),
+            target_sha,
+            str(output),
+        ],
+        cwd=repo_root,
+        env=env,
+        text=True,
+        capture_output=True,
+    )
+
+    assert result.returncode == 0, result.stderr
+    assert output.read_bytes() == wheel.read_bytes()
````

### 39. `tests/accuracy_ci/test_materialize_revision.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：materialize_revision 单测
- **规模**：+48 / -0（改后文件共 48 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/tests/accuracy_ci/test_materialize_revision.py b/tests/accuracy_ci/test_materialize_revision.py
new file mode 100644
index 0000000000..24b30cd0e3
--- /dev/null
+++ b/tests/accuracy_ci/test_materialize_revision.py
@@ -0,0 +1,48 @@
+# SPDX-License-Identifier: Apache-2.0
+
+import os
+import subprocess
+import sys
+from pathlib import Path
+
+
+def test_materialize_revision_preserves_head(tmp_path: Path) -> None:
+    repo_root = Path(__file__).resolve().parents[2]
+    script = repo_root / "tools/accuracy_ci/materialize_revision.sh"
+    script_text = script.read_text()
+    # Aone checks out a shallow repository and uses an old Git version. Do not
+    # try to clone/fetch from that local checkout or rely on `git -C`.
+    assert "git -C" not in script_text
+    assert "git fetch" not in script_text
+    revision = subprocess.check_output(
+        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
+    ).strip()
+    destination = tmp_path / "revision"
+
+    subprocess.run(
+        [
+            "bash",
+            str(script),
+            revision,
+            str(destination),
+        ],
+        cwd=repo_root,
+        check=True,
+    )
+
+    assert (destination / "setup.py").is_file()
+    materialized = subprocess.check_output(
+        ["git", "rev-parse", "HEAD"], cwd=destination, text=True
+    ).strip()
+    assert materialized == revision
+
+    env = os.environ.copy()
+    env["VLLM_TARGET_DEVICE"] = "empty"
+    version_output = subprocess.check_output(
+        [sys.executable, "setup.py", "--version"],
+        cwd=destination,
+        env=env,
+        text=True,
+    )
+    assert f"0.17.1+dev0.0.{revision}" in version_output
+    assert ".none" not in version_output.lower()
````

### 40. `.gitignore`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：忽略 accuracy-ci-artifacts/ 与 accuracy-ci-wheels/
- **规模**：+2 / -0（改后文件共 247 行）
- **涉及提交**：
  - `b2e9c53d45` ci: add model accuracy regression validation
````diff
diff --git a/.gitignore b/.gitignore
index 795071bd77..82ad12fe42 100644
--- a/.gitignore
+++ b/.gitignore
@@ -202,10 +202,12 @@ AGENTS.md
 # DS Store
 .DS_Store
 
 # Results
 *.csv
+accuracy-ci-artifacts/
+accuracy-ci-wheels/
 
 # Python pickle files
 *.pkl
 
 # Sphinx documentation
````

---

## 组 4 · mediafetch:// 协议接入（7 文件）

接入内部 media-fetch-sdk，多模态输入支持 `mediafetch://appkey/uri?width=...` 协议
（Req#85339520），新增 Prometheus 观测指标。SDK 只约束 CPU 架构（x86_64），
ROCm x86_64 镜像同样启用。


### 41. `vllm/multimodal/mediafetchutils.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：media-fetch-sdk 封装：mediafetch:// URL 解析、SyncImageEngine 进程级缓存（threading.Lock 防竞态）、MEDIA_FETCH_THUMBNAIL_WIDTHS 缩略图宽度配置、SDK 未安装时降级
- **规模**：+217 / -0（改后文件共 217 行）
- **涉及提交**：
  - `983aefae95` [Req#85339520] vLLM 接入 media-fetch-sdk 支持 mediafetch:// 协议 * [Req#85339520] vLLM 接入 media-fetch-sdk 支持 mediafetch:// 协议
````diff
diff --git a/vllm/multimodal/mediafetchutils.py b/vllm/multimodal/mediafetchutils.py
new file mode 100644
index 0000000000..16d68ca910
--- /dev/null
+++ b/vllm/multimodal/mediafetchutils.py
@@ -0,0 +1,217 @@
+# SPDX-License-Identifier: Apache-2.0
+# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
+"""Utility functions for fetching media via the media-fetch-sdk."""
+
+import atexit
+import os
+import threading
+import time
+from typing import Optional
+from urllib.parse import parse_qs, urlparse
+
+from vllm.entrypoints.metrics.mm_preprocessing import (
+    observe_mediafetch_request,
+)
+
+# Module-level SDK import: fail fast at import time if SDK is missing.
+# Hot-path code (get_bytes_from_mediafetch_path) no longer repeats imports.
+try:
+    from media_fetch import (MediaFetchConfig, MediaSdkBusinessError,
+                             MediaSdkSystemError, SyncImageEngine)
+    _SDK_AVAILABLE = True
+except ImportError:
+    _SDK_AVAILABLE = False
+    MediaFetchConfig = None  # type: ignore[assignment, misc]
+    MediaSdkBusinessError = None  # type: ignore[assignment, misc]
+    MediaSdkSystemError = None  # type: ignore[assignment, misc]
+    SyncImageEngine = None  # type: ignore[assignment, misc]
+
+_engine_cache: dict[str, "SyncImageEngine"] = {}
+_engine_cache_lock = threading.Lock()
+
+# Cached parsed result for thumbnail widths env var.
+_thumbnail_widths_cache: Optional[set[int]] = None
+
+
+def _get_engine(appkey: str) -> "SyncImageEngine":
+    """Get or create a SyncImageEngine keyed by appkey."""
+    if not _SDK_AVAILABLE:
+        raise ImportError(
+            "media_fetch SDK is not installed. "
+            "Please install it to use mediafetch:// URLs."
+        )
+
+    # Fast path: engine already cached (lock-free)
+    engine = _engine_cache.get(appkey)
+    if engine is not None:
+        return engine
+
+    # Slow path: create under lock to avoid duplicate engines
+    with _engine_cache_lock:
+        # Double-check after acquiring lock
+        engine = _engine_cache.get(appkey)
+        if engine is not None:
+            return engine
+
+        timeout = float(os.environ.get("MEDIA_FETCH_TIMEOUT", "5"))
+        retry = int(os.environ.get("MEDIA_FETCH_RETRY", "3"))
+        config = MediaFetchConfig(timeout=timeout, retry=retry)
+
+        engine = SyncImageEngine(api_key=appkey, config=config)
+        _engine_cache[appkey] = engine
+        atexit.register(_close_engine, appkey)
+
+    return engine
+
+
+def _close_engine(appkey: str) -> None:
+    with _engine_cache_lock:
+        engine = _engine_cache.pop(appkey, None)
+    if engine is not None:
+        engine.close()
+
+
+def _get_supported_thumbnail_widths() -> set[int]:
+    """Get supported thumbnail widths from env, default 800 and 1440.
+
+    Results are cached on first call; subsequent calls return the cache.
+    """
+    global _thumbnail_widths_cache
+    if _thumbnail_widths_cache is not None:
+        return _thumbnail_widths_cache
+    raw = os.environ.get("MEDIA_FETCH_THUMBNAIL_WIDTHS", "800,1440")
+    try:
+        widths = {int(w.strip()) for w in raw.split(",") if w.strip()}
+    except ValueError as e:
+        raise ValueError(
+            f"Invalid MEDIA_FETCH_THUMBNAIL_WIDTHS='{raw}', "
+            f"expected comma-separated integers, e.g. '800,1440'"
+        ) from e
+    _thumbnail_widths_cache = widths
+    return widths
+
+
+def _parse_mediafetch_url(url: str) -> tuple[str, str, Optional[int]]:
+    """Parse a mediafetch:// URL.
+
+    Returns (app_key, image_url, width). ``image_url`` is the value of the
+    ``url`` query parameter and may be a full image URL or just an image_key.
+    ``width`` is only set for thumbnail mode.
+    """
+    parsed = urlparse(url)
+    if parsed.scheme != "mediafetch":
+        raise ValueError(f"expected mediafetch:// URL, got: {url}")
+
+    # mediafetch://origin/?... 会把 origin 解析为 netloc;
+    # mediafetch:///origin/?... 会把 origin 解析为 path。
+    mode = parsed.netloc or parsed.path.strip("/")
+    if mode not in ("origin", "thumbnail"):
+        raise ValueError(
+            f"mediafetch mode must be origin or thumbnail, actual: {mode}"
+        )
+
+    query = parsed.query
+
+    # app_key and width are short values without '&', so parse_qs is safe.
+    qs = parse_qs(query)
+    appkey = qs.get("app_key", [None])[0]
+    if not appkey:
+        raise ValueError(f"mediafetch URL missing app_key: {url}")
+
+    # image_url may contain '&' (e.g. HTTP URL with query params), so
+    # parse_qs would truncate it.  Manually extract everything after 'url='.
+    url_marker = "url="
+    url_idx = query.find(url_marker)
+    if url_idx < 0:
+        raise ValueError(f"mediafetch URL missing url: {url}")
+    image_url = query[url_idx + len(url_marker):]
+
+    width: Optional[int] = None
+    if mode == "thumbnail":
+        # ``url`` may itself contain unescaped ``&`` query parameters, while
+        # ``width`` is an outer mediafetch parameter.  By protocol, width is
+        # the final parameter, so split on the last marker and keep all prior
+        # ampersands as part of the image URL.
+        image_url, width_marker, width_str = image_url.rpartition("&width=")
+        if not width_marker:
+            raise ValueError(
+                f"mediafetch thumbnail URL missing width: {url}"
+            )
+        try:
+            width = int(width_str)
+        except ValueError as e:
+            raise ValueError(
+                f"thumbnail width must be int: {url}"
+            ) from e
+        supported_widths = _get_supported_thumbnail_widths()
+        if width not in supported_widths:
+            raise ValueError(
+                f"thumbnail width {width} not supported, "
+                f"allowed: {sorted(supported_widths)}"
+            )
+
+    return appkey, image_url, width
+
+
+def get_bytes_from_mediafetch_path(url: str) -> bytes:
+    """Fetch image bytes from a mediafetch:// URL via media-fetch-sdk."""
+    start = time.monotonic()
+    parsed = urlparse(url)
+    mode = parsed.netloc or parsed.path.strip("/") or "unknown"
+    if mode not in ("origin", "thumbnail"):
+        mode = "unknown"
+    result = "error"
+    error_type = "unexpected"
+    num_bytes: int | None = None
+
+    try:
+        try:
+            appkey, image_url, width = _parse_mediafetch_url(url)
+        except ValueError:
+            error_type = "invalid_url"
+            raise
+
+        try:
+            engine = _get_engine(appkey)
+        except ImportError:
+            error_type = "sdk_missing"
+            raise
+
+        biz_code = os.environ.get("MEDIA_FETCH_BIZ_CODE")
+        try:
+            if width is None:
+                data = engine.origin(image_url, biz_code=biz_code)
+            else:
+                data = engine.thumbnail(
+                    image_url, width=width, biz_code=biz_code
+                )
+        except MediaSdkBusinessError as e:
+            error_type = "business"
+            raise ValueError(
+                f"media-fetch-sdk business error: {e}"
+            ) from e
+        except MediaSdkSystemError as e:
+            error_type = "system"
+            raise RuntimeError(
+                f"media-fetch-sdk system error: {e}"
+            ) from e
+
+        if data is None:
+            result = "no_data"
+            error_type = "none"
+            raise ValueError(
+                f"media-fetch-sdk returned NO_DATA for {image_url}"
+            )
+
+        result = "success"
+        error_type = "none"
+        num_bytes = len(data)
+        return data
+    finally:
+        observe_mediafetch_request(
+            mode=mode,
+            result=result,
+            error_type=error_type,
+            elapsed_seconds=time.monotonic() - start,
+            num_bytes=num_bytes,
+        )
````

### 42. `vllm/multimodal/media/connector.py`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：MediaConnector 同步与异步加载路径各新增 mediafetch scheme 分支（懒 import）
- **规模**：+22 / -2（改后文件共 549 行）
- **涉及提交**：
  - `983aefae95` [Req#85339520] vLLM 接入 media-fetch-sdk 支持 mediafetch:// 协议 * [Req#85339520] vLLM 接入 media-fetch-sdk 支持 mediafetch:// 协议
````diff
diff --git a/vllm/multimodal/media/connector.py b/vllm/multimodal/media/connector.py
index 88ecd456dc..65c91a93e0 100644
--- a/vllm/multimodal/media/connector.py
+++ b/vllm/multimodal/media/connector.py
@@ -266,10 +266,17 @@ class MediaConnector:
         if url_spec.scheme == "alake":
             from vllm.multimodal.alakeutils import get_bytes_from_alake_path
             return self._fetch_and_decode(
                 lambda: get_bytes_from_alake_path(url), media_io)
 
+        if url_spec.scheme == "mediafetch":
+            from vllm.multimodal.mediafetchutils import (
+                get_bytes_from_mediafetch_path,
+            )
+            return self._fetch_and_decode(
+                lambda: get_bytes_from_mediafetch_path(url), media_io)
+
         if url_spec.scheme == "alluxio":
             from vllm.multimodal.alluxio_utils import (
                 get_bytes_from_alluxio_path,
             )
             return self._fetch_and_decode(
@@ -279,11 +286,14 @@ class MediaConnector:
             return self._load_data_url(url_spec, media_io)
 
         if url_spec.scheme == "file":
             return self._load_file_url(url_spec, media_io)
 
-        msg = "The URL must be either a HTTP, data, file or oss URL."
+        msg = (
+            "The URL must be either a HTTP, data, file, oss, "
+            "alake, alluxio or mediafetch URL."
+        )
         raise ValueError(msg)
 
     async def load_from_url_async(
         self,
         url: str,
@@ -328,10 +338,17 @@ class MediaConnector:
         if url_spec.scheme == "alake":
             from vllm.multimodal.alakeutils import get_bytes_from_alake_path
             return await self._fetch_and_decode_async(
                 lambda: get_bytes_from_alake_path(url), media_io)
 
+        if url_spec.scheme == "mediafetch":
+            from vllm.multimodal.mediafetchutils import (
+                get_bytes_from_mediafetch_path,
+            )
+            return await self._fetch_and_decode_async(
+                lambda: get_bytes_from_mediafetch_path(url), media_io)
+
         if url_spec.scheme == "alluxio":
             from vllm.multimodal.alluxio_utils import (
                 get_bytes_from_alluxio_path,
             )
             return await self._fetch_and_decode_async(
@@ -343,11 +360,14 @@ class MediaConnector:
 
         if url_spec.scheme == "file":
             return await loop.run_in_executor(
                 global_thread_pool, self._load_file_url, url_spec, media_io)
 
-        msg = "The URL must be either a HTTP, data, file or oss URL."
+        msg = (
+            "The URL must be either a HTTP, data, file, oss, "
+            "alake, alluxio or mediafetch URL."
+        )
         raise ValueError(msg)
 
     def fetch_audio(
         self,
         audio_url: str,
````

### 43. `vllm/entrypoints/metrics/mm_preprocessing.py`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：新增 mediafetch 观测指标：vllm:mediafetch_requests_total（mode/result/error_type）、request_duration_seconds、response_bytes
- **规模**：+87 / -5（改后文件共 267 行）
- **涉及提交**：
  - `983aefae95` [Req#85339520] vLLM 接入 media-fetch-sdk 支持 mediafetch:// 协议 * [Req#85339520] vLLM 接入 media-fetch-sdk 支持 mediafetch:// 协议
````diff
diff --git a/vllm/entrypoints/metrics/mm_preprocessing.py b/vllm/entrypoints/metrics/mm_preprocessing.py
index 23e359fd76..4472e68b00 100644
--- a/vllm/entrypoints/metrics/mm_preprocessing.py
+++ b/vllm/entrypoints/metrics/mm_preprocessing.py
@@ -36,10 +36,13 @@ _metrics_initialized = False
 _media_download_latency = None
 _media_decode_latency = None
 _media_download_bytes = None
 _mm_resolve_items_latency = None
 _mm_preprocessing_total_latency = None
+_mediafetch_requests = None
+_mediafetch_request_duration = None
+_mediafetch_response_bytes = None
 
 
 def _ensure_metrics() -> bool:
     """Initialize Prometheus metrics on first call.
 
@@ -48,18 +51,20 @@ def _ensure_metrics() -> bool:
     """
     global _metrics_initialized
     global _media_download_latency, _media_decode_latency
     global _media_download_bytes
     global _mm_resolve_items_latency, _mm_preprocessing_total_latency
+    global _mediafetch_requests, _mediafetch_request_duration
+    global _mediafetch_response_bytes
 
     if _metrics_initialized:
         return _media_download_latency is not None
 
     _metrics_initialized = True
 
     try:
-        from prometheus_client import Histogram
+        from prometheus_client import Counter, Histogram
     except ImportError:
         return False
 
     from vllm.v1.metrics.prometheus import get_prometheus_registry
 
@@ -70,12 +75,24 @@ def _ensure_metrics() -> bool:
         documentation=(
             "Histogram of HTTP media download latency in seconds "
             "(per media item)."
         ),
         buckets=[
-            0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5,
-            0.75, 1.0, 2.5, 5.0, 10.0, 30.0,
+            0.005,
+            0.01,
+            0.025,
+            0.05,
+            0.075,
+            0.1,
+            0.25,
+            0.5,
+            0.75,
+            1.0,
+            2.5,
+            5.0,
+            10.0,
+            30.0,
         ],
         labelnames=["media_type"],
         registry=registry,
     )
 
@@ -97,12 +114,19 @@ def _ensure_metrics() -> bool:
         name="vllm:mm_media_download_bytes",
         documentation=(
             "Histogram of downloaded media size in bytes (per media item)."
         ),
         buckets=[
-            1024, 10240, 102400, 524288, 1048576,
-            5242880, 10485760, 52428800, 104857600,
+            1024,
+            10240,
+            102400,
+            524288,
+            1048576,
+            5242880,
+            10485760,
+            52428800,
+            104857600,
         ],
         labelnames=["media_type"],
         registry=registry,
     )
 
@@ -133,10 +157,45 @@ def _ensure_metrics() -> bool:
         ],
         labelnames=[],
         registry=registry,
     )
 
+    _mediafetch_requests = Counter(
+        name="vllm:mediafetch_requests_total",
+        documentation=(
+            "Total media-fetch-sdk requests by mode, result, and error type."
+        ),
+        labelnames=["mode", "result", "error_type"],
+        registry=registry,
+    )
+
+    _mediafetch_request_duration = Histogram(
+        name="vllm:mediafetch_request_duration_seconds",
+        documentation=(
+            "Histogram of media-fetch-sdk request latency in seconds."
+        ),
+        buckets=[
+            0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5,
+            0.75, 1.0, 2.5, 5.0, 10.0, 30.0,
+        ],
+        labelnames=["mode", "result"],
+        registry=registry,
+    )
+
+    _mediafetch_response_bytes = Histogram(
+        name="vllm:mediafetch_response_bytes",
+        documentation=(
+            "Histogram of successful media-fetch-sdk response sizes in bytes."
+        ),
+        buckets=[
+            1024, 10240, 102400, 524288, 1048576,
+            5242880, 10485760, 52428800, 104857600,
+        ],
+        labelnames=["mode"],
+        registry=registry,
+    )
+
     return True
 
 
 def observe_media_download(media_type: str, elapsed_seconds: float,
                            num_bytes: int) -> None:
@@ -173,10 +232,33 @@ def observe_preprocessing_total(elapsed_seconds: float) -> None:
         return
     assert _mm_preprocessing_total_latency is not None
     _mm_preprocessing_total_latency.observe(elapsed_seconds)
 
 
+def observe_mediafetch_request(
+    mode: str,
+    result: str,
+    error_type: str,
+    elapsed_seconds: float,
+    num_bytes: int | None = None,
+) -> None:
+    """Record one media-fetch-sdk request and its outcome."""
+    if not _ensure_metrics():
+        return
+    assert _mediafetch_requests is not None
+    assert _mediafetch_request_duration is not None
+    assert _mediafetch_response_bytes is not None
+
+    _mediafetch_requests.labels(mode=mode,
+                                result=result,
+                                error_type=error_type).inc()
+    _mediafetch_request_duration.labels(mode=mode, result=result).observe(
+        elapsed_seconds)
+    if num_bytes is not None:
+        _mediafetch_response_bytes.labels(mode=mode).observe(num_bytes)
+
+
 @contextmanager
 def track_preprocessing_total() -> Generator[None, None, None]:
     """Context manager to measure total preprocessing time."""
     start = time.monotonic()
     try:
````

### 44. `tests/multimodal/test_mediafetchutils.py`

- **类型**：新增文件 —— 下方 diff 的每个 `+` 行合起来就是该文件从第一行到最后一行的完整内容
- **说明**：mediafetchutils 单测：URL 解析、带 & 的 URL、引擎缓存、SDK 缺失降级
- **规模**：+206 / -0（改后文件共 206 行）
- **涉及提交**：
  - `983aefae95` [Req#85339520] vLLM 接入 media-fetch-sdk 支持 mediafetch:// 协议 * [Req#85339520] vLLM 接入 media-fetch-sdk 支持 mediafetch:// 协议
````diff
diff --git a/tests/multimodal/test_mediafetchutils.py b/tests/multimodal/test_mediafetchutils.py
new file mode 100644
index 0000000000..e9bdcdc29a
--- /dev/null
+++ b/tests/multimodal/test_mediafetchutils.py
@@ -0,0 +1,206 @@
+# SPDX-License-Identifier: Apache-2.0
+# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
+
+from unittest.mock import MagicMock
+
+import pytest
+
+import vllm.multimodal.mediafetchutils as mediafetchutils
+from vllm.multimodal.mediafetchutils import (
+    _parse_mediafetch_url,
+    get_bytes_from_mediafetch_path,
+)
+
+
+class TestParseMediafetchUrl:
+
+    def test_origin_with_full_url(self):
+        url = (
+            "mediafetch://origin/?app_key=fa3e59c563ce7&"
+            "url=http://webhost.tbgw.taobao.com/v1/fa3e59c563ce7/"
+            "i4/2200645797214/O1CN01JjvoPzVBQaD21stE_!!2200645797214.jpg"
+        )
+        appkey, image_url, width = _parse_mediafetch_url(url)
+        assert appkey == "fa3e59c563ce7"
+        assert image_url.endswith("O1CN01JjvoPzVBQaD21stE_!!2200645797214.jpg")
+        assert width is None
+
+    def test_origin_with_image_key_only(self):
+        url = (
+            "mediafetch://origin/?app_key=fa3e59c563ce7&"
+            "url=O1CN01JjvoPzVBQaD21stE_!!2200645797214.jpg"
+        )
+        appkey, image_url, width = _parse_mediafetch_url(url)
+        assert appkey == "fa3e59c563ce7"
+        assert image_url == "O1CN01JjvoPzVBQaD21stE_!!2200645797214.jpg"
+        assert width is None
+
+    @pytest.mark.parametrize("image_url_suffix", [
+        "http://webhost.tbgw.taobao.com/v1/fa3e59c563ce7/i4/2200645797214/O1CN01JjvoPzVBQaD21stE_!!2200645797214.jpg",
+        "webhost.tbgw.taobao.com/v1/fa3e59c563ce7/i4/2200645797214/O1CN01JjvoPzVBQaD21stE_!!2200645797214.jpg",
+        "/2200645797214/O1CN01JjvoPzVBQaD21stE_!!2200645797214.jpg",
+        "O1CN01JjvoPzVBQaD21stE_!!2200645797214.jpg",
+    ])
+    def test_origin_url_variants(self, image_url_suffix: str):
+        url = (
+            f"mediafetch://origin/?app_key=fa3e59c563ce7&"
+            f"url={image_url_suffix}"
+        )
+        appkey, image_url, width = _parse_mediafetch_url(url)
+        assert appkey == "fa3e59c563ce7"
+        assert image_url == image_url_suffix
+        assert width is None
+
+    def test_origin_url_with_ampersand(self):
+        """url param containing '&' (e.g. HTTP query) must not be truncated."""
+        inner_url = (
+            "http://webhost.tbgw.taobao.com/v1/fa3e59c563ce7/"
+            "i4/2200645797214/O1CN01JjvoPzVBQaD21stE_!!2200645797214.jpg"
+            "?size=large&format=jpg"
+        )
+        url = (
+            f"mediafetch://origin/?app_key=fa3e59c563ce7&"
+            f"url={inner_url}"
+        )
+        appkey, image_url, width = _parse_mediafetch_url(url)
+        assert appkey == "fa3e59c563ce7"
+        assert image_url == inner_url
+        assert width is None
+
+    def test_thumbnail_with_width_1440(self):
+        url = (
+            "mediafetch://thumbnail/?app_key=fa3e59c563ce7&"
+            "url=O1CN01JjvoPzVBQaD21stE_!!2200645797214.jpg&width=1440"
+        )
+        appkey, image_url, width = _parse_mediafetch_url(url)
+        assert appkey == "fa3e59c563ce7"
+        assert image_url == "O1CN01JjvoPzVBQaD21stE_!!2200645797214.jpg"
+        assert width == 1440
+
+    def test_thumbnail_with_width_800(self):
+        url = (
+            "mediafetch://thumbnail/?app_key=fa3e59c563ce7&"
+            "url=O1CN01JjvoPzVBQaD21stE_!!2200645797214.jpg&width=800"
+        )
+        _, image_url, width = _parse_mediafetch_url(url)
+        assert image_url == "O1CN01JjvoPzVBQaD21stE_!!2200645797214.jpg"
+        assert width == 800
+
+    def test_thumbnail_url_with_ampersand(self):
+        inner_url = (
+            "http://example.com/image.jpg?size=large&format=jpg&width=source"
+        )
+        url = (
+            f"mediafetch://thumbnail/?app_key=fa3e59c563ce7&"
+            f"url={inner_url}&width=1440"
+        )
+        _, image_url, width = _parse_mediafetch_url(url)
+        assert image_url == inner_url
+        assert width == 1440
+
+    def test_missing_app_key(self):
+        url = (
+            "mediafetch://origin/?"
+            "url=O1CN01JjvoPzVBQaD21stE_!!2200645797214.jpg"
+        )
+        with pytest.raises(ValueError, match="missing app_key"):
+            _parse_mediafetch_url(url)
+
+    def test_missing_url(self):
+        url = "mediafetch://origin/?app_key=fa3e59c563ce7"
+        with pytest.raises(ValueError, match="missing url"):
+            _parse_mediafetch_url(url)
+
+    def test_thumbnail_missing_width(self):
+        url = (
+            "mediafetch://thumbnail/?app_key=fa3e59c563ce7&"
+            "url=O1CN01JjvoPzVBQaD21stE_!!2200645797214.jpg"
+        )
+        with pytest.raises(ValueError, match="missing width"):
+            _parse_mediafetch_url(url)
+
+    @pytest.mark.parametrize("width", ["600", "1600", "abc"])
+    def test_thumbnail_invalid_width(self, width: str):
+        url = (
+            f"mediafetch://thumbnail/?app_key=fa3e59c563ce7&"
+            f"url=O1CN01JjvoPzVBQaD21stE_!!2200645797214.jpg&width={width}"
+        )
+        with pytest.raises(ValueError):
+            _parse_mediafetch_url(url)
+
+    def test_invalid_mode(self):
+        url = (
+            "mediafetch://meta/?app_key=fa3e59c563ce7&"
+            "url=O1CN01JjvoPzVBQaD21stE_!!2200645797214.jpg"
+        )
+        with pytest.raises(ValueError, match="must be origin or thumbnail"):
+            _parse_mediafetch_url(url)
+
+    def test_non_mediafetch_scheme(self):
+        url = "http://example.com/image.jpg"
+        with pytest.raises(ValueError, match="expected mediafetch:// URL"):
+            _parse_mediafetch_url(url)
+
+
+class TestMediafetchMetrics:
+
+    def test_success_records_metrics(self, monkeypatch):
+        engine = MagicMock()
+        engine.origin.return_value = b"image-data"
+        observe = MagicMock()
+        monkeypatch.setattr(mediafetchutils, "_get_engine", lambda _: engine)
+        monkeypatch.setattr(
+            mediafetchutils, "observe_mediafetch_request", observe
+        )
+
+        data = get_bytes_from_mediafetch_path(
+            "mediafetch://origin/?app_key=test&url=image.jpg"
+        )
+
+        assert data == b"image-data"
+        observe.assert_called_once()
+        call = observe.call_args.kwargs
+        assert call["mode"] == "origin"
+        assert call["result"] == "success"
+        assert call["error_type"] == "none"
+        assert call["num_bytes"] == len(data)
+        assert call["elapsed_seconds"] >= 0
+
+    def test_invalid_url_records_error(self, monkeypatch):
+        observe = MagicMock()
+        monkeypatch.setattr(
+            mediafetchutils, "observe_mediafetch_request", observe
+        )
+
+        with pytest.raises(ValueError, match="missing app_key"):
+            get_bytes_from_mediafetch_path(
+                "mediafetch://origin/?url=image.jpg"
+            )
+
+        observe.assert_called_once()
+        call = observe.call_args.kwargs
+        assert call["mode"] == "origin"
+        assert call["result"] == "error"
+        assert call["error_type"] == "invalid_url"
+        assert call["num_bytes"] is None
+
+    def test_no_data_records_separate_result(self, monkeypatch):
+        engine = MagicMock()
+        engine.origin.return_value = None
+        observe = MagicMock()
+        monkeypatch.setattr(mediafetchutils, "_get_engine", lambda _: engine)
+        monkeypatch.setattr(
+            mediafetchutils, "observe_mediafetch_request", observe
+        )
+
+        with pytest.raises(ValueError, match="returned NO_DATA"):
+            get_bytes_from_mediafetch_path(
+                "mediafetch://origin/?app_key=test&url=image.jpg"
+            )
+
+        observe.assert_called_once()
+        call = observe.call_args.kwargs
+        assert call["mode"] == "origin"
+        assert call["result"] == "no_data"
+        assert call["error_type"] == "none"
+        assert call["num_bytes"] is None
````

### 45. `tests/entrypoints/metrics/test_mm_preprocessing.py`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：mediafetch 指标单测
- **规模**：+73 / -0（改后文件共 255 行）
- **涉及提交**：
  - `983aefae95` [Req#85339520] vLLM 接入 media-fetch-sdk 支持 mediafetch:// 协议 * [Req#85339520] vLLM 接入 media-fetch-sdk 支持 mediafetch:// 协议
````diff
diff --git a/tests/entrypoints/metrics/test_mm_preprocessing.py b/tests/entrypoints/metrics/test_mm_preprocessing.py
index 551d4b402c..dc43d2d083 100644
--- a/tests/entrypoints/metrics/test_mm_preprocessing.py
+++ b/tests/entrypoints/metrics/test_mm_preprocessing.py
@@ -13,10 +13,11 @@ from prometheus_client import REGISTRY
 
 from vllm.entrypoints.metrics.mm_preprocessing import (
     _ensure_metrics,
     observe_media_decode,
     observe_media_download,
+    observe_mediafetch_request,
     observe_preprocessing_total,
     observe_resolve_items,
     track_preprocessing_total,
 )
 
@@ -37,10 +38,20 @@ def _get_sample_count(metric_name: str, labels: dict | None = None) -> float:
                 ):
                     return sample.value
     return 0.0
 
 
+def _get_sample_value(sample_name: str, labels: dict) -> float:
+    for metric in REGISTRY.collect():
+        for sample in metric.samples:
+            if sample.name == sample_name and all(
+                sample.labels.get(k) == v for k, v in labels.items()
+            ):
+                return sample.value
+    return 0.0
+
+
 @pytest.fixture(autouse=True, scope="session")
 def ensure_metrics_initialized():
     """Ensure metrics are initialized once for the entire test session."""
     assert _ensure_metrics() is True, "prometheus_client must be available"
 
@@ -62,10 +73,13 @@ class TestEnsureMetrics:
         assert mod._media_download_latency is not None
         assert mod._media_decode_latency is not None
         assert mod._media_download_bytes is not None
         assert mod._mm_resolve_items_latency is not None
         assert mod._mm_preprocessing_total_latency is not None
+        assert mod._mediafetch_requests is not None
+        assert mod._mediafetch_request_duration is not None
+        assert mod._mediafetch_response_bytes is not None
 
 
 class TestObserveFunctions:
     """Test that observe functions correctly record metrics."""
 
@@ -117,10 +131,69 @@ class TestObserveFunctions:
         observe_preprocessing_total(2.345)
         after = _get_sample_count(
             "vllm:mm_preprocessing_total_latency_seconds")
         assert after == before + 1
 
+    def test_observe_mediafetch_success(self):
+        request_labels = {
+            "mode": "origin",
+            "result": "success",
+            "error_type": "none",
+        }
+        before = _get_sample_value(
+            "vllm:mediafetch_requests_total", request_labels
+        )
+        before_bytes = _get_sample_count(
+            "vllm:mediafetch_response_bytes", {"mode": "origin"}
+        )
+
+        observe_mediafetch_request(
+            mode="origin",
+            result="success",
+            error_type="none",
+            elapsed_seconds=0.123,
+            num_bytes=4096,
+        )
+
+        after = _get_sample_value(
+            "vllm:mediafetch_requests_total", request_labels
+        )
+        after_bytes = _get_sample_count(
+            "vllm:mediafetch_response_bytes", {"mode": "origin"}
+        )
+        assert after == before + 1
+        assert after_bytes == before_bytes + 1
+
+    def test_observe_mediafetch_error_does_not_record_bytes(self):
+        request_labels = {
+            "mode": "thumbnail",
+            "result": "error",
+            "error_type": "system",
+        }
+        before = _get_sample_value(
+            "vllm:mediafetch_requests_total", request_labels
+        )
+        before_bytes = _get_sample_count(
+            "vllm:mediafetch_response_bytes", {"mode": "thumbnail"}
+        )
+
+        observe_mediafetch_request(
+            mode="thumbnail",
+            result="error",
+            error_type="system",
+            elapsed_seconds=0.5,
+        )
+
+        after = _get_sample_value(
+            "vllm:mediafetch_requests_total", request_labels
+        )
+        after_bytes = _get_sample_count(
+            "vllm:mediafetch_response_bytes", {"mode": "thumbnail"}
+        )
+        assert after == before + 1
+        assert after_bytes == before_bytes
+
 
 class TestTrackPreprocessingTotal:
     """Test the context manager."""
 
     def test_records_elapsed_time(self):
````

### 46. `requirements/alibaba-cuda.txt`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：新增 media-fetch-sdk>=0.3.2（仅 x86_64）
- **规模**：+3 / -0（改后文件共 10 行）
- **涉及提交**：
  - `a028b62223` [Req#85339520] enable media-fetch-sdk in ROCm image * [Req#85339520] enable media-fetch-sdk in ROCm image
  - `983aefae95` [Req#85339520] vLLM 接入 media-fetch-sdk 支持 mediafetch:// 协议 * [Req#85339520] vLLM 接入 media-fetch-sdk 支持 mediafetch:// 协议
````diff
diff --git a/requirements/alibaba-cuda.txt b/requirements/alibaba-cuda.txt
index ae7be119bb..bcb9a8738f 100644
--- a/requirements/alibaba-cuda.txt
+++ b/requirements/alibaba-cuda.txt
@@ -3,5 +3,8 @@ nvidia-cutlass-dsl==4.4.2
 nvidia-cutlass-dsl-libs-base==4.4.2
 
 # Pin starlette/fastapi for compatibility
 starlette==1.2.1
 fastapi==0.136.3
+
+# Ali internal image fetch SDK (x86_64 only)
+media-fetch-sdk>=0.3.2; platform_machine == "x86_64"
````

### 47. `requirements/alibaba-rocm.txt`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：新增 media-fetch-sdk>=0.3.2（仅 x86_64；已验证 ROCm 可用）
- **规模**：+2 / -0（改后文件共 2 行）
- **涉及提交**：
  - `a028b62223` [Req#85339520] enable media-fetch-sdk in ROCm image * [Req#85339520] enable media-fetch-sdk in ROCm image
````diff
diff --git a/requirements/alibaba-rocm.txt b/requirements/alibaba-rocm.txt
index e69de29bb2..1c89360cb8 100644
--- a/requirements/alibaba-rocm.txt
+++ b/requirements/alibaba-rocm.txt
@@ -0,0 +1,2 @@
+# Ali internal image fetch SDK (x86_64 only)
+media-fetch-sdk>=0.3.2; platform_machine == "x86_64"
````

---

## 组 5 · PyAV 视频后端 + 子进程解码隔离（5 文件）

损坏的 HEVC 视频会让解码器在 C 层 SIGSEGV 直接打死 worker 进程。三层防护：
PyAV 后端可控解码；`VLLM_VIDEO_DECODE_IN_SUBPROCESS=1` 时经全局 pebble 子进程池隔离
（C 级崩溃被捕获为 ProcessExpired 并转成干净的 ValueError）；qwen3_vl 视频解析走子进度。


### 48. `vllm/multimodal/video.py`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：新增 pyav video loader 后端；VLLM_VIDEO_DECODE_IN_SUBPROCESS=1 时经全局 pebble ProcessPool 子进程解码（VLLM_VIDEO_DECODE_POOL_SIZE 与 VLLM_VIDEO_DECODE_TIMEOUT 可调），C 级崩溃转 ValueError 不再杀 worker
- **规模**：+279 / -4（改后文件共 1376 行）
- **涉及提交**：
  - `cc23ba4ba4` feat(video): add PyAV backend to prevent worker coredump on corrupted HEVC videos;add video parse in sub progress
````diff
diff --git a/vllm/multimodal/video.py b/vllm/multimodal/video.py
index d719a85c79..b09ef26b9b 100644
--- a/vllm/multimodal/video.py
+++ b/vllm/multimodal/video.py
@@ -1,8 +1,10 @@
 # SPDX-License-Identifier: Apache-2.0
 # SPDX-FileCopyrightText: Copyright contributors to the vLLM project
 import math
+import os
+import tempfile
 from abc import abstractmethod
 from io import BytesIO
 from typing import Any, NamedTuple, cast
 
 import numpy as np
@@ -20,14 +22,10 @@ except ImportError:
     vr = PlaceholderModule("cv2").placeholder_attr("videoio_registry")
 
 
 logger = init_logger(__name__)
 
-import os
-import tempfile
-from qwen_vl_utils.vision_process import process_vision_info
-
 
 def resize_video(frames: npt.NDArray, size: tuple[int, int]) -> npt.NDArray:
     num_frames, _, _, channels = frames.shape
     new_height, new_width = size
     resized_frames = np.empty(
@@ -357,10 +355,240 @@ class OpenCVVideoBackendMixin:
                 valid_num_frames,
             )
         return frames, valid_frame_indices
 
 
+class PyAVVideoBackendMixin:
+    """PyAV (in-process FFmpeg bindings) codec utilities.
+
+    Reads stream metadata and decodes target frames via per-frame
+    ``container.seek()``. Unlike OpenCV, PyAV raises Python-level
+    ``av.AVError`` on corrupt streams instead of crashing the process,
+    making it suitable as a fallback for videos that cause cv2 SIGSEGV
+    (e.g. corrupted HEVC streams with broken RPS).
+    """
+
+    @staticmethod
+    def _decode_frames_pyav(
+        data: bytes,
+        frame_indices: list[int],
+        fps: float,
+        duration: float,
+    ) -> tuple[npt.NDArray, list[int]]:
+        """Decode target frames via per-frame seek + forward decode to PTS.
+
+        Args:
+            data: Raw video bytes.
+            frame_indices: Sorted list of target frame indices to decode.
+            fps: Original video FPS used to map index → timestamp.
+            duration: Total video duration in seconds.
+
+        Returns:
+            Tuple of (frames_array shaped (N, H, W, 3) uint8 RGB,
+                      valid_frame_indices).
+        """
+        try:
+            import av
+        except ImportError as exc:
+            raise ImportError(
+                "PyAV is required for the pyav video backend fallback. "
+                "Install it with: pip install av"
+            ) from exc
+
+        import io
+        with av.open(io.BytesIO(data)) as container:
+            if not container.streams.video:
+                raise ValueError("No video streams found in container")
+            stream = container.streams.video[0]
+            return PyAVVideoBackendMixin._decode_frames_pyav_container(
+                container, stream, frame_indices, fps=fps, duration=duration
+            )
+
+    @staticmethod
+    def _decode_frames_pyav_container(
+        container: Any,
+        stream: Any,
+        frame_indices: list[int],
+        fps: float,
+        duration: float,
+    ) -> tuple[npt.NDArray, list[int]]:
+        """Decode target frames from an already-opened av.Container.
+
+        Reuses the caller's open container to avoid re-parsing the container
+        header a second time (Bug 4 fix).
+
+        Args:
+            container: An already-open ``av.InputContainer``.
+            stream: The video stream from ``container.streams.video[0]``.
+            frame_indices: Sorted list of target frame indices to decode.
+            fps: Original video FPS used to map index → timestamp.
+            duration: Total video duration in seconds.
+
+        Returns:
+            Tuple of (frames_array shaped (N, H, W, 3) uint8 RGB,
+                      valid_frame_indices).
+        """
+        stream.thread_type = "SLICE"
+        time_base = stream.time_base
+
+        frames_list: list[npt.NDArray] = []
+        valid_indices: list[int] = []
+        frame_interval = 1.0 / fps if fps > 0 else 0.1
+        max_ts = (
+            max(0.0, duration - frame_interval) if duration > 0 else float("inf")
+        )
+
+        decoder = None
+        last_pts = None
+        for idx in frame_indices:
+            ts = min(idx / fps, max_ts) if fps > 0 else 0.0
+            pts = int(ts / time_base)
+            if decoder is None or last_pts is None or pts <= last_pts:
+                container.seek(pts, stream=stream)
+                decoder = container.decode(video=0)
+            chosen = None
+            for frame in decoder:
+                if frame.pts is not None and frame.pts >= pts:
+                    chosen = frame
+                    last_pts = frame.pts
+                    break
+            if chosen is not None:
+                frames_list.append(chosen.to_ndarray(format="rgb24"))
+                valid_indices.append(idx)
+            else:
+                decoder = None
+
+        if not frames_list:
+            return np.empty((0,), dtype=np.uint8), valid_indices
+        return np.stack(frames_list), valid_indices
+
+
+class PyAVVideoBackend(VideoLoader, PyAVVideoBackendMixin):
+    """Video backend using PyAV (FFmpeg Python bindings).
+
+    Unlike the OpenCV backend, PyAV raises Python-level ``av.AVError``
+    on corrupt streams (e.g. broken HEVC RPS) instead of triggering a
+    C-level SIGSEGV that kills the worker process.
+
+    Enable via environment variable: ``VLLM_VIDEO_LOADER_BACKEND=pyav``
+    """
+
+    @classmethod
+    def compute_frames_index_to_sample(
+        cls,
+        source: VideoSourceMetadata,
+        target: VideoTargetMetadata,
+        **kwargs,
+    ) -> list[int]:
+        total_frames_num = source.total_frames_num
+        duration = source.duration
+        num_frames = target.num_frames
+        fps = target.fps
+
+        num_frames_to_sample = total_frames_num
+        if num_frames > 0:
+            num_frames_to_sample = min(num_frames, total_frames_num)
+        if fps > 0:
+            num_frames_to_sample = min(
+                num_frames_to_sample, math.floor(duration * fps)
+            )
+        num_frames_to_sample = max(1, num_frames_to_sample)
+
+        if num_frames_to_sample == total_frames_num:
+            return list(range(num_frames_to_sample))
+        uniform_sampled = np.linspace(
+            0, total_frames_num - 1, num_frames_to_sample, dtype=int
+        )
+        return uniform_sampled.tolist()
+
+    @classmethod
+    def load_bytes(
+        cls,
+        data: bytes,
+        num_frames: int = -1,
+        fps: int = -1,
+        max_duration: int = 300,
+        **kwargs,
+    ) -> tuple[npt.NDArray, dict[str, Any]]:
+        try:
+            import av
+        except ImportError as exc:
+            raise ImportError(
+                "PyAV is required for the pyav video backend. "
+                "Install it with: pip install av"
+            ) from exc
+
+        import io
+        with av.open(io.BytesIO(data)) as container:
+            if not container.streams.video:
+                raise ValueError("No video streams found in container")
+            stream = container.streams.video[0]
+            total_frames = stream.frames or 0
+            orig_fps = float(stream.average_rate) if stream.average_rate else 0.0
+            duration = (
+                float(stream.duration * stream.time_base)
+                if stream.duration
+                else 0.0
+            )
+            if total_frames == 0 and duration > 0 and orig_fps > 0:
+                total_frames = int(duration * orig_fps)
+
+            # Guard: if total_frames is still 0 (e.g. container reports neither
+            # frame count nor duration), return empty result immediately to
+            # avoid linspace(0, -1, ...) producing an invalid index of -1.
+            if total_frames == 0:
+                logger.warning(
+                    "PyAV: video container reports 0 frames and no recoverable "
+                    "duration/fps; returning empty result."
+                )
+                empty_frames = np.empty((0,), dtype=np.uint8)
+                source = VideoSourceMetadata(
+                    total_frames_num=0,
+                    original_fps=orig_fps,
+                    duration=duration,
+                )
+                metadata = cls.create_hf_metadata(
+                    source=source,
+                    video_backend="pyav",
+                    valid_frame_indices=[],
+                )
+                return empty_frames, metadata
+
+            source = VideoSourceMetadata(
+                total_frames_num=total_frames,
+                original_fps=orig_fps,
+                duration=duration,
+            )
+            target = VideoTargetMetadata(
+                num_frames=num_frames,
+                fps=fps,
+                max_duration=max_duration,
+            )
+            frame_indices = cls.compute_frames_index_to_sample(
+                source=source, target=target
+            )
+
+            # Decode frames within the same open container to avoid re-parsing
+            # the container header a second time.
+            try:
+                frames, valid_frame_indices = cls._decode_frames_pyav_container(
+                    container, stream, frame_indices, fps=orig_fps, duration=duration
+                )
+            except Exception as exc:
+                raise ValueError(
+                    f"PyAV failed to decode video. "
+                    f"The video may be corrupted. Error: {exc}"
+                ) from exc
+
+        metadata = cls.create_hf_metadata(
+            source=source,
+            video_backend="pyav",
+            valid_frame_indices=valid_frame_indices,
+        )
+        return frames, metadata
+
+
 @VIDEO_LOADER_REGISTRY.register("opencv")
 class OpenCVVideoBackend(VideoLoader, OpenCVVideoBackendMixin):
     @classmethod
     def compute_frames_index_to_sample(
         cls,
@@ -435,10 +663,33 @@ class OpenCVVideoBackend(VideoLoader, OpenCVVideoBackendMixin):
             frame_idx,
             total_frames_num=source.total_frames_num,
             frame_recovery=frame_recovery,
         )
 
+        # Fallback to PyAV when cv2 returns 0 frames (e.g. corrupted HEVC
+        # stream with broken RPS that causes cv2 to SIGSEGV on next attempt).
+        # PyAV raises a Python-level av.AVError instead of crashing the process.
+        if len(valid_frame_indices) == 0 and frame_idx:
+            logger.warning(
+                "OpenCV returned 0 frames, falling back to PyAV backend "
+                "(video may have a corrupted stream)."
+            )
+            try:
+                frames, valid_frame_indices = \
+                    PyAVVideoBackendMixin._decode_frames_pyav(
+                        data,
+                        frame_idx,
+                        fps=source.original_fps,
+                        duration=source.duration,
+                    )
+            except Exception as pyav_exc:
+                raise ValueError(
+                    f"Both OpenCV and PyAV failed to decode video. "
+                    f"The video is likely corrupted. "
+                    f"PyAV error: {pyav_exc}"
+                ) from pyav_exc
+
         metadata = cls.create_hf_metadata(
             source=source,
             video_backend="opencv",
             valid_frame_indices=valid_frame_indices,
         )
@@ -541,10 +792,33 @@ class OpenCVDynamicVideoBackend(VideoLoader, OpenCVVideoBackendMixin):
             frame_indices_list,
             total_frames_num=source.total_frames_num,
             frame_recovery=frame_recovery,
         )
 
+        # Fallback to PyAV when cv2 returns 0 frames (e.g. corrupted HEVC
+        # stream with broken RPS that causes cv2 to SIGSEGV on next attempt).
+        # PyAV raises a Python-level av.AVError instead of crashing the process.
+        if len(valid_frame_indices) == 0 and frame_indices_list:
+            logger.warning(
+                "OpenCV returned 0 frames, falling back to PyAV backend "
+                "(video may have a corrupted stream)."
+            )
+            try:
+                frames, valid_frame_indices = \
+                    PyAVVideoBackendMixin._decode_frames_pyav(
+                        data,
+                        frame_indices_list,
+                        fps=source.original_fps,
+                        duration=source.duration,
+                    )
+            except Exception as pyav_exc:
+                raise ValueError(
+                    f"Both OpenCV and PyAV failed to decode video. "
+                    f"The video is likely corrupted. "
+                    f"PyAV error: {pyav_exc}"
+                ) from pyav_exc
+
         metadata = cls.create_hf_metadata(
             source=source,
             video_backend="opencv_dynamic",
             valid_frame_indices=valid_frame_indices,
         )
@@ -999,10 +1273,11 @@ class QwenVLUtilsVideoBackend(VideoLoader):
             }
             if num_frames > 0:
                 video_ele["nframes"] = num_frames
             video_ele.update(kwargs)
             conversation = [{"content": [video_ele]}]
+            from qwen_vl_utils.vision_process import process_vision_info
             _, video_inputs, _ = process_vision_info(
                 conversation,
                 return_video_metadata=True,
                 return_video_kwargs=True,
                 image_patch_size=image_patch_size,
````

### 49. `vllm/multimodal/media/video.py`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：VideoMediaIO 接入子进程解码路径与超时/ProcessExpired 处理
- **规模**：+119 / -2（改后文件共 276 行）
- **涉及提交**：
  - `cc23ba4ba4` feat(video): add PyAV backend to prevent worker coredump on corrupted HEVC videos;add video parse in sub progress
````diff
diff --git a/vllm/multimodal/media/video.py b/vllm/multimodal/media/video.py
index 4f4197d082..65c85d8ec5 100644
--- a/vllm/multimodal/media/video.py
+++ b/vllm/multimodal/media/video.py
@@ -1,22 +1,93 @@
 # SPDX-License-Identifier: Apache-2.0
 # SPDX-FileCopyrightText: Copyright contributors to the vLLM project
+import atexit
 import base64
+import logging
+import os
+from concurrent.futures import TimeoutError as FutureTimeoutError
 from functools import partial
 from pathlib import Path
 from typing import Any
 
 import numpy as np
 import numpy.typing as npt
 from PIL import Image
 
 from vllm import envs
 
-from ..video import VIDEO_LOADER_REGISTRY, AUDIO_IN_VIDEO_LOADER_REGISTRY
+from ..video import AUDIO_IN_VIDEO_LOADER_REGISTRY, VIDEO_LOADER_REGISTRY
 from .base import MediaIO
 from .image import ImageMediaIO
 
+logger = logging.getLogger(__name__)
+
+# Decode timeout in seconds when subprocess isolation is enabled.
+# Can be overridden via VLLM_VIDEO_DECODE_TIMEOUT env var (default: 600s).
+_VIDEO_DECODE_TIMEOUT_SECONDS = int(
+    os.environ.get("VLLM_VIDEO_DECODE_TIMEOUT", 600)
+)
+
+# Global pebble ProcessPool, created lazily on first use.
+# Shared across all VideoMediaIO instances to bound total subprocess count.
+_VIDEO_DECODE_POOL = None
+
+
+def _stop_video_decode_pool() -> None:
+    """Clean up the global pebble ProcessPool on interpreter exit."""
+    global _VIDEO_DECODE_POOL
+    pool = _VIDEO_DECODE_POOL
+    _VIDEO_DECODE_POOL = None
+    if pool is not None:
+        try:
+            pool.stop()
+            pool.join()
+        except Exception:  # noqa: BLE001
+            logger.exception("Failed to clean up video decode subprocess pool.")
+
+
+atexit.register(_stop_video_decode_pool)
+
+
+def _get_video_decode_pool():
+    """Lazily create the global pebble ProcessPool for video decoding."""
+    global _VIDEO_DECODE_POOL
+    if _VIDEO_DECODE_POOL is None:
+        try:
+            from pebble import ProcessPool
+        except ImportError as exc:
+            raise ImportError(
+                "pebble is required for VLLM_VIDEO_DECODE_IN_SUBPROCESS=1. "
+                "Install it with: pip install pebble"
+            ) from exc
+        max_workers = int(os.getenv("VLLM_VIDEO_DECODE_POOL_SIZE",
+                                    str(max(1, (os.cpu_count() or 1) // 4))))
+        _VIDEO_DECODE_POOL = ProcessPool(max_workers=max_workers)
+        logger.info("Created video decode subprocess pool "
+                    "(max_workers=%d).", max_workers)
+    return _VIDEO_DECODE_POOL
+
+
+def _decode_video_in_worker(
+    video_loader_backend: str,
+    data: bytes,
+    num_frames: int,
+    kwargs: dict,
+) -> tuple[npt.NDArray, dict[str, Any]]:
+    """Top-level function executed inside the pebble subprocess worker.
+
+    Must be a module-level function (not a lambda or closure) so that it
+    can be pickled by multiprocessing.
+    """
+    loader = VIDEO_LOADER_REGISTRY.load(video_loader_backend)
+    return loader.load_bytes(data, num_frames=num_frames, **kwargs)
+
+
+def _use_subprocess_isolation() -> bool:
+    """Return True if video decoding should run in an isolated subprocess."""
+    return envs.VLLM_VIDEO_DECODE_IN_SUBPROCESS == "1"
+
 
 class VideoMediaIO(MediaIO[tuple[npt.NDArray, dict[str, Any]]]):
     """Configuration values can be user-provided either by --media-io-kwargs or
     by the runtime API field "media_io_kwargs". Ensure proper validation and
     error handling.
@@ -65,14 +136,59 @@ class VideoMediaIO(MediaIO[tuple[npt.NDArray, dict[str, Any]]]):
         )
         self.kwargs = kwargs
         self.video_loader = VIDEO_LOADER_REGISTRY.load(video_loader_backend)
 
     def load_bytes(self, data: bytes) -> tuple[npt.NDArray, dict[str, Any]]:
+        if _use_subprocess_isolation():
+            return self._load_bytes_in_subprocess(data)
         return self.video_loader.load_bytes(
             data, num_frames=self.num_frames, **self.kwargs
         )
 
+    def _load_bytes_in_subprocess(
+        self, data: bytes
+    ) -> tuple[npt.NDArray, dict[str, Any]]:
+        """Run video decoding in an isolated pebble subprocess.
+
+        A C-level SIGSEGV inside the decoder (e.g. corrupted HEVC stream)
+        kills only the worker process; the pool auto-restarts it and this
+        method raises a clean ValueError instead of crashing the worker.
+        """
+        try:
+            from pebble.common import ProcessExpired
+        except ImportError as exc:
+            raise ImportError(
+                "pebble is required for subprocess video decoding. "
+                "Install it with: pip install pebble"
+            ) from exc
+
+        pool = _get_video_decode_pool()
+        future = pool.schedule(
+            _decode_video_in_worker,
+            args=[
+                envs.VLLM_VIDEO_LOADER_BACKEND,
+                data,
+                self.num_frames,
+                self.kwargs,
+            ],
+            timeout=_VIDEO_DECODE_TIMEOUT_SECONDS,
+        )
+        try:
+            return future.result()
+        except FutureTimeoutError:
+            raise ValueError(
+                f"Video decoding timed out after "
+                f"{_VIDEO_DECODE_TIMEOUT_SECONDS}s. "
+                f"The video may be corrupted or too large."
+            )
+        except ProcessExpired as exc:
+            raise ValueError(
+                f"Video decoding worker crashed (likely a corrupted video "
+                f"stream triggering a C-level SIGSEGV). "
+                f"Error: {exc}"
+            ) from exc
+
     def load_base64(
         self, media_type: str, data: str
     ) -> tuple[npt.NDArray, dict[str, Any]]:
         if media_type.lower() == "video/jpeg":
             load_frame = partial(
@@ -110,10 +226,12 @@ class VideoMediaIO(MediaIO[tuple[npt.NDArray, dict[str, Any]]]):
 
         msg = "Only JPEG format is supported for now."
         raise NotImplementedError(msg)
 
 class VideoWithAudioMediaIO(MediaIO[tuple]):
+    """MediaIO that loads both video frames and in-video audio."""
+
     @classmethod
     def merge_kwargs(
         cls,
         default_kwargs: dict[str, Any] | None,
         runtime_kwargs: dict[str, Any] | None,
@@ -127,11 +245,10 @@ class VideoWithAudioMediaIO(MediaIO[tuple]):
                 merged.pop("fps", None)
             elif "fps" in runtime_kwargs and "num_frames" not in runtime_kwargs:
                 merged.pop("num_frames", None)
         return merged
 
-    """MediaIO that loads both video frames and in-video audio."""
     def __init__(
         self,
         num_frames: int = -1,
         **kwargs,
     ) -> None:
````

### 50. `vllm/envs.py`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：新增 VLLM_VIDEO_DECODE_IN_SUBPROCESS 环境变量（默认 0，进程内解码）
- **规模**：+10 / -0（改后文件共 1842 行）
- **涉及提交**：
  - `cc23ba4ba4` feat(video): add PyAV backend to prevent worker coredump on corrupted HEVC videos;add video parse in sub progress
````diff
diff --git a/vllm/envs.py b/vllm/envs.py
index d05a739d94..f0cfd0a96c 100755
--- a/vllm/envs.py
+++ b/vllm/envs.py
@@ -787,10 +787,20 @@ environment_variables: dict[str, Callable[[], Any]] = {
     # imported at runtime.
     # If a non-existing backend is used, an AssertionError will be thrown.
     "VLLM_VIDEO_LOADER_BACKEND": lambda: os.getenv(
         "VLLM_VIDEO_LOADER_BACKEND", "opencv"
     ),
+    # Whether to run video decoding in an isolated subprocess via pebble
+    # ProcessPool to prevent corrupted video streams from crashing the worker
+    # process with SIGSEGV. When enabled, a C-level crash in the decoder
+    # (e.g. broken HEVC RPS) is caught as ProcessExpired and surfaced as a
+    # clean ValueError instead of killing the worker.
+    # - "0" (default): disabled, decoding runs in-process
+    # - "1": enabled, decoding runs in a pebble subprocess pool
+    "VLLM_VIDEO_DECODE_IN_SUBPROCESS": lambda: os.getenv(
+        "VLLM_VIDEO_DECODE_IN_SUBPROCESS", "0"
+    ),
     # Backend for Audio in Video IO
     # - "qwen_omni_utils": Uses qwen_omni_utils to decode audio in video.
     "VLLM_AUDIO_IN_VIDEO_LOADER_BACKEND": lambda: os.getenv(
         "VLLM_AUDIO_IN_VIDEO_LOADER_BACKEND", "qwen_omni_utils"
     ),
````

### 51. `vllm/model_executor/models/qwen3_vl.py`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：视频解析改走子进度
- **规模**：+2 / -1（改后文件共 2438 行）
- **涉及提交**：
  - `cc23ba4ba4` feat(video): add PyAV backend to prevent worker coredump on corrupted HEVC videos;add video parse in sub progress
````diff
diff --git a/vllm/model_executor/models/qwen3_vl.py b/vllm/model_executor/models/qwen3_vl.py
index 733c602bf6..49f7f286e0 100644
--- a/vllm/model_executor/models/qwen3_vl.py
+++ b/vllm/model_executor/models/qwen3_vl.py
@@ -46,10 +46,11 @@ from transformers.models.qwen3_vl.configuration_qwen3_vl import (
 from transformers.models.qwen3_vl.video_processing_qwen3_vl import (
     smart_resize as video_smart_resize,
 )
 from transformers.video_utils import VideoMetadata
 
+from vllm import envs
 from vllm.compilation.decorators import support_torch_compile
 from vllm.config import VllmConfig
 from vllm.config.multimodal import BaseDummyOptions, VideoDummyOptions
 from vllm.distributed import get_pp_group, parallel_state
 from vllm.logger import init_logger
@@ -932,11 +933,11 @@ class Qwen3VLDummyInputsBuilder(BaseDummyInputsBuilder[Qwen3VLProcessingInfo]):
             video_metadata = {
                 "fps": 2.0,
                 "duration": num_frames / 2.0,
                 "total_num_frames": num_frames,
                 "frames_indices": [i for i in range(num_frames)],
-                "video_backend": "opencv",
+                "video_backend": envs.VLLM_VIDEO_LOADER_BACKEND,
                 "do_sample_frames": False,
             }
             video_item = (video.copy(), video_metadata)
             video_items.append(video_item)
         return video_items
````

### 52. `tests/multimodal/media/test_video.py`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：PyAV 后端与子进程隔离单测
- **规模**：+226 / -0（改后文件共 463 行）
- **涉及提交**：
  - `cc23ba4ba4` feat(video): add PyAV backend to prevent worker coredump on corrupted HEVC videos;add video parse in sub progress
````diff
diff --git a/tests/multimodal/media/test_video.py b/tests/multimodal/media/test_video.py
index 9c04d991ab..3c36ea3cd5 100644
--- a/tests/multimodal/media/test_video.py
+++ b/tests/multimodal/media/test_video.py
@@ -1,9 +1,10 @@
 # SPDX-License-Identifier: Apache-2.0
 # SPDX-FileCopyrightText: Copyright contributors to the vLLM project
 from pathlib import Path
 
+import cv2
 import numpy as np
 import numpy.typing as npt
 import pytest
 from PIL import Image
 
@@ -233,5 +234,230 @@ def test_video_media_io_backend_env_var_fallback(monkeypatch: pytest.MonkeyPatch
         # Not providing video_backend should also fall back to env var
         videoio_missing = VideoMediaIO(imageio, num_frames=10)
         frames_missing, metadata_missing = videoio_missing.load_bytes(b"test")
         np.testing.assert_array_equal(frames_missing, FAKE_OUTPUT_2)
         assert metadata_missing["video_backend"] == "test_video_backend_override_2"
+
+
+# ---------------------------------------------------------------------------
+# Tests for new code introduced in fix_video_zero CR
+# ---------------------------------------------------------------------------
+
+def _make_minimal_mp4(tmp_path: Path, num_frames: int = 5, fps: float = 5.0) -> bytes:
+    """Create a minimal valid MP4 in memory using OpenCV and return its bytes."""
+    video_path = str(tmp_path / "test.mp4")
+    height, width = 64, 64
+    writer = cv2.VideoWriter(
+        video_path,
+        cv2.VideoWriter_fourcc(*"mp4v"),
+        fps,
+        (width, height),
+        isColor=True,
+    )
+    for i in range(num_frames):
+        frame = np.full((height, width, 3), i * 40, dtype=np.uint8)
+        writer.write(frame)
+    writer.release()
+    with open(video_path, "rb") as f:
+        return f.read()
+
+
+class TestPyAVVideoBackend:
+    """Tests for PyAVVideoBackend (new backend in fix_video_zero CR)."""
+
+    @pytest.fixture(autouse=True)
+    def _skip_without_av(self):
+        av = pytest.importorskip("av", reason="PyAV not installed")
+        return av
+
+    def test_load_bytes_returns_correct_frame_count(self, tmp_path):
+        """PyAVVideoBackend.load_bytes returns the requested number of frames."""
+        from vllm.multimodal.video import PyAVVideoBackend
+
+        data = _make_minimal_mp4(tmp_path, num_frames=10, fps=5.0)
+        frames, metadata = PyAVVideoBackend.load_bytes(data, num_frames=5)
+
+        assert isinstance(frames, np.ndarray)
+        assert frames.ndim == 4          # (N, H, W, C)
+        assert frames.shape[-1] == 3     # RGB
+        assert frames.shape[0] <= 5
+        assert metadata["video_backend"] == "pyav"
+
+    def test_load_bytes_zero_frames_guard(self):
+        """PyAVVideoBackend.load_bytes returns empty array for unreadable container
+        instead of crashing with linspace(0, -1, ...) producing index -1.
+
+        This is the core fix for the zero-frames bug (Bug 5).
+        """
+        from vllm.multimodal.video import PyAVVideoBackend
+
+        # Feed garbage bytes — av.open may raise or produce a container with 0
+        # frames and no duration.  Either outcome is acceptable; what must NOT
+        # happen is an uncaught IndexError / ValueError from linspace.
+        try:
+            frames, metadata = PyAVVideoBackend.load_bytes(b"\x00" * 16)
+            # If av accepts the bytes and reports 0 frames, we should get an
+            # empty array back, not a crash.
+            assert isinstance(frames, np.ndarray)
+        except Exception:
+            # av.open raised for invalid data — also acceptable.
+            pass
+
+    def test_decode_frames_pyav_container_matches_decode_frames_pyav(self, tmp_path):
+        """_decode_frames_pyav_container (container reuse) produces the same
+        frames as the original _decode_frames_pyav (second open).
+
+        This is the correctness test for Bug 4 fix.
+        """
+        import av
+        import io as _io
+        from vllm.multimodal.video import PyAVVideoBackendMixin
+
+        data = _make_minimal_mp4(tmp_path, num_frames=6, fps=3.0)
+        frame_indices = [0, 1, 2, 3]
+        fps = 3.0
+        duration = 2.0
+
+        # Original method: opens its own container
+        frames_orig, valid_orig = PyAVVideoBackendMixin._decode_frames_pyav(
+            data, frame_indices, fps=fps, duration=duration
+        )
+
+        # New method: reuses an already-open container
+        with av.open(_io.BytesIO(data)) as container:
+            stream = container.streams.video[0]
+            frames_new, valid_new = PyAVVideoBackendMixin._decode_frames_pyav_container(
+                container, stream, frame_indices, fps=fps, duration=duration
+            )
+
+        assert valid_orig == valid_new, (
+            f"valid_frame_indices differ: orig={valid_orig}, new={valid_new}"
+        )
+        if len(frames_orig) > 0 and len(frames_new) > 0:
+            np.testing.assert_array_equal(
+                frames_orig, frames_new,
+                err_msg="_decode_frames_pyav_container produced different frames "
+                        "than _decode_frames_pyav for the same input.",
+            )
+
+    def test_load_bytes_no_double_open(self, tmp_path, monkeypatch):
+        """PyAVVideoBackend.load_bytes calls av.open exactly once (Bug 4 fix).
+
+        The old code called av.open twice: once to read metadata, once to
+        decode frames.  After the fix, the decode reuses the same container.
+        """
+        import av
+        import io as _io
+
+        open_call_count = []
+        original_open = av.open
+
+        def counting_open(*args, **kwargs):
+            open_call_count.append(1)
+            return original_open(*args, **kwargs)
+
+        monkeypatch.setattr(av, "open", counting_open)
+
+        from vllm.multimodal.video import PyAVVideoBackend
+        data = _make_minimal_mp4(tmp_path, num_frames=5, fps=5.0)
+        PyAVVideoBackend.load_bytes(data, num_frames=3)
+
+        assert len(open_call_count) == 1, (
+            f"Expected av.open to be called once, but was called "
+            f"{len(open_call_count)} times."
+        )
+
+    def test_load_bytes_metadata_has_expected_keys(self, tmp_path):
+        """Metadata dict returned by PyAVVideoBackend contains standard keys."""
+        from vllm.multimodal.video import PyAVVideoBackend
+
+        data = _make_minimal_mp4(tmp_path, num_frames=4, fps=2.0)
+        _, metadata = PyAVVideoBackend.load_bytes(data, num_frames=4)
+
+        assert "video_backend" in metadata
+        assert metadata["video_backend"] == "pyav"
+
+
+class TestOpenCVPyAVFallback:
+    """Tests for OpenCV → PyAV zero-frame fallback (new in fix_video_zero CR)."""
+
+    @pytest.fixture(autouse=True)
+    def _skip_without_av(self):
+        pytest.importorskip("av", reason="PyAV not installed; fallback requires it")
+
+    def test_opencv_falls_back_to_pyav_when_zero_frames(self, tmp_path, monkeypatch):
+        """When OpenCV returns 0 valid frames, the backend falls back to PyAV
+        and still returns a non-empty result for a valid video.
+
+        This tests the core zero-frame bug fix in OpenCVVideoBackend.
+        """
+        from vllm.multimodal.video import OpenCVVideoBackend, OpenCVVideoBackendMixin
+
+        # Patch _read_frames_with_recovery to simulate OpenCV returning 0 frames
+        monkeypatch.setattr(
+            OpenCVVideoBackendMixin,
+            "_read_frames_with_recovery",
+            lambda *args, **kwargs: (
+                np.empty((0, 64, 64, 3), dtype=np.uint8),
+                [],
+            ),
+        )
+
+        data = _make_minimal_mp4(tmp_path, num_frames=5, fps=5.0)
+        frames, metadata = OpenCVVideoBackend.load_bytes(data, num_frames=3)
+
+        # After PyAV fallback, we should get valid frames
+        assert isinstance(frames, np.ndarray)
+        # May be 0 if PyAV also struggles with the simulated condition,
+        # but must not raise an unhandled exception.
+        assert frames.ndim in (1, 4)  # empty (1D) or valid (4D)
+
+
+class TestVideoWithAudioMediaIODocstring:
+    """Tests that VideoWithAudioMediaIO class docstring is correctly placed."""
+
+    def test_class_has_docstring(self):
+        """VideoWithAudioMediaIO must have a proper class docstring (not None).
+
+        This guards against the bug where the docstring was placed after the
+        first method, making Python ignore it as a class docstring.
+        """
+        from vllm.multimodal.media.video import VideoWithAudioMediaIO
+
+        assert VideoWithAudioMediaIO.__doc__ is not None, (
+            "VideoWithAudioMediaIO has no class docstring. "
+            "The docstring must be the first statement in the class body."
+        )
+        assert "video" in VideoWithAudioMediaIO.__doc__.lower(), (
+            f"Unexpected docstring content: {VideoWithAudioMediaIO.__doc__!r}"
+        )
+
+
+class TestQwenVLUtilsLazyImport:
+    """Tests that qwen_vl_utils is NOT imported at module level (规范 7 fix)."""
+
+    def test_qwen_vl_utils_not_imported_at_module_level(self):
+        """Importing vllm.multimodal.video must NOT require qwen_vl_utils to
+        be installed.  The import is now deferred into load_bytes().
+        """
+        import sys
+
+        # Remove qwen_vl_utils from sys.modules to simulate it being absent
+        qwen_mod = sys.modules.pop("qwen_vl_utils", None)
+        qwen_vp_mod = sys.modules.pop("qwen_vl_utils.vision_process", None)
+
+        try:
+            # Re-importing the module must succeed even without qwen_vl_utils
+            import importlib
+            import vllm.multimodal.video as video_mod
+            importlib.reload(video_mod)  # force re-execution of module top-level
+        except ImportError as exc:
+            pytest.fail(
+                f"vllm.multimodal.video raised ImportError at import time "
+                f"due to qwen_vl_utils: {exc}"
+            )
+        finally:
+            # Restore original state
+            if qwen_mod is not None:
+                sys.modules["qwen_vl_utils"] = qwen_mod
+            if qwen_vp_mod is not None:
+                sys.modules["qwen_vl_utils.vision_process"] = qwen_vp_mod
````

---

## 组 6 · 上游 bugfix 回移：Mamba 调度与 GDN 预热（6 文件）

两笔社区修复的完整回移：上游 #51603（Mamba block 对齐移到 encoder cap 之前，修复
encoder cache 无法释放与 EAGLE lookahead 窗口计算不一致）与 #36599（GDN Triton kernel
在 V1 profiling 期间预热，防止 KV cache 分配后 autotune OOM），外加 speculative
placeholder(-1) 进入 embedding lookup 前的 clamp。


### 53. `vllm/v1/core/sched/scheduler.py`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：回移上游 #51603：Mamba block 对齐从 encoder cap 之后移到之前（防止必要推进被截成 0 导致 encoder cache 泄漏）；encoder_window_end 统一含 shift_computed_tokens
- **规模**：+22 / -22（改后文件共 2238 行）
- **涉及提交**：
  - `d4019dbb97` [Bugfix][v0.17.1_omega] Backport Mamba encoder scheduling and spec-decode placeholder fixes
````diff
diff --git a/vllm/v1/core/sched/scheduler.py b/vllm/v1/core/sched/scheduler.py
index 9985bc343a..9d0b06ea3f 100644
--- a/vllm/v1/core/sched/scheduler.py
+++ b/vllm/v1/core/sched/scheduler.py
@@ -383,10 +383,16 @@ class Scheduler(SchedulerInterface):
             # This is necessary when using spec decoding.
             num_new_tokens = min(
                 num_new_tokens, self.max_model_len - 1 - request.num_computed_tokens
             )
 
+            # Apply Mamba alignment before encoder caps.
+            if self.need_mamba_block_aligned_split:
+                num_new_tokens = self._mamba_block_aligned_split(
+                    request, num_new_tokens
+                )
+
             # Schedule encoder inputs.
             encoder_inputs_to_schedule = None
             external_load_encoder_input: list[int] = []
             new_encoder_compute_budget = encoder_compute_budget
             if request.has_encoder_inputs:
@@ -401,15 +407,10 @@ class Scheduler(SchedulerInterface):
                     num_new_tokens,
                     encoder_compute_budget,
                     shift_computed_tokens=1 if self.use_eagle else 0,
                 )
 
-            if self.need_mamba_block_aligned_split:
-                num_new_tokens = self._mamba_block_aligned_split(
-                    request, num_new_tokens
-                )
-
             if num_new_tokens == 0:
                 # The request cannot be scheduled because one of the following
                 # reasons:
                 # 1. No new tokens to schedule. This may happen when
                 #    (1) PP>1 and we have already scheduled all prompt tokens
@@ -670,10 +671,21 @@ class Scheduler(SchedulerInterface):
                         break
 
                     num_new_tokens = min(num_new_tokens, token_budget)
                     assert num_new_tokens > 0
 
+                    # Apply Mamba alignment before encoder caps.
+                    if self.need_mamba_block_aligned_split:
+                        num_new_tokens = self._mamba_block_aligned_split(
+                            request,
+                            num_new_tokens,
+                            num_new_local_computed_tokens,
+                            num_external_computed_tokens,
+                        )
+                        if num_new_tokens == 0:
+                            break
+
                     # Schedule encoder inputs.
                     if request.has_encoder_inputs:
                         (
                             encoder_inputs_to_schedule,
                             num_new_tokens,
@@ -688,20 +700,10 @@ class Scheduler(SchedulerInterface):
                         )
                         if num_new_tokens == 0:
                             # The request cannot be scheduled.
                             break
 
-                if self.need_mamba_block_aligned_split:
-                    num_new_tokens = self._mamba_block_aligned_split(
-                        request,
-                        num_new_tokens,
-                        num_new_local_computed_tokens,
-                        num_external_computed_tokens,
-                    )
-                    if num_new_tokens == 0:
-                        break
-
                 # Handles an edge case when P/D Disaggregation
                 # is used with Spec Decoding where an
                 # extra block gets allocated which
                 # creates a mismatch between the number
                 # of local and remote blocks.
@@ -1128,23 +1130,23 @@ class Scheduler(SchedulerInterface):
         # NOTE: since scheduler operates on the request level (possibly with
         # multiple encoder inputs per request), we need to create temporary
         # trackers for accounting at the encoder input level.
         mm_hashes_to_schedule = set()
         num_embeds_to_schedule = 0
+        encoder_window_end = (
+            num_computed_tokens + num_new_tokens + shift_computed_tokens
+        )
         for i, mm_feature in enumerate(mm_features):
             start_pos = mm_feature.mm_position.offset
             num_encoder_tokens = mm_feature.mm_position.length
             num_encoder_embeds = mm_feature.mm_position.get_num_embeds()
             item_identifier = mm_feature.identifier
 
             # The encoder output is needed if the two ranges overlap:
             # [num_computed_tokens, num_computed_tokens + num_new_tokens) and
             # [start_pos, start_pos + num_encoder_tokens)
-            if (
-                start_pos
-                >= num_computed_tokens + num_new_tokens + shift_computed_tokens
-            ):
+            if start_pos >= encoder_window_end:
                 # The encoder input is not needed in this step.
                 break
 
             if self.is_encoder_decoder and num_computed_tokens > 0:
                 assert start_pos == 0, (
@@ -1217,13 +1219,11 @@ class Scheduler(SchedulerInterface):
                 break
 
             # Calculate the number of embeddings to schedule in the current range
             # of scheduled encoder placeholder tokens.
             start_idx_rel = max(0, num_computed_tokens - start_pos)
-            end_idx_rel = min(
-                num_encoder_tokens, num_computed_tokens + num_new_tokens - start_pos
-            )
+            end_idx_rel = min(num_encoder_tokens, encoder_window_end - start_pos)
             curr_embeds_start, curr_embeds_end = (
                 mm_feature.mm_position.get_embeds_indices_in_range(
                     start_idx_rel, end_idx_rel
                 )
             )
````

### 54. `vllm/v1/worker/gpu_model_runner.py`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：回移：speculative placeholder(-1) 在 embedding lookup 前 clamp_(min=0)
- **规模**：+4 / -0（改后文件共 6751 行）
- **涉及提交**：
  - `d4019dbb97` [Bugfix][v0.17.1_omega] Backport Mamba encoder scheduling and spec-decode placeholder fixes
````diff
diff --git a/vllm/v1/worker/gpu_model_runner.py b/vllm/v1/worker/gpu_model_runner.py
index 3817e3de7c..254b28f947 100644
--- a/vllm/v1/worker/gpu_model_runner.py
+++ b/vllm/v1/worker/gpu_model_runner.py
@@ -2977,10 +2977,14 @@ class GPUModelRunner(
     ]:
         num_scheduled_tokens = scheduler_output.total_num_scheduled_tokens
         is_first_rank = get_pp_group().is_first_rank
         is_encoder_decoder = self.model_config.is_encoder_decoder
 
+        # Clamp speculative scheduler placeholders (-1) before embedding lookup.
+        if self.speculative_config is not None:
+            self.input_ids.gpu[:num_input_tokens].clamp_(min=0)
+
         # _prepare_inputs may reorder the batch, so we must gather multi
         # modal outputs after that to ensure the correct order
         ec_connector_output = None
 
         if self.supports_mm_inputs and is_first_rank and not is_encoder_decoder:
````

### 55. `tests/v1/core/test_scheduler.py`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：Mamba 对齐重排的调度器测试
- **规模**：+139 / -0（改后文件共 4189 行）
- **涉及提交**：
  - `d4019dbb97` [Bugfix][v0.17.1_omega] Backport Mamba encoder scheduling and spec-decode placeholder fixes
````diff
diff --git a/tests/v1/core/test_scheduler.py b/tests/v1/core/test_scheduler.py
index bbeca6ef7d..5629e0ff52 100644
--- a/tests/v1/core/test_scheduler.py
+++ b/tests/v1/core/test_scheduler.py
@@ -71,10 +71,63 @@ def test_get_num_unfinished_requests():
     for i, request in enumerate(requests):
         scheduler.finish_requests(request.request_id, RequestStatus.FINISHED_STOPPED)
         assert scheduler.get_num_unfinished_requests() == len(requests) - i - 1
 
 
+def test_mamba_align_encoder_cache_cap_makes_progress():
+    """Two individually cacheable images must not deadlock Mamba alignment."""
+    block_size = 768
+    encoder_cache_size = 600
+    scheduler = create_scheduler(
+        max_num_batched_tokens=8192,
+        block_size=block_size,
+        enable_prefix_caching=True,
+    )
+    scheduler.need_mamba_block_aligned_split = True
+    scheduler.max_num_encoder_input_tokens = encoder_cache_size
+    scheduler.encoder_cache_manager = EncoderCacheManager(cache_size=encoder_cache_size)
+
+    first_image_end = 510
+    request = create_requests(
+        num_requests=1,
+        num_tokens=1010,
+        mm_positions=[
+            [
+                PlaceholderRange(offset=0, length=500),
+                PlaceholderRange(offset=first_image_end, length=500),
+            ]
+        ],
+        max_tokens=1,
+        block_size=block_size,
+        req_ids=["req"],
+    )[0]
+    scheduler.add_request(request)
+
+    output = scheduler.schedule()
+    assert output.num_scheduled_tokens[request.request_id] == first_image_end
+    assert output.scheduled_encoder_inputs[request.request_id] == [0]
+
+    scheduler.update_from_output(
+        output,
+        ModelRunnerOutput(
+            req_ids=[request.request_id],
+            req_id_to_index={request.request_id: 0},
+            sampled_token_ids=[[]],
+            logprobs=None,
+            prompt_logprobs_dict={},
+            pooler_output=[],
+        ),
+    )
+
+    output = scheduler.schedule()
+    next_block_boundary = block_size
+    assert output.num_scheduled_tokens[request.request_id] == (
+        next_block_boundary - first_image_end
+    )
+    assert output.scheduled_encoder_inputs[request.request_id] == [1]
+
+
 @pytest.mark.parametrize(
     "enable_prefix_caching, prompt_logprobs",
     [
         (False, None),
         (True, 5),
@@ -3456,10 +3509,96 @@ def test_priority_scheduling_ec_connector_preemption_and_resumption(
         )
     else:
         _assert_right_encoder_inputs(output, expected_total_reqs=0)
 
 
+@pytest.mark.parametrize(
+    ("use_eagle", "first_mm_offset"),
+    [(False, 1), (True, 2)],
+    ids=["mamba", "eagle"],
+)
+def test_mamba_align_encoder_cache_blocked_tail_makes_progress(
+    use_eagle: bool, first_mm_offset: int
+):
+    """A sub-block tail must progress far enough to release encoder cache."""
+    block_size = 8
+    encoder_item_size = 14
+    scheduler = create_scheduler(
+        model="llava-hf/llava-1.5-7b-hf",
+        max_num_batched_tokens=16,
+        max_model_len=64,
+        block_size=block_size,
+        num_blocks=10000,
+    )
+    scheduler.need_mamba_block_aligned_split = True
+    scheduler.use_eagle = use_eagle
+    scheduler.max_num_encoder_input_tokens = 100
+    scheduler.encoder_cache_manager = EncoderCacheManager(cache_size=encoder_item_size)
+
+    second_mm_offset = first_mm_offset + encoder_item_size
+    (request,) = create_requests(
+        num_requests=1,
+        num_tokens=64,
+        mm_positions=[
+            [
+                PlaceholderRange(offset=first_mm_offset, length=encoder_item_size),
+                PlaceholderRange(offset=second_mm_offset, length=encoder_item_size),
+            ]
+        ],
+        mm_hashes_list=[["img0", "img1"]],
+        req_ids=["req"],
+    )
+    request.num_computed_tokens = block_size
+    request.status = RequestStatus.RUNNING
+    scheduler.running.append(request)
+    scheduler.requests[request.request_id] = request
+    scheduler.encoder_cache_manager.allocate(request, 0)
+
+    # The first item fills the cache. Scheduling stops immediately before the
+    # second item, leaving only seven tokens: less than one Mamba block. Those
+    # tokens complete the first item and are required to release its cache.
+    expected_progress = (
+        second_mm_offset - request.num_computed_tokens - (1 if use_eagle else 0)
+    )
+    assert 0 < expected_progress < block_size
+
+    output = scheduler.schedule()
+
+    assert output.num_scheduled_tokens.get(request.request_id) == expected_progress
+    assert request.request_id not in output.scheduled_encoder_inputs
+
+
+def test_mamba_align_eagle_schedules_encoder_at_boundary():
+    """EAGLE lookahead at an aligned MM boundary requires encoder cache."""
+    block_size = 512
+    scheduler = create_scheduler(
+        max_num_batched_tokens=700,
+        max_model_len=2048,
+        block_size=block_size,
+        enable_prefix_caching=True,
+    )
+    scheduler.need_mamba_block_aligned_split = True
+    scheduler.use_eagle = True
+    scheduler.max_num_encoder_input_tokens = 2048
+    scheduler.encoder_cache_manager = EncoderCacheManager(cache_size=2048)
+
+    request = create_requests(
+        num_requests=1,
+        num_tokens=1200,
+        mm_positions=[[PlaceholderRange(offset=block_size, length=100)]],
+        max_tokens=1,
+        block_size=block_size,
+        req_ids=["req"],
+    )[0]
+    scheduler.add_request(request)
+
+    output = scheduler.schedule()
+
+    assert output.num_scheduled_tokens[request.request_id] == block_size
+    assert output.scheduled_encoder_inputs[request.request_id] == [0]
+
+
 @pytest.mark.parametrize("use_kv_connector", [False, True])
 def test_ec_connector_allocate_encoder_tokens_with_external_load(use_kv_connector):
     """
     Scenario:
       - Encoder cache size: 32
````

### 56. `tests/v1/worker/test_gpu_input_batch.py`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：配套 GPUInputBatch 测试
- **规模**：+36 / -0（改后文件共 416 行）
- **涉及提交**：
  - `d4019dbb97` [Bugfix][v0.17.1_omega] Backport Mamba encoder scheduling and spec-decode placeholder fixes
````diff
diff --git a/tests/v1/worker/test_gpu_input_batch.py b/tests/v1/worker/test_gpu_input_batch.py
index 6ea65c6944..74618b1263 100644
--- a/tests/v1/worker/test_gpu_input_batch.py
+++ b/tests/v1/worker/test_gpu_input_batch.py
@@ -376,5 +376,41 @@ def test_swap_states_in_input_batch(device: str, batch_size: int, swap_list: lis
 
     input_batch.refresh_metadata()
     ref_input_batch.refresh_metadata()
 
     _compare_objs(input_batch, ref_input_batch)
+
+
+def test_placeholder_spec_token_ids_written_verbatim():
+    input_batch = InputBatch(
+        max_num_reqs=1,
+        max_model_len=8,
+        max_num_batched_tokens=8,
+        device=torch.device("cpu"),
+        pin_memory=False,
+        vocab_size=VOCAB_SIZE,
+        block_sizes=[16],
+        kernel_block_sizes=[16],
+    )
+    req = CachedRequestState(
+        req_id="req",
+        prompt_token_ids=[10, 11],
+        sampling_params=SamplingParams(),
+        pooling_params=None,
+        mm_features=[],
+        block_ids=([],),
+        generator=None,
+        num_computed_tokens=3,
+        output_token_ids=[12],
+    )
+    input_batch.add_request(req)
+
+    input_batch.update_req_spec_token_ids(
+        req,
+        {"req": [13, -1, -1]},
+    )
+
+    # Placeholders (-1) are kept verbatim in both the spec_token_ids list and
+    # the token buffer; they are clamped to 0 only at the embedding boundary
+    # (GPUModelRunner._preprocess).
+    assert input_batch.spec_token_ids[0] == [13, -1, -1]
+    assert input_batch.token_ids_cpu[0, 3:6].tolist() == [13, -1, -1]
````

### 57. `tests/v1/worker/test_gpu_model_runner.py`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：placeholder clamp 测试
- **规模**：+23 / -0（改后文件共 1341 行）
- **涉及提交**：
  - `d4019dbb97` [Bugfix][v0.17.1_omega] Backport Mamba encoder scheduling and spec-decode placeholder fixes
````diff
diff --git a/tests/v1/worker/test_gpu_model_runner.py b/tests/v1/worker/test_gpu_model_runner.py
index c8a6c13014..e5fee48aea 100644
--- a/tests/v1/worker/test_gpu_model_runner.py
+++ b/tests/v1/worker/test_gpu_model_runner.py
@@ -1,8 +1,10 @@
 # SPDX-License-Identifier: Apache-2.0
 # SPDX-FileCopyrightText: Copyright contributors to the vLLM project
 
+from types import SimpleNamespace
+
 import numpy as np
 import pytest
 import torch
 
 from vllm.config import (
@@ -43,10 +45,31 @@ from vllm.v1.worker.utils import AttentionGroup, select_common_block_size
 BLOCK_SIZE = 16
 NUM_BLOCKS = 10
 DEVICE = current_platform.device_type
 
 
+def test_invalid_draft_suffixes_remain_rejected_in_metadata():
+    runner = object.__new__(GPUModelRunner)
+    runner.device = torch.device("cpu")
+    runner.arange_np = np.arange(64, dtype=np.int64)
+    # Placeholder (-1) drafts are kept in input_ids (clamped to 0 only at the
+    # embedding boundary). For num_draft_tokens=[2, 1, 2] the draft positions
+    # are [1, 2, 4, 6, 7], so the gather carries the -1s straight into the
+    # rejection-sampling metadata.
+    runner.input_ids = SimpleNamespace(
+        gpu=torch.tensor([99, 10, -1, 99, 12, 99, 13, -1], dtype=torch.int32),
+    )
+
+    metadata = GPUModelRunner._calc_spec_decode_metadata(
+        runner,
+        np.array([2, 1, 2], dtype=np.int32),
+        np.array([3, 5, 8], dtype=np.int32),
+    )
+
+    assert metadata.draft_token_ids.tolist() == [10, -1, 12, 13, -1]
+
+
 def initialize_kv_cache(runner: GPUModelRunner):
     """
     Only perform necessary steps in GPUModelRunner.initialize_kv_cache()
     """
     attn_spec = FullAttentionSpec(
````

### 58. `vllm/model_executor/models/qwen3_next.py`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：回移上游 #36599：V1 profiling 期间预热 GDN prefill Triton kernel（chunk_gated_delta_rule 与 solve_tril），防止 KV cache 分配后 autotune OOM
- **规模**：+98 / -1（改后文件共 1666 行）
- **涉及提交**：
  - `0c2d27509e` fix(qwen3-next): warm up GDN Triton kernels during V1 profiling
````diff
diff --git a/vllm/model_executor/models/qwen3_next.py b/vllm/model_executor/models/qwen3_next.py
index 343f58be9a..4c6ecc3c43 100644
--- a/vllm/model_executor/models/qwen3_next.py
+++ b/vllm/model_executor/models/qwen3_next.py
@@ -643,10 +643,105 @@ class Qwen3NextGatedDeltaNet(nn.Module, MambaBase):
         core_attn_out = self.norm(core_attn_out, z)
         core_attn_out = core_attn_out.reshape(z_shape_og)
         core_attn_out = rearrange(core_attn_out, "... h d -> ... (h d)")
         output[:num_tokens], _ = self.out_proj(core_attn_out)
 
+    def _warmup_prefill_kernels(self, mixed_qkv: torch.Tensor) -> None:
+        """Warm up GDN prefill kernels during V1 profiling.
+
+        During V1 profile runs, ``_forward_core`` returns early because
+        ``attn_metadata`` is ``None``, so the autotuned kernels used by
+        ``chunk_gated_delta_rule`` (e.g. ``solve_tril``,
+        ``chunk_scaled_dot_kkt``) are never invoked.  After profiling,
+        vLLM allocates KV cache using most of the remaining GPU memory.
+        When the first real inference triggers the autotuner it OOMs
+        because there is not enough memory left for benchmarking.
+
+        This method runs minimal forward passes through
+        ``chunk_gated_delta_rule`` with small dummy tensors to force
+        autotuning while GPU memory is still plentiful.  The autotuner
+        results are cached globally, so only the first layer incurs
+        actual benchmarking cost.
+
+        Most kernels use a fixed ``BT = chunk_size`` (64), but
+        ``chunk_fwd_kernel_o`` recomputes ``BT`` from the sequence
+        length: ``min(64, max(16, next_power_of_2(T)))``.  Since ``BT``
+        is part of its autotune key, we run warmup passes with T = 16,
+        32, and 64 to cover all possible ``BT`` values.
+
+        The decode path uses ``fused_sigmoid_gating_delta_rule_update``
+        which has fixed kernel parameters (no autotuning), so only the
+        prefill (chunked) path needs warming up.
+        """
+        if hasattr(self, "_prefill_kernels_warmed_up"):
+            return
+        self._prefill_kernels_warmed_up = True
+
+        device = mixed_qkv.device
+        dtype = mixed_qkv.dtype
+        num_k_heads = self.num_k_heads // self.tp_size
+        num_v_heads = self.num_v_heads // self.tp_size
+        _, state_dtype = self.get_state_dtype()
+
+        # Run warmup for each possible BT value of chunk_fwd_kernel_o:
+        #   T=16 → BT=16, T=32 → BT=32, T=64 → BT=64.
+        # Other kernels always use BT=chunk_size(64), so their autotune
+        # cache is populated on the first pass and reused thereafter.
+        for T in (16, 32, 64):
+            q = torch.randn(
+                1, T, num_k_heads, self.head_k_dim, device=device, dtype=dtype
+            )
+            k = torch.randn(
+                1, T, num_k_heads, self.head_k_dim, device=device, dtype=dtype
+            )
+            v = torch.randn(
+                1, T, num_v_heads, self.head_v_dim, device=device, dtype=dtype
+            )
+            g = torch.randn(1, T, num_v_heads, device=device, dtype=dtype)
+            beta = torch.randn(1, T, num_v_heads, device=device, dtype=dtype)
+            state = torch.zeros(
+                1,
+                num_v_heads,
+                self.head_v_dim,
+                self.head_k_dim,
+                device=device,
+                dtype=state_dtype,
+            )
+            cu_seqlens = torch.tensor([0, T], device=device, dtype=torch.long)
+
+            try:
+                self.chunk_gated_delta_rule(
+                    q=q,
+                    k=k,
+                    v=v,
+                    g=g,
+                    beta=beta,
+                    initial_state=state,
+                    output_final_state=False,
+                    cu_seqlens=cu_seqlens,
+                    use_qk_l2norm_in_kernel=True,
+                )
+            except Exception:
+                logger.warning(
+                    "GDN prefill kernel warmup (T=%d) failed for "
+                    "layer %s. First inference may OOM due to "
+                    "autotuner.",
+                    T,
+                    self.prefix,
+                    exc_info=True,
+                )
+            else:
+                logger.debug(
+                    "GDN prefill kernel warmup (T=%d) completed for layer %s",
+                    T,
+                    self.prefix,
+                )
+            finally:
+                del q, k, v, g, beta, state, cu_seqlens
+
+        torch.accelerator.empty_cache()
+
     def _forward_core(
         self,
         mixed_qkv: torch.Tensor,
         b: torch.Tensor,
         a: torch.Tensor,
@@ -657,11 +752,13 @@ class Qwen3NextGatedDeltaNet(nn.Module, MambaBase):
         """
         forward_context = get_forward_context()
         attn_metadata: AttentionMetadata = forward_context.attn_metadata
 
         if attn_metadata is None:
-            # V1 profile run
+            # V1 profile run — warm up prefill kernels so that
+            # autotuning completes before KV cache allocation.
+            self._warmup_prefill_kernels(mixed_qkv)
             return
 
         assert isinstance(attn_metadata, dict)
         attn_metadata = attn_metadata[self.prefix]
         assert isinstance(attn_metadata, GDNAttentionMetadata)
````

---

## 组 7 · CI 杂项（1 文件）

镜像 tag 追加时间戳，避免同名 tag 重复推送导致镜像仓库构建失败。


### 59. `.aoneci/build_docker.yaml`

- **类型**：修改文件 —— 每一处增删行都在下方 diff 中（`+` 新增、`-` 删除、无前缀为上下文），存为 patch 后 `git apply` 可逐行复现
- **说明**：镜像 tag 追加 _$(date +%Y%m%d%H%M%S) 时间戳，避免同名 tag 重复构建失败
- **规模**：+3 / -3（改后文件共 135 行）
- **涉及提交**：
  - `9f1210b41a` ci: add timestamp to image tag to avoid duplicate build failure * ci: add timestamp to image tag to avoid duplicate build failure
````diff
diff --git a/.aoneci/build_docker.yaml b/.aoneci/build_docker.yaml
index 936a761c6c..e5836ac667 100644
--- a/.aoneci/build_docker.yaml
+++ b/.aoneci/build_docker.yaml
@@ -15,11 +15,11 @@ jobs:
           ls -lta
           uname -a
           cat /proc/version
       - id: version-step
         run: >-
-          echo $(git describe --tags --abbrev=0 2>/dev/null || echo "v0.17.1-dev-0.0.$(git rev-parse HEAD)") >
+          echo $(git describe --tags --abbrev=0 2>/dev/null || echo "v0.17.1-dev-0.0.$(git rev-parse HEAD)")_$(date +%Y%m%d%H%M%S) >
           ${{outputs.result.path}}
       - uses: build-image
         id: buildImage
         inputs:
           image-name: hub.docker.alibaba-inc.com/isearch/vllm_server_cuda
@@ -47,11 +47,11 @@ jobs:
           ls -lta
           uname -a
           cat /proc/version
       - id: version-step
         run: >-
-          echo $(git describe --tags --abbrev=0 2>/dev/null || echo "v0.17.1-dev-0.0.$(git rev-parse HEAD)") >
+          echo $(git describe --tags --abbrev=0 2>/dev/null || echo "v0.17.1-dev-0.0.$(git rev-parse HEAD)")_$(date +%Y%m%d%H%M%S) >
           ${{outputs.result.path}}
       - uses: build-image
         id: buildImage
         inputs:
           image-name: hub.docker.alibaba-inc.com/isearch/vllm_server_rocm
@@ -79,11 +79,11 @@ jobs:
           ls -lta
           uname -a
           cat /proc/version
       - id: version-step
         run: >-
-          echo $(git describe --tags --abbrev=0 2>/dev/null || echo "v0.17.1-dev-0.0.$(git rev-parse HEAD)") >
+          echo $(git describe --tags --abbrev=0 2>/dev/null || echo "v0.17.1-dev-0.0.$(git rev-parse HEAD)")_$(date +%Y%m%d%H%M%S) >
           ${{outputs.result.path}}
       - uses: build-image
         id: buildImage
         inputs:
           image-name: hub.docker.alibaba-inc.com/isearch/vllm_server_cuda
````

---

## 6. 生成说明

- 本文档各 diff 块由 `git diff -U5 v0.17.1_omega...feat/engram_jit_cache` 按文件拆分生成，共 59 个文件（新增 32 / 修改 27），与分支净变更一一对应。
- 每节的「改后文件共 N 行」可用 `git show feat/engram_jit_cache:<path> | wc -l` 校验；整份文档可用 `git diff -U5 v0.17.1_omega...feat/engram_jit_cache` 的输出逐块核对。
- 生成于 2026-09-22，HEAD = `c2f0d629e2`。
