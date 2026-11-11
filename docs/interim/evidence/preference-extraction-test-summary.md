# Preference-extraction test summary

This is a transcription of the team's “Note worker testing” image supplied on 11 November 2026 for the interim report. It records reported results, not a new experiment or a replacement for raw logs. The image cites `local-process-model-benchmark.md` dated 3 November 2026; that underlying file was not found in this checkout.

## Current test method

- Input: two synthetic, speaker-labelled text conversations. Whisper and recorded audio are not connected.
- Targets: three expected guest facts and six selected service-standard labels. The prompt contains the transcript and the selected 15-item F&B rubric.
- Schema-constrained JSON has separate `guest_information[]` and `staff_assessment[]` arrays. Guest information includes category, value, and an exact guest quotation. Staff assessment includes criterion ID, candidate mark, and a staff quotation.
- A Python evidence gate checks that quotations match the appropriate speaker's turn and that extracted guest values appear in their quotations. It also checks all 15 criterion IDs and required evidence sources. Unsupported marks become `INSUFFICIENT_EVIDENCE`.
- Output remains pending; nothing is saved to guest records.

## Reported results

| Model tag as supplied | Schema-valid JSON calls | Targeted staff labels matched | Expected guest facts matched |
|---|---:|---:|---:|
| `llama3.2:3b` | 2/2 | 0/6 | 1/3 |
| `qwen3:4b-instruct` | 2/2 | 2/6 | 2/3 |
| `gemma4:e2b` | 2/2 | 6/6 | 2/3 |

All six model calls returned schema-valid JSON. This does not establish correct interpretation. The six staff labels are targeted examples, not an accuracy estimate over the entire 15-item rubric. No overall LQA score is defined.

The earlier supplied presentation separately reports an exploratory M1 Mac comparison with mean processing times of 76.1, 67.2, and 86.4 seconds per transcript respectively. Those timings are not printed in the newly supplied testing image. The report attributes them to the presentation, and does not treat them as recognition/display latency.

## Errors and iteration

The summary reports that Gemma tagged “too sweet” as a preference and a dessert-safety question as dietary information. One complaint rerun changed `DRINKS-35` from `BELOW` to `MET`.

Added measures reported in the image: quote/role checks, narrow category fixes, a refusal rule, and human confirmation for N/A. Quote matching alone cannot establish whether a sentence supports a lasting preference or a service judgement.

Planned evaluation: build reviewer-agreed labels and a held-out set; change one prompt or rule at a time; run held-out cases three times; track category precision/recall, per-item LQA accuracy, quotation grounding, and repeatability. Add Whisper later and evaluate transcript accuracy and speaker labels separately.

These are exploratory synthetic-text results. They do not establish real-audio performance, hotel-guest accuracy, reliable staff grading, or integration into the smart-glasses workflow.
