# Retrieval mode comparison — 2 November 2026

## Updated table — unplugged battery replay trial

Two five-minute observations with USB disconnected, controlled over Wi-Fi ADB:

| Mode | Scheduled duty cycle | Frames sent | Retrieval calls | Reported battery drop per 5 min |
| --- | ---: | ---: | ---: | --- |
| Continuous | 100% | 141 | 141 | 1 percentage point (100% → 99%) |
| Temple-touch + 15-second silence timeout | 25% | 34 | 34 | 2 percentage points (95% → 93%) |

**This short trial did not demonstrate battery savings.** The two windows began
at different charge levels, the first near the full-charge plateau, and the
gauge only reports whole percentages. The apparent difference is insufficient
to establish which mode consumes more power. Do not turn these drops into
battery-life estimates or claim a power-saving percentage.

The display was asleep. This is the scripted JPEG-replay workload, excluding
camera, microphone/VAD and on-lens rendering. Audio activity is still simulated.
It does not measure battery use of a deployed audio/camera streaming feature.

The continuous window lasted 300,026 ms, with 140 health checks. Its final
request started at 298,975 ms and was cancelled by the client at the observation
deadline; the other 140 responses completed. Server face-result logs confirm
the last frame was processed despite cancellation of its client response.
The original harness's zero-error assertion stopped after that window. The
valid measurement was preserved and the timeout mode was resumed separately.
An aborted repeated baseline and approximately five minutes of setup/install
activity between valid windows were excluded from the recorded drops, but
explain the different starting charge levels. The modes are not a seamless
ten-minute discharge trace.

The timeout window lasted 300,020 ms, with 34 completed retrieval requests,
zero failures, and 139 health checks. The silence gate expired at 75,022 ms.
The last retrieval started at 72,790 ms and completed at 74,037 ms; no retrieval
started after expiry. Eleven battery samples per mode all reported plugged=0.
Android's charge counter returned its unsupported sentinel (-2147483648), so
no consumed-charge/energy measurement is available. Thirty-second current
snapshots are too sparse for reliable integration of the bursty workload.

The resumed timeout measurement and scripted timeout-edge test passed. The
initial continuous test's end-of-window cancellation remains in the raw report;
it has not been relabeled as a completed response. Timing/battery metadata is
saved locally in `.artifacts/latency/battery-mode-comparison.json`.

## Earlier USB-powered traffic comparison

Measured over two separate five-minute real-time replay windows. Audio activity
was scripted; duty cycle is the policy's scheduled active fraction. Counts are
actual successful JPEG uploads to the current face-recognition endpoint.

| Mode | Duty cycle | Frames sent | Retrieval calls | Power or battery |
| --- | ---: | ---: | ---: | --- |
| Continuous | 100% (300/300 s) | 143 | 143 | Not measured — USB charging |
| Temple-touch + 15-second silence timeout | 25% (75/300 s) | 36 | 36 | Not measured — USB charging |

The continuous observation lasted 300,008 ms; the speech-controlled observation
lasted 300,000 ms. Both had zero failed requests and 144 health checks, excluded
from the table's frame/retrieval counts. The speech-controlled run's last request
started at 73,177 ms and completed at 74,505 ms. No requests started at or after
the 75-second deadline. The gate remained idle through the end of the cycle.
This is **74.8% fewer image uploads/retrieval requests** for the specified
schedule, not a measured reduction in total device power.

Both instrumented tests passed (real-time comparison and scripted timeout-edge
checks), taking 600.492 seconds in total. The full timing trace is saved locally
in `.artifacts/latency/audio-mode-comparison.json`. The normal glasses app was
reopened afterward and continues using its existing 10-second activation policy;
the experiment does not install a production audio timeout.

Slide timeout-test wording supported by this experiment:

