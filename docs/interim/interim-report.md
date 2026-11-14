# Guest-context cues for personalised hotel service

**CDE4301 Innovation & Design Capstone · Interim assessment · Team IS-432**  
**Team:** Neha Rajan · Tan Ping Hui · Wong Weng Hong · Nigel Yeo Tong Wei  
**Presentation:** 5 November 2026 · **Report prepared:** 10 November 2026  
**Case setting:** PARKROYAL club lounge · **Stage:** Semester 1 proof of concept

<!-- REPORT_BODY -->

## Executive summary {#executive-summary}

Hotels can collect guest preferences without consistently turning them into useful service at the next encounter. This project investigates how luxury-hotel staff could capture, share, and retrieve relevant guest context during the same stay, particularly when a first-time guest has little prior service history. The initial application is food-and-drink service in a club lounge. The intended value is continuity between employees: something a guest tells one employee becomes available to the next, at a suitable moment.

Semester 1 produced a working smart-glasses recognition-and-display prototype, a separate lounge-services scaffold, early preference-extraction experiments, and formative testing. The Rokid application tracks faces locally, sends a selected face crop to a laptop for recognition, and displays a recognised name with one or two fictional preference/allergy cues. A temple tap activates the session; 15 seconds without detected speech ends it. Automatic conversation-to-profile updating and contextual cue selection remain development tasks. [P1](#p1), [P3](#p3)

Four documented successful warm rendering samples averaged **1.18 seconds** from handled temple tap to Android frame commit, above the project's provisional sub-second target. A team-confirmed 20-minute comparison reported battery-level drops of **28 versus 9 percentage points** for continuous and triggered operation. In a walkthrough with **10 non-hotel participants**, all described activation as easy and 70% saw potential usefulness, but incorporating cues naturally remained difficult. These findings support further development; they do not establish improved guest satisfaction, recognition accuracy, or hotel revenue. The next phase prioritises reliable extraction, relevant cues, and comparison with ordinary profile lookup using hotel staff. [P1](#p1), [P4](#p4), [P7](#p7)

## 1. Context, evidence, and design opportunity {#context}

### 1.1 From hotel performance to an actionable service problem

The presentation begins with a hotel-management concern: preserving service quality while manpower and operating costs rise. Revenue per available room, RevPAR, equals average daily rate multiplied by occupancy expressed as a fraction. Personalised service might influence guest evaluations and future choices, but many other factors affect those financial measures. Neither a working wearable nor a positive usability response demonstrates increased RevPAR. The present project therefore measures the nearer outcomes it can influence: accurate information, timely retrieval, and an appropriate service action. [P1](#p1)

Here, **personalisation** means using relevant, permitted knowledge about an individual guest to adapt an interaction or service. Recognition, context access, service adaptation, and the guest's perception of fit are separate steps. Lei et al.'s three-study investigation shows that a hotel's personalisation attempt need not be perceived as personal by its recipient. This distinction makes cue comprehension and relevance necessary evaluation outcomes alongside technical performance. [R1](#r1)

Medallia's study of 1,749 U.S. hotel guests found a relationship between perceived personalisation and satisfaction, with opportunities to improve ordinary interactions during a stay. Its findings are survey associations from a vendor-produced report. Piccoli, Lui, and Grün's observational hotel study also connects structured preference capture with service/value evaluations and booking-channel behaviour. These sources justify investigating continuity of guest knowledge; they do not prove that glasses cause loyalty or profit. [R2](#r2), [R3](#r3)

### 1.2 What the fieldwork establishes

The team investigated hotel operations through visits and stakeholder discussions. Two documented cases are particularly useful. They describe different properties and should retain that distinction. [P2](#p2)

| Setting and evidence | Relevant observation | Design implication |
|---|---|---|
| Novotel Singapore on Stevens; formatted visit notes | ACDC guest profiles, pre-arrival review, role-dependent access, and memory or hardcopy aids in F&B service were described. | Test whether relevant context can be retrieved during an encounter with less searching. ACDC belongs to this Accor example. |
| PARKROYAL; visit summary and later discussion transcript | Interest in lounge guest recognition; guest information already entered into a PMS; some notes surfaced through the breakfast system, with reports as a fallback. | Build on existing information flows. Investigate where visibility, confirmation, or action still breaks down. |
| Interim presentation and walkthrough | The team described delayed manual entry, inconsistent interpretation, and difficulty referring to notes during conversation. | Treat timely capture and natural interaction as requirements, then measure them in the target workflow. |

PARKROYAL's existing PMS-to-breakfast flow is significant: the problem is more specific than an absence of guest data. The notes are qualitative evidence, not a measured incidence of missed preferences. Unclear system names and numerical claims in the noisy visit transcript require confirmation before becoming specifications.

First-time guests motivate the same-stay focus because little historical interaction data may exist. They can nevertheless supply booking details, pre-arrival preferences, requests, and conversational context. The design opportunity is to make that emerging knowledge useful during the current stay. The presentation's single-digit retention statement is stakeholder-reported; no cohort definition or retention dataset is available for analysis. [P1](#p1), [P2](#p2)

### 1.3 The service opportunity

An illustrative case is a guest telling one employee that they usually drink coffee with oat milk. A later server can offer that option and confirm whether the guest wants it now. Remembering the statement supports continuity; automatically treating every past order as a permanent preference would undermine it. A complaint that a drink is too sweet is also time-specific evidence, rather than permission to infer every future beverage choice.

The lounge offers a bounded place to study repeated food-and-drink encounters and staff handovers. The project records permission to use PARKROYAL's lounge as a POC setting; the conditions for staff participation, live guest data, and biometric testing still need to be established. [P2](#p2), [P6](#p6)

<div class="flow" role="group" aria-label="Proposed service continuity loop">
<div><b>01 · Capture</b>A guest states a preference.<small>Emerging capability</small></div>
<div><b>02 · Check & share</b>Staff confirm the guest and meaning.<small>Planned approval workflow</small></div>
<div><b>03 · Retrieve</b>The next employee sees relevant context.<small>Demo profiles implemented</small></div>
<div><b>04 · Adapt</b>Staff make a suitable offer and confirm it.<small>Service benefit to evaluate</small></div>
</div>

These problem findings lead to the solution requirements in [Chapter 2: Aim, scope, and requirements](#requirements).

## 2. Aim, scope, and requirements {#requirements}

The design question is:

> How might we enable luxury-hotel staff to capture, share, and access relevant guest information seamlessly, so they can deliver consistently personalised, high-quality service?

**First-time guest use case.** A first-time guest may already have booking or pre-arrival information, but often has less recorded service history for staff to draw on. The design target is to use an early interaction to establish one useful, guest-confirmed detail for the current stay, then make it available to another employee when relevant. This does not assume every new guest has no information or that a single comment is an enduring preference. A visit-specific request remains scoped to that encounter or stay unless the guest or an authorised record confirms otherwise. The lounge prototype explores recognition, retrieval, and concise cues using fictional profiles and manual activation; production PMS integration and demonstrated service outcomes remain outside the current evidence. [P1](#p1), [P3](#p3)

**Functional requirements.** The solution has two linked functions: capture and process guest context, then select and display the information staff need for the current service moment.

| Function | Required behaviour and boundary |
|---|---|
| **Capture and process** | Record a guest-stated preference, request, or concern with its source and time. Keep explicit statements distinct from staff observations and model inferences; retain enough supporting wording for staff to review a draft. |
| **Associate and prepare** | Associate a draft with a likely guest and current stay only when the evidence is sufficiently strong. Keep the scope, source, timestamp, and review state. If identity or meaning is uncertain, ask staff to resolve it or leave the information unlinked. |
| **Review and carry forward** | Let staff correct the wording, confirm the guest and stay, and approve the record before it becomes shared context. Make a confirmed detail available to another employee; do not silently convert a one-off request into a permanent preference. |
| **Select and display** | Select the smallest detail relevant to the current service task and show it as a concise, actionable cue. Do not display raw transcripts or unrelated profile fields. Suppress personal cues when a match is uncertain, and retain normal greeting or manual profile lookup as the fallback. |

This makes the first-time guest goal explicit: one early, confirmed detail can support a later interaction during the same stay, even before a long service history exists. In the proposed complete workflow, one deliberate tap starts recognition and conversation capture together. Audio capture, reviewed record updates, and the complete next-employee handover are not integrated in the current glasses path; any recording study also needs an approved purpose and participant protocol. The current demonstration covers narrower recognition, prepared-profile retrieval, and cue-display stages. [P1](#p1), [P3](#p3)

**Service criteria and proposed measures.** The project-selected PARKROYAL F&B LQA subset includes acknowledgement within one minute of lounge entry and an offer to take a drinks order within three minutes of seating. These are staff-action windows, not system-latency targets. The selected 15-item table is a departmental subset rather than a complete audit or an official LQA score; LQA assessment is also distinct from hotel star classification. [P8](#p8), [R4](#r4)

| Criterion | Service behaviour | Requirement and proposed measure | Interim evidence |
|---|---|---|---|---|
| **DR1 · On-time service support** | Timely acknowledgement and offer of service. | Make the first correct, readable cue available within **1.0 s** of deliberate activation when a supported guest match and relevant context are available. Measure activation-to-first-correct-visible-cue latency, target-attainment rate, and late, missing, or incorrect cues; separately time the staff service action. | Four successful warm frame commits averaged 1.18 s. The full trigger-to-visible-cue target, failures, and latency distribution remain unestablished. |
| **DR2 · Low-effort capture** | Active listening and natural engagement. | Start capture with one deliberate action and avoid lengthy note-taking. Measure activation and capture time, actions, correction effort, and disruption to conversation. | Single-tap activation and a 15-second no-speech timeout are implemented; realistic speech/noise and end-to-end capture remain to be evaluated. |
| **DR3 · Glanceable interaction** | Natural, friendly engagement and discreet use of the guest's name. | Keep the cue short and understandable during conversation. Measure correct comprehension, glance duration, attention shifts, and interruption. | Name and concise cues render in the prototype. Formative feedback supports readability but reports difficulty using cues naturally. |
| **DR4 · Preference continuity** | Use confirmed context to personalise service. | Preserve source, time, stay scope, and review status. Measure whether the correct approved detail reaches another employee in time and is interpreted correctly. | A shared demo store exists, but reliable extraction and the complete approval-to-next-employee path remain incomplete. |

**Cross-cutting safeguards.** DR5 suppresses personal cues for unknown, ambiguous, lost, or stale tracks. DR6 minimises displayed fields, distinguishes preferences from allergies, and keeps a manual fallback. An allergy cue is a prompt to check the authorised guest record and the relevant menu or kitchen source; a face match does not establish that food is safe. Current suppression paths exist but field false-reveal rates are unmeasured. Fictional allergy cues demonstrate display only; operational verification, access roles, and participant handling need review.

**Timing rationale and boundary.** The report adopts **1.0 s** as the proposed cue target; the supplied slide labels it **<1 s**. Shiwa et al. (2009) found that preference for a communication robot's response peaked at one second. Applying that result to a visual hotel-service cue is an analogy to test, not a smart-glasses standard or an LQA requirement. [R12](#r12)

For the visual prototype, timing starts when staff deliberately activate the interaction and ends when the first correct, readable cue appears on the glasses. This end-to-end interval includes capture, guest association, transfer, and rendering; measuring server processing alone would omit important delays. Keep cold and warm trials, count all valid attempts, and report latency distributions (including p50 and p95), target attainment, late or missing cues, and incorrect cues separately. On unknown-guest trials, assess correct suppression and fallback rather than expecting a personal cue.

Four successful warm frame commits averaged **1.18 seconds**. That small successful-only set exceeds the proposed one-second target but cannot establish the complete trigger-to-visible-cue latency, target-attainment rate, p95 performance, or physical lens visibility. [P3](#p3), [P4](#p4)

These requirements define the functions and safeguards that each concept must support. [Chapter 3: concept generation and selection](#concepts) compares complete workflows against the same first-stay service scenario.

## 3. Concept generation and selection {#concepts}

The concepts address the same first-stay scenario: a guest shares a preference early in the stay, and another employee needs it during a later service interaction. We compare complete workflows while keeping guest information, task, and staff review support as consistent as possible. [P1](#p1)

| Comparison row | Phone/PMS baseline | Audio badge + earpiece | Camera-free glasses hybrid | Vision-assisted smart glasses |
|---|---|---|---|---|
| **Capture** | Staff enters a note in the existing profile after or during the interaction; familiar, but screen use and delayed entry may interrupt or lose detail. | A deliberate push-to-talk action captures speech hands-free; noise, speaker attribution, and correction needs require testing. | The microphone captures speech after a deliberate trigger; a companion interface selects or confirms the guest. | Triggered microphone capture adds visual context from the camera, with greater collection and battery demands. |
| **Guest and stay association** | Staff selects the guest and stay in the profile; the step is visible and correctable but takes time. | Staff still selects or confirms the guest and stay in a companion interface; speech does not identify its speaker by itself. | The same explicit selection avoids face matching and helps isolate the display's value. | Vision can suggest a guest match and reduce lookup when correct; ambiguous or unstable matches must not reveal profile details. |
| **Processing and review** | The existing profile workflow handles the note; the staff member checks what they entered. | A transcript can become a structured draft, but staff checks the wording and confirms the guest and stay before saving. | Use the same processing and staff-review path as the audio concept, so the display can be compared separately. | Use the same draft and review path; recognition is an association aid, not approval to save or act on an inferred preference. |
| **Cue delivery** | The phone offers profile detail but requires staff to look down and navigate. | A short earpiece cue can be private and hands-free; audibility, comfort, and comprehension in a noisy lounge need testing. | A concise in-lens cue keeps information near the line of sight without a camera. | A concise in-lens cue can follow a visual match, but may draw attention from the guest or affect eye contact. |
| **Staff effort** | Manual navigation and note entry add steps, though the workflow uses familiar equipment. | Capture is hands-free, but guest selection and companion-interface review remain. | Capture and glanceable display may reduce device switching; fitting, controls, and review still take effort. | It may combine capture, association, and cue delivery, while confirmation and camera/display setup add work. |
| **Privacy and comfort** | No new wearable sensor is needed, but viewing a profile in front of the guest may feel intrusive. | No camera is used; recorded speech still needs clear purpose, access, retention, and guest-notice decisions. | A microphone and display still affect privacy and comfort; removing the camera reduces visual collection. | Camera, microphone, and display create the greatest face-data, recording, comfort, and acceptance questions. |
| **Integration and fallback** | Uses the current profile and phone path, with manual lookup as the baseline. | Needs a reliable mic, speech processing, and earpiece; use phone/PMS if capture fails. | Also needs a working microphone, display, companion selection, and device link; fall back to phone/PMS. | Needs a validated camera/display link and safe matching against the active guest set; on uncertainty or device failure, suppress cues and use phone/PMS. |

The row-by-row comparison makes the trade-off clearer: audio capture avoids a camera but still needs reliable speaker and guest association; glasses can provide an eye-line cue, and the vision-assisted version may reduce manual lookup while introducing face-matching risk. The camera-free glasses variant is a useful control: comparing it with audio tests the display, while comparing it with vision-assisted glasses tests whether visual matching adds enough value to justify its cost and risk. These are hypotheses, not measured advantages.

### Why carry forward smart glasses as a package

The first-time-guest problem is not simply remembering a preference. A first-time guest may have little useful prior-stay history, and information shared in one encounter may not reach the employee handling the next. The concept therefore links five functions: capture what the guest says during service; associate it with the correct guest and current stay; turn it into a consistent draft with its source and uncertainty visible; let staff review and confirm it before saving; then select a task-relevant cue for a later service moment. Each function addresses a different break in continuity: without capture, the request can be lost; without correct association, it can be attributed to the wrong person; without review, an inference can be recorded as fact; without a concise cue, staff still need to stop and search the profile; without a confirmed handover, the next employee may not receive the useful detail. [P1](#p1)

Smart glasses are being prototyped as a package because a wearable workflow could combine staff-triggered capture, contextual association, and a concise cue near the service moment, while a companion review path carries confirmed information forward. This is a design hypothesis, not evidence that glasses outperform the alternatives. An audio badge and earpiece could also support hands-free capture and private cue delivery, but still need reliable guest/stay association, review, and handover. The phone/PMS is the familiar baseline and fallback. Camera-free glasses can help isolate whether the visual output adds value; vision-assisted glasses test whether matching adds enough value to justify its accuracy, privacy, comfort, and integration costs. The functions should be assessed individually and then as a complete workflow.

The specific reason to test the glasses display against an audio-only cue is that a short, silent fact or action prompt can be checked without adding another voice to the guest conversation and can remain available for a deliberate recheck. A cue such as “confirm unsweetened tea” can guide staff while leaving them to choose natural wording, rather than asking them to listen to and repeat a full script. This may fit a face-to-face service exchange. The trade-off is visual attention and reading load, with possible effects on eye contact. The display is a starting hypothesis to compare with equivalent audio, not a settled advantage.

### Visual cues compared with audio cues

The service encounter is already a conversation: staff need to listen, observe the guest, and decide when to speak or act. A cue is useful only if it supports that decision without making staff miss something more important. The comparison below isolates the **output channel** as far as possible; it is design reasoning, not a result from a hotel-staff trial.

A visual cue can keep a short detail available for a brief recheck without adding another spoken message. However, a heads-up display does not guarantee that attention remains on the guest. Lewis and Neider (2016) found that secondary information on Google Glass disrupted a concurrent visual-search task across five laboratory experiments. Their study did not test hotel conversations or compare earpieces, so it supports measuring interruption rather than assuming that a display is distraction-free. [R9](#r9)

An audio cue avoids reading a display and may help when staff are visually occupied or request information between conversational turns. But a spoken prompt that feeds staff a suggested sentence could become distracting if it arrives while the guest is speaking: the wearer must process the guest and a second verbal message, and may miss words or delay a response. Brungart (2001) found interference between simultaneous spoken phrases; applying this result to staff guidance through an earpiece is an inference, not a direct hotel study. A short factual prompt on request or during a pause is a testable alternative to a full spoken script. [R13](#r13)

Studies do not establish a universal winner. In a continuous visual-tracking experiment, Nees and Sampsell (2021) found simple visual alerts more disruptive to tracking than auditory tones; the auditory condition had lower workload when no noise was present. Ward, Smith, and Helton (2023) compared words delivered on an HMD, on the same visual plane as the task, or audibly: HMD and audio words both impaired manual tracking relative to tracking alone, while same-plane visual words did not. In a face-to-face AR-glasses study with 32 participants in 16 pairs, Rzayev et al. (2020) found that notification position and alignment affected how people perceived the notifications. Together, these studies suggest that cue content, placement, timing, ambient noise, and the task matter. None tests spoken service suggestions through an earpiece while hotel staff listen to guests, so they support a matched prototype trial rather than a claim that the screen is less distracting. [R14](#r14), [R15](#r15), [R16](#r16)

| Service question | Proposed visual-cue approach | Proposed audio-cue approach | What to compare |
|---|---|---|---|
| **Can staff keep listening?** | Show a small amount of information without adding speech. | Play a brief message on request or at a suitable pause. | Missed guest details, overlapping messages, and conversational interruptions. |
| **Can staff recover a missed detail?** | Keep the cue available briefly for a deliberate second glance. | Provide a simple replay action. | Recovery time, repeated glances or replays, and interpretation accuracy. |
| **What happens in difficult surroundings?** | Test contrast, placement, and readability against changing backgrounds. | Test intelligibility amid lounge noise and conversation. | Correct comprehension under matched quiet and busy conditions. |
| **Does the cue help the service action?** | Use a concise label or understood symbol tied to the task. | Speak the equivalent fact in a short phrase. | Correct offer or response, assistance required, and time until staff can act. |
| **Is it acceptable to wear and use?** | Assess fit, visual obstruction, perceived attention, and guest comfort. | Assess earpiece fit, environmental awareness, volume, and audio leakage. | Staff and role-play guest feedback, alongside observed task performance. |

For example, the same encounter could convey that a guest requested unsweetened tea earlier in the stay. One condition could show a short visual label; another could speak the equivalent phrase. Both must support the same decision: whether and how to confirm the preference now. Keep the information, task, capture and processing support, and guest-selection method constant while changing the output. For speech, measure both time to playback onset and time until the actionable fact has been conveyed. Google's AI-glasses guidance supports brief, glanceable elements that appear when needed and recede afterwards, but the project device still needs evaluation. [R8](#r8)

The audio badge and earpiece were discussed as an alternative concept; they were not implemented or comparatively tested. A camera-free glasses condition can help isolate the value of a visual cue from face matching, while a vision-assisted condition tests whether camera-based association adds enough value to justify its privacy, accuracy, comfort, and integration costs.

For a fair evaluation, give each concept the same guest information, service task, and staff-review support. Measure capture time, correct guest/stay association and errors, unsupported notes, time to a usable cue, staff interruption, comprehension, privacy and comfort, and effort. Treat privacy and safe association as pass/fail constraints; score other criteria only after weights are justified with staff or partner input. For each comparison row, record capture time/correction effort; correct and false associations; evidence-supported notes/edit time; cue latency/comprehension; interaction steps/interruption; privacy/comfort; and integration failures/recovery. A morphological chart should generate combinations of capture, association, processing, and output methods; a separate decision matrix should assess the complete workflows.

Smart glasses remain the concept selected for further prototyping because the package could join guest-stated capture, supported guest/stay association, staff-reviewed preference handling, and a concise cue at a later service moment. This could reduce the gap between what a first-time guest shares and what the next employee can use. The reason to prototype glasses is therefore the possible fit of the complete service workflow, not a demonstrated advantage of its screen over audio. The comparison has no weighted scores or comparative hotel-staff results, and the glasses direction remains subject to the camera/display integration gate and the [requirements already defined for the project](#requirements).

Existing products establish substantial prior capability. Oracle OPERA Cloud documents profiles containing preferences and images; hotelkit supports guest-request assignment, escalation, and follow-up; SoftServe has demonstrated wearable AR face identification, including VIP recognition. Face recognition on glasses and shared guest records are therefore not themselves novel. The project's contribution is to investigate a same-stay service workflow linking low-effort context capture, checked association, and timely presentation of a relevant cue. The lounge proposal additionally explores an **active lounge cohort** bounded by entry and exit; the implemented glasses demo recognises against its loaded gallery, not that card-derived cohort. [R5](#r5), [R6](#r6), [R7](#r7), [P3](#p3), [P6](#p6)

The comparison keeps smart glasses as a prototyping choice rather than a proven winner. [Chapter 4: system architecture and prototype development](#prototype) describes the proposed workflow and demonstrated stages; [Chapter 5: evaluation](#testing) assesses the evidence against the requirements.


## 4. System architecture and prototype development {#prototype}

### 4.1 Solution overview and staff journey {#initial-concept}

The proposed journey connects capture and display through a same-stay handover. For a first-time guest, a concise detail from an early encounter can help another employee continue the service later. The journey below keeps the two solution functions linked while adding confidence, safety, and review boundaries. [Chapter 2: requirements](#requirements), [Chapter 3: concept comparison](#concepts)

<figure>
<a href="assets/initial-concept.svg" target="_blank" rel="noopener" aria-label="Open the initial smart-glasses concept diagram">
<img src="assets/initial-concept.svg" alt="The wearer interface sends faces for recognition against cached ArcFace reference vectors. A recognised identity selects the SQLite guest record, which returns name and preference cues directly to the wearer interface." width="1200" height="505">
</a>
<figcaption><strong>Figure 1.</strong> Core functions, models, and guest-data setup, before examining the design iterations.</figcaption>
</figure>

**Proposed staff journey**

1. **Start the interaction.** The staff member taps the glasses to begin. In the proposed complete workflow, this action starts recognition and conversation capture together. Audio recording and extraction remain proposed; any real-participant use requires an approved purpose and study protocol.
2. **Check the guest association.** The system looks for a stable, sufficiently supported match. If identity is unknown, ambiguous, or lost, it shows no personal profile cue. Staff continue with the normal greeting, ask the guest directly, or use the usual phone/PMS lookup.
3. **Select and display context.** When the match is sufficiently supported, show only the small amount of information relevant to the current service task. An unrelated room preference should not compete with a lounge drinks cue.
4. **Confirm today's need.** Staff use the cue to make a natural offer and confirm that the preference still applies. They listen for corrections rather than treating an earlier statement as permanent.
5. **Verify allergy information.** An allergy cue prompts a check against the authorised guest record and the relevant menu or kitchen source before staff advises the guest or offers an alternative. A face match alone cannot establish that a dish is safe.
6. **Prepare a sourced draft.** After the conversation, the proposed processing step extracts only evidence-supported guest statements and keeps their supporting wording, source, timestamp, guest association, and current-stay scope. A one-time request stays distinct from a broader preference.
7. **Review and approve.** Staff correct the wording and confirm the guest and stay before approving the update. The information remains a draft until this check is complete.
8. **Carry context forward.** Another employee can retrieve the approved detail when it is relevant to a later service task and confirm that it still applies.

<figure>
<a href="assets/staff-journey.svg" target="_blank" rel="noopener" aria-label="Open the intended staff service journey">
<img src="assets/staff-journey.svg" alt="Intended service journey: approach the guest, see context, adapt the offer and confirm today's need; a proposed, reviewed preference update may inform later staff." width="1200" height="350">
</a>
<figcaption><strong>Figure 2.</strong> Intended staff journey. The figure shows the normal service path; the text above adds no-match fallback, allergy verification, and the proposed reviewed handover.</figcaption>
</figure>

**Demonstrated versus proposed.** The current glasses demonstration covers manual activation, recognition against a loaded gallery, prepared-profile retrieval, and cue rendering. Preference extraction has been explored separately. Conversation recording, confirmed guest/stay association, staff-approved record writes, task-ranked cue selection, and next-employee retrieval are not integrated into that path. Chapter 5 evaluates the demonstrated stages and identifies what remains to validate. [P1](#p1), [P3](#p3)

### 4.2 Capture {#capture}

Capture iterations use measurable tests: battery depletion, traffic, silence-timeout duration, latency, and guest facts matched against expected answers. The intended pipeline associates insights with guests and records checked preferences; automatic extraction and updates remain under development.

<figure>
<a href="assets/capture-pipeline.svg" target="_blank" rel="noopener"><img src="assets/capture-pipeline.svg" alt="Intended capture pipeline: video/audio clip, multimodal processing, relevant insight extraction, guest association through face recognition, then recording preferences in the database." width="1200" height="245" loading="lazy"></a>
<figcaption><strong>Figure 3.</strong> Intended capture workflow, before refining activation and processing allocation.</figcaption>
</figure>

#### 4.2.1 Temple-touch activation {#activation}

Continuous capture requires less staff input but keeps processing active between encounters. Reported battery life was only slightly over an hour, insufficient for a hotel shift. Temple-touch activation trades a single tap for longer battery life. [P1](#p1)

The timeout balances battery use with **DR2, low effort**: one tap starts capture, speech sustains it, and 15 seconds without speech ends it automatically, without repeated taps or a separate stop action. Expiry stops camera/microphone activity, cancels requests, and clears cues. Speech cannot activate idle capture. [P3](#p3)

<figure>
<a href="assets/activation-iteration.svg" target="_blank" rel="noopener"><img src="assets/activation-iteration.svg" alt="Continuous activity is replaced by idle, tap-activated interaction, and automatic stopping after 15 seconds without speech; speech extends the active session." width="1200" height="415" loading="lazy"></a>
<figcaption><strong>Figure 4.</strong> Encounter activation and speech-controlled session expiry.</figcaption>
</figure>

Local WebRTC voice activity detection distinguishes speech-like activity from silence. The timeout was tested and verified at approximately **15.4 seconds in a quiet-room setting**; restaurant and front-desk conditions still need verification. [P3](#p3)

The 20-minute battery experiment used a one-minute conversation every five minutes. Including the 15-second silence period gives 75/300 seconds of scheduled activity, or 25%. [P1](#p1), [P7](#p7)

| Activation comparison | Continuous | Temple touch + silence timeout |
|---|---:|---:|
| Scheduled duty cycle | 100% | 25% |
| Reported traffic count | 705 | 170 |
| Battery-level drop | 28 percentage points | 9 percentage points |

Traffic fell by 75.9%; battery depletion fell by 19 percentage points, approximately 68% relative depletion. This measures battery-gauge change, not electrical power. [P1](#p1), [P7](#p7)

#### 4.2.2 Selective server processing {#processing}

Local photo recognition alone averaged **1,927.9 ms**, almost twice **DR1's one-second budget** for the complete cue workflow. This delay prompted analysis of the capture pipeline's bottlenecks. SCRFD preparation/inference/postprocessing took **1,268.7 ms**, and alignment, ArcFace inference, and matching **639.1 ms**, versus **20.1 ms** for JPEG decoding. Recognition dominated even before camera and display costs were included, motivating selective offloading. [P5](#p5)

Camera handling, tracking, crop preparation, and rendering remain local; the laptop handles InsightFace `buffalo_l` recognition and lookup. Planned extraction also belongs there. This targets **DR1**, keeping position updates responsive. A separate battery benefit remains unmeasured. [P3](#p3)

<figure>
<a href="assets/capture-offload-pipeline.svg" target="_blank" rel="noopener"><img src="assets/capture-offload-pipeline.svg" alt="Capture responsibilities: glasses handle temple touch and video/audio sensing; the server handles heavier multimodal analysis, insight extraction, guest association, and database updates in the intended full pipeline." width="1200" height="260" loading="lazy"></a>
<figcaption><strong>Figure 5.</strong> Selective server allocation. Recognition is implemented; automatic preference extraction and updates remain planned.</figcaption>
</figure>

The comparison used 15 warm probes per mode, the same enrolled 800 × 800 photo, five gallery identities, CPU execution, and 0.50/0.10 score/margin settings. Offline testing disabled Wi-Fi and stopped the laptop server. [P5](#p5)

| Warm photo-recognition path | Mean | Median | Observed range |
|---|---:|---:|---:|
| Glasses → Wi-Fi → laptop → parsed response | 1,350.6 ms | 1,311.6 ms | 1,220.1–1,513.7 ms |
| Entire recognition on glasses | 1,927.9 ms | 1,896.0 ms | 1,848.6–2,379.7 ms |

<figure class="chart">
<div class="chart-title">Recognition offloading: approximately 30% lower elapsed time</div>
<div class="chart-subtitle">15 warm photo probes per mode · camera, enrolment and display excluded</div>
<div class="bar-row"><span>Laptop via Wi-Fi</span><div class="bar-track"><div class="bar-fill" style="width:56.275%"></div></div><span class="bar-value">1,350.6 ms</span></div>
<div class="bar-row"><span>On glasses</span><div class="bar-track"><div class="bar-fill secondary" style="width:80.329%"></div></div><span class="bar-value">1,927.9 ms</span></div>
<div class="chart-axis"><span>0</span><span>1,200</span><span>2,400 ms</span></div>
<figcaption><strong>Figure 6.</strong> Elapsed time decreased 29.9%. Self-reference probes establish neither recognition accuracy nor complete touch-to-cue performance.</figcaption>
</figure>

The offloaded mean of **1,350.6 ms still exceeds one second**. Only one CPU laptop was tested; a more powerful server or accelerated inference could help. Gains require measurement alongside image-preparation and scheduling optimisation, then complete-path retesting (Section 5.2). [P5](#p5)

#### 4.2.3 Independent preference-extraction testing {#preference-extraction}

For **DR4, preference continuity**, independent feasibility and accuracy tests isolate interpretation errors before glasses integration. Input is currently text; Whisper/audio capture is not connected. [P13](#p13)

Two synthetic, speaker-labelled conversations supply three expected guest facts. The text-only prompt requests category, value, and exact guest quote in schema-constrained JSON. Python checks quotations against guest turns and requires values to appear in them. Outputs remain pending, without guest-record writes. The exploratory M1 Mac comparison evaluates guest-fact matches and processing time. [P1](#p1), [P13](#p13)

| Reported local model | Valid JSON calls | Guest facts matched | Mean time/transcript |
|---|---:|---:|---:|
| `llama3.2:3b` | 2/2 | 1/3 | 76.1 s |
| `qwen3:4b-instruct` | 2/2 | 2/3 | 67.2 s |
| `gemma4:e2b` | 2/2 | 2/3 | 86.4 s |

**Qwen is the provisional best model:** it tied Gemma at 2/3 guest facts and was fastest at 67.2 seconds. Three facts cannot establish general accuracy; timing excludes recognition. [P1](#p1), [P13](#p13)

Valid JSON did not prevent semantic confusion: Gemma treated “too sweet” as a preference and a dessert-safety question as dietary information. These errors motivate improvements **before integration**, including distinguishing complaints from lasting preferences and questions from disclosures. Quote/role checks, category rules, and refusal handling have been added; reviewer-labelled, held-out cases should test negation, corrections, attribution, and repeatability. Evaluate transcription separately when adding audio. [P13](#p13)

### 4.3 Display {#display}

Display testing uses user feedback on placement, readability, and relevance (Section 5.1); implementation checks verify rendering and stale-cue suppression. The pipeline identifies the guest, retrieves their record, and returns cues.

<figure>
<a href="assets/display-pipeline.svg" target="_blank" rel="noopener"><img src="assets/display-pipeline.svg" alt="Display pipeline: temple touch activates capture on the glasses, the server recognises the guest and retrieves preferences, then returns information for display." width="1200" height="328" loading="lazy"></a>
<figcaption><strong>Figure 7.</strong> Identity-to-record-to-display flow; the placement iteration adds local position updates.</figcaption>
</figure>

#### 4.3.1 Positioning information beside the guest {#display-position}

Initially, cues occupied a fixed display position. User feedback and prototype validation prompted face-relative placement and central guest selection, aiming to reduce looking away from the guest and competing details from several visible faces. These iterations address **DR3, glanceability**. [P1](#p1), [P7](#p7)

Google **ML Kit**, an on-device machine-learning toolkit, detects faces and tracks positions locally; InsightFace identifies the guest. The central **30% of both view axes** defines the selection region, choosing the face nearest its centre. This aims to show preferences for the guest receiving the employee's eye contact, avoiding details for everyone visible. Technically, it uses head direction as a proxy, not measured gaze. Only the latest frame is kept; a padded selected-face crop is sent about every two seconds. Bystanders may remain inside that crop. [P3](#p3), [R11](#r11)

Local tracking updates placement between server responses. Calibration checks boundaries and overlap, suppressing labels without suitable space. Wearer fit and distance still need evaluation.

<figure>
<div class="comparison-grid">
<div><p class="comparison-label">Before · fixed position</p><a href="assets/ui/01-position-before.png" target="_blank" rel="noopener"><img src="assets/ui/01-position-before.png" alt="Generated UI before placement refinement: Ethan Tan's name is at the upper right, away from his face." width="1200" height="1200" loading="lazy"></a></div>
<div><p class="comparison-label">After · beside the face</p><a href="assets/ui/02-position-after.png" target="_blank" rel="noopener"><img src="assets/ui/02-position-after.png" alt="Generated UI after placement refinement: Ethan Tan's name is beside his face." width="1200" height="1200" loading="lazy"></a></div>
</div>
<figcaption><strong>Figure 8.</strong> Generated UI comparison: local tracking brings the cue beside the guest; eye contact is unmeasured. [P12](#p12)</figcaption>
</figure>

**Current identity matters (DR5).** Crossing, sudden movement, or ambiguity clears the association. Responses older than two seconds are rejected, identities expire four seconds after submission, and stalled tracking clears cues within 500 ms. Tests check these safeguards and coordinate mapping, not field error rates. [P11](#p11)

For DR1, cropping before processing removed a 2.2–2.4-second full-frame preparation bottleneck. On 27 October, the earlier SFace configuration averaged 200 ms from analysis callback to parsed response across 14 uploads. This supports that image-path iteration, not current-model or optical-display performance. [P3](#p3)

#### 4.3.2 Replacing descriptions with concise icons {#display-content}

For **DR3**, long descriptions become a name and two compact cues; DR6 requires preferences and safety warnings to remain distinct. [P1](#p1)

<figure>
<div class="comparison-grid">
<div><p class="comparison-label">Before · written description</p><a href="assets/ui/03-content-before.png" target="_blank" rel="noopener"><img src="assets/ui/03-content-before.png" alt="Generated UI before content refinement: Ethan Tan's name and the words Shellfish allergy." width="1200" height="1200" loading="lazy"></a></div>
<div><p class="comparison-label">After · compact icon</p><a href="assets/ui/04-content-after.png" target="_blank" rel="noopener"><img src="assets/ui/04-content-after.png" alt="Generated UI after content refinement: the written allergy description becomes a shellfish symbol with a warning marker." width="1200" height="1200" loading="lazy"></a></div>
</div>
<figcaption><strong>Figure 9.</strong> Generated UI comparison: text becomes an item-and-warning icon. The allergy is a fictional demo cue. [P12](#p12)</figcaption>
</figure>

Item symbols combine with heart, crossed-out-heart, and warning markers for preference, dislike, and fictional allergy, without relying on colour alone. Bundled icons appear beneath the name without extra downloads. [P3](#p3)

<figure>
<a href="assets/icon-reference.svg" target="_blank" rel="noopener"><img src="assets/icon-reference.png" alt="Complete supported icon catalogue: king room, twin room, suite, smoking-allowed room, black coffee, green tea, still water, vegetarian food, shellfish, peanuts, milk, and eggs; separate prefer, dislike, and demo-allergy markers; three combined examples." width="1600" height="1000" loading="lazy"></a>
<figcaption><strong>Figure 10.</strong> All 12 supported item icons and three independent markers, with combined examples. Allergy assignments are fictional. [P3](#p3)</figcaption>
</figure>

Two-cue limits, warning priority, and Unknown suppression are implemented. Device/tracking tests verify cue placement and simultaneous name/icon clearing; unaided symbol comprehension needs user evaluation. [P11](#p11)

Transient content follows platform guidance, while attention research cautions against assuming unobtrusiveness. Comprehension, glance duration, and conversational use need evaluation in Section 5.1. [R8](#r8), [R9](#r9)

#### 4.3.3 Retrieving contextually relevant preferences {#contextual-retrieval}

In the proposed pipeline, face recognition determines **whose record** to retrieve; audio-derived conversation context determines **which fields** to show. The server combines them to return selected preferences.

<figure>
<a href="assets/context-pipeline.svg" target="_blank" rel="noopener"><img src="assets/context-pipeline.svg" alt="Proposed server pipeline: audio determines conversation context, face recognition determines guest identity, and both guide retrieval of selected guest preferences for display." width="1200" height="400" loading="lazy"></a>
<figcaption><strong>Figure 11.</strong> Proposed contextual retrieval, combining identity and conversation context.</figcaption>
</figure>

A twin-room icon may be readable but irrelevant to a drinks order. Filtering targets **DR3 and DR6** by selecting a confirmed drink preference during dining, using checked records for DR4. Safety-related information needs explicit priority and hotel verification rules rather than disappearing when another topic is selected. [P1](#p1)

<figure>
<div class="comparison-grid">
<div><p class="comparison-label">Before · unrelated room preferences</p><a href="assets/ui/05-context-before-extra-room-icons.png" target="_blank" rel="noopener"><img src="assets/ui/05-context-before-extra-room-icons.png" alt="Generated UI before contextual filtering: several room preference icons are displayed during a restaurant interaction." width="1254" height="1254" loading="lazy"></a></div>
<div><p class="comparison-label">Proposed after · relevant drink preference</p><a href="assets/ui/06-context-after.png" target="_blank" rel="noopener"><img src="assets/ui/06-context-after.png" alt="Generated UI of the proposed context refinement: a coffee preference replaces unrelated room icons during dining." width="1200" height="1200" loading="lazy"></a></div>
</div>
<figcaption><strong>Figure 12.</strong> Generated UI comparison illustrating the proposed relevance filter; it is not evidence of implemented conversation understanding. [P12](#p12)</figcaption>
</figure>

**Implementation boundary.** The prototype prioritises warnings and selects up to two prepared cues. Conversation-based ranking is not implemented; microphone activity only controls session duration. [P3](#p3)

Participants' feedback motivates comparing filtering in identical scenarios, recording useful/omitted cues, interpretation, and interruption.

### 4.4 Complete system architecture {#system-architecture}

Figure 13 combines the iterations in the **Rokid RV101 → Wi-Fi/HTTP → laptop → display** architecture. Solid paths describe current functions; the dashed extension is planned. [P10](#p10)

<figure>
<a href="assets/system-architecture.svg" target="_blank" rel="noopener" aria-label="Open the full system architecture as a scalable diagram">
<img src="assets/system-architecture.png" alt="Full Rokid architecture: local session control, camera tracking, focus gate, speech activity, network client and display; laptop HTTP API, SCRFD and ArcFace recognition, gallery embeddings and guest-cue caches; dashed future audio-preference pipeline." loading="lazy" width="2400" height="1560">
</a>
<figcaption><strong>Figure 13.</strong> Full implemented architecture and proposed audio-preference extension. <a href="assets/system-architecture.svg" target="_blank" rel="noopener">Open the scalable diagram ↗</a> or <a href="assets/system-architecture.png" target="_blank" rel="noopener">view the full-resolution PNG ↗</a>. Source: <a href="#p10">P10</a>.</figcaption>
</figure>

**Communication.** One request at a time prevents backlogs; expiry rejects late answers. A swipe checks connectivity. [P3](#p3)

**Recognition.** Cached-template matching uses a 0.45 similarity threshold and 0.10 margin over the next identity. Lowering the threshold from 0.50 after frequent Unknown results made acceptance more permissive; false matches need representative validation. Similarity is not a correctness probability. [P3](#p3), [P11](#p11)

**Records.** Cached profiles avoid repeated reads; Unknown/missing profiles receive no cues. Incoming camera images are not saved.

For DR4, SQLite edits still require restart to refresh cues; opaque guest IDs must replace name-based lookup for same-name guests. Shared storage alone cannot establish live continuity.

The dashed extension adds audio upload, local Whisper, hosted Gemini extraction, and reviewed SQLite updates; no cloud endpoint is connected yet. The separate card-entry scaffold's active cohort and temporal voting are not integrated here. [P6](#p6), [P10](#p10)

## 5. User validation and system evaluation {#testing}

This chapter checks the requirements in [Chapter 2](#requirements) and the concept taken forward in [Chapter 3](#concepts) against the narrower demonstrated journey in [Chapter 4](#prototype). It distinguishes observed prototype behaviour from the proposed capture-to-approved-record-to-next-employee workflow.

### 5.1 User validation {#user-validation}

The team conducted a walkthrough and product testing with **10 non-hotel participants**, examining activation, potential usefulness, and cue use. This formative work supports problem finding and prototyping, rather than proving improved hotel service. [P1](#p1)

| Walkthrough question | Reported finding | Design implication |
|---|---|---|
| Is starting capture/display easy? | All 10 described activation as easy. | Retain single-tap activation; test it during realistic staff tasks. |
| Could cues help serve guests? | 70% saw potential usefulness, but some icons were unrelated to the conversation. | Develop contextual retrieval and assess whether it enables a specific service action. |
| Can cues be used naturally? | Most described a quick glance as sufficient, but incorporating cues into conversation was challenging. | Test timing, meaning, and conversational flow together; investigate design changes as well as training. |

The distinction between reading and using a cue is central. Recognising a coffee icon does not establish when or how to introduce a preference naturally. The findings connect the icon iteration in Section 4.3.2 to the relevance iteration in Section 4.3.3: shorter content can still interrupt service if it is poorly timed or unrelated to the task.

Without a controlled baseline, archived individual responses, or objective glance/attention measurements, the non-staff study cannot establish hotel-employee usability. Its value is identifying problems for the next prototype, rather than proving reduced cognitive load, maintained eye contact, or satisfaction.

### 5.2 Design requirements and whole-system testing {#requirements-check}

The requirements check combines the walkthrough with the demonstrated **tap → guest selection → recognition → prepared-profile retrieval → rendering** path. Conversation → approved preference update → another employee's appropriate service action remains incomplete. The assessment below covers Chapter 2's service requirements and the safeguards needed for correct association and appropriate information.

On 3 November, 13 live activations included rapid retaps. Five produced known-name-plus-icon drawing events; four also recorded Android frame commits. Those four successful warm retaps averaged **1,180 ms**, median **1,198.5 ms**, range **974–1,349 ms**. [P4](#p4)

| Integrated stage, four recorded commits | Mean |
|---|---:|
| Handled tap → successful request sent: camera, detection, selection, encoding, scheduling | 693 ms |
| HTTP request → parsed response, including inference | 302 ms |
| Parsed response → name/icon drawing | 101.3 ms |
| Drawing → Android frame commit | 83.8 ms |
| Total | **1,180 ms** |

Inference averaged 177.5 ms within HTTP time and must not be counted twice. The largest stage precedes sending the successful request, directing improvement toward capture/selection and scheduling as well as server inference. One additional draw took 4,412 ms without a commit recorded before the next activation; eight activations had no accepted information draw before another tap. Retaps interrupt work, so these counts do not establish accuracy or an independent success rate. Frame commit is a software endpoint, and clean cold-start performance remains unconfirmed.

| Requirement | Current evidence | Assessment and next verification |
|---|---|---|
| **DR1 · Timely support:** cue within 1.0 s | Four successful warm commits averaged 1.18 s; slower/interrupted cases also occurred. | **Target not met.** Repeat independent cold/warm trials and count failures. |
| **DR2 · Low effort:** single tap and automatic silence expiry | Activation was easy for all 10 participants; component checks support the deadline and resource release. | **Supported formatively.** Test staff task interference and expiry in realistic noise. |
| **DR3 · Glanceability:** concise cues during conversation | Icons are implemented; 70% reported needing only a quick glance, but natural conversational use remained difficult. | **Partially achieved.** Compare comprehension, attention shifts, and conversational flow with a baseline. |
| **DR4 · Preference continuity:** approved update reaches another employee | Prepared profiles are retrieved; extraction is inconsistent and profiles are cached at startup. | **Incomplete.** Test captured statement → review → refreshed record → next employee's action. |
| **DR5 · Correct association:** suppress uncertain/stale cues | Tests exercise Unknown, reused/crossing tracks, expiry, and cancellation. | **Safeguards implemented; field performance unknown.** Count wrong-profile reveals and misses on held-out, crowded scenes. |
| **DR6 · Appropriate information:** relevant fields and distinct allergy handling | Two-cue limit and fictional allergy markers exist; irrelevant content was reported. | **Partially achieved in demo data.** Validate contextual selection, interpretation, permissions, and fallback. |

The system demonstrates a working retrieval-and-display mechanism, while the service benefit and complete handover remain evaluation tasks. The component offloading experiment has different timing boundaries and cannot enlarge the four-commit sample.

### 5.3 Limitations and guest acceptance {#guest-acceptance}

A separate exploratory survey asked how comfortable respondents would be with hotels noting and storing preferences for better service. Ratings 4 and 5 account for 31.3% and 9.4%, giving **40.7% rating 4 or 5**. Responses therefore do not establish majority acceptance. The recruitment method and denominator are not supplied, so this is exploratory feedback rather than a representative guest estimate. [P1](#p1)

Preference-storage comfort also does not establish acceptance of facial images, purchase-history processing, or recorded conversations. The next study should distinguish those activities, explain purpose and access, and allow guests to express different choices. A lounge access tap alone does not demonstrate permission for every proposed use. The PDPA and PDPC biometric guidance are reference points for review with the hotel and university; the latter concerns security applications rather than approving this hospitality workflow. [R10](#r10)

The implemented microphone currently detects activity locally, whereas the planned extension would introduce audio/transcript handling and an external model service. That change needs its own participant and data protocol. Face thresholds and track guards reduce particular failure paths but have not been evaluated for representative error rates. Fictional allergy icons likewise test presentation, not food safety. These limits define the next-stage study boundary; they do not negate the present prototype's value for discovering usability and integration problems.

### 5.4 Next development and validation steps {#next-development}

The findings identify three priorities for the next phase, each with evidence needed to judge progress. Hotel-staff evaluation will determine whether the revised workflow is useful in practice. [P1](#p1)

**Refine extraction and contextual retrieval.** Create a human-labelled set covering explicit preferences, requests, complaints, negation, corrections, and multiple speakers. Compare transcript-only and multimodal processing on the same cases, retaining prompts, model versions, supporting excerpts, and timing. Add staff correction and approval before a write, reliable guest association, and cache refresh. Success requires a supported preference to reach a second employee, with irrelevant or superseded cues withheld; a shared database alone is insufficient.

**Run a hotel-staff usability pilot.** Compare glasses with ordinary profile lookup using equivalent guest information, counterbalanced scenarios, and equal practice. Measure correct interpretation, service action, time to the first useful cue, interruptions, and perceived conversational fit. Distinguish interface problems from training needs. Guiding-question cues may help staff elicit preferences, but should be tested for naturalness rather than installed as a mandatory script. Broader cold/warm latency, identity, network-failure, and battery trials should accompany the service tasks.

**Develop evidence-linked LQA support.** Begin with the selected 15-item F&B subset and provisional, human-reviewed observations. Each output should identify the applicable criterion, timestamped supporting evidence, and missing context. Keep “not applicable,” “insufficient evidence,” and a supported service gap distinct. Compare outputs with trained reviewers before using them for coaching or service recovery; the prototype cannot yet justify an overall LQA grade or automatic employee ranking. [P8](#p8)

Chapter 6 provides the phased work plan, while Appendix B specifies the comparison protocol. This progression turns the interim prototype into a more complete, testable service workflow without presenting planned validation as an accomplished result.

## 6. Limitations, responsible use, and next-stage plan {#next-stage}

The strongest interim outcome is a tangible recognition-and-display prototype supported by component measurements and formative feedback. The complete capture → approved update → another employee's relevant service action has not yet been validated. Several implementation and study boundaries determine the next phase.

**Identity and data quality.** A similarity threshold is not a calibrated guarantee. The current demo lacks a held-out, representative test of false identity matches, missed matches, and incorrect profile disclosure. New preference records need a confirmed guest, an exact supporting statement, a timestamp, and a distinction between current-stay and enduring information. Corrections must supersede outdated cues. Fictional allergy assignments demonstrate display behaviour only; an empty cue list does not mean a guest has no allergy. [P3](#p3)

**Guest and employee control.** The planned use links face images, service conversations, preferences, and potentially staff-performance assessments. Each needs a defined purpose, appropriate notification and consent or other reviewed basis, limited access, correction, and retention arrangements. The official PDPC biometric guide concerns security applications and is a reference point rather than approval for this hospitality use. A room-card access tap or a preference-storage survey response does not itself authorise face recognition or audio capture. Approval for the test setting must therefore be extended into an explicit study protocol before real-guest testing. [R10](#r10), [P2](#p2)

**Allergy handling.** A cue should prompt discreet reconfirmation and checking against the authorised allergen/menu source. Staff must follow the hotel's food-service procedure. Face matching must not infer an allergy, and the prototype does not certify that a meal is safe.

**Service-standard analysis.** Future LQA-related processing should return evidence-linked provisional observations for human review. Missing evidence, an inapplicable criterion, and a demonstrated service gap require separate labels. The selected 15-item F&B subset cannot support an overall LQA grade or automatic staff ranking. Expert agreement and factual grounding need evaluation before such outputs affect employee assessment. [P8](#p8)

The following is a proposed sequence for Semester 2, with weeks relative to its start; it is a work plan rather than a confirmed hotel booking.

| Window | Work package and deliverable | Decision or evidence required |
|---|---|---|
| Weeks 1–2 | Confirm one lounge service moment, staff roles, existing profile path, data permissions, and cue categories with the partner. | Agreed workflow map, baseline task, and participant/data protocol. |
| Weeks 2–4 | Build an extraction evaluation set with explicit preferences, questions, complaints, corrections, multiple speakers, and visual-only observations. | Versioned prompts/models; human-labelled facts; precision, recall, unsupported claims, and attribution errors. |
| Weeks 3–5 | Implement staff review/correction before profile writes and contextual retrieval for one F&B task. | Approved update reaches a second employee; irrelevant and superseded cues are withheld. |
| Weeks 4–6 | Test recognition on held-out images, ambiguous guests, track changes, and network failure; repeat independent cold/warm timing and longer battery trials. | Report every activation and failure, p50/p95 where supported, false reveals, starting charge, duration, and complete traces. |
| Weeks 6–8 | Run an approved formative pilot with approximately 6–8 hotel staff, subject to access, using counterbalanced phone and glasses tasks. | Correct guest/action, cue comprehension, task time, attention shifts, guest-perceived fit in staged encounters, and qualitative feedback. |
| Weeks 9–10 | Refine the most consequential failures; demonstrate the complete same-stay handover and report the comparison. | A traceable requirements check and a supported decision about continuing with the wearable. |

Proposed acceptance gates are zero observed wrong-profile reveals in the defined test set, source-supported approved preferences, reliable no-match fallback, and improved task performance without poorer comprehension or conversational flow. Zero observed errors would remain a bounded sample result. Final numerical targets and sample sizes should be agreed before testing. Deployment cost should subsequently include hardware, server/network resources, integration, charging, maintenance, and training; the current evidence is insufficient for a credible ROI estimate.

## 7. Team contributions {#contributions}

The team confirmed the following division, following the presentation split. This records the main areas of work without assigning undocumented individual ownership of particular experiments. [P7](#p7)

| Team member | Main area of contribution |
|---|---|
| Neha Rajan | Problem investigation and framing; hotel/business context, service quality, and the rationale for personalisation. |
| Nigel Yeo Tong Wei | Problem investigation and framing; current guest-information practices, first-time guest needs, and the design challenge. |
| Wong Weng Hong | Solution development: [functional requirements](#requirements), [concept comparison](#concepts), and the [proposed staff/guest journey](#initial-concept). |
| Tan Ping Hui | Solution development; technical implementation, prototype iterations, testing, and the next development steps. |

The interim contribution is an implemented service-support mechanism and a clearer account of what must be tested next. Whether the mechanism improves hotel service remains the central evaluation question for the next stage.

## References and project evidence {#references}

<div class="references">

<p id="r1"><strong>R1.</strong> Lei, S. S. I., Wang, D., Fong, L. H. N., & Ye, S. (2024). “Recipe for perceived personalization in hotels.” <em>Tourism Management, 100</em>, 104818. <a href="https://research.polyu.edu.hk/en/publications/recipe-for-perceived-personalization-in-hotels/">Institutional publication record and abstract</a> · <a href="https://doi.org/10.1016/j.tourman.2023.104818">DOI</a>.</p>
<p id="r2"><strong>R2.</strong> Medallia Market Research (2024). <em>Understanding Personalization Efforts in the Hospitality and Retail Industries.</em> <a href="https://www.medallia.com/wp-content/uploads/pdf/resources/Medallia-Understanding-Personalization-Efforts-in-the-Hospitality-and-Retail-Industries-Report.pdf">Original report</a>. Vendor-produced U.S. guest survey.</p>
<p id="r3"><strong>R3.</strong> Piccoli, G., Lui, T.-W., & Grün, B. (2017). “The impact of IT-enabled customer service systems on service personalization, customer service perceptions, and hotel performance.” <em>Tourism Management, 59</em>, 349–362. <a href="https://dds.cct.lsu.edu/ddslab/pdf/piccoliLuiGruen.pdf">Author-hosted article</a> · <a href="https://doi.org/10.1016/j.tourman.2016.08.015">DOI</a>.</p>
<p id="r4"><strong>R4.</strong> LQA. <a href="https://lqagroup.com/hotel-assessments/">Hotel assessments</a>. Public description of its quality-assessment framework; accessed 10 November 2026.</p>
<p id="r5"><strong>R5.</strong> Oracle. <a href="https://docs.oracle.com/en/industries/hospitality/opera-cloud/25.4/ocsuh/ch_profiles_intro.htm">OPERA Cloud 25.4: Profiles</a>. Official product documentation; accessed 10 November 2026.</p>
<p id="r6"><strong>R6.</strong> hotelkit. <a href="https://hotelkit.net/solutions/guest-services/">Guest services</a>. Vendor-described request assignment and complaint follow-up; accessed 10 November 2026.</p>
<p id="r7"><strong>R7.</strong> SoftServe. <a href="https://www.softserveinc.com/en-us/resources/hands-free-face-id-demo">Hands-Free Face ID</a>. Public AR identification demonstration; accessed 10 November 2026.</p>
<p id="r8"><strong>R8.</strong> Google. <a href="https://developer.android.com/design/ui/ai-glasses/guides/foundations/design-principles">AI Glasses design principles</a>. Official design guidance; accessed 10 November 2026.</p>
<p id="r9"><strong>R9.</strong> Lewis, J. E., & Neider, M. B. (2016). “Through the Google Glass: The impact of heads-up displays on visual attention.” <em>Cognitive Research: Principles and Implications, 1</em>, 13. <a href="https://doi.org/10.1186/s41235-016-0015-6">Open-access article</a>.</p>
<p id="r10"><strong>R10.</strong> Personal Data Protection Commission Singapore (2022). <a href="https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/other-guides/guide-to-biometric_17may2022.pdf">Guide on Responsible Use of Biometric Data in Security Applications</a>. Scope: security applications. See also <a href="https://sso.agc.gov.sg/Act/PDPA2012">Personal Data Protection Act 2012</a>, Singapore Statutes Online.</p>
<p id="r11"><strong>R11.</strong> Google. <a href="https://developers.google.com/ml-kit/vision/face-detection">Face detection documentation</a>. On-device detection and tracking, distinct from identity recognition; accessed 10 November 2026.</p>
<p id="r12"><strong>R12.</strong> Shiwa, T., Kanda, T., Imai, M., Ishiguro, H., &amp; Hagita, N. (2009). “How Quickly Should a Communication Robot Respond? Delaying Strategies and Habituation Effects.” <em>International Journal of Social Robotics, 1</em>, 141–155. <a href="https://doi.org/10.1007/s12369-009-0012-8">DOI and publisher abstract</a>. Used only as an analogy for the proposed response target.</p>
<p id="r13"><strong>R13.</strong> Brungart, D. S. (2001). “Informational and energetic masking effects in the perception of two simultaneous talkers.” <em>Journal of the Acoustical Society of America, 109</em>(3), 1101–1109. <a href="https://doi.org/10.1121/1.1345696">DOI</a> · <a href="https://scholar.usuhs.edu/en/publications/informational-and-energetic-masking-effects-in-the-perception-of--2/">Author’s institutional abstract</a>.</p>
<p id="r14"><strong>R14.</strong> Rzayev, R., Korbely, S., Maul, M., Schark, A., Schwind, V., &amp; Henze, N. (2020). “Effects of Position and Alignment of Notifications on AR Glasses during Social Interaction.” <em>Proceedings of the 11th Nordic Conference on Human-Computer Interaction</em>. <a href="https://doi.org/10.1145/3419249.3420095">DOI and conference paper</a>. Face-to-face notification study with 32 participants in 16 pairs.</p>
<p id="r15"><strong>R15.</strong> Nees, M. A., &amp; Sampsell, N. G. (2021). “Simple auditory and visual interruptions of a continuous visual tracking task: modality effects and time course of interference.” <em>Ergonomics, 64</em>(7), 879–890. <a href="https://doi.org/10.1080/00140139.2021.1873424">DOI</a>. The alerts were simple visual icons and auditory tones in a laboratory tracking task.</p>
<p id="r16"><strong>R16.</strong> Ward, M. D., Smith, S. L., &amp; Helton, W. S. (2023). “Dual-task Interference while Receiving Information on a Head Mounted Display, Visually on the Same Depth Plane, or Audibly.” <em>Proceedings of the Human Factors and Ergonomics Society Annual Meeting, 67</em>(1), 888–892. <a href="https://doi.org/10.1177/21695067231192613">DOI and publisher abstract</a>. Compared HMD, same-plane visual, and audible word presentation during manual tracking.</p>
<p id="p1"><strong>P1.</strong> Team IS-432 (5 November 2026). <a href="Slides.pdf">Interim presentation, 37 slides</a>; <a href="Recording.mp4">presentation recording, 29 min 18 s</a>; <a href="transcript.html">timestamped transcript</a>. Slide numbers in this report refer to the supplied PDF.</p>
<p id="p2"><strong>P2.</strong> Project field records: <a href="https://github.com/wongwh2002/CDE4301-Hotel-Hospitality/blob/main/hotel-visit/novotel-formatted.md">Novotel formatted visit notes</a>; <a href="https://github.com/wongwh2002/CDE4301-Hotel-Hospitality/blob/main/hotel-visit/parkroyal-main-points.md">PARKROYAL visit summary</a>; <a href="https://github.com/wongwh2002/CDE4301-Hotel-Hospitality/blob/main/hotel-visit/raw-notes/parkroyal-oct-visit-transcript.md">later PARKROYAL discussion transcript and source caveats</a>. These records have different evidence quality; formatted field notes are paraphrases.</p>
<p id="p3"><strong>P3.</strong> <a href="https://github.com/wongwh2002/CDE4301-Hotel-Hospitality/blob/main/rokid/README.md">Rokid prototype implementation and validation notes</a>; <a href="https://github.com/wongwh2002/CDE4301-Hotel-Hospitality/tree/main/rokid/app/src/main/java/com/example/rokid_app">Android implementation</a>; <a href="https://github.com/wongwh2002/CDE4301-Hotel-Hospitality/blob/main/rokid/server/GUEST_PREFERENCES.md">demo guest cue schema and rendering</a>.</p>
<p id="p4"><strong>P4.</strong> <a href="https://github.com/wongwh2002/CDE4301-Hotel-Hospitality/blob/main/rokid/DISPLAY_LATENCY_BENCHMARK.md">Temple touch to displayed information</a>, live RV101 series, 3 November 2026. This is the source for the four frame-commit observations and their timing boundaries.</p>
<p id="p5"><strong>P5.</strong> <a href="https://github.com/wongwh2002/CDE4301-Hotel-Hospitality/blob/main/rokid/LATENCY_BENCHMARK.md">Server versus on-device photo-recognition benchmark</a> and <a href="https://github.com/wongwh2002/CDE4301-Hotel-Hospitality/blob/main/rokid/RETRIEVAL_MODE_BENCHMARK.md">retrieval-mode and battery replay comparisons</a>, 2 November 2026.</p>
<p id="p6"><strong>P6.</strong> <a href="https://github.com/wongwh2002/CDE4301-Hotel-Hospitality/blob/main/README.md">Local POC scaffold</a>; <a href="../architecture/hotel-lounge-smart-glasses-poc.html">interactive proposed architecture</a>; <a href="https://github.com/wongwh2002/CDE4301-Hotel-Hospitality/blob/main/docs/agents/hotel-smart-glasses-poc.md">project framing</a>. Architecture status remains proposed.</p>
<p id="p7"><strong>P7.</strong> Team clarifications, 10–11 November 2026: the 20-minute battery test was verified; no local raw file is available. Neha/Nigel mainly addressed the problem; Weng Hong/Ping Hui the solution. Battery life motivated temple touch; user feedback/validation preceded face-relative placement and central selection.</p>
<p id="p8"><strong>P8.</strong> <a href="../research/source-materials/PARKROYAL-COLLECTION-2026-FB-LQA-15-Selected.csv">Current selected 15-item F&B table</a> · <a href="../research/source-materials/PARKROYAL-COLLECTION-2026-FB-LQA-15-Selected.pdf">PDF preview</a> · <a href="https://github.com/wongwh2002/CDE4301-Hotel-Hospitality/blob/main/docs/research/fb-conversation-checker-prototype-subset.md">checker evidence and evaluation guidance</a>. The current table supersedes earlier candidate-list numbering.</p>
<p id="p9"><strong>P9.</strong> CDE4301 <a href="../rubrics/CDE4301%20assessment%20brief%20and%20rubrics%20-%20AY2026%20-%20interim%20assessment.pdf">interim assessment brief and rubric</a>. Four-person group: 6,000-word limit excluding appendices; individual areas of work must be identified.</p>
<p id="p10"><strong>P10.</strong> <a href="assets/system-architecture.png">Full Rokid system architecture</a> · <a href="assets/system-architecture.svg">scalable SVG</a>. Adapted from <code>rokid/output/architecture/rokid-system-architecture.svg</code>: local detector label generalised; architecture unchanged. The dashed audio-preference extension remains planned.</p>
<p id="p11"><strong>P11.</strong> Implementation-level checks: <a href="https://github.com/wongwh2002/CDE4301-Hotel-Hospitality/tree/main/rokid/app/src/test/java/com/example/rokid_app">Android unit tests for session, focus, tracking, and image buffers</a>; <a href="https://github.com/wongwh2002/CDE4301-Hotel-Hospitality/tree/main/rokid/app/src/androidTest/java/com/example/rokid_app">device tests for microphone/VAD, request deadlines, and cue rendering</a>; <a href="https://github.com/wongwh2002/CDE4301-Hotel-Hospitality/tree/main/rokid/server">server recognition, API, and guest-cue tests</a>. Test presence describes verification coverage; recorded execution results are attributed to P3.</p>
<p id="p12"><strong>P12.</strong> <a href="https://github.com/wongwh2002/CDE4301-Hotel-Hospitality/tree/main/rokid/output/slide-20-ui/screenshots">Generated prototype UI illustrations</a>, reproduced unchanged: position, content, and context before/after pairs. Pipeline diagrams redraw the supplied presentation's flows; contextual filtering remains proposed.</p>
<p id="p13"><strong>P13.</strong> Team-supplied “Note worker testing” summary, provided 11 November 2026. <a href="evidence/preference-extraction-test-summary.md">Transcribed method and reported findings</a>. Synthetic text-only evaluation; raw model runs are not supplied.</p>

</div>

<!-- APPENDICES -->

## Appendix A. Evidence reconciliation {#evidence-notes}

This appendix records differences between presentation summaries and the narrower evidence retained in the repository. It makes the report's interpretation reproducible without changing the supplied slides or recording.

| Presentation statement | Treatment in this report |
|---|---|
| Slide 27: 67% “power reduction,” traffic 705 → 170, battery 28% → 9% | Included as a team-confirmed 20-minute test. The directly reported quantity is battery-level depletion. The relative reduction calculated from the rounded values is 67.9%; electrical energy and average power were not measured. |
| Slide 28: 30% faster, 1.69 → 1.18 s, average over 15 runs | Kept separate from documented protocols. The reproducible 15-probe photo test measured 1.9279 → 1.3506 s, also approximately 30% faster. The 1.18 s figure is supported by four successful warm frame commits in a different live series; a paired 15-run touch-to-display comparison is not archived. |
| Slide 28: three local extraction models | Timing retained from the presentation; P13 adds the text-only protocol, JSON checks, six targeted staff labels, three guest facts, and reported errors. These are exploratory summaries, not broad accuracy estimates or a complete LQA score. |
| Slides 33–34: 70% usefulness / quick glance | Attributed to the team's 10-person non-staff walkthrough. The two questions are not treated as interchangeable objective performance measures. |
| Slide 35: >40% willingness, “rated >4/5,” extended to facial images and purchase history | The displayed preference-storage chart has 31.3% at 4 and 9.4% at 5: 40.7% rated **4 or 5**, while only 9.4% rated **above 4**. The displayed question does not establish willingness to share facial images, purchase histories, or recorded conversations. Recruitment and denominator are not given. |
| Slide 19: first-time guests have “no information” | Narrowed to limited prior-stay history. Pre-arrival and same-stay information can already exist. |
| Slide 11 / speech: loyalty membership treated as returning-guest share | No retention estimate is derived from membership. Membership and a completed repeat stay are different measures. |
| Slides 7–8: LQA and classification | Used as a quality/service framework. LQA assessment is not treated as the authority assigning hotel star classification. |
| Demonstration describes “eye contact” | Described technically as a centred face/head-direction proxy. The current prototype has no eye tracker. |

## Appendix B. Reproducible next-stage evaluation {#evaluation-protocol}

**Staged service comparison.** Recruit an approved formative staff sample, record role and relevant experience, and use synthetic profiles with consenting role-play guests. Counterbalance phone and glasses conditions and scenario order. Give both conditions the same guest context and equal practice. Include a relevant drink preference, an unrelated room preference, a corrected preference, an unknown guest, two nearby enrolled guests, a fictional allergy alert, and a disconnected-server case.

For each trial, record activation, first correctly rendered cue, correct interpretation, chosen service action, interruptions/attention shifts, assistance, and completion. Count all attempts, including no-result cases. Ask the role-play guest whether the action fitted the stated need. Use an observer and a fixed rubric; separate interpretation errors from wrong guest association and model extraction failures. Report participant-level results and uncertainty rather than treating repeated trials from one wearer as independent users.

To isolate the output channel, add a matched role-play comparison that keeps the guest information, capture, processing, association method, and service task constant while varying only the cue: brief in-lens text; an equivalent short spoken earpiece prompt delivered on request or between turns; and the phone/PMS baseline. If proactive audio timing is explored, use a consenting role-play scenario and treat prompts during guest speech as a deliberate interruption condition, not a proposed service default. Record missed guest details, correct interpretation and action, interruptions or conversational repairs, attention shifts, time to an actionable response, cue rechecks or replays, staff workload, and role-play guest comfort. Report cue onset separately from the time needed to read or hear the actionable information.

**Extraction evaluation.** Define reference facts before comparing models. Two reviewers should identify the speaker, explicit statement, current-stay/enduring scope, and whether a preference is actually supported. Include negation, corrections, ambiguity, requests, complaints, and visual-only evidence. Report true supported facts, missed facts, unsupported facts, attribution errors, and processing time. Compare transcript-only and multimodal approaches on identical cases and retain model version, prompts, parameters, input hashes, and reviewed outputs.

**Battery and latency evaluation.** Repeat balanced conditions from comparable charge levels with the same brightness, network, gallery, capture policy, and workload. Include actual camera, microphone/VAD, inference, transfer, and display. Distinguish wall-clock duration, active time, traffic count/bytes, battery percentage points, and measured energy if instrumentation supports it. Begin independent latency trials from idle, then separately measure warm retaps. Record misses, cancellations, and frame commits; do not infer physical lens presentation from software timestamps.

## Appendix C. Recording and supporting material {#supporting-material}

- [Read and search the timestamped transcript](transcript.html).
- [Download the transcript as Markdown](Recording.transcript.md), [plain text](Recording.transcript.txt), or [WebVTT captions](Recording.vtt).
- [View the original slide deck](Slides.pdf) and [recording](Recording.mp4).
- [Read the fuller project research synthesis](https://github.com/wongwh2002/CDE4301-Hotel-Hospitality/blob/main/docs/research/cde4301-interim-report-research-synthesis.md).

The transcript is machine-generated with terminology checks and uncertainty notes; it is not a certified verbatim or speaker-diarised record. Spoken claims are preserved as speech and do not acquire verified status merely by appearing in the transcript. The recording ends just as Q&A begins, so it does not contain a complete question-and-answer session.

<details>
<summary>Play the supplied presentation recording</summary>
<video controls preload="none" aria-label="Interim presentation recording">
<source src="Recording.mp4" type="video/mp4">
<track kind="captions" src="Recording.vtt" srclang="en" label="English — machine transcript">
Your browser does not support embedded video. <a href="Recording.mp4">Open the recording.</a>
</video>
</details>
