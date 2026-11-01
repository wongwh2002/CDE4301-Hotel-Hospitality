# Hotel personalisation project: revised presentation outline

## Presentation focus

Enable increasingly personalised service for first-time hotel guests within the same stay by capturing relevant, guest-approved insights and making them accessible to the next relevant staff member. Smart glasses are the selected concept to justify and evaluate, rather than the starting assumption.

The outline retains the agreed first six slides, combines concept selection with competitor analysis, places the demonstration after testing methods, and evaluates technical components without claiming completed real-world user validation.

## Revised outline

| Slide | Title and purpose | Content and suggested examples | Rubric |
|---|---|---|---|
| 1 | Why personalisation matters | Open with: “Think of a time someone remembered your usual order. How did that make you feel?” Connect recognition to hotel service. Present evidence on satisfaction, spending and retention, distinguishing stated intentions from measured behaviour. | A1 |
| 2 | The personalisation gap | Use the supplied report excerpt: first-time guests report less personalisation; everyday on-site interactions are less personalised than digital and high-touch interactions. Explain why first-time guests during their current stay are the chosen scope. The excerpt establishes a gap, not its causes. | A1 |
| 3 | Why current approaches fall short: learning about guests | Explain limited previous-stay history for new guests, what booking/pre-arrival information already exists, and how forms/manual notes capture preferences. Show interview evidence of difficulties noticing, remembering and recording insights during busy service. Avoid claiming new guests have no information at all. | A1 |
| 4 | Why current approaches fall short: using guest knowledge | Explain current briefings, messaging and guest-profile retrieval. Show where relevant information does not reach the next employee in time. Example: a dining preference shared with reception is unavailable during a later restaurant interaction. Use observed partner-hotel practices rather than assumed failures. | A1 |
| 5 | Problem statement and scope | Define the gap in capture and availability of guest knowledge across interactions within a first stay. Specify staff roles, hotel setting, selected service scenarios and exclusions. | A1 |
| 6 | Design requirements | Present user need → measurable requirement → justification → verification method. Cover capture accuracy, correct guest association, timely access, recording effort and interaction disruption. Set justified targets; identify requirements not yet evaluated. | A1 |
| 7 | Generating possible solutions | Use a morphological chart to explore capture, guest association, storage/sharing, retrieval and presentation. Options include manual entry, speech-to-text, staff-confirmed guest selection, shared profiles, phones, earpieces and glasses. Form complete candidate concepts from these options. | A2 |
| 8 | Competitor and alternative-concept analysis; selected solution | Compare relevant commercial products and complete concepts against Slide 6. Examples: manual notes + phone; audio capture + earpiece; audio capture + glasses. Use justified criteria/weights, include disadvantages and costs, and conclude with the selected concept and accepted trade-offs. Identify what existing systems already provide and what your system adds. | A1, A2 |
| 9 | What will we personalise—and why? | Select two or three information categories and connect each to a service action during the same stay. Explain the supporting research or interview insight. Candidate examples are below. Mark choices awaiting validation as hypotheses. | A1, A2 |
| 10 | Proposed guest and staff journey | Storyboard: guest shares preference → relevant insight captured/checked → record updated → another employee retrieves it → personalised action. Show confirmation/correction and guest choice. Label proposed, implemented and simulated stages. | A2, A3 |
| 11 | System architecture | Show devices, processing server where used, extraction, guest database, retrieval and display. Explain guest association and data updates. Clearly distinguish implemented, simulated and planned functions. | A3 |
| 12 | Engineering decisions | Justify device choice, local versus server processing, identification and retrieval methods. Explain latency, accuracy, connectivity and resource trade-offs using measurements, calculations or relevant technical principles. | A2, A3 |
| 13 | Interface design for live interactions | Show actual display variants: placement, text/icons, prompt length, prioritisation and activation/dismissal. Explain readability and attention trade-offs. Label claims about eye contact or natural engagement as unvalidated if no user tests exist. | A2, A3 |
| 14 | Prototypes and iterations | Show actual versions as question/purpose → prototype → observation → design change. Example, only if conducted: move from dynamic to fixed positioning after calibration difficulties. Explain the purpose of each prototype and the engineering work performed. | A3, A5 |
| 15 | Component testing methods | State questions, setup, conditions, repetitions, baseline and metrics. Define latency endpoints. For recognition, explain enrolled identities, unknown people, distance, lighting and success/error definitions. Distinguish component tests from integrated-system tests. | A4 |
| 16 | Prototype demonstration | Demonstrate currently working functions after explaining evaluation methods. Show information capture and later retrieval if implemented. Disclose preloaded profiles, scripted inputs and simulated stages. Have a backup recording. This demonstrates operation, not validated usability. | A3 |
| 17 | Component results and analysis | Report actual latency, recognition accuracy, extraction accuracy or other tested metrics. Include sample sizes, variation, operating conditions and failure cases. Explain causes and trade-offs. Split into additional slides by component if needed. | A4, A5 |
| 18 | Achievement against requirements | Table: requirement → target → measured result → met/partly met/not met/not evaluated. Separate component performance from end-to-end performance. Mark personalisation effectiveness and real-world usability as not evaluated where appropriate. | A5 |
| 19 | Limitations and future work | Pair component and system-level shortcomings with feasible actions and validation methods. Include lack of real-world testing, staff attention, guest acceptance, information relevance, connectivity and integration where applicable. Prioritise the most consequential limitations. | A6 |
| 20 | Real-world potential and contribution | Explain demonstrated technical contribution, deployment setting, integration/training needs, indicative costs and genuine partner interest. Present improved service, retention or spending as intended benefits pending validation. End with the next development milestone. | A7 |

