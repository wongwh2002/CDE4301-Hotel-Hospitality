# Hotel presentation: research and plan for Slides 7–13

**Updated:** 2026-10-30  
**Scope:** Slide planning and evidence for the revised presentation outline. Vendor claims below are attributed to vendor sources; they are not independent performance findings.

## The story these slides need to tell

> We explored ways to make relevant guest context usable at the service moment, compared complete approaches, and selected a staff-facing glasses concept to evaluate. The team still needs to confirm whether the target is retrieval of existing hotel information, capture and handover of a new insight, or a staged path between them. The current prototypes establish only parts of the proposed journey.

This is the bridge between the problem and the prototype. The revised outline currently proposes keeping one food-and-drink example in view: a guest shares a preference, an employee records or confirms it, and another employee uses it later in the stay. Smart glasses are a presentation option to justify and evaluate; face matching is a separate guest-association option.

### Scope alignment: show capture as an extension to the POC

The revised presentation can include **capturing a new guest-approved insight and making it available to another employee** by extending the POC and its architecture. Keep the current and proposed parts visible: the POC framing and proposed lounge architecture currently cover guest information already held in a profile, an entry tap, a temporary active lounge cohort, face matching, and a cue. The standalone Rokid demo is narrower still: it matches a local image gallery and displays a name/status. New preference capture and cross-staff handover are additions to that baseline, not completed capabilities.

For the added path, show an explicit staff action to record or correct a short note, confirmation of the guest/stay association, and a stay-scoped update to the mock profile store. The next employee can then retrieve that note through the existing cue path. Keep the architecture proposal labelled as proposed until the team adopts it, and label each function implemented, simulated, or proposed in the slides.

### Important boundary from the current project evidence

The revised outline focuses on capturing a new insight from a first-time guest during the current stay. The implemented systems currently cover different pieces:

- The **main hotel POC** simulates entry taps, a temporary lounge cohort, synthetic guest data, matching, and cue presentation.
- The **standalone Rokid demo** captures camera images, sends them to a laptop server, matches against a local gallery, and displays a name/status. It is not integrated with the hotel POC, does not use the lounge cohort, and does not capture or share preferences.
- The standalone demo README reports 30 capture requests, an average of 944 ms and p95 of 1,114 ms from capture request to response. Only 11 samples contained a detected face; the timing excludes waiting for the next two-second capture and physical display rendering. This is a latency result, not recognition accuracy or end-to-end service performance. See [`rokid/README.md`](../../rokid/README.md) and the [interim report plan](../reporting/cde4301-interim-report-plan.md).

Use visible labels such as **implemented**, **simulated**, and **proposed** in Slides 10–13. Do not show the two prototypes as one integrated system. Describe the story as an extension: current profile retrieval provides the baseline; guest-approved capture and handover add a new path into that baseline.

## Slide 7 — Generate concepts from functions

**Purpose:** Show that the team considered different ways to do the work before choosing glasses. Start with the service scenario and Slide 6 requirements, then use a compact morphological chart to explore each function.

| Function | Candidate methods |
|---|---|
| Capture a guest-approved insight | Staff adds a short structured note after the conversation; staff uses push-to-talk dictation and checks the transcript; guest uses a short form/QR; existing reservation/pre-arrival fields |
| Associate it with the correct guest/stay | Staff selects a guest or room from the active stay list; guest taps/scans a room or lounge card; staff confirms a face match against the temporary lounge set |
| Store and share it | Existing authorized PMS/profile note; a structured handover/guest-request tool; a temporary stay-scoped context record |
| Get it to the next relevant employee | Search on a staff phone/tablet; handover/notification to a role or team; glanceable glasses cue; earpiece audio cue |
| Check, correct, and end its use | Staff reviews/edits before saving; guest can correct/decline; note carries source/time and expiry; manual path if identity or content is uncertain |

Build complete candidate bundles from these options. Do not let the chart itself “select” a winner. It is the concept-generation tool; the next slide evaluates whole workflows.

