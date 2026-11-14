# Proposed staff journey

## Intended first-time guest outcome

Use an early encounter to establish one useful, guest-confirmed detail for the current stay. A later employee should be able to retrieve that approved detail when it matters to the next service task.

## Report-level journey

1. **Start the encounter.** The staff member deliberately taps the glasses to start the interaction.
2. **Check guest association.** The system looks for a stable, sufficiently confident guest match.
3. **Choose the safe path.**
   - If the match is uncertain or unavailable, show no personal profile cue. Staff continue with the normal greeting, ask the guest directly, or use the usual phone/PMS lookup.
   - If the match is sufficiently confident, select only the small amount of context relevant to the current service task.
4. **Use the context in conversation.** Staff confirm that a preference still applies before acting on it.
5. **Verify allergy information.** Treat an allergy cue as a prompt to check the authorised guest record and relevant menu or kitchen source. A face match alone cannot establish that a dish is safe.
6. **Prepare a record draft.** After the interaction, extract only evidence-supported guest statements into a time-stamped, stay-scoped draft with source and review status.
7. **Review and approve.** Staff correct the wording and confirm the guest and stay before saving.
8. **Carry context forward.** The next employee retrieves the approved detail when it is relevant to their service task.

## Compact flow

Encounter starts → confident guest association? → relevant confirmed context? → cue or normal greeting/manual lookup → staff confirms today's need → check authoritative source for allergies → serve guest → prepare a sourced draft → staff reviews and approves → next employee retrieves the approved same-stay detail.

At every uncertain association, suppress personal details and leave the manual path available.

## Source-slide journey

GEDI slide 25 shows: capture frame → retrieve profile and show allergy plus preference → ask whether the guest has preferences/allergies → branch to a repeated allergy question when the profile has no preference/allergy, or offer the preference and an alternative food when it does → record and process the conversation, log it, and create an LQA result.

The report-level version adds a match-confidence gate, a manual fallback, allergy verification, and human review before a new shared record. These are design requirements and proposed workflow stages; the full loop is not integrated in the current prototype.

## Current demonstration boundary

The interim report documents a narrower path: manual activation, recognition against a loaded gallery, prepared-profile retrieval, and display. Text preference extraction is tested separately. Audio capture, confirmed guest/stay association, staff-approved record updates, next-employee retrieval, and task-ranked cue selection remain to be integrated.
