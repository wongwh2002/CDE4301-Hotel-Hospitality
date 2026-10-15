# ONNX Runtime CoreML on Docker Desktop for Apple Silicon

**Checked:** 2026-10-10
**Scope:** ONNX Runtime's CoreML Execution Provider (EP) on an Apple Silicon Mac, compared across a macOS host process and Docker Desktop Linux containers. Also assesses the proposed local hybrid path where Docker services call a native macOS `face-worker`. This is documentation research, not a performance benchmark or an adopted architecture decision.

## Findings

**A standard Docker Desktop Linux container cannot use ONNX Runtime's CoreML EP.** ONNX Runtime documents CoreML EP requirements for iOS 13+ and macOS 10.15+ and says its official macOS Python wheels include CoreML support. A custom/local ONNX Runtime build must be built on a Mac with `--use_coreml`. Docker Desktop for Mac runs the Docker daemon and Linux containers in a lightweight Linux VM. The conclusion that CoreML is unavailable *inside that Linux container* follows from those OS requirements: an `arm64` Linux image is still Linux and does not gain the macOS CoreML framework from the Mac host. ([ONNX Runtime CoreML EP](https://onnxruntime.ai/docs/execution-providers/CoreML-ExecutionProvider.html), [Docker Desktop Mac permissions and Linux VM](https://docs.docker.com/desktop/setup/install/mac-permission-requirements/))

The local Docker image check agrees with the documentation: its runtime reported `Linux aarch64`, ONNX Runtime `1.30.0`, and only `AzureExecutionProvider` plus `CPUExecutionProvider`; `CoreMLExecutionProvider` was absent. I then explicitly requested `CoreMLExecutionProvider` for a tiny ONNX identity model in a disposable container. ONNX Runtime warned that CoreML was not an available provider, created the session with `CPUExecutionProvider`, and returned the correct identity output on CPU. This confirms the behavior of that tested image and version, not every custom image someone could build.

