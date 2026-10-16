# Python runtime for the Docker POC

**Checked:** 2026-10-07
**Scope:** Python minor-version choice for the existing Docker services, including the InsightFace CPU worker.

## Recommendation

For this POC, target **standard CPython 3.14** for all service images (`python:3.14-slim`). Python 3.14 is in bug-fix support through October 2030. The current FastAPI stack and selected face-worker packages build for this runtime on the Docker host. The [Docker Official Images index](https://github.com/docker-library/official-images/blob/master/library/python) lists the 3.14 slim variants.

The five Dockerfiles use `python:3.14-slim`. All five images build with the current face-worker dependencies; the core services pass their Compose health checks, and a synthetic model-backed recognition flow is documented in the [face-recognition demo guide](../architecture/face-recognition-demo.md). The latest Docker setup recheck is recorded below.

Use the regular CPython build, not a free-threaded `3.14t` build. The POC does not require free-threading, and a normal `python:3.14-slim` image is the simpler, conventional runtime.

## Support and practical tradeoffs

Python’s current release schedule lists the following branch status and end-of-life dates. These are CPython support dates, not guarantees about third-party package support.

| Version | Current CPython status (2026-10-07) | End of life | Practical assessment for this POC |
| --- | --- | --- | --- |
| 3.11 | Security-only | 2027-10 | Works with the current dependencies and is the version already exercised here, but has about one year of upstream support left. Poor choice for a fresh baseline unless a required model/package needs it. |
| 3.12 | Security-only | 2028-10 | A viable conservative runtime, but has a shorter remaining support window than 3.13 or 3.14 and no clear compatibility advantage for the current stack. |
| 3.13 | Security-only | 2029-10 | Mature, widely supported, and a reasonable fallback if a future native CV dependency fails on 3.14. It has one year less support remaining than 3.14. |
| 3.14 | Bug-fix support | 2030-10 | Best default for a new baseline: longest support horizon here and current ecosystem support for the relevant web and common CV packages. Validate the exact native package set before adopting it. |
| 3.10 | End of life (2026-10-01) | 2026-10 | Do not choose as the fallback: it no longer receives security fixes. |

The Python Developer’s Guide is the source for the support status and dates. Python 3.15 is still a prerelease on the checked date, so it is not a production/POC alternative to the stable branches. ([Python version status](https://devguide.python.org/versions/))

## Why the Dockerfiles used 3.11

Before this update, all five service Dockerfiles started from `python:3.11-slim`. The shared contracts project declares `requires-python = ">=3.10"`; the Dockerfiles therefore chose a narrower runtime than the project’s stated minimum. I found no repository note or ADR explaining that choice, so its original motivation cannot be confirmed from the repo.

Possible reasons for choosing 3.11 include that it was an established baseline and supported the declared dependencies. It also delivered a substantial CPython performance improvement over 3.10: the Python 3.11 release notes report an average 25% speedup in the `pyperformance` suite, while warning that I/O-heavy or C-extension-heavy workloads may see little difference. Those are plausible historical reasons, not a rationale recorded in this repository. They do not make 3.11 preferable to currently supported later branches. ([Python 3.11 release notes](https://docs.python.org/3.14/whatsnew/3.11.html))

## Dependency compatibility checked

The application requirements include FastAPI, Uvicorn with its `standard` extras, Pydantic v2, HTTPX, and `websockets`. The current repository requirements are lower bounds, not a lockfile, so a future image build can resolve newer package releases than the ones used for the original test run. ([Application requirements](../../apps/lounge-control/requirements.txt), [Uvicorn standard extras](https://github.com/Kludex/uvicorn/blob/main/pyproject.toml))

Upstream compatibility signals for normal CPython 3.14 are positive, with a few package-specific caveats:

- FastAPI and Uvicorn currently declare Python 3.14 classifiers; their package metadata requires Python 3.10 or newer. ([FastAPI metadata](https://github.com/fastapi/fastapi/blob/master/pyproject.toml), [Uvicorn metadata](https://github.com/Kludex/uvicorn/blob/main/pyproject.toml))
- Pydantic 2.12.0 announced initial Python 3.14 support. This POC imports Pydantic v2 APIs and does not use the legacy Pydantic v1 namespace. ([Pydantic 2.12.0 release notes](https://pypi.org/project/pydantic/2.12.0/))
- `websockets` 16.0 records that compatibility with Python 3.14 was validated. The current Uvicorn `standard` extra also includes `uvloop`; the current `uvloop` release publishes CPython 3.14 manylinux wheels. ([websockets changelog](https://github.com/python-websockets/websockets/blob/main/docs/project/changelog.rst), [uvloop files](https://pypi.org/project/uvloop/#files))
- For the selected CV layer, current upstream releases publish normal CPython 3.14 Linux wheels for NumPy, OpenCV, and ONNX Runtime on both x86-64 and ARM64. ([NumPy 2.4.4 files](https://pypi.org/project/numpy/2.4.4/#files), [OpenCV 4.14 release](https://github.com/opencv/opencv-python/releases), [OpenCV 4.14.0.94 files](https://pypi.org/project/opencv-python-headless/4.14.0.94/#files), [ONNX Runtime 1.30.0 files](https://pypi.org/project/onnxruntime/1.30.0/#files))

### CV and inference package compatibility

The selected face-worker stack declares NumPy, ONNX, CPU ONNX Runtime, headless OpenCV, SciPy, scikit-image, and related dependencies in `apps/face-worker/requirements.txt`; its Dockerfile installs InsightFace 2.1.0 without dependencies to avoid adding a second OpenCV wheel. MediaPipe remains an unselected alternative. The table records the upstream compatibility evidence used during selection; the current image build and model-backed demo are recorded separately below.

| Package checked | Python 3.14 / Linux ARM64 and x86-64 evidence | Practical notes |
| --- | --- | --- |
| NumPy 2.4.4 | PyPI lists regular `cp314` wheels for both architectures, targeting glibc 2.27/2.28+. | Suitable NumPy baseline for a standard CPython 3.14 Debian slim image. |
| OpenCV `opencv-python-headless` 5.0.0.93 / 4.14.0.94 | Both releases publish `cp37-abi3` manylinux wheels for ARM64 and x86-64. The 4.14 wheels target glibc 2.17+ and include Python 3.14. | The worker pins 4.14 for this POC. an upstream issue reports a `cv2.applyColorMap` output-shape change between 4.x and 5.0. The still-open Python 3.14/NumPy 2.3.3 import report is Windows-specific and traces through a local `W:\cv2\__init__.py`; it is not evidence of a Linux wheel failure. Use headless in a server container unless GUI functions are needed, and install only one OpenCV wheel flavor because each provides `cv2`. ([headless package guidance](https://github.com/opencv/opencv-python), [OpenCV 4.14.0.94 wheels](https://pypi.org/project/opencv-python-headless/4.14.0.94/#files), [OpenCV issue #1201](https://github.com/opencv/opencv-python/issues/1201), [OpenCV 4.x/5 API difference #1263](https://github.com/opencv/opencv-python/issues/1263)) |
| ONNX Runtime CPU 1.30.0 | PyPI lists standard `cp314-cp314` manylinux_2_28 wheels for ARM64 and x86-64 (not only free-threaded `cp314t` wheels). | Good portable inference option for current x86-64 and ARM64 Docker hosts. An upstream issue reports a segfault in ONNX Runtime 1.24.1's own exception test suite on macOS ARM64 with Python 3.14.3; the issue is closed and does not report a Linux application inference failure. The selected stack's build and model-backed synthetic demo are recorded below. Use the CPU package for the POC baseline; the GPU distribution is separate and needs an appropriate CUDA/cuDNN and NVIDIA environment. ([ONNX Runtime 1.30.0 files](https://pypi.org/project/onnxruntime/1.30.0/#files), [install guide](https://onnxruntime.ai/docs/get-started/with-python), [issue #27392](https://github.com/microsoft/onnxruntime/issues/27392)) |
| InsightFace 2.1 | Its PyPI wheel is `py3-none-any`, and package metadata requires Python >=3.10. Its install guide uses ONNX Runtime. | Selected for the current worker. The Dockerfile installs it without dependencies so the image keeps the headless OpenCV wheel. Its pretrained models have separate terms and are identified as non-commercial research models. ([InsightFace package](https://pypi.org/project/insightface/2.1/), [requirements](https://github.com/deepinsight/insightface/blob/master/python-package/setup.py), [runtime guide](https://github.com/deepinsight/insightface/blob/master/python-package/docs/runtime.md)) |
| MediaPipe 1.1.0 | PyPI lists `py3-none` manylinux_2_28 wheels for ARM64 and x86-64 and a Python 3.14 classifier. | Wheel coverage is positive, but the package currently marks this release as Alpha. Treat it as an experiment rather than assuming it's the conservative default. ([MediaPipe 1.1.0 files and metadata](https://pypi.org/project/mediapipe/1.1.0/)) |

For OpenCV, use a current NumPy 2.x pair. Older OpenCV 4.12 wheels constrained NumPy below 2.3; OpenCV 4.14 has current Linux ARM64/x86-64 wheels. The unresolved #1201 report does demonstrate a Python 3.14 / NumPy 2.3.3 import problem on Windows, so it remains a reason to test the exact pairing if Windows becomes a target. It does not show the equivalent failure on Linux. ([OpenCV 4.12 NumPy issue](https://github.com/opencv/opencv-python/issues/1135), [OpenCV #1201](https://github.com/opencv/opencv-python/issues/1201), [OpenCV 4.14 wheels](https://pypi.org/project/opencv-python-headless/4.14.0.94/#files))

The web-framework forum/issue scan did not reveal a blocker for the current stack: a FastAPI/Pydantic report traced to a stale Python 3.14 alpha interpreter rather than the final runtime; an Uvicorn/httptools report's later reproduction matrix succeeded on Python 3.14; and HTTPX's Python 3.14 compatibility fix landed in httpcore 1.0.8. The repository's requirements are unpinned, so the built image must resolve the current fixed versions. ([FastAPI discussion #15819](https://github.com/fastapi/fastapi/discussions/15819), [Uvicorn discussion #3038](https://github.com/Kludex/uvicorn/discussions/3038), [HTTPX issue #3644](https://github.com/encode/httpx/issues/3644))

The dependency research supports Python 3.14 for the selected service and inference packages. The current Docker build validates installation on this host, and the model-backed synthetic demo validates the selected pipeline for its documented fixtures. Neither establishes behavior across all model inputs or target architectures; repeat the build and recognition smoke on each architecture the project intends to support.

## Build and test status

Checked 2026-10-07 on the Docker host's ARM64 platform:

- `docker compose --profile sim build`: all five images built successfully with `python:3.14-slim`, including both simulator images. The build resolved the current unpinned FastAPI/Uvicorn/Pydantic/HTTPX/WebSocket stack to CPython 3.14 ARM64 wheels.
- Repository tests in an ephemeral `python:3.14-slim` container: **34 passed**. Pytest reported a Starlette warning that using HTTPX with `starlette.testclient` is deprecated, plus a cache-write warning because the repository was mounted read-only for the test.
- Core Compose stack with `up --detach --wait`: `mock-hotel`, `face-worker`, and `lounge-control` all became healthy. The default host port 8002 was already occupied, so this smoke run used host ports 18000–18002; service-to-service ports stayed unchanged.
- One-shot `frame-replay`: authenticated over WebSocket, sent one synthetic 635-byte JPEG fixture, and exited successfully.
- Tap simulator in once mode: all four synthetic entry taps were accepted with HTTP 200.
- The test stack's containers and network were removed afterward; the named mock-hotel data volume was retained.

### Docker setup recheck (2026-10-16)

- `docker compose config --quiet` and `docker compose --profile sim config --quiet` both passed. The default profile resolves to the three core services; the `sim` profile adds `tap-simulator` and `frame-replay`.
- `docker compose --profile sim build` built all five images successfully with the current Dockerfiles and requirements.
- The built `face-worker` image contains the allowlisted synthetic fixtures only; local files added to `fixtures/` are excluded by `.dockerignore`.
- The core stack started under a temporary Compose project on host ports 18000–18003 with face recognition disabled. All three health checks passed, as did the lounge roster and dashboard checks. The temporary containers, network, and volumes were removed afterward.
- This recheck did not download InsightFace model weights or exercise model inference; it validates image builds, service startup, health endpoints, and the dashboard path.

The 2026-10-07 dependency notes record wheel and metadata research. The current worker installs OpenCV, ONNX Runtime, and InsightFace in Docker, and the model-backed synthetic run is documented in the face-recognition demo guide. The 2026-10-16 recheck above intentionally disabled recognition, so it did not repeat model download or inference.

## Bottom line

Keep standard Python 3.14 as the Docker baseline: all five current images build with the selected face-worker dependencies, the repository suite and simulator smoke flows passed in the earlier check, and the latest core Compose health checks passed. If a concrete 3.14 incompatibility appears on another target architecture, use 3.13 as the maintained fallback. Python 3.10 is not a safe fallback: it reached end of life on October 1, 2026 and no longer receives security updates. The original 3.11 choice was a sensible stable starting point, but it has a shorter support window than 3.13 or 3.14.