| Test | Result suitable for the slide |
| --- | --- |
| Natural pauses | Scripted policy test passed: pauses shorter than 15 s stay active; 15 s of silence ends retrieval. Real speech/VAD accuracy not tested. |
| Background noise | Real noise not tested. Non-speech input leaves the timer unchanged; a false speech classification extends it. |
| Missed touches | Scripted no-touch case stays idle. Physical sensor missed-touch rate not measured. |

## Requested five-minute conversation schedule

The requested scenario is one new conversation every five minutes, lasting one
minute, followed by a 15-second silence timeout. The separate
`scenario=audio-15s` experiment uses two real 300-second observation windows:
continuous, then touch plus scripted audio activity. A simulated touch occurs at
the start. Scripted speech events occur once per second from t=0 through t=60 s;
silence follows until the end of the five-minute window. With no natural pause
of 15 seconds or longer, expiry is t=75 s. The scheduled active fraction is
75/300 = **25%**, versus **100%** for continuous operation.

This is a test of a **proposed policy**, not a production audio feature. Speech
events are supplied directly to a test-only silence gate. It never records a
microphone, runs VAD, or transcribes/retrieves spoken content. The workload is
the existing JPEG-to-face-recognition endpoint, held at the current nominal
two-second request interval. No audio/RAG retrieval calls are represented.

At an ideal exact two-second cadence, the budget would be 150 versus 38 JPEGs
(start at t=0, then t=2, etc.). Those are calculated budgets, not observed counts.
Real scheduling and synchronous health checks introduce drift; measured counts
can be lower. The harness runs calls serially, whereas production schedules
health checks asynchronously through its shared I/O worker. This is a controlled
comparison, not a reproduction of every production scheduling detail.

The test-only gate also checks these deterministic event cases:

- Audio alone while idle does not activate retrieval (including a missed touch).
- A natural pause shorter than 15 seconds retains the active state.
- New speech resets the deadline; exactly 15 seconds of silence expires it.
- Speech after expiry requires another touch.
- Noise already classified as non-speech does not reset the deadline.
- A false speech classification does reset it, illustrating why real VAD quality
  needs a separate microphone/noise test.

These classification inputs are scripted. They cannot establish detection
accuracy for real background noise or the physical temple sensor's miss rate.

During the real-time scripted-audio replay, the loop observed expiry at
**75,019 ms**, versus the intended 75,000 ms deadline. Subsequent log samples
showed only continuing health checks; the final report verifies all retrieval
starts against the 75-second deadline. This measures test-loop scheduling,
not microphone/VAD processing or camera shutdown latency.

## Scope

This is a controlled JPEG-replay experiment on the physical glasses using the
existing Wi-Fi server. It compares recognition-window scheduling and actual
HTTP uploads, not live-camera capture or physical touch reliability.

The slide's design uses audio activity to reset a 15-second silence timeout.
The current face-recognition app has no microphone/audio-activity pipeline:
one temple touch opens a fixed 10-second window, and another touch resets it.
The experiment measures that implemented policy without changing the app.

Each mode gets a separate 60-second observation. Continuous mode permits
recognition for all 60 seconds. Temple-touch mode simulates one activation at
the start, permits recognition for 10 seconds, then remains idle for 50 seconds.
The same preloaded JPEG is used throughout, representing a continuously
available, centered face. It bypasses camera capture, local ML Kit face/focus
filtering, image encoding, and rendering. Requests are attempted every two
seconds when eligible, through the production `FaceServerClient` with the
production `InteractionWindow` eligibility/deadline rules. Health checks
continue in both active and idle periods.

“Duty cycle” means scheduled recognition-window active time divided by the
observation time. It is not CPU utilization, radio duty cycle, or camera-on time.
“Frames sent” means JPEG uploads, not camera frames captured. “Retrieval calls”
means POST `/detect` calls; every successful call uploads one JPEG. GET `/health`
calls are counted separately and excluded from both slide columns.

## Timeout and activation checks

The preliminary current-app-policy replay completed successfully before the
five-minute audio-policy experiment:

