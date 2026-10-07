# Python runtime for the Docker POC

**Checked:** 2026-10-07
**Scope:** Python minor-version choice for the existing Docker services and the planned computer-vision worker.

## Recommendation

For this POC, target **standard CPython 3.14** for all service images (`python:3.14-slim`). Python 3.14 is in bug-fix support through October 2030, and the current FastAPI stack and plausible computer-vision dependencies publish 3.14 support or Linux wheels. The [Docker Official Images index](https://github.com/docker-library/official-images/blob/master/library/python) lists the 3.14 slim variants.

The five Dockerfiles now use `python:3.14-slim`. All five images built, and the current POC tests and simulator smoke flows passed on the Docker host's ARM64 platform; details are recorded below. This validates the dependencies currently declared by the repo, not the future face-recognition model/library, which has not been selected.

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
- For the planned CV layer, current upstream releases publish normal CPython 3.14 Linux wheels for NumPy, OpenCV, and ONNX Runtime on both x86-64 and ARM64. ([NumPy 2.4.4 files](https://pypi.org/project/numpy/2.4.4/#files), [OpenCV 4.14 release](https://github.com/opencv/opencv-python/releases), [OpenCV 4.14.0.94 files](https://pypi.org/project/opencv-python-headless/4.14.0.94/#files), [ONNX Runtime 1.30.0 files](https://pypi.org/project/onnxruntime/1.30.0/#files))

### CV and inference package compatibility

The repo does not currently declare NumPy, OpenCV, ONNX Runtime, MediaPipe, or a face-recognition library in `apps/face-worker/requirements.txt`. The following is an upstream wheel/metadata check, not a successful installation or runtime test of the repo's future CV stack.

| Package checked | Python 3.14 / Linux ARM64 and x86-64 evidence | Practical notes |
| --- | --- | --- |
| NumPy 2.4.4 | PyPI lists regular `cp314` wheels for both architectures, targeting glibc 2.27/2.28+. | Suitable NumPy baseline for a standard CPython 3.14 Debian slim image. |
| OpenCV `opencv-python-headless` 5.0.0.93 / 4.14.0.94 | Both releases publish `cp37-abi3` manylinux wheels for ARM64 and x86-64. The 4.14 wheels target glibc 2.17+ and include Python 3.14. | Prefer 4.14 for this POC until its model code is selected: an upstream issue reports a `cv2.applyColorMap` output-shape change between 4.x and 5.0. The still-open Python 3.14/NumPy 2.3.3 import report is Windows-specific and traces through a local `W:\cv2\__init__.py`; it is not evidence of a Linux wheel failure. Use headless in a server container unless GUI functions are needed, and install only one OpenCV wheel flavor because each provides `cv2`. ([headless package guidance](https://github.com/opencv/opencv-python), [OpenCV 4.14.0.94 wheels](https://pypi.org/project/opencv-python-headless/4.14.0.94/#files), [OpenCV issue #1201](https://github.com/opencv/opencv-python/issues/1201), [OpenCV 4.x/5 API difference #1263](https://github.com/opencv/opencv-python/issues/1263)) |
| ONNX Runtime CPU 1.30.0 | PyPI lists standard `cp314-cp314` manylinux_2_28 wheels for ARM64 and x86-64 (not only free-threaded `cp314t` wheels). | Good portable inference option for current x86-64 and ARM64 Docker hosts. An upstream issue reports a segfault in ONNX Runtime 1.24.1's own exception test suite on macOS ARM64 with Python 3.14.3; the issue is closed and does not report a Linux application inference failure. Still smoke-test the selected runtime when it is added. Use the CPU package for the POC baseline; the GPU distribution is separate and needs an appropriate CUDA/cuDNN and NVIDIA environment. ([ONNX Runtime 1.30.0 files](https://pypi.org/project/onnxruntime/1.30.0/#files), [install guide](https://onnxruntime.ai/docs/get-started/with-python), [issue #27392](https://github.com/microsoft/onnxruntime/issues/27392)) |
| InsightFace 2.1 | Its PyPI wheel is `py3-none-any`, and package metadata requires Python >=3.10. Its install guide uses ONNX Runtime. | A plausible face-recognition candidate, but validate the complete dependency resolution and model package on the target image. Its upstream requirements include `opencv-python`, which conflicts with choosing the headless distribution if both are installed; use one OpenCV flavor. Its pretrained models have separate terms and are identified as non-commercial research models. ([InsightFace package](https://pypi.org/project/insightface/2.1/), [requirements](https://github.com/deepinsight/insightface/blob/master/python-package/setup.py), [runtime guide](https://github.com/deepinsight/insightface/blob/master/python-package/docs/runtime.md)) |
| MediaPipe 1.1.0 | PyPI lists `py3-none` manylinux_2_28 wheels for ARM64 and x86-64 and a Python 3.14 classifier. | Wheel coverage is positive, but the package currently marks this release as Alpha. Treat it as an experiment rather than assuming it's the conservative default. ([MediaPipe 1.1.0 files and metadata](https://pypi.org/project/mediapipe/1.1.0/)) |

For OpenCV, use a current NumPy 2.x pair. Older OpenCV 4.12 wheels constrained NumPy below 2.3; OpenCV 4.14 has current Linux ARM64/x86-64 wheels. The unresolved #1201 report does demonstrate a Python 3.14 / NumPy 2.3.3 import problem on Windows, so it remains a reason to test the exact pairing if Windows becomes a target. It does not show the equivalent failure on Linux. ([OpenCV 4.12 NumPy issue](https://github.com/opencv/opencv-python/issues/1135), [OpenCV #1201](https://github.com/opencv/opencv-python/issues/1201), [OpenCV 4.14 wheels](https://pypi.org/project/opencv-python-headless/4.14.0.94/#files))

The web-framework forum/issue scan did not reveal a blocker for the current stack: a FastAPI/Pydantic report traced to a stale Python 3.14 alpha interpreter rather than the final runtime; an Uvicorn/httptools report's later reproduction matrix succeeded on Python 3.14; and HTTPX's Python 3.14 compatibility fix landed in httpcore 1.0.8. The repository's requirements are unpinned, so the built image must resolve the current fixed versions. ([FastAPI discussion #15819](https://github.com/fastapi/fastapi/discussions/15819), [Uvicorn discussion #3038](https://github.com/Kludex/uvicorn/discussions/3038), [HTTPX issue #3644](https://github.com/encode/httpx/issues/3644))

These checks support Python 3.14 as a viable target for the current services and a plausible base for the future inference stack. They do not prove every dependency combination, model asset, or runtime provider works. Lock the exact package set after selecting the face pipeline, then build and smoke-test both target architectures if both are deployment requirements.

## Build and test status

Checked 2026-10-07 on the Docker host's ARM64 platform:

- `docker compose --profile sim build`: all five images built successfully with `python:3.14-slim`, including both simulator images. The build resolved the current unpinned FastAPI/Uvicorn/Pydantic/HTTPX/WebSocket stack to CPython 3.14 ARM64 wheels.
- Repository tests in an ephemeral `python:3.14-slim` container: **34 passed**. Pytest reported a Starlette warning that using HTTPX with `starlette.testclient` is deprecated, plus a cache-write warning because the repository was mounted read-only for the test.
- Core Compose stack with `up --detach --wait`: `mock-hotel`, `face-worker`, and `lounge-control` all became healthy. The default host port 8002 was already occupied, so this smoke run used host ports 18000–18002; service-to-service ports stayed unchanged.
- One-shot `frame-replay`: authenticated over WebSocket, sent one synthetic 635-byte JPEG fixture, and exited successfully.
- Tap simulator in once mode: all four synthetic entry taps were accepted with HTTP 200.
- The test stack's containers and network were removed afterward; the named mock-hotel data volume was retained.

These are service/runtime checks only. The CV dependency checks above are wheel and issue-tracker research; OpenCV, ONNX Runtime, and a face-recognition package are not currently in the repository requirements and were not installed or runtime-tested here.

## Bottom line

Keep standard Python 3.14 as the Docker baseline: all five current images built, the repository suite passed, and the Compose health and simulator smoke flows passed. If the eventual face/CV dependency set has a concrete 3.14 incompatibility, use 3.13 as the maintained fallback. Python 3.10 is not a safe fallback: it reached end of life on October 1, 2026 and no longer receives security updates. The original 3.11 choice was a sensible stable starting point, but it has a shorter support window than 3.13 or 3.14.
