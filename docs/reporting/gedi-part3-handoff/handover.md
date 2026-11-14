# Handover for Sol Ultra

## Task context

This is Wong Weng Hong's solution-development contribution to the CDE4301 hotel-personalisation project. It follows the team's problem framing and covers the functions, service requirements, concept alternatives, and proposed staff journey for GEDI slides 22–25.

The presentation script labels this content as slides 3–6 because it follows the problem section in the speaking sequence. Use the mapping in [README.md](README.md) whenever slide numbers are mentioned.

## Main design intent

The project focuses on a first-time guest during the current stay. A first-time guest can already have booking or pre-arrival information, while often having less recorded service history. The design opportunity is to capture one useful, guest-confirmed detail early and make it available to another employee later in the same stay.

The proposed system has two linked functions:

1. **Capture and process:** record a guest-stated preference, request, or concern; associate it with the likely guest and stay when sufficiently supported; prepare a time-stamped draft for staff review.
2. **Select and display:** select the smallest detail relevant to the current service task, then show it as a concise, actionable cue.

## Evidence and implementation boundaries

- The current interim report describes a working smart-glasses recognition-and-display path using a loaded gallery, prepared profiles, manual activation, and a rendered cue.
- Preference extraction has been explored separately. Audio capture, checked guest/stay association, staff-approved record updates, task-ranked cue selection, and the complete next-employee handover remain proposed or incomplete.
- The smart-glasses direction is a prototyping choice. The current concept comparison has no weighted decision scores or comparative hotel-staff results that establish a winner.
- Do not describe the full slide 25 flow as an integrated implementation or claim that it has improved LQA performance or guest outcomes.

## Important item to reconcile

GEDI slide 23 prints a cue target of **less than one second**. The speaker script and current interim report use a provisional **1.5-second p95** engineering target. The report records four successful warm frame commits averaging 1.18 seconds; that small successful-only average does not establish p95 performance, include failures, or measure physical lens visibility. Keep the two figures labelled by source and resolve the slide before reusing it.

The one-minute acknowledgement and three-minute drinks-order windows are service-action targets from the project-selected PARKROYAL F&B LQA subset. They are separate from cue-processing latency.

## Service and data safeguards

- A guest match can supply context for staff. It does not establish that an allergy is current or that a food item is safe.
- Suppress personal cues when identity is unknown, ambiguous, stale, or lost. Let staff continue with the normal greeting or manual profile lookup.
- Confirm the guest's current preference in conversation.
- Verify allergy information against the authorised guest record and the appropriate menu or kitchen source before advising the guest.
- Keep an extracted statement as a time-stamped, stay-scoped draft until staff checks the wording, guest, and stay and approves it.

## Suggested next steps

1. Keep [source-slides-22-25.md](source-slides-22-25.md), [speaker-script-slides-3-6.md](speaker-script-slides-3-6.md), and the current interim report as separate source layers: original slide wording, spoken explanation, and report-level synthesis.
2. If revising the report, edit the canonical docs/interim/interim-report.md; the full contribution is already covered there. Do not append another overlapping chapter.
3. Check any revision against the final-assessment rubric and keep references complete and consistent.
4. Preserve the distinction between demonstrated recognition/display stages and the proposed capture-to-approved-record-to-next-employee workflow.
5. For concept comparison, hold the scenario and staff-review support constant. Compare the phone/PMS, audio badge, camera-free glasses, and vision-assisted glasses across capture, guest/stay association, review, cue delivery, effort, privacy/comfort, and integration/fallback.
6. Measure capture time, correction effort, correct and false associations, unsupported notes, cue latency including failures, staff interruption, comprehension, privacy/comfort, and recovery from device/link failures. Treat privacy and safe association as pass/fail constraints.

## Useful repo files

- [Interim report](../../interim/interim-report.md)
- [Project problem framing and working context](../../agents/hotel-smart-glasses-poc.md)
- [Laptop-first architecture proposal](../../architecture/hotel-lounge-smart-glasses-poc.md)
- [Preference-extraction prototype](../../../apps/note-worker/README.md)
- [LQA review](../../research/lqa-15-criteria-review.md)
- [Presentation outline](../hotel_presentation_outline.md)

## Prompt for the next model

You are helping Wong Weng Hong continue his CDE4301 hotel-personalisation work. Read this handover and the linked Markdown files first. Keep GEDI source slide numbers 22–25 distinct from script sequence slides 3–6. Use the current interim report on main as the canonical report wording. Preserve evidence boundaries, the first-time guest same-stay handover goal, the row-by-row audio/glasses comparison, and the allergy and uncertain-match safeguards. Ask only when a missing choice would materially change the deliverable.