Slides are content units: expand dense results slides or combine brief ones according to evidence and presentation time. The supplied final-assessment brief allows up to 40 minutes for group presentations; confirm any separate instructions for the actual assessment session.

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

### Slides 15 and 17: component testing examples

| Component/question | Example method | Results to present |
|---|---|---|
| End-to-end retrieval latency | Measure elapsed time from a defined trigger to usable information appearing on the display, across repeated trials under stated network conditions. | Trial count, median, spread and slow cases; optionally break down capture, transfer, processing and rendering. |
| Guest recognition/association | Use a defined set of enrolled identities and unknown people under specified distances, lighting and poses. | Correct identification, false matches and rejection/missed identification, with denominators and conditions. |
| Preference extraction, if implemented | Compare extracted facts with manually labelled statements from a fixed test set, including ambiguous or irrelevant statements. | Correct, missed and incorrectly added facts; errors linking information to a guest. |
| Display behaviour | Verify update, clearing, activation and stale-information handling with repeatable technical scenarios. | Observed success/failure and limitations. Technical correctness does not prove readability or low distraction. |

Use identical conditions where feasible for device comparisons. Show only measurements actually collected; label planned tests and hypotheses separately.

### Slide 18: example requirement scorecard structure

| Requirement | Target and justification | Actual result | Status |
|---|---|---|---|
| Information displayed within acceptable delay | Insert a justified target. | Insert measured end-to-end result and conditions. | Met / partly met / not met |
| Correct guest association | Insert justified error thresholds. | Insert actual test results. | Met / partly met / not met |
| Minimal disruption to face-to-face service | Define a future comparative user test. | No real-world user evaluation completed. | Not evaluated |
| More relevant personalisation across staff | Define how a later employee should use newly learned information. | No service-effectiveness study completed. | Not evaluated |

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

## Rubric coverage and remaining risks

| Criterion | Where addressed | What is needed beyond having a slide |
|---|---|---|
| A1: Objective, scope and context | 1–6, 9, 18 | Feasible scope; justified specifications; compelling value; relevant, authoritative and current sources. |
| A2: Methodology/concept development | 7–8, 12–13 | Systematic evaluation of alternatives and reasoned trade-offs. |
| A3: Prototypes | 10–14, 16 | Clear prototype purposes; sound technical principles; evidence of actual implementation and workmanship. |
| A4: Testing | 15, 17 | Appropriate, repeatable tests for the claims made. Component-only tests leave service-effectiveness claims untested. |
| A5: Analysis | 14, 17–18 | Explain results, variability and failures with appropriate methods; distinguish component and integrated-system findings. |
| A6: Future work | 19 | Identify major shortcomings and provide feasible, justified remedies and evaluation plans. |
| A7: Impact/visibility | 20 | Credible potential beyond the module, supported by evidence rather than assumed business benefits. |
| B1–B3: Report | Separate documentation | Logical organisation, annotated illustrations and complete consistent references. Slides alone do not satisfy report criteria. |
| C1: Presentation materials | Throughout | Professional, readable visuals; labelled axes/units/sample sizes; accurate citations; consistent formatting. |
| C2: Delivery | Throughout | Logical, concise delivery; rehearsed transitions and demo; time management. |
| C3: Questions | Preparation and backup slides | Accurate, thoughtful answers supported by methods, technical details and evidence boundaries. |
| D1–D4: Effort and initiative | Supervisor-observed work | Motivation, preparation, independent inquiry and ownership throughout the project; cannot be established solely by presentation claims. |

Coverage of every rubric topic does not guarantee the highest achievement level. The principal remaining assessment risk is the gap between technical component validation and the intended service benefit.

## Useful backup slides

- Full decision matrix and justification of weights.
- Test protocols, trial counts and detailed results.
- Device specifications and cost assumptions.
- Guest association, corrections and failure handling.
- Individual team contributions and implementation ownership.
- Proposed real-world evaluation and deployment workflow.
- Full references for all primary and secondary evidence.
