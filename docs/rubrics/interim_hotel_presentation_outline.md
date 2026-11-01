# Hotel personalisation project: revised presentation outline

## Presentation focus

Enable increasingly personalised service for first-time hotel guests within the same stay by capturing relevant, guest-approved insights and making them accessible to the next relevant staff member. Smart glasses are the selected concept to justify and evaluate, rather than the starting assumption.

The outline retains Slides 1–11. Former standalone engineering and UI slides, and separate iteration/method/result slides, are now integrated into three component sections: information capture, retrieval and display. Each tells a complete requirement → design → measurement → iteration → outcome story. The integrated demonstration follows these sections. Real-world user validation has not yet been completed.

## Revised outline

| Slide | Title and purpose | Content and suggested examples | Rubric |
|---|---|---|---|
| 1 | Hook and luxury-service context | Open with: “A guest shares one preference. Will the next staff member know it before the guest has to repeat it?” Connect the scenario to personalisation and consistent hotel service. The Parkroyal contact described LQA (Leading Quality Assurance) as the hotel’s corporate-mandated core framework and “Forbes” as an additional aspiration; confirm whether this means Forbes Travel Guide and verify the hotel’s status. Explain that these standards set a service-quality context; the project addresses guest-specific information handoff, not standards-compliance scoring. Support claims about satisfaction, spending and retention with evidence, distinguishing stated intentions from measured behaviour. Sources: [Parkroyal visit transcript](../../hotel-visit/raw-notes/parkroyal-oct-visit-transcript.md), [LQA](https://lqagroup.com/about-us/), [Forbes Travel Guide](https://www.forbestravelguide.com/media-center). | A1 |
| 2 | The personalisation gap | Use the supplied report excerpt: first-time guests report less personalisation; everyday on-site interactions are less personalised than digital and high-touch interactions. Explain why first-time guests during their current stay are the chosen scope. The excerpt establishes a gap, not its causes. | A1 |
| 3 | What information hotels already have | Explain limited previous-stay history for new guests, what booking/pre-arrival information already exists, and how forms/manual notes capture preferences. Use the Parkroyal visit as a concrete example of guest data already being entered in the PMS; distinguish stored profile information from new insights shared during a stay. Show interview evidence of difficulties noticing, remembering and recording relevant information during busy service. Avoid claiming new guests have no information at all. | A1 |
| 4 | Why current approaches fall short: using guest knowledge | Explain current briefings, messaging and guest-profile retrieval. Use the Parkroyal example carefully: the transcript describes some PMS notes surfacing in the breakfast system, reports as a fallback, and staff needing to confirm and act on the information; it also describes cases where a cue may be missed. Show where relevant information does not reach or help the next employee in time. Treat allergy handling as a safety procedure, not as proof of a personalization benefit. Use observed partner-hotel practices rather than assumed failures. | A1 |
| 5 | Problem statement and scope | Define the gap in capture and availability of guest knowledge across interactions within a first stay. Specify staff roles, hotel setting, selected service scenarios and exclusions. | A1 |
| 6 | Design requirements | Present user need → measurable requirement → justification → verification method. Cover capture accuracy, correct guest association, timely access, recording effort and interaction disruption. Set justified targets; identify requirements not yet evaluated. | A1 |
| 7 | Generating possible solutions | Use a morphological chart to explore capture, guest association, storage/sharing, retrieval and presentation. Options include manual entry, speech-to-text, staff-confirmed guest selection, shared profiles, phones, earpieces and glasses. Form complete candidate concepts from these options. | A2 |
| 8 | Competitor and alternative-concept analysis; selected solution | Compare relevant commercial products and complete concepts against Slide 6. Examples: manual notes + phone; audio capture + earpiece; audio capture + glasses. Use justified criteria/weights, include disadvantages and costs, and conclude with the selected concept and accepted trade-offs. Identify what existing systems already provide—including the Parkroyal PMS-to-breakfast workflow and, after confirming details, its check-in vendor’s reported photo-recognition capability—and what your system adds. | A1, A2 |
| 9 | What will we personalise—and why? | Select two or three information categories and connect each to a service action during the same stay. Explain the supporting research or interview insight. Candidate examples are below. Mark choices awaiting validation as hypotheses. | A1, A2 |
| 10 | Proposed guest and staff journey | Storyboard: guest shares preference → relevant insight captured/checked → record updated → another employee retrieves it → personalised action. Show confirmation/correction and guest choice. Label proposed, implemented and simulated stages. | A2, A3 |
| 11 | System architecture | Show devices, processing server where used, extraction, guest database, retrieval and display. Explain guest association and data updates. Clearly distinguish implemented, simulated and planned functions. | A3 |
| 12 | Information capture: models, observations and preferences | Integrate model selection, technical design, prototype iterations, methods and results. Show how video inputs (including audio where used) become useful, evidence-linked observations and guest preferences. Compare candidate models using the same labelled clips, then explain actual changes and measured outcomes. See detailed examples below. | A2–A5 |
| 13 | Information retrieval: processing, activation and performance | Integrate local-to-server processing, latency and scalability evaluation, and the shift from continuous camera capture/retrieval to temple-touch activation with a 15-second silence timeout. Show processing flow, interaction state diagram, actual iterations, measurements and accepted trade-offs. | A2–A5 |
| 14 | Information display: useful context with less visual load | Integrate UI decisions and iterations: prioritised information, placement near the interaction area, text-to-icon changes, and display timing. Show before/after screenshots, explain each change and report technical results. Eye-contact and comfort improvements remain hypotheses until tested. | A2–A5 |
| 15 | Integrated demonstration and requirements check | Demonstrate the implemented capture → guest association → retrieval → display workflow. Follow with a table: requirement → target → evidence/result → status. Identify scripted inputs, preloaded profiles and simulated stages. Mark untested service benefits as not evaluated. | A3–A5 |
| 16 | Limitations and future work | Pair component and system shortcomings with feasible actions and tests. Include model inference errors, incorrect guest association, server/network dependencies, activation errors, battery measurements and lack of real-world evaluation. | A6 |
| 17 | Contribution and next milestone | Explain the demonstrated contribution, intended deployment, integration/training needs, realistic costs and genuine partner feedback. Keep improved personalisation, retention and spending as intended benefits pending field validation. End with the next project milestone. | A1, A6 |

Slides are content units: expand dense results slides or combine brief ones according to evidence and the scheduled presentation slot. For the interim assessment, the limit is 30 minutes for a group presentation or 15 minutes for an individual presentation, including any prototype demonstration. Rehearse to the applicable limit.

## Slide 9: candidate personalisation examples

| Information category | Information learned | Possible action during the same stay | Why consider it? |
|---|---|---|---|
| Purpose and schedule of visit | Guest mentions an early business appointment. | Another employee offers suitable breakfast or transport arrangements. | Links conversational information to practical assistance. |
| Dining preferences | Guest prefers vegetarian food or wants local cuisine. | Staff tailor dining suggestions and confirm current preferences. | Provides a concrete, repeatable recommendation scenario. |
| Special occasions | Guest mentions an anniversary. | Relevant staff offer an appropriate acknowledgement or celebration option. | Demonstrates continuity of attention across employees. |

These are proposed examples, not validated preferences of your target users. Choose categories using primary research and partner feedback. Name recognition can support interaction but need not be the principal personalised action. Allergy-related applications require confirmation and established food-service procedures; do not treat stored information as proof a meal is safe.

## Practical examples for design and evaluation slides

### Slides 7–8: separate generation from selection

- Morphological chart: list alternative ways to fulfil each function; it does not itself establish the best concept.
- Decision matrix: evaluate complete concepts against justified requirements. Do not compare a fully featured glasses system with deliberately weak alternatives.
- Competitors are actual products; manual workflows, phones and earpieces are alternative concepts. Name and cite commercial examples only after verifying their relevant capabilities.
- Keep the earlier current-practice discussion focused on why the problem persists. Use Slide 8 to explain design selection, avoiding repetition.

### Shared structure for Slides 12–14

Each component section should show:

1. **Requirement and rationale:** what the component must achieve and why.
2. **Initial design:** model, pipeline, device configuration or interface, with an icon/screenshot.
3. **Measurement:** test conditions, baseline, trial count and metric definitions.
4. **Iteration:** what actually changed, the observed issue prompting it, and the trade-off.
5. **Outcome:** before/after evidence and whether the requirement was met.

Use arrows and actual screenshots or clearly labelled image placeholders. Expand a component into more than one slide when necessary; numbering here identifies sections. Suggested iterations are not evidence that those changes have already been implemented or tested.

### Slide 12: information capture — video to useful guest knowledge

**Focus:** the models used to analyse and break down video inputs into useful observations and preferences. Name only models actually selected or evaluated; model names and versions are still to be supplied.

Suggested visual pipeline:

Video clip → visual/audio processing → observed events and explicit statements → relevant insight extraction → guest association and review → structured guest record.

Include audio transcription only if it is part of the implemented pipeline. Distinguish a directly observed event, a guest's explicit preference and an inferred preference. One observed action alone should not be presented as a confirmed lasting preference.

| Design question | Example iteration or comparison | Method and evidence |
|---|---|---|
| Which model best extracts useful insights? | Candidate multimodal model A → model B, or broad prompt → structured extraction prompt. | Same labelled clips, model versions, prompts and output schema; compare correct, missed and unsupported facts and processing time. |
| How much video should be processed? | Full clip → selected frames or shorter segments. | Compare latency, frames/data processed and insight recall; check whether sampling misses relevant events. |
| How should observations become preferences? | Free-form description → structured fields with evidence and confidence/review status. | Check relevance, unsupported inference rate, duplicate records and field completeness. |
| How are statements attributed? | Unverified clip-level extraction → guest association and confirmation. | Test multiple people/speakers, ambiguous statements and uncertain identities; report attribution errors. |
| How are preferences updated? | Repeated entries → deduplication and handling of corrections. | Test conflicting or time-specific statements; retain source/time and distinguish current-stay from enduring preferences. |

**Illustrative example:** “I prefer vegetarian food” can support an explicit dining-preference field. A guest selecting one vegetarian dish supports an observation; a lasting preference needs confirmation or further evidence.

Possible record fields: guest identifier, observation/preference category, value, source clip or statement, timestamp and review status. Present these as design examples unless implemented.

Suggested metrics: precision/recall of labelled insights, unsupported facts, incorrect guest attribution, processing time per clip and cost per clip. Report failures and dataset size. A faster model is not necessarily a better choice if it invents more preferences.

### Slide 13: information retrieval — processing and activation

**Iteration A: local → server processing**

Show glasses/local-processing icon → network arrow → server/database icon → return to glasses. Explain which tasks moved and which remain on the glasses. The intended goals are lower on-device processing delay and improved scalability; verify both rather than assume offloading always helps.

Measure end-to-end time from a defined trigger to correct information appearing. Break down capture, transfer, server queue/processing, database lookup, return and rendering. Compare local and server configurations under comparable workloads and report typical and slow-case latency.

For scalability, vary concurrent devices/requests and/or database size. Report latency, throughput and errors at each load. A server implementation alone does not demonstrate scalability; network overhead and server contention may offset processing gains.

**Iteration B: continuous capture/retrieval → staff-triggered active session**

Previous approach: continuous camera capture and repeated retrieval, creating an energy and processing burden.

Revised approach: temple touch starts the active session; the session continues while speech/audio activity is detected and stops after **15 continuous seconds without detected audio activity**. This outline interprets 15 seconds as an inactivity timeout, not a fixed session duration. Confirm that this matches the actual implementation and whether activity means any sound or detected speech.

Suggested state diagram:

Idle → temple touch → active capture/retrieval → audio activity resets silence timer → 15 seconds of silence → stop capture/retrieval and return to idle.

| Question | Example test | Useful result |
|---|---|---|
| Does offloading reduce delay? | Repeat identical retrieval tasks locally and via server. | Median and slow-case latency, n trials and correctness. |
| Can the system serve more users? | Increase concurrent clients and record response time/errors. | Throughput, latency under load and sustainable tested capacity. |
| Does activation reduce unnecessary work? | Replay the same interaction/idle schedule under continuous and triggered modes. | Active duty cycle, frames transmitted, retrieval calls and data volume. |
| Does it save energy? | Measure power or battery discharge over matched duration, brightness, network and workload. | Average power/energy or battery drain. Traffic reduction is only a proxy if power is unmeasured. |
| Does the timeout behave correctly? | Test silence, natural pauses, background noise, renewed speech and missed touches. | Actual shutdown timing, false stops and sessions kept active by noise. |

Additional candidate improvements: rate-limit repeated lookups; reuse a verified profile within a session; suppress duplicate requests; clear stale context after guest changes; show connection failure. These are optional examples, not claimed implemented features. Idle listening or audio detection may still consume energy and should be included in measurements.

### Slide 14: information display — UI iterations

**Focus:** show what is important, how the UI changed and why the change should help. Each before/after pair should identify the design variable, intended benefit, evidence and trade-off.

| UI iteration example | Intended improvement | What to evaluate |
|---|---|---|
| Corner-positioned information → position closer to the guest interaction area | Reduce gaze travel and support eye contact. | Compare glance direction/duration and guest-rated engagement. Avoid covering eyes or facial cues. Nearer placement does not enforce eye contact. |
| Long text → familiar icons with short labels where needed | Reduce visual clutter and information load. | Icon comprehension, interpretation errors and reading time. Unfamiliar or ambiguous icons may increase cognitive effort. |
| Full guest profile → prioritised context for the current interaction | Make relevant information easier to find. | Relevant-fact retrieval, omitted useful details and information density. Example: dining preference during meal service. |
| Persistent panel → brief or on-demand display | Reduce obstruction and sustained viewing demands. | Missed information, repeat activation and viewing duration; determine whether disappearance is too fast. |
| Small/dense text → larger type, spacing and suitable contrast | Improve legibility. | Recognition at actual display size, lighting and wearing conditions; balance legibility against field-of-view obstruction. |
| Dynamic face-following panel → stable position, if justified by actual trials | Reduce movement/jitter and calibration burden. | Position stability, tracking failures and readability. Do not claim fixed or dynamic placement is universally better. |

For eye discomfort, discuss plausible factors such as placement, viewing duration, contrast, brightness and headset fit. Assess comfort through an appropriate wearer study; a screenshot or successful rendering test cannot establish reduced discomfort. Record viewing duration and baseline, and distinguish informal internal feedback from real-world validation.

Technical checks can cover rendering delay, correct icon selection, update/clear reliability and stale data. Claims about improved eye contact, reduced overload and comfort remain intended benefits until tested.

### Slide 15: integrated demonstration and scorecard

Show one coherent same-stay scenario. Example: a guest explicitly shares a dining preference; the system captures and associates it; another employee triggers retrieval; the glasses show concise relevant context. Disclose simulated stages.

| Requirement | Target | Evidence/result to insert | Status |
|---|---|---|---|
| Relevant insight extraction | Justified accuracy threshold | Labelled clip results, unsupported facts and attribution errors | Met / partly met / not met / not evaluated |
| Retrieval delay | Justified end-to-end time | Local → server latency with conditions and n | Same status options |
| Correct guest association | Justified error threshold | Known/unknown guest results and false matches | Same status options |
| Scalability | Defined client/load requirement | Load-test capacity, latency and error rate | Same status options |
| Controlled activation | Temple touch; 15-second silence timeout | Trigger and timeout tests; noise failure cases | Same status options |
| Reduced energy use | Justified power/energy target | Matched power/battery test; label proxies clearly | Same status options |
| Reliable information display | Defined update/clear target | Rendering and stale-context checks | Same status options |
| Eye contact, comfort and low information load | User-study criteria | Not yet established without appropriate evaluation | Not evaluated where untested |
| Improved first-stay personalisation | Defined service outcomes | No real-world service-effectiveness study completed | Not evaluated |

## Unresolved issues and evidence still needed

1. **Central value proposition is not validated.** Component tests do not establish improved personalised service, natural engagement, retention or spending. Frame current achievement as technical feasibility within the functions and conditions actually tested.
2. **End-to-end capability versus isolated components.** Fast recognition and fast database retrieval separately do not prove a fast complete interaction. Measure the integrated pipeline if claiming end-to-end performance.
3. **Personalisation categories remain to be justified.** Select the most relevant categories through partner input and existing research. Explain why staff can act on them during the same stay.
4. **Requirement targets need justification.** Tie thresholds to service needs, relevant research, partner input or an explicit engineering rationale. Do not choose targets retrospectively to match results.
5. **Guest association and information correctness remain critical.** Explain handling of unknown guests, uncertain matches, ambiguous information, corrections and stale records according to actual implementation.
6. **Real-world user testing is future work.** A possible next study compares equivalent tasks with the existing workflow and glasses, measuring correct use of guest information, repeated questions, lookup interruptions and staff/guest feedback. Use a suitable approved setup and state sample and setting limitations.
7. **Concept selection must be defensible.** Include disadvantages, credible alternatives and reasons for criteria/weights. A selected concept need not outperform every alternative on every criterion.
8. **Adoption potential needs supporting evidence.** Use documented partner feedback, integration plans, training needs and realistic costs. Do not present interest in testing as a purchase or adoption commitment.
9. **Evidence boundaries must be explicit.** The supplied report excerpt supports lower reported personalisation for certain guest groups and touchpoints; it does not prove the proposed causes. Support capture/sharing barriers with your interviews or other appropriate evidence.

10. **Activation semantics need confirmation.** Confirm whether 15 seconds means continuous silence, whether background sound resets the timer, and what processing remains active in idle mode.
11. **Offloading and energy benefits need separate evidence.** Measure network/server effects, concurrent-load behaviour and energy use; lower request volume does not alone prove longer battery life.
12. **Video observations are not automatically preferences.** Identify which facts are explicit, observed or inferred; evaluate unsupported inference and attribution errors.
13. **UI benefits need appropriate validation.** Placement and icons may support engagement and reduce clutter, but do not establish better eye contact, reduced discomfort or lower cognitive load without tests.

## Rubric coverage and remaining risks

| Interim criterion | Where addressed | What is needed beyond having a slide |
|---|---|---|
| A1: Objective, scope and context | 1–6, 9, 17 | Feasible scope, justified specifications, a compelling value proposition, and relevant, authoritative, current context. |
| A2: Methodology / concept development | 7–10, 12–14 | Systematic evaluation of the chosen approach and credible alternatives, with reasoned trade-offs. |
| A3: Fabrication of prototypes | 10–15 | Clear prototype purpose, sound technical principles, and evidence of actual implementation. |
| A4: Testing | 12–15 | Appropriate, repeatable tests with clear purposes, methods, conditions and results. |
| A5: Analysis | 12–15 | Explain important results, variability and failures; distinguish component results from integrated-system findings. |
| A6: Problems and project plan | 16–17 | Identify shortcomings and provide feasible remedies, next steps and milestones. |
| B1: Presentation material | Throughout | Professional, organized, accurate slides with clear annotated illustrations, labels, units and citations. |
| B2: Delivery and presentation skills | Rehearsal and live presentation | Logical, concise flow; confident delivery; controlled pace and timing. |
| B3: Response to questions/comments | Q&A and backup material | Thoughtful, accurate, concise answers supported by methods, evidence and limitations. |
| C1–C4: Effort and initiative | Ongoing project work | Motivation, meeting preparation, independent inquiry, ownership and resourcefulness are assessed by supervisors throughout the semester, not by adding a slide. |
| Online report/documentation | Separate deliverable | Follow the report word limit and identify each member’s individual work in the documentation; this is not B1–B3 presentation material. |

Coverage of every rubric topic does not guarantee the highest achievement level. The principal remaining assessment risk is the gap between technical component validation and the intended service benefit.

## Useful backup slides

- Full decision matrix and justification of weights.
- Test protocols, trial counts and detailed results.
- Device specifications and cost assumptions.
- Guest association, corrections and failure handling.
- Individual team contributions and implementation ownership.
- Proposed real-world evaluation and deployment workflow.
- Full references for all primary and secondary evidence.
