# Recognition latency benchmark — 2 November 2026

The repeatable photo test ran on the physical RG_glasses/RV101 over USB control.
Recognition requests used Wi-Fi directly to the laptop, without `adb reverse`.
The wearer selected a photo benchmark before attempting a live camera test.

## Measured results

One untimed-from-summary first probe followed by 15 serial warm probes per mode.
Each probe used the existing 800×800 `server/faces/Neha.jpg` (67,118-byte JPEG)
and the five current reference identities. These are self-reference recognition
checks, **not an accuracy evaluation**. Percentile uses nearest rank; with only
15 samples the reported p95 equals the maximum, and is not a robust tail estimate.

| Recognition path | Mean | Median | Observed p95 | Range |
| --- | ---: | ---: | ---: | ---: |
| Glasses → Wi-Fi → laptop → glasses response parsed | 1,350.6 ms | 1,311.6 ms | 1,513.7 ms | 1,220.1–1,513.7 ms |
| Entire photo recognition on glasses, offline | 1,927.9 ms | 1,896.0 ms | 2,379.7 ms | 1,848.6–2,379.7 ms |

Local recognition was about 43% slower on average in this test. All samples
produced an accepted identity. The initial offline smoke run also passed, but
the table uses the subsequent run with **the face server stopped and glasses
Wi-Fi disabled**. Server health was verified unreachable during that run.
Wi-Fi and the previously running face server were restored afterward.

Mean stage timings:

| Stage | Time |
| --- | ---: |
| Server reported inference | 998.8 ms |
| Server request total minus reported inference | 351.8 ms |
| Local JPEG decode | 20.1 ms |
| Local preprocessing, SCRFD inference, decoding and NMS | 1,268.7 ms |
| Local alignment, ArcFace inference and gallery matching | 639.1 ms |

The 351.8 ms residual includes upload/download, HTTP and endpoint overhead,
image processing outside the reported inference timer, and client JSON parsing.
It is **not a pure network RTT measurement**.

Local session construction took 797.5 ms. Building the five reference embeddings
locally took another 9,844.3 ms. These startup costs are excluded from warm
samples. The first probe after enrollment took 1,897.2 ms; enrollment had already
exercised both models, so that is not cold inference. Embeddings stayed in memory.

An in-run `dumpsys meminfo` observation showed 424,225 KiB total PSS (~414 MiB)
and 483,480 KiB RSS (~472 MiB). This is a single process observation including
instrumentation, not a measured peak or an incremental model-memory estimate.
The device reports 1,816,600 KiB RAM, arm64-v8a, Qualcomm platform `neo`.
Thermal zone 0 rose from 37.7°C before testing to 46.2°C during the offline run;
the sensor's physical location is unverified. Battery drain and sustained thermal
throttling were not measured.

## Scope and implementation

Both paths use the existing FP32 `buffalo_l` SCRFD-10GF detector at 640×640 and
ResNet50 ArcFace model at 112×112, CPU execution, threshold 0.50, margin 0.10.
Local ONNX Runtime Android is 1.30.0 with four intra-op threads and one inter-op
thread. The laptop is an Intel Core i9-12900H and runs the existing Python server.
No NNAPI, GPU, quantization, or smaller replacement model was tested.

The Kotlin benchmark implements SCRFD preprocessing/output decoding/NMS,
five-landmark similarity alignment, RGB/NCHW normalization, ArcFace inference,
and normalized cosine matching. Android bitmap resizing/alignment can differ
slightly from Python/OpenCV; passing this reference check does not establish
numerical equivalence across arbitrary images.

ONNX Runtime is an **androidTest-only dependency**, following its official
[Java/Android runtime support](https://onnxruntime.ai/docs/get-started/with-java).
The production app still uses server recognition. This experiment does not add
an offline mode to the wearer-facing app.

**Full camera-capture-to-visible-name latency remains unmeasured.** These tests
start from an in-memory JPEG and end with a parsed/accepted recognition result.
They exclude camera startup/exposure, CameraX frame delivery, ML Kit tracking,
focus gating, camera crop/JPEG encoding, the app's two-second request cadence,
track association, UI scheduling, and display presentation. A live measurement
must instrument those boundaries and count rejected/stale results separately.
The current app rejects identity responses older than two seconds, so some
observed offline samples would exceed that limit even before camera/UI costs.

## Repeating the benchmark

Build and install `:app:assembleDebug` and `:app:assembleDebugAndroidTest`.
The benchmark is explicitly opt-in and skips during ordinary instrumented tests.
Place the following existing files inside the debuggable app's private
`files/latency/` directory using `adb push` to a staging directory and
`adb shell run-as com.example.rokid_app` to copy them into private storage:

- `probe.jpg`: the selected reference JPEG (default expected identity `Neha`).
- `gallery/`: the current five reference JPG/PNG files.
- `det_10g.onnx` and `w600k_r50.onnx`: existing buffalo_l weights.

Stop the foreground app before starting instrumentation. Run server mode while
the normal server is available over Wi-Fi:

```powershell
adb shell am force-stop com.example.rokid_app
adb shell am instrument -w -r -e class com.example.rokid_app.LocalModelLatencyTest -e benchmark true -e mode server -e samples 15 com.example.rokid_app.test/androidx.test.runner.AndroidJUnitRunner
```

For the offline condition, stop the face server, disable Wi-Fi through USB ADB,
verify no route/health endpoint, then run:

```powershell
adb shell svc wifi disable
adb shell am instrument -w -r -e class com.example.rokid_app.LocalModelLatencyTest -e benchmark true -e mode local -e samples 15 com.example.rokid_app.test/androidx.test.runner.AndroidJUnitRunner
adb shell svc wifi enable
```

Restore the server afterward if it was previously running. Optional arguments
are `-e expected NAME` and `-e server http://HOST:8000`. Sample count is 1–50.
Timing logs use `LocalBenchmark`. Reports are in app-private
`files/latency/server-results.json` and `files/latency/local-results.json`; read
them with `adb shell run-as com.example.rokid_app cat ...`.
The measured run's timing-only reports are also saved locally under ignored
`.artifacts/latency/`. No live camera images or derived reference embeddings
were saved by the experiment.
