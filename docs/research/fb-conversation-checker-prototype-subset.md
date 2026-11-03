# F&B conversation checker: 15-item prototype subset

Checked 2026-11-03 against the team-supplied PARKROYAL COLLECTION 2026 scores template and conversational keywords document. The original files remain in the local `docs/research/source-materials/` folder and are not included in this public-repository change; the selected criteria and their source-cell references are reproduced in the accompanying justification workbook.

The workbook supplies a useful F&B starting point, especially its **Drinks Service** sheet for a lounge. This is a proposed subset for a conversation-processing prototype, not an official LQA score or a complete audit. Confirm that this workbook is the current, authorized standard for the target hotel and outlet before using its wording in a deployed grader. Sheet-local standard numbers repeat; use the sheet and cell reference.

## Candidate items

| # | Source cell / standard | What the checker reviews | Evidence needed and limit |
|---:|---|---|---|
| 1 | `DRINKS SERVICE|Food And Beverag` B7 / #1 | Guest acknowledged on entering bar/lounge | Audio/video plus a reliable arrival timestamp; a transcript alone cannot prove the one-minute interval. |
| 2 | Same sheet B8 / #2 | Drinks order offered within the seating interval | Seating timestamp plus audio/video; only apply when a seating event is known. |
| 3 | Same sheet B9 / #3 | Beverage knowledge and relevant local/signature recommendation | Audio plus an approved beverage/menu reference; fluent wording alone does not prove accuracy. |
| 4 | Same sheet B11 / #5 | Response to a reasonable custom drink request | Audio can show the response; the order or service record is needed to confirm fulfilment. |
| 5 | Same sheet B12 / #6 | Choice of brand or variety when available and relevant | Audio plus menu/availability context; mark not applicable when there was no choice to offer. |
| 6 | `RESTAURANT|Food And Beverage` B28 / #20 | Answer to a menu, ingredient or allergy question | Audio plus an authoritative menu/ingredient/allergen source; do not let the model certify food safety. |
| 7 | Same sheet B30 / #22 | Completeness of the order, including relevant instructions | Transcript plus the final order record; conversation alone may omit details entered elsewhere. |
| 8 | Same sheet B31 / #23 | Discreet reconfirmation of a previously shared dietary requirement | Requires prior authorized profile context and the recorded exchange; no prior disclosure means not applicable. |
| 9 | `DRINKS SERVICE|Food And Beverag` B37 / #29 | Speech clarity sufficient for two-way conversation | Audio; use trained human labels because the assessment has a subjective component. |
| 10 | Same sheet B38 / #30 | Natural, friendly, interested engagement | Audio and optionally video; human-reviewed, not exact-keyword matching. |
| 11 | Same sheet B39 / #31 | Natural and discreet use of the guest's name | Audio plus context; don't reward repeated name use or expose a name when inappropriate. |
| 12 | Same sheet B43 / #35 | Effort to meet a request or offer an alternative | Audio can identify the response; operational evidence may be needed to verify the result. |
| 13 | Same sheet B44 / #36 | Personalisation of the interaction | Requires relevant guest context and human review; a phrase such as “based on your preference” is not sufficient evidence by itself. |
| 14 | Same sheet B46 / #38 | Listening, clarification, interruption and repetition | Audio can show clarification, overlap or repeated requests; visual attention is not established by transcript alone. |
| 15 | Same sheet B48 / #40 | Empathy and a suitable resolution in a challenging interaction | Only apply when a challenging interaction occurs; use human review for the final judgement. |

The selected source cells are in the provided workbook's Drinks Service, Restaurant and F&B behavioural rows. Their classifications include Efficiency, Service, Sales Opportunity and EI Behavioural. The proposed checker should not force every item onto every conversation.

## How to use the keyword document

The keyword document covers Bell, Concierge and One Connect; it is not an F&B-specific standard. Its greeting, needs-discovery, dietary-request, recommendation and confirmation examples can help seed paraphrase examples for the checker. Treat them as **examples of possible wording**, not required phrases. LQA criteria describe service behaviours; exact string matching would miss natural paraphrases and could reward a phrase without the behaviour.

## Suggested Processing output

For each applicable item, return:

- A provisional status: **evidence supports met**, **possible gap**, **insufficient evidence**, or **not applicable**.
- The supporting transcript excerpt and timestamp, or video-frame reference where available.
- Any required context/source used to check correctness (for example, menu or prior dietary detail).
- A short reason for the status and a human-review flag.

Keep **insufficient evidence** distinct from **not applicable**. Missing audio/video or missing context is not proof that service failed. A human reviewer confirms the final Met/Below/N/A entry in the supplied scoring workflow. Keep the guest preference note separate from the internal service-review result. Do not produce an overall LQA score from this subset.

## Metrics for testing the checker

These measure the checker, not the hotel's LQA performance:

1. **Per-item precision, recall and macro-F1** for provisional Met/Below labels against an expert-labelled set. Report each item separately; macro-F1 avoids high-frequency easy items hiding weaker criteria.
2. **Reviewer agreement** between the model and trained hotel reviewers, per item (percent agreement and Cohen's kappa where the sample supports it).
3. **Evidence-grounding rate:** share of verdicts whose cited excerpt/frame actually supports the conclusion.
4. **Abstention quality:** decision coverage, correct “insufficient evidence” rate, and false confident conclusions when evidence is missing.
5. **F&B factual correctness:** for menu/ingredient/allergy answers, correctness against the approved source; report incorrect reassurance separately.
6. **Workflow measures:** correct guest association, time-to-cue and staff actions/time. These show whether the three functions are usable; they are not LQA grades.

Use consented or approved staged interactions, with two reviewers independently labelling applicability and evidence. Include paraphrases, interruptions, noisy audio, missing profile/menu context, off-menu requests and cases where a spoken promise is not fulfilled. Set acceptance targets with the hotel team before testing.

## Slide implication

On Slide 15, show the checker against a **15-item F&B subset** but display only three examples to keep the slide readable: beverage/menu knowledge, dietary reconfirmation, and active listening. Put the full subset and evidence limits in speaker notes or backup material. On Slide 16, use one lounge conversation to show Capture → Process → Retrieve; label any video grading and human-reviewed status as proposed until implemented and validated.
