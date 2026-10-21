# Native M1 inference for the lounge POC

**Checked:** 2026-10-20
**Status:** Implemented and locally benchmarked; Docker remains the default deployment.

## Recommendation

Keep Docker Compose as the portable baseline for the team. On the M1 Mac, use the opt-in hybrid setup when faster local inference is useful: `lounge-control` and `mock-hotel` stay in Docker, while `face-worker` runs natively on macOS with ONNX Runtime Core ML. The native option uses a separate Python environment, model cache, and ports; it does not change the normal Compose path.

This split is useful because the Docker Linux container cannot load Apple's Core ML framework. The native worker can, and it can still use ONNX Runtime's CPU provider when a graph operation falls back. ONNX Runtime documents `CPUAndGPU`, `CPUAndNeuralEngine`, and `ALL` compute-unit choices, with placement depending on the model and supported operations ([Core ML provider options](https://onnxruntime.ai/docs/execution-providers/CoreML-ExecutionProvider.html)).

## What changed

- Added `FACE_EXECUTION_PROVIDER=cpu|coreml|auto`. Docker defaults to `cpu`; the native launcher defaults to `coreml` with `CPUAndGPU` and CPU fallback.
- Added actual per-model session-provider reporting, provider availability, Core ML compute units, model initialization time, service startup time, and whether model files were warm at startup to `/health` and worker logs.
- Added a Compose overlay that leaves only `lounge-control` and `mock-hotel` in Docker and directs the former to the native worker through `host.docker.internal`.
- Added an ARM64 native setup script, worker launcher, sanitized benchmark tool, and comparison tool. The benchmark writes counts and timings plus input hashes; it discards image bytes, crops, names, candidate IDs, and embeddings.
- Kept the standard `compose.yaml` and CPU worker as the default for Windows, Linux, CI, and ordinary development.

The explicit provider list must survive InsightFace model preparation. `InsightFaceAnalysis.prepare(ctx_id=-1)` resets model sessions to CPU; the worker now uses `ctx_id=0` while explicitly configuring CPU mode for Docker. Core ML mode fails at startup if the runtime lacks `CoreMLExecutionProvider`.

## M1 test setup

The native environment used macOS 26.6.2 on ARM64, Python 3.14.2, ONNX Runtime 1.30.0, and the repository's `buffalo_l` detector/recognizer. Docker ran the same model with CPU ONNX Runtime. The checked-in scripts and exact commands are in the [M1 README section](../../README.md#optional-run-the-face-worker-natively-on-an-m1-mac).

The Core ML compute plan for these two graphs had 137 profiled entries. With `CPUAndGPU`, the plan assigned those entries to Core ML GPU. With `CPUAndNeuralEngine`, it assigned them to Core ML CPU, with no Neural Engine entries. This is an observation from this M1, ONNX Runtime build, model, and input shape; it is not a general rule that `CPUAndGPU` is always faster.

### Direct inference: native CPU vs native Core ML

Both modes used the same synthetic two-face frame and two reference photos in separate processes. Both detected and matched two faces. The largest detected-box difference was about 0.00006 pixels, with detector-score differences around 1e-7.

| Native provider | Warm worker detect p50 | Warm worker detect p95 |
| --- | ---: | ---: |
| CPU | 595 ms | 886 ms |
| Core ML `CPUAndGPU` | 90 ms | 117 ms |

### End-to-end stream: Docker CPU vs native Core ML

Both benchmark runs sent the same 10 synthetic frames at 0.5-second intervals through the lounge-control WebSocket. Comparison found 100% face-count agreement and 100% raw candidate-match-count agreement on the five frames both workers returned. This benchmark does not compare stable identity snapshots returned to a client and does not measure recognition accuracy.

| Result | Docker CPU | Native Core ML hybrid |
| --- | ---: | ---: |
| Frames returned | 5/10 | 10/10 |
| Stale frames dropped | 5 | 0 |
| Worker detect p50 | 941 ms | 87 ms |
| Worker detect p95 | 1,930 ms | 100 ms |
| Client capture-to-result p50 | 1,342 ms | 167 ms |
| Client capture-to-result p95 | 2,219 ms | 194 ms |
| Delivered throughput | 0.81 fps | 2.01 fps |

This short run shows the Docker CPU worker could not keep up with a 2 fps send cadence on this synthetic two-face fixture, while native Core ML did in this run. The Docker model volume was cold and its approximately 27.9-second initialization included downloading the model; native inference used a warm model cache and initialized in approximately 4.25 seconds. Those startup times are not an apples-to-apples comparison. Compare warm inference separately from model download and Core ML compilation.

## Limits and next steps

- This was a 10-frame synthetic POC benchmark on one M1 MacBook Air, not a sustained thermal test, a camera test, or a recognition-accuracy evaluation on representative guests.
- The 100% match agreement is only over five common returned frames from the synthetic sample. It does not validate false accept/reject rates or resolve threshold quality.
- Run a longer stream at the intended phone sampling rate and inspect queue age/drop counters before deciding on operational cadence. Keep the latest-frame drop behavior so the worker does not process stale backlogs.
- Use the Docker setup for friends' Windows laptops with GPUs; this M1 Core ML path is macOS-specific. If a Windows GPU benchmark is needed later, add a separate CUDA/TensorRT-compatible runtime rather than trying to pass the Mac GPU into Docker.
- Keep guest templates in worker memory for the POC. This experiment does not justify adding a vector database; consider persistence only when restart recovery, multi-worker replication, or larger cohorts require it.

## Primary references

- [ONNX Runtime Core ML Execution Provider](https://onnxruntime.ai/docs/execution-providers/CoreML-ExecutionProvider.html)
- [ONNX Runtime execution provider ordering](https://onnxruntime.ai/docs/execution-providers/)
- [Apple Core ML overview](https://developer.apple.com/documentation/coreml/)
- [InsightFace 2.1 runtime guide](https://github.com/deepinsight/insightface/blob/master/python-package/docs/runtime.md)
- [Docker Desktop networking](https://docs.docker.com/desktop/features/networking/networking-how-tos/)
- [Local model notes](../../apps/face-worker/MODELS.md)