### Fair concept bundles to compare

1. **Current-style workflow:** Staff records a concise guest-approved detail in the hotel’s existing profile or handover process; the next employee searches or reads the handover on a phone.
2. **Structured mobile note:** Staff enters or dictates a short note, explicitly selects the guest/stay, checks the text, and shares it through an approved mobile workflow.
3. **Glasses-assisted workflow:** Staff triggers and checks a short note, associates it with a guest using a deliberate selection or validated lounge event, and the next employee receives a brief glasses cue at a useful service moment.
4. **Automatic visual association as an optional variant:** Glasses attempt to match a visible guest against an active candidate set. Keep this as a component to test; it does not by itself capture a new insight or make the note available to another employee.

Prefer staff-triggered dictation over passive recording as a concept for this presentation. It makes the capture action explicit and reviewable. If voice is considered, note that Android’s `SpeechRecognizer` implementation may send audio to remote servers; do not promise on-device transcription without checking the exact implementation and SDK behavior ([Android SpeechRecognizer documentation](https://developer.android.com/reference/android/speech/SpeechRecognizer)).

**Visual:** Use a compact chart with a few representative options per row. Highlight the options used in each complete concept bundle with consistent colors or outlines. Keep exhaustive variants in backup material.

**Transition:** “These are ways to fulfil the functions. We next compared complete workflows against the requirements, and against products hotels can already use.”

## Slide 8 — Compare alternatives and explain the selection

**Purpose:** Separate commercial products from the team’s own concepts. Product examples establish what hotels can already buy; the concept matrix explains why the team chose its own workflow to prototype.

### Relevant commercial examples

| Product | Documented overlap | What remains distinct from the project’s proposed flow |
|---|---|---|
| [Oracle OPERA Cloud](https://docs.oracle.com/en/industries/hospitality/opera-cloud/26.4/ocsuh/t_create_manage_adding_notes_to_a_profile.htm) | Staff can create, update, and delete guest profile notes. The mobile PWA can display profile notes and preferences ([mobile profile guide](https://docs.oracle.com/en/industries/hospitality/opera-cloud/26.1/ocsuh/t_managing_profiles_mobile_app_pwa.htm)). | The documents describe staff-managed profiles and lookups. They do not document automatic capture of a new conversational insight or an in-lens cue to the next employee. |
| [hotelkit Collaboration](https://hotelkit.net/products/collaboration/) | Digital shift handovers, team chat, guest requests/complaints, and activity tracking; its FAQ also describes read confirmations for handovers. It is a direct alternative to informal messages and handover routines. | It organizes team communication and requests. Its product pages do not document face association or a wearable cue tied to a guest’s current service preference. |
| [Alliants Core Platform](https://www.alliants.com/products/core-platform) | Unifies guest profiles across connected systems and includes restaurant patrons, event attendees, and other visitors. Alliants reports staff profile lookup in under three seconds; treat that as a vendor claim, not a benchmark. | A strong profile and mobile-workflow substitute. The reviewed pages do not document automatic wearer-POV matching or a lounge-entry-bounded candidate set. |
| [SoftServe Hands-Free Face ID demo](https://www.softserveinc.com/en-us/resources/hands-free-face-id-demo) | A demo for real-time face identification on Android and AR headsets; it explicitly lists hospitality and VIP identification as use cases. | It is labelled a demo. Its page does not describe a hotel profile integration, capture of guest-approved preferences, or their transfer to another employee. It means the project should not claim face recognition on AR glasses is itself novel. |

These examples show that profile notes, mobile lookup, and handover software already exist. The more focused comparison is whether the selected concept captures a new insight with less burden and makes it useful to the next staff member at the right moment.

### Suggested decision matrix structure

Compare the three or four complete concept bundles from Slide 7 using the same Slide 6 requirements. Criteria might include:

- Correct capture and guest/stay association.
- Availability to the next relevant employee at the service moment.
- Staff effort and time to record/retrieve.
- Effect on attention and guest interaction.
- Integration with approved hotel systems and role permissions.
- Privacy/consent and handling of uncertainty.
- Feasibility and total cost, including device, software integration, training, support, and maintenance.

Use weights only when you can explain why the partner/team prioritizes them. A useful rating key is **1 = poor fit, 3 = acceptable, 5 = strong fit**, with evidence notes next to every score. Use **unknown** where you lack evidence rather than giving an optimistic score. Treat privacy, safety, and permissions as gates rather than allowing high scores elsewhere to compensate. The vendor pages reviewed do not provide comparable prices, so do not invent cost numbers; show cost categories or mark cost as pending estimates.

**Possible conclusion:** The team selected the glasses interface to evaluate hands-free delivery in the service moment. The insight-capture method, guest association, and integration remain open design decisions. Avoid saying the matrix proves glasses are objectively best if scores depend on untested assumptions.

**Transition:** “The interface is only useful if the information itself is relevant. We narrowed the first cue to a specific service action.”

## Slide 9 — Choose the information to carry

**Purpose:** Make the concept tangible by choosing one information category and action that fit the target service moment.

**Recommended primary example:** a guest-stated food or drink preference that affects an F&B interaction during the same stay. The lounge is the current case setting and F&B is the current prototype scenario. Choose the exact preference after incorporating the industrial partner’s feedback; the notes currently in the repo establish interest in preferences and allergies but do not document PARKROYAL’s actual F&B workflow.

| Candidate information | Possible same-stay action | Presentation treatment |
|---|---|---|
| Guest-stated food/drink preference | Offer a suitable drink or menu suggestion, then confirm it still applies | Good primary personalization example if the partner confirms it is useful and appropriate |
| Purpose/schedule | Suggest an appropriate breakfast/transport option | Use only if staff can act on it and the guest has agreed to share it |
| Special occasion | Offer a fitting acknowledgement or service option | Use only if it fits real operations; can feel intrusive if unexpected |
| Allergy | Verify against the authoritative source and follow the food-safety process | Safety alert, not a preference or proof that food is safe; never let a face match alone trigger the decision |

Keep the concept small: one primary preference cue; a safety alert is a separate requirement with explicit verification steps. The project’s allergy-cue note recommends explicit text plus a symbol; color and emoji alone are insufficient ([W3C use-of-color guidance](https://www.w3.org/WAI/WCAG21/Understanding/use-of-color.html)).

**Transition:** “With that cue selected, here is the complete journey from what the guest shares to what the next employee does.”

## Slide 10 — Show the guest and staff journey

**Purpose:** Connect the service need to the proposed prototype without implying every step is implemented.

1. A guest shares a preference in conversation or through an agreed form.
2. Staff asks/checks whether it should be recorded for the current stay.
3. Staff records a short, structured note and verifies the text and guest/stay association.
4. The note becomes available to the next relevant employee through an approved shared record.
5. At the next F&B moment, the employee sees a brief cue and confirms the preference still applies before acting.
6. The guest can correct or decline; the note expires or is removed according to the chosen stay policy.

Show three evidence states in the storyboard: **implemented in main POC**, **shown in standalone Rokid demo**, and **proposed/not yet integrated**. For example, simulated tap/cohort and synthetic profile matching are in the main POC; standalone image delivery and name/status display are in the Rokid demo; new preference capture and sharing between staff are not yet demonstrated.

**Transition:** “The journey depends on four separate jobs: capturing the insight, linking it to the right stay, sharing it safely, and presenting it at the service moment.”

## Slide 11 — Architecture for the proposed journey

**Purpose:** Show how information moves and where project boundaries sit. Organize the diagram around the guest note, not around vendor names.

Suggested architecture flow:

```text
Guest shares preference
        ↓
Staff-triggered capture on phone → staff checks/corrects note
        ↓
Guest/stay association + source/time/expiry metadata
        ↓
Mock-hotel profile API / stay-scoped POC note
        ↓
Role-appropriate retrieval by the next employee
        ↓
Phone / earpiece / glasses cue → staff confirms and acts
        ↓
Correct or clear note; expire at checkout or agreed TTL
```

Keep these components visually separate:

- **Insight capture:** how a new preference becomes a structured note.
- **Identity association:** how the note is linked to the correct guest/stay. Manual selection, a card event, and face matching are alternatives, not the same function.
- **Storage and access:** hotel system of record if authorized; synthetic/mock store for the POC; role controls, provenance, correction, and expiry.
- **Retrieval and display:** when the next employee receives the cue and what device displays it.

For the added capture path, a phone form with a small set of fields and a review step is a straightforward POC addition; it avoids making passive audio capture a dependency. Require an explicit guest/stay selection or a separately validated association before saving a new note. That write-time check is distinct from the proposed automatic face-match cue used for read-time retrieval.

For the deployment concept, do not imply that a temporary lounge cohort is the complete same-stay data model. A first-stay preference may need to be available across departments; the partner must confirm source-of-truth, retention, and access rules. In the demo, label the mock record as such.

**Visual:** Use solid outlines for implemented components, dashed outlines for planned components, and grey for external hotel systems. Add arrows for data and a separate feedback arrow for correction/expiry. Avoid placing the entire design into one box labelled “AI.”

## Slide 12 — Explain the engineering choices

**Purpose:** Explain the reasons behind choices and show the measured boundary of current technical evidence.

| Decision | Candidate choice and reason | Trade-off or evidence still needed |
|---|---|---|
| Capture | Staff-triggered structured note or push-to-talk dictation, followed by review | More deliberate than passive recording; adds a step. Measure time and transcription/correction errors if dictation is implemented. |
| Guest association | Explicit guest/stay selection or known lounge-entry event as the low-complexity baseline; face match as a hypothesis | Face matching may reduce manual lookup but creates false-association and consent risks. Unknown or ambiguous cases must abstain. |
| Storage | Prefer an approved hotel profile/service system if integration and permissions are confirmed; use synthetic/mock stay records for the POC | A stay-scoped note may fit first-stay context better than a permanent preference, but the hotel needs to define record, retention, and deletion rules. |
| Processing/network | State the path that was actually measured: camera capture on glasses, Android app, Wi-Fi, laptop server, response to glasses | The separate demo’s mean request-to-response was 944 ms and p95 1,114 ms across 30 captures. Capture/JPEG delivery averaged 637 ms; the request/processing/response portion averaged 307 ms, with server face processing averaging 69 ms. The measure excludes wait to next capture and display rendering; it does not prove end-to-end service latency. |
| Display | One relevant service cue, with identity and current preference separated from longer profile details | Exact timing, permissions, readability, staff understanding, and effect on attention need evaluation. |

Do not transfer these measured values to the main hotel POC or to the unintegrated guest-insight journey. For the next integrated test, define latency from **the staff capture/trigger** or **the recognition frame timestamp** through to **a usable cue rendered**, and report the start/end definition explicitly.

## Slide 13 — Design for a short, live interaction

**Purpose:** Show the interface as a testable hypothesis for capture and later retrieval, not a proven usability result.

Show two screens or moments rather than cramming the whole workflow onto one lens:

1. **Capture/check:** `Save for this stay?` with the short note and clear `Save / Edit / Don't save` actions. Show the associated guest/stay and where the staff member corrects the wording.
2. **Later retrieval:** a compact cue such as `ALEX · PREFERS OAT MILK` plus a small source/time hint if needed. Keep the first view to one service-relevant note; let staff request more detail deliberately.

If displaying an allergy, use explicit words and a warning symbol; keep the established verification step visible in the service flow. Never rely on color or emoji alone. Add an “uncertain match” example that reveals no guest-specific note and offers manual selection.

Google’s Glass Enterprise guidance recommends glanceable, timely, simple information that supplements other devices; treat it as interface guidance, not validation of this hardware or hotel task ([Google Glass design guidelines](https://developers.google.com/glass-enterprise/guides/design-guidelines)). W3C says color should not be the only visual signal ([W3C guidance](https://www.w3.org/WAI/WCAG21/Understanding/use-of-color.html)). A controlled Google Glass study found that even a single word could disrupt concurrent visual-search tasks; it studied lab visual-search tasks, not hotel service, so use it to justify measuring timing and interruption rather than claiming all lens text is harmful ([Lewis & Neider, 2016](https://link.springer.com/article/10.1186/s41235-016-0015-6)).

**Make only design claims:** “we designed the cue to be short and task-specific” is supportable from the prototype. “It preserves eye contact,” “feels natural,” or “does not distract” requires user evaluation.

## Transitions across the seven slides

- **7 → 8:** From possible building blocks to complete alternatives and evidence-based selection.
- **8 → 9:** From selected delivery approach to the information that will make it useful.
- **9 → 10:** From one concrete information category to the guest/staff journey.
- **10 → 11:** From journey steps to the system components and data boundaries.
- **11 → 12:** From architecture to trade-offs and measured technical evidence.
- **12 → 13:** From engineering choices to what staff actually see and do.

## Evidence to collect from the industrial partner

The notes currently saved for PARKROYAL record interest in glasses and VIP name/allergy/preference cues, but do not establish the property’s existing note system or F&B workflow. First establish whether the operational gap is capturing a new insight, retrieving an existing profile detail, or both. Then ask for one recent example and record:

- What the guest shared and whether it was guest-approved for later use.
- Who captured it, where it was saved, and how the next staff member found it.
- Whether the detail changed an action and whether the guest found that action useful.
- What delay, correction, missed handover, or extra work occurred, if any.
- Which existing software or staff devices already support this, and what permissions apply.
- What should be kept only for the current stay and what the guest may correct or decline.

Do not present WhatsApp failures, staff overload, preference repetition, or allergy-record failures as facts unless the partner provides an example or an appropriate measure. The local problem remains to be validated.

## Primary sources

- Oracle OPERA Cloud: [profile notes](https://docs.oracle.com/en/industries/hospitality/opera-cloud/26.4/ocsuh/t_create_manage_adding_notes_to_a_profile.htm) · [mobile profiles](https://docs.oracle.com/en/industries/hospitality/opera-cloud/26.1/ocsuh/t_managing_profiles_mobile_app_pwa.htm)
- hotelkit: [team collaboration and handovers](https://hotelkit.net/products/collaboration/) · [guest service management](https://hotelkit.net/solutions/guest-services/)
- Alliants: [Core Platform](https://www.alliants.com/products/core-platform) · [mobile staff-app hotel case](https://www.alliants.com/success-stories/lyle)
- SoftServe: [Hands-Free Face ID demo](https://www.softserveinc.com/en-us/resources/hands-free-face-id-demo)
- Android: [SpeechRecognizer API](https://developer.android.com/reference/android/speech/SpeechRecognizer)
- Google: [Glass Enterprise design guidelines](https://developers.google.com/glass-enterprise/guides/design-guidelines)
- W3C: [Use of Color accessibility guidance](https://www.w3.org/WAI/WCAG21/Understanding/use-of-color.html)
- Lewis and Neider: [Through the Google Glass: The impact of heads-up displays on visual attention](https://link.springer.com/article/10.1186/s41235-016-0015-6)

## Related project material

- [Revised presentation outline](../reporting/hotel_presentation_outline.md)
- [Interim report plan and current prototype status](../reporting/cde4301-interim-report-plan.md)
- [Hotel personalization in the moment of service](hotel-personalization-in-the-moment-service.md)
- [Hotel personalization project review](hotel-personalization-project-review.md)
- [PARKROYAL visit notes](../../hotel-visit/parkroyal-main-points.md)
- [Rokid standalone demo README](../../rokid/README.md)