| Mode | Observation | Scheduled duty | JPEG uploads | POST `/detect` | Failed requests | GET `/health` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Continuous | 60.004 s | 100% | 29 | 29 | 0 | 29 |
| One 10-second activation | 60.010 s | 16.7% | 5 | 5 | 0 | 29 |

These rows describe the existing fixed-window policy in the replay harness,
not the requested 15-second audio-silence design.

All seven `InteractionWindowTest` cases passed, covering default idle state,
the exact 10-second deadline, stopping new requests near expiry, another touch
resetting the deadline and rejecting old results, status-only swipes, swipes
not extending detection, and cancellation preserving status display timing.
The full existing JVM suite passed: 26 tests, zero failures/errors.
These are timing/state tests, not hardware gesture trials.

| Slide test | What can be concluded now |
| --- | --- |
| Natural pauses | Audio-driven timeout is not implemented. Under the current policy, speech and pauses do not alter the fixed 10-second deadline. |
| Background noise | No audio input/VAD exists, so noise-triggered timeout resets cannot be tested. The current policy has no audio-reset input. |
| Missed touches | Physical miss rate is unmeasured. A missed activation leaves recognition idle; a wearer trial with a known number of deliberate touches is needed to measure reliability. |

## Power/battery limitation

An additional unplugged trial was completed at the wearer's request. It uses the
same two five-minute replay windows over Wi-Fi ADB, with USB disconnected.
The instrumentation samples battery level/scale, plugged/status, voltage,
temperature, current-now and charge-counter properties every 30 seconds and at
the end of each mode. It checks every sample is unplugged and rejects the trial
if charging is detected. Reports are saved separately in app-private
`files/latency/battery-mode-comparison.json` (`-e battery true`).

The display was asleep in this replay harness. The measurements exclude live
camera, microphone/VAD, and on-lens display loads. They include idle device and
Wi-Fi/request activity. A single sequential pair from full charge is a short
exploratory observation, not a battery-life estimate or a controlled repeated
power study. Whole-percent readings near full charge may not resolve a change.

In the earlier USB-connected trial, the device reported USB powered, charging
status FULL, and battery level 100%.
The battery charge counter reported zero, and `current_now` reported 1000 with
no validated useful discharge signal. An unchanged percentage while connected
to USB cannot establish power savings or battery life. For that earlier run,
power/battery cells remain **not measured (USB charging)**. Fewer requests do not imply
the same percentage reduction in total power.

A battery comparison needs equal-duration unplugged runs from comparable charge
levels, the same scene/network/display settings, and a longer measurement period
or validated current/energy telemetry. Wi-Fi ADB can collect observations without
USB charging. The audio-silence design needs an implemented audio/VAD path before
its natural-pause and background-noise behavior can be evaluated.

## Reproduction

Use the app-private `files/latency/probe.jpg` provisioned for
[`LATENCY_BENCHMARK.md`](LATENCY_BENCHMARK.md), with the configured server online.
Build/install the debug app and test APK, then run:

```powershell
adb shell am force-stop com.example.rokid_app
adb shell am instrument -w -r -e class com.example.rokid_app.RetrievalModeComparisonTest -e benchmark true com.example.rokid_app.test/androidx.test.runner.AndroidJUnitRunner
adb shell run-as com.example.rokid_app cat files/latency/mode-comparison.json
adb shell am start -n com.example.rokid_app/.MainActivity
```

The opt-in test takes approximately two minutes. It logs each mode's start/end
under `ModeBenchmark` and writes timing/request metadata only. No camera frames
are recorded. Normal instrumented tests skip this experiment unless explicitly
enabled.

For the requested five-minute audio-policy scenario, add `-e scenario audio-15s`
to the instrumentation command. It takes approximately ten minutes and writes
`files/latency/audio-mode-comparison.json`. Its `observed_expiry_ms` reports when
the loop first observes the speech-controlled deadline expire. Reports saved
locally under `.artifacts/latency/` contain request timings and counts only.
