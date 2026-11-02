# Temple touch to displayed information

Live RV101 measurement, 2026-11-03 (Asia/Singapore), over Wi-Fi to
`10.111.207.147:8000`. Server: CPU `buffalo_l`, threshold 0.45, margin 0.10,
seven gallery names and seven cue profiles. The measured endpoint is the first
recognized name plus one or two preference/allergy icons, not an Unknown label.

## Combined live series

The recording contains thirteen activations across the initial and follow-up
runs, including rapid retaps. Five scans produced a known-name-and-icons drawing
event; four also have a matching frame
commit event. These successful samples are retaps during active capture, not
independent starts from idle.

| Trial / scan | Touch to icon draw | Touch to frame commit |
| --- | ---: | ---: |
| 4 | 987 ms | 1,085 ms |
| 7 | 4,412 ms | Not recorded before next activation |
| 8 | 1,208 ms | 1,312 ms |
| 10 | 1,304 ms | 1,349 ms |
| 13 (scan 3 after resume) | 886 ms | 974 ms |

For the four confirmed commits: mean **1,180 ms**, median **1,198.5 ms**,
range **974–1,349 ms**. For all five drawing events: mean **1,759.4 ms**,
median **1,208 ms**, range **886–4,412 ms**. These are separate cohorts.

Average stage breakdown for the four confirmed commits:

| Stage | Average |
| --- | ---: |
| Touch handling to sending the successful request (camera, local detection, crop/encode, gating and scheduling) | 693 ms |
| HTTP request to parsed response | 302 ms |
| Server inference, included within HTTP time | 177.5 ms |
| Response to name/icon draw | 101.3 ms |
| Draw to frame-commit callback | 83.8 ms |
| Total touch to frame commit | 1,180 ms |

The slower scan first returned zero faces, then waited for the next recognition
opportunity at roughly the two-second cadence. The successful request started
3,983 ms after touch, took 330 ms over HTTP, and reached drawing 99 ms later.
The next tap arrived about 27 ms after that draw; its frame commit was not
recorded before the scan changed. Thus its 4.41-second wait was predominantly
before the successful request, rather than a four-second server inference.

Eight scans had no accepted name-plus-icons draw recorded before another tap.
Some pending requests were cancelled by retaps. These logs do not distinguish
all Unknown results, rejected track associations, or unavailable label placements,
so this is not a recognition-accuracy or display-success-rate benchmark.

The first start from idle took 5,842 ms to the first completed local analysis,
but did not produce a recognized information draw in that scan. It cannot be
reported as a successful cold-start end-to-end result.
The follow-up also restarted capture but included another tap about 474 ms after
the initial activation, then a status swipe/retap sequence. Its successful draw
was a subsequent active-session tap. A clean isolated cold-start latency remains
unconfirmed; no further retries were requested from the wearer.

## Measurement boundaries and reproduction

Start: `InteractionWindow.detectionStartedAt`, set when the app handles the
temple tap, with permissions already granted. It excludes the physical touch
sensor's event-delivery delay and any initial permission interaction.

Drawing endpoint: `FaceOverlayView.onDraw` has drawn the name and icons on its
canvas, after layout, track/freshness checks and UI scheduling. Unknown and debug
face labels never count as information displays.

Commit endpoint: Android's hardware frame-commit callback. It is a software
rendering milestone, not an optical measurement of photons on the lens. Physical
display scanout, optics and wearer perception are not measured. A missing commit
is not silently substituted with a drawing timestamp.

`FaceEndToEnd` logs once for the first name and first icons per activation. It
contains only timing fields, scan/request IDs and cue counts; no names or cue
values. `FaceLatency` retains per-request and server-inference timings.

Collect logs for one app process:

```powershell
adb logcat -d --pid=APP_PID -v time -s FaceEndToEnd:I FaceInteraction:I FaceLatency:I "*:S"
```

Save that output and summarize it:

```powershell
python server/summarize_display_latency.py --log .artifacts/display-latency/live.log --out .artifacts/display-latency/summary.json
```

The current capture and JSON are in the ignored `.artifacts/display-latency/`
directory. For comparable future trials, begin each from idle with the same
centered test subject, no status swipe or retap, and no competing speech. Report
misses and cold/warm starts separately. Small samples do not establish p95/p99
performance or restaurant-condition reliability.
