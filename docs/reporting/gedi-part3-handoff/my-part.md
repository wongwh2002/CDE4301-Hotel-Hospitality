# My part in the interim report

## Canonical report text

The current report on the repository's main branch is the source of truth:

- [Requirements and the first-time guest use case](../../interim/interim-report.md#requirements)
- [Concept generation and selection](../../interim/interim-report.md#concepts)
- [Proposed staff journey](../../interim/interim-report.md#initial-concept)
- [Team contributions](../../interim/interim-report.md#contributions)
- [Published report](https://wongwh2002.github.io/CDE4301-Hotel-Hospitality/interim/)

The contribution table credits Wong Weng Hong with solution development: functional requirements, concept comparison, and the proposed staff/guest journey.

## Contribution at a glance

### 1. Functions for the first-time guest use case

The system has two responsibilities: capture and process guest context, then select and display what matters for the current service task. A complete same-stay handover associates an explicit guest statement with a likely guest and stay, keeps the source and time, lets staff check and approve the record, and makes the approved detail available to the next employee.

The goal is one useful, guest-confirmed detail from an early interaction, rather than an assumption that a first-time guest has no information or that every comment is a lasting preference.

### 2. Service criteria and measures

The criteria translate service behaviours into measurable requirements:

- **DR1, on-time service support:** the report adopts a proposed **<1 s** trigger-to-first-correct-visible-cue target. Measure target attainment and p50/p95; count late, missing, and incorrect cues. This is an engineering target, not an LQA timing rule.
- **DR2, low-effort capture:** capture time, actions, correction effort, and disruption to conversation.
- **DR3, glanceable interaction:** comprehension, glance duration, attention shifts, and interruption.
- **DR4, preference continuity:** whether the correct approved detail reaches the next employee in time and is interpreted correctly.
- **DR5, correct association:** suppress personal cues for unknown, ambiguous, stale, or lost matches.
- **DR6, appropriate information:** distinguish preferences from allergies, minimise display, and preserve manual fallback.

The project-selected LQA subset supplies service-action windows, including acknowledgement within one minute of lounge entry and a drinks-order offer within three minutes of seating. Those times are distinct from cue-processing latency.

### 3. Concept comparison

The report compares phone/PMS, audio badge plus earpiece, camera-free glasses, and vision-assisted smart glasses. It considers capture, guest/stay association, processing and review, cue delivery, staff effort, privacy and comfort, and integration/fallback.

The camera-free glasses option isolates the value of a visual cue. Comparing it with audio tests the output channel; comparing it with vision-assisted glasses tests the added value and risks of camera-based matching. The glasses direction remains a prototyping choice; the current comparison has no weighted result or comparative hotel-staff study that proves it is best.

### 4. Proposed staff journey

The report adds a confidence gate before profile details appear. Uncertain matches lead to normal greeting or manual profile lookup. Staff confirm a current preference in conversation. Allergy cues trigger verification against the authorised guest record and the relevant menu or kitchen source. A time-stamped draft remains pending until staff checks the wording, guest, and stay and approves it for same-stay use by another employee.

## Evidence boundary

The current glasses demo covers manual activation, recognition against a loaded gallery, prepared-profile retrieval, and cue rendering. Preference extraction is explored separately. Audio capture, confirmed guest/stay association, approved updates, contextual cue ranking, and the complete next-employee loop remain incomplete or proposed. See the canonical report for test results, citations, and limitations.

## Source transcription and script

For the exact original slide wording, see [GEDI slides 22–25 in Markdown](source-slides-22-25.md). For the spoken explanation and transitions, see the [speaker script for sequence slides 3–6](speaker-script-slides-3-6.md). The standalone [proposed staff journey](proposed-staff-journey.md) includes both the source flow and the safer report version.