**Running the worker natively on macOS is supported and the Docker-to-host network path is documented.** The official macOS ONNX Runtime wheel includes the CoreML EP, and Docker Desktop documents `host.docker.internal` as the address containers use to reach a service on the host. Docker Desktop also documents reaching a container from the Mac through its published `localhost` port. ([ONNX Runtime CoreML EP](https://onnxruntime.ai/docs/execution-providers/CoreML-ExecutionProvider.html), [Docker Desktop networking how-tos](https://docs.docker.com/desktop/features/networking/networking-how-tos/))

This makes the proposed hybrid path technically viable for a local Mac development setup: keep `lounge-control` and `mock-hotel` in Compose, run the ONNX Runtime/CoreML `face-worker` as a native macOS service, and configure the container's worker URL as `http://host.docker.internal:<port>`. For the existing callback direction, the native worker can reach a Compose service through that service's published host port, for example `http://127.0.0.1:<published-port>`. The actual worker binding, firewall rules, and request/response contract still need a device-independent spike.

CoreML acceleration is not a performance guarantee for a selected model. ONNX Runtime requires explicitly registering the EP, documents a finite supported-operator set, and exposes compute-unit options for CPU, GPU, and Neural Engine. Its documentation also cautions that selecting ANE-capable CoreML behavior does not guarantee that the whole model executes on the ANE. Verify provider availability, graph placement, correctness, and latency with the selected detector and recognition models. ([ONNX Runtime CoreML EP](https://onnxruntime.ai/docs/execution-providers/CoreML-ExecutionProvider.html))

## Architecture implications for this POC

- Keep CPU ONNX Runtime inside Linux containers as the portable baseline for Apple Silicon, Linux ARM64, and x86-64 hosts. Treat the native macOS/CoreML worker as an optional local profile; it cannot be shipped as the same Linux container image.
- Set the `lounge-control` worker base URL through configuration. Use the Compose service name for the all-container path, and `host.docker.internal:<port>` only for the Docker Desktop + native-worker path.
- Preserve the current callback contract. Publish the relevant `lounge-control` port on the Mac so the native worker can post results back through `localhost:<host-port>`; test both directions, since the container-to-host alias does not itself configure host-to-container callbacks.
- Make the host worker listen on an address reachable from Docker Desktop, and restrict access with an authentication token and macOS firewall policy. Avoid exposing the inference endpoint to the lounge LAN just to make the local bridge work.
- Compare end-to-end results, not just model inference time: container-to-host image transfer, serialization, CoreML model/session startup, warm inference, callback time, and cue rendering all contribute to capture-to-cue latency. Keep the proposal's transient-frame and no-persistence behavior in either deployment mode.

Docker's documented `--gpus` pass-through to Linux containers is specifically for Docker Desktop on Windows with WSL 2; I found no official Docker Desktop for Mac path that passes CoreML.framework into an ordinary Linux container. This is supporting evidence for the boundary above, not a claim that no custom or future Docker feature could ever add other acceleration. ([Docker Desktop GPU support](https://docs.docker.com/desktop/features/gpu/))

## Windows laptop GPU path

Docker remains useful on Windows, but GPU acceleration depends on the GPU vendor and execution provider:

- **NVIDIA GPU:** Docker Desktop for Windows documents GPU-PV for Linux containers with the WSL 2 backend. It requires a supported NVIDIA GPU and current NVIDIA/Windows/WSL drivers. ONNX Runtime's CUDA EP is the matching ONNX path. The image needs the GPU-enabled ONNX Runtime package and compatible CUDA/cuDNN libraries; requesting the GPU in Compose alone does not install or select those. Compose supports reserving GPU devices (for example, `gpus: all` on supported Compose versions or a `deploy.resources.reservations.devices` entry). ([Docker GPU support](https://docs.docker.com/desktop/features/gpu/), [ONNX Runtime CUDA EP](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html), [Compose GPU support](https://docs.docker.com/compose/how-tos/gpu-support/))
- **AMD or Intel GPU:** Docker Desktop's documented `--gpus` path is NVIDIA GPU-PV, so it does not establish a supported GPU passthrough path for these adapters into Linux containers. ONNX Runtime's DirectML EP targets Windows and DirectX 12 hardware, including many NVIDIA, AMD, and Intel GPUs; ONNX Runtime now describes DirectML as sustained engineering and recommends WinML for new Windows deployments. That means use a Windows-native worker for this route, or use CPU inference in the Linux container. ([Docker GPU support](https://docs.docker.com/desktop/features/gpu/), [ONNX Runtime DirectML EP](https://onnxruntime.ai/docs/execution-providers/DirectML-ExecutionProvider.html), [ONNX Runtime Windows install guide](https://onnxruntime.ai/docs/get-started/with-windows.html))

For this repo, retain a CPU-only Compose default for the M1 Mac and generic laptops. Add a separate NVIDIA GPU image/Compose override for Windows users with NVIDIA hardware, using `onnxruntime-gpu` and CUDA-compatible libraries; configure the worker to select `CUDAExecutionProvider`. Do not put `gpus: all` in the default Compose service if the same file must start on Macs and non-NVIDIA machines. The current `vision.py` explicitly requests `CPUExecutionProvider`, and the current requirements install the CPU package `onnxruntime`, so neither CoreML nor CUDA can be enabled just by changing the Compose device setting.

## Validation steps

1. On the Apple Silicon Mac host, install the official macOS `onnxruntime` wheel in a native Python environment. Record `platform.platform()`, `ort.__version__`, and `ort.get_available_providers()`; confirm `CoreMLExecutionProvider` is listed. If it is absent, check that Python is running natively on macOS and that the package/build includes CoreML.
2. Create a session for each selected ONNX model with CoreML explicitly registered, then run a separate CPU-only comparison on the same fixtures. Check output parity. Enable ONNX Runtime's CoreML `ProfileComputePlan` option (`1`) or equivalent platform profiling to confirm which hardware handles operators; do not treat provider registration alone as proof of ANE execution.
3. Start the native worker on a configured port. From the actual `lounge-control` container, resolve `host.docker.internal` and call the worker's health endpoint and one synthetic enrollment/frame request. Confirm that the worker is reachable through the host binding and that an unavailable worker produces a bounded, visible error rather than a stale cue.
4. Publish `lounge-control` on a host port and send one synthetic match callback from the native worker to `http://127.0.0.1:<published-port>`. This verifies the reverse leg and the callback contract.
5. Run the complete synthetic or consented-frame flow in both layouts: all-container CPU inference and native macOS/CoreML inference. Record cold-start and warm p50/p95 inference and capture-to-cue latency, throughput, frame drops, output parity, CPU/GPU/ANE placement where observable, and behavior after worker/container restart. Use the same model, input size, fixtures, and workload for both runs.
6. On a supported Windows/NVIDIA laptop, validate Docker Desktop's WSL 2 GPU support with Docker's published GPU smoke command, then check `ort.get_available_providers()` and run a model session requested with `CUDAExecutionProvider`. A working `nvidia-smi`/CUDA sample alone does not prove the face model is using the GPU.

## Limits and unresolved points

- The sources establish platform support and network routing, not that a particular ONNX model is CoreML-compatible or faster on the target Mac. CoreML operator support and model graph placement can vary.
- Docker Desktop's `host.docker.internal` behavior is documented for Docker Desktop. The native-host URL should be a local configuration value; do not assume it applies to a remote Linux Docker Engine or deployment machine.
- Docker Desktop forwards networking through its backend, and local firewall/VPN/network settings can still affect access. Verify on the exact Mac, Docker Desktop version, and Compose setup used for the POC.
- The current smart-glasses architecture remains a proposal. This research supports an optional Mac-host inference experiment; it does not change the selected deployment shape or validate RV101 camera streaming.

## Primary sources

- [ONNX Runtime CoreML Execution Provider](https://onnxruntime.ai/docs/execution-providers/CoreML-ExecutionProvider.html)
- [ONNX Runtime build options for execution providers](https://onnxruntime.ai/docs/build/eps.html)
- [Docker Desktop for Mac permission requirements](https://docs.docker.com/desktop/setup/install/mac-permission-requirements/)
- [Docker Desktop networking overview](https://docs.docker.com/desktop/features/networking/)
- [Docker Desktop networking how-tos](https://docs.docker.com/desktop/features/networking/networking-how-tos/)
- [Docker Desktop GPU support](https://docs.docker.com/desktop/features/gpu/)
- [Docker Compose GPU support](https://docs.docker.com/compose/how-tos/gpu-support/)
- [ONNX Runtime CUDA Execution Provider](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html)
- [ONNX Runtime DirectML Execution Provider](https://onnxruntime.ai/docs/execution-providers/DirectML-ExecutionProvider.html)
- [ONNX Runtime Windows install guide / WinML](https://onnxruntime.ai/docs/get-started/with-windows.html)
- [Apple Core ML documentation](https://developer.apple.com/documentation/coreml/)
