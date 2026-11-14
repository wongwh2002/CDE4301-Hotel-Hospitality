# GEDI source slides 22–25

This is a text transcription of the source slides. Line breaks and obvious grammar have been normalised; slide numbers below are the numbers printed in the GEDI deck and match PDF pages 22–25.

## Slide 22 — Important functions

**Subtitle:** Targeted at the problems faced for first-time guests.

**Summary line:** Capture the interaction, process and extract information, then display what matters now.

| Capture (+ process) | Display |
|---|---|
| Capture guest preferences / complaints. | Select information for the current service task. |
| Associate the interaction with the guest. | Rank by location, task, and urgency. |
| Process and store information for easy lookup. | Choose concise visuals, rendered with low latency. |
| **Output:** Time-stamped interaction plus guest context. | **Output:** Short, actionable glasses cue. |
| Supports timely, complete capture. | Supports relevance, discretion, and speed. |

**Footer:** Capture and process protect completeness and accuracy; display carries relevance, low distraction, and latency.

## Slide 23 — Design criteria for the service

| Function | Criterion | Targeted LQA service standard | Design requirement | How to measure |
|---|---|---|---|---|
| Display | On-time service support | Greet within one minute; offer a drinks order within three minutes. | Show the useful cue promptly so staff can act within the service window. | Time from first interaction to first visible cue; slide target: less than one second, cited as [13]. |
| Display | Glanceable interaction | Natural, friendly engagement; discreet name use. | Show a concise cue that staff can understand while speaking. | Correct understanding, glance duration, attention shifts. |
| Capture | Low-effort capture | Active listening and natural, friendly engagement. | Staff starts capture with a simple action. | Time spent capturing information. |
| Capture | Preference continuity | Allow confirmed preferences to personalise service. | Capture a guest-stated preference and make it available for the next shift. | Whether the correct preference reaches the next staff member. |

## Slide 24 — Morphological matrix

| Function / criterion | Manual profile + phone (current) | Smart glasses | Audio badge + earpiece |
|---|---|---|---|
| Display / on-time service support | Staff remember the customer based on memory. | Computer vision identifies the customer. | Staff remember the customer based on memory. |
| Display / glanceable interaction | Manually identify the customer; open the profile on a phone or paper. | Glanceable glasses cue. | Short audio cue in the earpiece. |
| Capture / low-effort capture | Manually identify the customer and write after the conversation. | Camera identifies the customer; hands-free audio capture. | Manually identify the customer; hands-free audio. |
| Capture / preference continuity | Staff input the customer and record to the backend manually. | Customer and record automatically processed in the server. | Staff input the customer and record processed in the server. |

## Slide 25 — Proposed staff journey

The source diagram reads:

1. Capture frame.
2. Retrieve profile and show allergy plus preference.
3. Ask whether the guest has preferences and allergies.
4. **No:** greet the guest, ask for the order, and ask again about allergy.
5. **Yes:** greet the guest, offer the preference, and offer alternative food for allergies.
6. Record and process the conversation, log it, and produce an LQA result.

## Notes for interpreting the source

- The slide 25 “no” branch says to ask repeatedly about allergy. The report and speaking script use a more natural fallback: continue the normal greeting and ask relevant questions directly.
- The source journey does not show a confidence gate before displaying profile details. The proposed report journey adds one; suppress personal cues if the match is uncertain.
- An allergy cue is a prompt to verify. Staff should check the authorised guest record and the relevant menu or kitchen source before advising the guest or suggesting an alternative.
- Slide 23's less-than-one-second target is printed in the source. Its reference [13] also appears on the deck's Singapore hospitality-market slide, so it does not establish a service or engineering latency standard.
- The full interim report uses a provisional 1.5-second p95 engineering target and reports four successful warm commits averaging 1.18 seconds. These are differently defined figures; retain their labels and measurement boundaries.
