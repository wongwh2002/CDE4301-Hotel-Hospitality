# Guest-context cues for personalised hotel service

**CDE4301 Innovation & Design Capstone · Interim assessment · Team IS-432**  
**Team:** Neha Rajan · Tan Ping Hui · Wong Weng Hong · Nigel Yeo Tong Wei  
**Presentation:** 5 November 2026 · **Report prepared:** 10 November 2026 · **Revised:** 14 November 2026  
**Case setting:** PARKROYAL club lounge · **Stage:** Semester 1 proof of concept

<!-- REPORT_BODY -->

## Executive summary 
Hotels may collect guest preferences without making them available at the next service moment. This project investigates same-stay guest-context capture and reuse in a lounge, including for first-time guests with limited service history.

Semester 1 produced a working smart-glasses recognition-and-display prototype, a separate lounge-services scaffold, early preference-extraction experiments, and formative testing. The glasses app recognises against a loaded gallery and displays a name with fictional preference or allergy cues. Automatic conversation-to-profile updating and task-based cue selection are not integrated. [P1](#p1), [P3](#p3)

Four successful warm frame commits averaged **1.18 seconds** from handled temple tap to Android submission; this cannot establish p95 or physical lens visibility, and the report adopts a **1.0 s** cue target; the supplied slide labels it **<1 s**. The revised speaker script uses the one-second target; an earlier draft said **1.5 s**. A 20-minute comparison reported battery-gauge drops of **28 versus 9 percentage points** for continuous and triggered operation. In a walkthrough with **10 non-hotel participants**, all found activation easy and 70% saw potential usefulness, while natural cue use remained difficult. These findings guide further prototyping; they do not establish recognition accuracy, improved guest satisfaction, or hotel performance. Next, the team should test extraction, cue relevance, and the complete handover against ordinary profile lookup with hotel staff. [P1](#p1), [P4](#p4), [P7](#p7)

## 1. Introduction
How do hotel guests decide where to stay? Various factors influence these decisions, including price, reviews, and ratings. Singapore is home to 400+ hotels [e]. Yet, in the luxury hotel industry, only 5 players have captured nearly 50% of the market [f]. A discussion with the partner hotel (Appendix E) revealed that the hotel’s revenue is decreasing significantly due to increasing manpower and operational costs. Hence, this project aims to explore how luxury hotels generate revenue to become key players.


## 2. Problem Identification
### 2.1 Iterations: Manpower and Satisfaction Stagnation
Based on interviews across various hotels in Singapore, manpower shortages and retention was identified as a common issue (Appendix). The shortage often leads to cognitive overload among staff, preventing them from meeting certain service standards (Appendix). In recent years, this has led to a stagnation in guest satisfaction, driven by rising customer expectations (Appendix). Iterating through these problems led to the conclusion that all these issues contribute to the overarching problem faced by the industry partner: revenue generation.

### 2.2 The Revenue Problem
While revenue can be increased by decreasing costs, this can compromise the quality of luxury services in an industry already struggling with external factors driving up cost. Hence, profit generation will be the aim of this project. Revenue in hotels is measured by Revenue Per Available Room (RevPAR) [source]. It is represented by 

RevPAR = ADR OR

Where ADR represents Average Daily Rate of the hotel [source] and OR represents Occupancy Rate [source]. While there are common factors affecting both, such as location, season, economic conditions, and competitor landscape, the classification (star rating) of a hotel significantly affects ADR while reputation and reviews affect OR [source].

#### 2.2.1 ADR and Service Quality
Ratings of hotels depend on their quality, and are assessed by the Leading Quality Assurance (LQA) framework [source]. While these criteria span across emotional intelligence, service quality, efficiency, and more, a large number of standards strongly link to personalized service. Currently, there is a gap in delivering human-centered service, with the partner claiming that staff fail to notice emotional cues like sick guests in the lobby (Appendix).

#### 2.2.2 OR and Customer Satisfaction
Hotel reputation and reviews depend on customer satisfaction. Satisfaction drives increased retention rate and guest acquisition–measured by an increase in Net Promoter Scores (NPS) [source]. This subsequently increases hotel occupancy rate. Satisfaction significantly increases loyalty, as shown by a guest survey (Appendix) in consensus with Marriot’s occupancy analysis (Figure). However, the industry partner is facing “single-digit retention rates” (Appendix).

Guest satisfaction has stagnated over the past few years (Figure) [source], due to rising guest expectations. Different guest demographics expect different services and amenities [a]. Scaling automations to increase overall satisfaction leads to standardization, failing to address the unique expectations of the individual [b].

#### 2.2.3 The Need for Personalization
Hence, it is established that revenue depends on both service quality (driving ADR), which demands interpersonal service and customer satisfaction [Medallia] (driving OR) which requires addressing individual expectations. Synthesizing these needs leads to the demand for personalization in the luxury hotel industry.

This is further supported by the following:
> **86% of travelers sought at least 1 aspect of their experience to be personalized [c]**
> **61% of consumers are willing to spend more for personalized experiences [d]**
> **87% of guests are more likely to recommend a hotel if they receive a personalized experience (Appendix)**


The broader case for personalised hotel service leads to an operational question: can staff obtain and use relevant guest information at the moment it is needed? In a Medallia survey of 1,749 hotel guests, 23% rated their recent stay 9 or 10 for personalisation, while recall of the surveyed in-stay elements averaged 46%. Perceived personalisation was associated with satisfaction, although the survey does not establish that access to guest data caused either outcome. The finding directs attention to service encounters, where recorded information must become a useful staff action. [R2](#r2)

### 2.3 Current guest-information workflow
#### 2.3.1 Accor Customer Digital Card (ACDC) Case Study
The Accor Customer Digital Card case study maps a five-stage information cycle. A general manager retrieves guest details from a database and communicates relevant points in a morning briefing. Hard-copy or WhatsApp notes can serve as a fallback when staff need to check a detail. During service, staff draw on the briefing or profile while learning new preferences or concerns through conversation. They enter newly learned details into the database afterwards, potentially making them available for later encounters. [P1](#p1) This sequence is a case-study mapping, not a measured description of every hotel or of PARKROYAL's daily operations.

<figure>
<a href="assets/guest-information-five-step-workflow.svg" target="_blank" rel="noopener" aria-label="Open the five-step guest-information workflow diagram">
<img src="assets/guest-information-five-step-workflow.svg" alt="Five-step Accor case-study workflow: retrieve profile, morning brief, fallback notes, serve guest, update record." width="1200" height="315">
</a>
<figcaption><strong>Case-study workflow.</strong> The mapped Accor Customer Digital Card sequence. [P1](#p1)</figcaption>
</figure>

Information must cross several human and system handoffs in this cycle. Staff need to remember or find the right profile, select a detail relevant to the immediate interaction, and record new information accurately enough for another employee to use. A stored profile therefore has limited service value if access is slow, consultation interrupts conversation, or updates arrive after the next encounter.

Information may already exist but remain difficult to act upon because it is separated from the service task, carried in a briefing that staff must remember, or entered only after the encounter has ended. Each route puts a different demand on staff: recall, search, or delayed documentation. These demands are especially consequential during short face-to-face exchanges, when there is little time to recover a missed detail.

#### 2.3.2 The Gaps

The guest-journey mapping identifies three related gaps. First, recognising a guest from a description or profile photograph and filtering the profile can be difficult; a stored preference may consequently be missed. Second, consulting notes or a phone during conversation can divert attention from the guest while staff are expected to listen and engage naturally. Third, a busy employee may postpone an update, and different staff may phrase the same information differently, reducing its reliability for colleagues. [P1](#p1)

Guest identification and information relevance are distinct problems. Finding a profile quickly is insufficient if it belongs to the wrong person; finding the correct profile is also insufficient if staff must search through unrelated details while serving the guest. A preference about a drink may matter at the lounge, whereas a room-setting preference may not. The design need is therefore timely access to the *right* information for the *right* guest and task. This is a design inference from the mapped journey, not evidence that a particular retrieval method will improve service.

<figure>
<a href="assets/guest-information-need-derivation.svg" target="_blank" rel="noopener" aria-label="Open the guest-information cause-to-need diagram">
<img src="assets/guest-information-need-derivation.svg" alt="Three pathways connect guest recognition and search difficulties to missed preferences and a need for rapid retrieval; intrusive note lookup to interrupted conversation and discreet referencing; and delayed, inconsistent updates to lost or unclear details and reliable capture." width="1200" height="500">
</a>
<figcaption><strong>Problem-analysis diagram.</strong> Workflow gaps, likely service consequences, and derived needs. The arrows represent the team's design reasoning, not measured causal effects.</figcaption>
</figure>

The resulting needs are **recognition and rapid retrieval**, **discreet referencing during service**, and **prompt, consistent capture of confirmed information**. They form a connected information cycle: the correct guest must be identified before a cue is useful, and a new detail must be recorded in a usable form before it can support a later interaction.

#### 2.3.3 The First-Time Guest Problem

Returning guests may have accumulated preferences and established rapport; first-time guests may have booking or pre-arrival details but less recorded service history. Their initial encounter is therefore an important opportunity to learn a specific, guest-confirmed detail. If that detail is captured and shared in time, another employee could use it during the same stay. If it remains only in one staff member's memory, the next interaction begins with much of the same information gap.

This creates a possible feedback pattern: limited history offers fewer cues for tailoring service, while failure to capture what is learned leaves the history limited. The pattern is a hypothesis, rather than an established explanation of guest behaviour. It also shows why the first stay is a useful test case. The goal is not to build a complete long-term profile immediately; it is to determine whether one relevant detail from an early interaction can reach a later employee accurately and in time to inform their service.

An industry-partner account reported a single-digit first-time guest retention figure, but its cohort, definition, and time period were not supplied. It is treated here as a preliminary observation, not a verified baseline or evidence that limited personalisation caused low retention. [P1](#p1) The proposed same-stay handover is consequently a design opportunity to test, rather than a demonstrated route to higher return visits.

### 2.4 Design Challenge

The problem is to make guest context available across encounters while preserving natural service. For the first employee, this means recognising the guest and recording an explicit preference or concern with sufficient context. For the next employee, it means finding the correct, relevant detail quickly enough to act on it appropriately.

The intended value differs across the service relationship. Staff may spend less effort recalling briefings or searching notes; guests may experience greater continuity between interactions; and the hotel may have a more dependable basis for consistent personalised service. The next stage must establish whether faster access and more reliable sharing actually help staff make better service decisions without adding disruption or creating incorrect guest associations. These needs lead to the project's design question:

> **How might we enable luxury hotel staff to capture, share, and access relevant guest information seamlessly so that they can deliver consistent, personalised, high-quality service?**

These problem findings lead to the functions, service criteria, and boundaries in [Chapter 3: Aim, scope, and requirements](#requirements).

<div class="flow" role="group" aria-label="Proposed service continuity loop">
<div><b>01 · Capture</b>A guest states a preference.<small>Emerging capability</small></div>
<div><b>02 · Check & share</b>Staff confirm the guest and meaning.<small>Planned approval workflow</small></div>
<div><b>03 · Retrieve</b>The next employee sees relevant context.<small>Demo profiles implemented</small></div>
<div><b>04 · Adapt</b>Staff make a suitable offer and confirm it.<small>Service benefit to evaluate</small></div>
</div>

## 3. Aim, scope, and requirements {#requirements}

The preceding problem analysis identifies three needs: recognise and retrieve guest context quickly, refer to it discreetly during service, and capture new information reliably. These needs concern continuity across encounters. A guest-stated detail must be captured with its context and made available to another employee at the relevant service moment. This section translates the design challenge into two functions and four service criteria, providing a common basis for comparing phone/PMS, audio-cue, and smart-glasses concepts. [P1](#p1)

**First-time guest use case.** A first-time guest may have booking or pre-arrival details but limited recorded service history. The target is to capture one useful, guest-confirmed detail during an early encounter and make it available to another employee during the same stay. For example, a request for unsweetened tea can inform a later lounge visit. A one-off request retains its encounter or stay context rather than becoming a permanent preference.

**Functional requirements.** The solution has two linked functions: capture and process guest context, then select and display information for the current service task.

| Function | Required behaviour | Output |
|---|---|---|
| **Capture and process** | In the proposed complete workflow, one tap starts guest recognition and conversation recording together. Extract explicit guest preferences, requests, or concerns with supporting wording, source, timestamp, guest association, and current-stay context. Prepare a draft for staff review, correction, and approval before saving. | Time-stamped interaction draft associated with the guest and stay; shared only after staff approval. |
| **Select and display** | Retrieve the guest's context, select the smallest detail relevant to the current location, task, and urgency, and present it as a concise cue. Suppress personal cues for unknown, ambiguous, stale, or lost guest associations. | A short, actionable prompt for the employee serving the guest. |

**Service criteria and proposed measures.** The selected PARKROYAL F&B LQA items connect the functions to timely acknowledgement, active listening, natural engagement, and personalisation. [P8](#p8), [R4](#r4)

| Criterion | Service behaviour | Design requirement and measure |
|---|---|---|
| **DR1 · On-time service support** | Timely acknowledgement and offer of service. | Deliver the first correct, readable cue within **1.0 s** of deliberate activation. On enrolled-guest trials with a relevant stored fact, measure activation-to-visible-cue latency and count late, missing, or incorrect cues as target nonattainment. Assess unknown-guest cue suppression separately. |
| **DR2 · Low-effort capture** | Active listening and natural engagement. | Use one tap to start recognition and conversation recording together in the proposed workflow. Measure activation actions, capture time, correction effort, and disruption to listening. |
| **DR3 · Glanceable interaction** | Natural engagement and discreet use of the guest's name. | Present the name and up to two task-relevant cues. Measure correct interpretation, glance duration, attention shifts, missed guest information, and conversational interruption. |
| **DR4 · Preference continuity** | Use guest-confirmed information during a later encounter. | Preserve the statement, source, timestamp, and current-stay context. Measure whether another employee retrieves the correct detail for the correct guest and uses it appropriately during the same stay. |

**Cue timing.** Shiwa et al. (2009) found that preference for a communication robot's response peaked at one second. This finding informs the project's **1.0-second cue-response target**. Applying a robot-response result to smart glasses is an analogy to test, not a smart-glasses standard or LQA requirement. The defined measurement includes capture, guest association, transfer, and rendering, ending when the first correct, readable cue appears. [R12](#r12)

These requirements guide the concept comparison in [Chapter 4](#concepts).

## 4. Concept generation and selection {#concepts}

### 4.1 Functional comparison of the concepts

Three main concepts address the same first-stay scenario: a guest shares a preference, and another employee uses it during a later encounter. The concepts combine alternative methods of capture, guest association, processing, and cue delivery. A camera-free glasses configuration is also considered as a control to isolate the display's contribution. [P1](#p1)

| Function or consideration | Phone/PMS baseline | Audio badge + earpiece | Vision-assisted smart glasses |
|---|---|---|---|
| **Capture** | Staff type a note during or after the encounter. | A deliberate trigger captures speech hands-free. | The proposed tap starts recognition and conversation recording together. |
| **Guest and stay association** | Staff select the guest and stay in the profile. | Staff select the guest through a companion interface. | Visual matching supplies guest context; uncertain matches lead to normal greeting or manual lookup. |
| **Processing and storage** | Staff enter the information manually. | Speech processing extracts guest-stated information with source and stay context. | The same speech-processing function is combined with visual guest association. |
| **Cue delivery** | Staff navigate and read a separate screen. | A short spoken prompt conveys the relevant fact. | A brief visual cue appears near the line of sight. |
| **Staff effort** | Requires profile navigation and note entry. | Keeps the hands available; missed messages require replay and guest selection requires an interface. | Keeps the hands available and allows a brief recheck; fitting and display controls add device interaction. |
| **Privacy and comfort** | Uses the existing profile and handheld screen. | This configuration avoids a camera; microphone use, earpiece fit, volume, and leakage require consideration. | Camera, microphone, and display affect collection, fit, environmental awareness, and acceptance. |
| **Fallback** | Normal service and existing manual procedures. | Mute or replay the cue, or return to phone/PMS lookup. | Suppress personal details on uncertainty, then continue normal service or phone/PMS lookup. |

Guest association and cue delivery are separate design choices. A camera-assisted match can feed either a visual or spoken cue, and display glasses can use manual guest selection. A camera-free glasses configuration therefore provides a useful control for isolating the display's contribution. The baseline, capture method, guest information, and processing should remain consistent when comparing output modalities.

### 4.2 Literature-based benchmarking of visual and audio cues

We benchmarked the visual and audio concepts against published studies of competing speech, dual-task performance, and notifications during face-to-face interaction. This qualitative benchmark links the findings to the service criteria: preserving listening, keeping cues understandable, recovering missed information, and controlling attention demands. The cited studies use controlled tasks rather than hotel staff; they inform design hypotheses for a matched prototype comparison.

Spoken earpiece cues introduce another speech stream into a service conversation. Brungart (2001) demonstrated interference between simultaneously presented spoken phrases. A cue delivered while the guest speaks can therefore compete with the message staff are trying to understand. For this conversation-centred task, a concise visual cue lets staff consult a factual prompt without receiving another spoken message and choose their own wording when replying. [R13](#r13)

Visual presentation also places demands on attention. Lewis and Neider (2016) found that Google Glass information disrupted concurrent visual search. Ward et al. (2023) found interference from both HMD and audible word presentation during manual tracking. The selected display should consequently contain a small amount of task-relevant information, appear at an appropriate moment, and permit a brief recheck. [R9](#r9), [R16](#r16)

| Benchmark consideration | Evidence from published research | Implication for the concept |
|---|---|---|
| **Listening during conversation** | Brungart (2001) found competing speech interfered with recognition of a target spoken phrase. [R13](#r13) | Prefer a short visual fact during guest speech. Reserve spoken cues for on-request delivery or a suitable conversational pause. |
| **Visual attention and workload** | Lewis and Neider (2016) found HUD information disrupted visual search; Ward et al. (2023) observed tracking interference with HMD and audible words. [R9](#r9), [R16](#r16) | Keep either cue brief and relevant. Assess missed guest information and service interruption alongside cue comprehension. |
| **Placement during social interaction** | Rzayev et al. (2020) found notification position and alignment affected perception during face-to-face communication. [R14](#r14) | Treat cue placement as part of the interaction design and assess whether staff can consult it naturally. |
| **Visually demanding tasks** | Nees and Sampsell (2021) found visual icon alerts disrupted visual tracking more than auditory tones. [R15](#r15) | Retain audio as an alternative when visual attention is occupied. Distinguish a simple alert tone from a spoken factual message. |

For this conversation-led lounge scenario, we prioritise visual factual cues to avoid adding a spoken message while the guest is talking. Audio remains a comparator for visually demanding tasks; spoken prompts can be offered on request or between conversational turns. Google's AI-glasses guidance reinforces the display treatment: concise, glanceable elements that appear when needed and recede after the task. [R8](#r8)

For example, equivalent cues could communicate the same guest-stated tea preference: a short visual label or a brief spoken phrase. A matched comparison would measure correct comprehension, missed guest details, service action, time to act, conversational interruptions, rechecks or replays, and comfort. Keeping the fact and task constant separates the effect of the cue modality from the effect of receiving more or less information.

### 4.3 Selected concept and design rationale

**Vision-assisted smart glasses are selected for the prototype** because they package three functions for the lounge encounter: hands-free capture, guest-context retrieval, and a concise visual prompt. Capture can reduce device switching, matching can reduce profile search when reliable, and a short visual fact can be rechecked without adding another voice while the guest speaks. Staff remain free to choose natural wording. These features address DR2 and DR3, while guest association and same-stay information reuse address DR1 and DR4.

The phone/PMS workflow remains the baseline and manual fallback. The camera-free glasses configuration separates visual presentation from face matching, and the audio concept remains a comparator for visually demanding service tasks. The contribution is the connected service workflow: capture a guest-stated detail with its context, retrieve it for the correct guest, and present it when it supports another employee's service action.

[Section 5.1](#initial-concept) translates this selected concept into the proposed staff journey, linking the functional requirements to the interaction and capture design that follow.

## 5. System architecture and prototype development {#prototype}

### 5.1 Solution overview and staff journey {#initial-concept}

The proposed workflow carries one guest-confirmed detail from an early encounter to another employee's later service moment. It links capture, guest/stay association, staff review, and a task-relevant cue. [Chapter 3: requirements](#requirements), [Chapter 4: concept comparison](#concepts)

<figure>
<a href="assets/initial-concept.svg" target="_blank" rel="noopener" aria-label="Open the initial smart-glasses concept diagram">
<img src="assets/initial-concept.svg" alt="The wearer interface sends faces for recognition against cached ArcFace reference vectors. A recognised identity selects the SQLite guest record, which returns name and preference cues directly to the wearer interface." width="1200" height="505">
</a>
<figcaption><strong>Figure 1.</strong> Core functions, models, and guest-data setup, before examining the design iterations.</figcaption>
</figure>

**Proposed staff journey**

1. **Start recognition and recording.** The employee taps the glasses once to start guest recognition and conversation recording together. Staff begin normal service while the system retrieves relevant context.
2. **Check guest association.** A stable, sufficiently supported match enables personal context. For unknown, ambiguous, or lost matches, suppress personal details and continue with normal greeting or phone/PMS lookup.
3. **Present relevant context.** Show only the small amount of information useful to the current task. A lounge drinks cue takes priority over an unrelated room preference.
4. **Confirm today's need.** Staff use the cue to make a natural offer and confirm that the preference still applies, accepting corrections from the guest.
5. **Verify allergy information.** Staff check the authorised guest record and the relevant menu or kitchen source before advising the guest or proposing food.
6. **Process the interaction.** Extract explicit guest statements from the captured conversation and retain their supporting wording, source, timestamp, guest association, and current-stay context.
7. **Review and approve.** Staff correct the wording and confirm the guest and stay before approving the update. The information remains a draft until this check is complete.
8. **Carry context forward.** Another employee retrieves the approved detail during a later encounter, confirms the guest's present need, and uses it to support a suitable service action.

<figure>
<div class="flow" role="group" aria-label="Proposed same-stay staff journey">
<div><b>01 · Activate</b>One tap starts recognition and recording.</div>
<div><b>02 · Serve</b>Use relevant context, confirm today's need, and verify allergy information.</div>
<div><b>03 · Process and review</b>Prepare a sourced, stay-scoped draft; staff correct, confirm, and approve it before saving.</div>
<div><b>04 · Carry forward</b>A later employee retrieves the relevant detail and confirms the guest's present need.</div>
</div>
<figcaption><strong>Figure 2.</strong> Proposed staff journey, from deliberate activation to reuse during the same stay. Unknown or ambiguous guest associations lead to normal greeting or manual lookup.</figcaption>
</figure>

For example, a guest requests unsweetened tea during an early lounge visit. The information is associated with that guest and stay. During a later encounter, another employee receives the relevant cue and asks whether the guest would like unsweetened tea again. The detail informs the offer while the guest remains free to change their preference.

This journey defines the intended behaviour from a single activation to a later service encounter. [Section 5.2: Capture](#capture) develops the capture component through temple-touch activation, session timeout, and processing allocation. It connects these service requirements to the prototype's implementation decisions.

### 5.2 Capture {#capture}

Capture iterations use measurable tests: battery depletion, traffic, silence-timeout duration, latency, and guest facts matched against expected answers. The intended path stores an explicit, time-stamped statement as a sourced draft, associates it with a likely guest/stay, and tracks scope and review status. Staff approval is required before the shared record is updated. Display ranks checked context by location, task, urgency, and validity. Text extraction is explored separately; audio capture and reviewed updates are not integrated.

<figure>
<a href="assets/capture-pipeline.svg" target="_blank" rel="noopener"><img src="assets/capture-pipeline.svg" alt="Intended capture pipeline: video/audio clip, multimodal processing, relevant insight extraction, guest association through face recognition, then recording preferences in the database." width="1200" height="245" loading="lazy"></a>
<figcaption><strong>Figure 3.</strong> Intended capture workflow, before refining activation and processing allocation.</figcaption>
</figure>

#### 5.2.1 Temple-touch activation {#activation}

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

#### 5.2.2 Selective server processing {#processing}

On-device photo recognition averaged **1,927.9 ms**, longer than the proposed **1.0 s** end-to-end cue target. SCRFD and ArcFace recognition dominated the component path, motivating selective offloading. Camera handling, tracking, crop preparation, and rendering remain local; the laptop handles recognition and lookup. This targets **DR1** by keeping position updates responsive; a separate battery benefit remains unmeasured. [P3](#p3), [P5](#p5)

<figure>
<a href="assets/capture-offload-pipeline.svg" target="_blank" rel="noopener"><img src="assets/capture-offload-pipeline.svg" alt="Capture responsibilities: glasses handle temple touch and video/audio sensing; the server handles heavier multimodal analysis, insight extraction, guest association, and database updates in the intended full pipeline." width="1200" height="260" loading="lazy"></a>
<figcaption><strong>Figure 5.</strong> Selective server allocation. Recognition is implemented; automatic preference extraction and updates remain planned.</figcaption>
</figure>

In a 15-probe warm photo test, Wi-Fi offloading averaged **1,350.6 ms**, about 30% below on-device recognition at **1,927.9 ms**. The chart compares this isolated component, not full cue latency or p95 performance. Its protocol, observed ranges, and component timings are in Appendix D. [P5](#p5)

<figure class="chart">
<div class="chart-title">Recognition offloading: approximately 30% lower elapsed time</div>
<div class="chart-subtitle">15 warm photo probes per mode · camera, enrolment and display excluded</div>
<div class="bar-row"><span>Laptop via Wi-Fi</span><div class="bar-track"><div class="bar-fill" style="width:56.275%"></div></div><span class="bar-value">1,350.6 ms</span></div>
<div class="bar-row"><span>On glasses</span><div class="bar-track"><div class="bar-fill secondary" style="width:80.329%"></div></div><span class="bar-value">1,927.9 ms</span></div>
<div class="chart-axis"><span>0</span><span>1,200</span><span>2,400 ms</span></div>
<figcaption><strong>Figure 6.</strong> Elapsed time decreased 29.9%. Self-reference probes establish neither recognition accuracy nor complete touch-to-cue performance.</figcaption>
</figure>

The offloaded mean remains above the proposed 1-second target, and the benchmark excludes camera, image preparation, and display. Only one CPU laptop was tested; a faster server or accelerated inference may help, but any gain needs complete-path testing (Section 6.2).
#### 5.2.3 Independent preference-extraction testing {#preference-extraction}

Text extraction is tested separately for **DR4, preference continuity**; written transcripts are not connected to glasses audio. Two synthetic conversations contained three expected guest facts. Qwen and Gemma each matched two facts, with Qwen fastest at **67.2 seconds per transcript**. All models produced valid JSON, but Gemma misclassified a complaint and a safety question. These small tests provide examples for refinement, not general accuracy estimates. No result is written to a guest record; the full model comparison and checks are in Appendix D. [P1](#p1), [P13](#p13)

Next, improve text-only extraction, then compare it with video from the same interactions to test whether visual context adds useful, supported detail. Evaluate audio transcription separately.

### 5.3 Display {#display}

Display testing uses user feedback on placement, readability, and relevance. The pipeline identifies the guest, retrieves their record, and returns cues.

<figure>
<a href="assets/display-pipeline.svg" target="_blank" rel="noopener"><img src="assets/display-pipeline.svg" alt="Display pipeline: temple touch activates capture on the glasses, the server recognises the guest and retrieves preferences, then returns information for display." width="1200" height="328" loading="lazy"></a>
<figcaption><strong>Figure 7.</strong> Identity-to-record-to-display flow; the placement iteration adds local position updates.</figcaption>
</figure>

#### 5.3.1 Positioning information beside the guest {#display-position}

Initially, cues occupied a fixed display position. User feedback and prototype validation prompted face-relative placement and central guest selection, aiming to reduce looking away from the guest and competing details from several visible faces. These iterations address **DR3, glanceability**. [P1](#p1), [P7](#p7)

Google **ML Kit**, an on-device machine-learning toolkit, detects faces and tracks positions locally; InsightFace identifies the guest. The central **30% of both view axes** defines the selection region, choosing the face nearest its centre. This aims to show preferences for the guest receiving the employee's attention, avoiding details for everyone visible. Selection uses where the glasses point; it does not measure eye contact. [P3](#p3), [R11](#r11)

Face coordinates also allow cropping before image preparation, removing a 2.2–2.4-second full-frame preparation delay. In an earlier SFace-model test, 14 uploads averaged 200 ms from image-analysis callback to server response. This supports the cropping change for **DR1**; the timing excludes tap handling and display and is separate from the current-model benchmark. [P3](#p3)

<figure>
<div class="comparison-grid">
<div><p class="comparison-label">Before · fixed position</p><a href="assets/ui/01-position-before.png" target="_blank" rel="noopener"><img src="assets/ui/01-position-before.png" alt="Generated UI before placement refinement: Ethan Tan's name is at the upper right, away from his face." width="1200" height="1200" loading="lazy"></a></div>
<div><p class="comparison-label">After · beside the face</p><a href="assets/ui/02-position-after.png" target="_blank" rel="noopener"><img src="assets/ui/02-position-after.png" alt="Generated UI after placement refinement: Ethan Tan's name is beside his face." width="1200" height="1200" loading="lazy"></a></div>
</div>
<figcaption><strong>Figure 8.</strong> Generated UI comparison: local tracking brings the cue beside the guest; eye contact is unmeasured. <a href="#p12">P12</a></figcaption>
</figure>

#### 5.3.2 Replacing descriptions with concise icons {#display-content}

Even beside the guest's face, long descriptions require staff to read while listening. To support **DR3**, the display instead shows a name and up to two icons. Preferences and allergy alerts must remain distinguishable. [P1](#p1)

<figure>
<div class="comparison-grid">
<div><p class="comparison-label">Before · written description</p><a href="assets/ui/03-content-before.png" target="_blank" rel="noopener"><img src="assets/ui/03-content-before.png" alt="Generated UI before content refinement: Ethan Tan's name and the words Shellfish allergy." width="1200" height="1200" loading="lazy"></a></div>
<div><p class="comparison-label">After · compact icon</p><a href="assets/ui/04-content-after.png" target="_blank" rel="noopener"><img src="assets/ui/04-content-after.png" alt="Generated UI after content refinement: the written allergy description becomes a shellfish symbol with a warning marker." width="1200" height="1200" loading="lazy"></a></div>
</div>
<figcaption><strong>Figure 9.</strong> Generated UI comparison: text becomes an item-and-warning icon. The allergy is a fictional demo cue. <a href="#p12">P12</a></figcaption>
</figure>

The main icon shows an item, such as coffee; its corner marker means preference (heart), dislike (crossed-out heart), or allergy alert (warning triangle). Icons appear beneath the name and are stored on the glasses, avoiding extra downloads. [P3](#p3)

<figure>
<a href="assets/icon-reference.svg" target="_blank" rel="noopener"><img src="assets/icon-reference.png" alt="Complete supported icon catalogue: king room, twin room, suite, smoking-allowed room, black coffee, green tea, still water, vegetarian food, shellfish, peanuts, milk, and eggs; separate prefer, dislike, and demo-allergy markers; three combined examples." width="1600" height="1000" loading="lazy"></a>
<figcaption><strong>Figure 10.</strong> All 12 supported item icons and three independent markers, with combined examples. Allergy assignments are fictional. <a href="#p3">P3</a></figcaption>
</figure>

The prototype shows at most two icons, puts allergy alerts first, and hides personal details when a guest is unrecognised or the face association is lost. Automated checks verify placement and that names and icons disappear together. [P11](#p11)

Concise information follows display guidance, but short symbols can still distract. User testing must check whether people understand the icons without coaching and use them without interrupting conversation. [R8](#r8), [R9](#r9)

#### 5.3.3 Retrieving contextually relevant preferences {#contextual-retrieval}

The next proposed iteration selects information to fit the moment. Face recognition determines **whose record** to retrieve; conversation and service context determine **which details** to show. Location, task, urgency, and validity could rank the candidates: during breakfast, for example, a checked drink preference should take precedence over an unrelated room arrangement.

<figure>
<a href="assets/context-pipeline.svg" target="_blank" rel="noopener"><img src="assets/context-pipeline.svg" alt="Proposed server pipeline: audio determines conversation context, face recognition determines guest identity, and both guide retrieval of selected guest preferences for display." width="1200" height="400" loading="lazy"></a>
<figcaption><strong>Figure 11.</strong> Proposed contextual retrieval, combining identity and conversation context.</figcaption>
</figure>

This addresses **DR3** and the task-relevance safeguard: an easily understood room icon can still be unhelpful during a drinks order. The proposed filter would select relevant, checked preferences from the shared record (DR4), while retaining priority for allergy alerts under the hotel's verification rules. [P1](#p1)

<figure>
<div class="comparison-grid">
<div><p class="comparison-label">Before · unrelated room preferences</p><a href="assets/ui/05-context-before-extra-room-icons.png" target="_blank" rel="noopener"><img src="assets/ui/05-context-before-extra-room-icons.png" alt="Generated UI before contextual filtering: several room preference icons are displayed during a restaurant interaction." width="1254" height="1254" loading="lazy"></a></div>
<div><p class="comparison-label">Proposed after · relevant drink preference</p><a href="assets/ui/06-context-after.png" target="_blank" rel="noopener"><img src="assets/ui/06-context-after.png" alt="Generated UI of the proposed context refinement: a coffee preference replaces unrelated room icons during dining." width="1200" height="1200" loading="lazy"></a></div>
</div>
<figcaption><strong>Figure 12.</strong> Generated UI comparison illustrating the proposed relevance filter; it is not evidence of implemented conversation understanding. <a href="#p12">P12</a></figcaption>
</figure>

**Current status.** The prototype shows up to two stored reminders, with allergy alerts first. It does not yet interpret conversations to select preferences; microphone activity only controls how long the session runs. [P3](#p3)

Testing should compare the same scenarios with and without filtering: does the system identify the topic correctly, show useful information, or hide something staff need? This tests relevance as well as readability.

### 5.4 Complete system architecture {#system-architecture}

Figure 13 combines the iterations in the **Rokid RV101 → Wi-Fi/HTTP → laptop → display** architecture. Solid paths describe current functions; the dashed extension is planned. [P10](#p10)

<figure>
<a href="assets/system-architecture.svg" target="_blank" rel="noopener" aria-label="Open the full system architecture as a scalable diagram">
<img src="assets/system-architecture.png" alt="Full Rokid architecture: local session control, camera tracking, focus gate, speech activity, network client and display; laptop HTTP API, SCRFD and ArcFace recognition, gallery embeddings and guest-cue caches; dashed future audio-preference pipeline." loading="lazy" width="2400" height="1560">
</a>
<figcaption><strong>Figure 13.</strong> Full implemented architecture and proposed audio-preference extension. <a href="assets/system-architecture.svg" target="_blank" rel="noopener">Open the scalable diagram ↗</a> or <a href="assets/system-architecture.png" target="_blank" rel="noopener">view the full-resolution PNG ↗</a>. Source: <a href="#p10">P10</a>.</figcaption>
</figure>

**Communication.** The glasses send one recognition request at a time to avoid a queue of old images. Late results are ignored so outdated details are not displayed. A swipe checks the server connection. [P3](#p3)

**Recognition.** The server compares faces with stored references. A match needs at least 0.45 similarity and must beat the next candidate by 0.10. Lowering the minimum from 0.50 reduced unrecognised results but may admit wrong matches. These scores measure similarity, not confidence percentages. [P3](#p3), [P11](#p11)

**Shared records.** The server loads guest profiles into memory at startup. This speeds lookup, but database edits require a restart before displayed information changes. DR4 therefore still needs reliable updates reaching another employee. Unique guest IDs should replace name-based lookup to distinguish guests with the same name. Incoming camera images are not saved; unrecognised guests receive no personal details.

The dashed extension would add audio upload, local Whisper transcription, Gemini extraction, and staff-reviewed database updates. These are not connected to the glasses workflow yet. The separate card-entry prototype is also not integrated. [P6](#p6), [P10](#p10)

## 6. User validation and system evaluation {#testing}

This chapter checks the requirements in [Chapter 3](#requirements) and the concept taken forward in [Chapter 4](#concepts) against the narrower demonstrated journey in [Chapter 5](#prototype). It distinguishes observed prototype behaviour from the proposed capture-to-approved-record-to-next-employee workflow.

### 6.1 User validation {#user-validation}

A formative walkthrough with **10 non-hotel participants** examined activation, usefulness, and cue use. It supports problem finding, not proof of improved hotel service. [P1](#p1)

| Walkthrough question | Reported finding | Design implication |
|---|---|---|
| Is starting capture/display easy? | All 10 described activation as easy. | Retain single-tap activation; test it during realistic staff tasks. |
| Could cues help serve guests? | 70% saw potential usefulness, but some icons were unrelated to the conversation. | Develop contextual retrieval and assess whether it enables a specific service action. |
| Can cues be used naturally? | Most described a quick glance as sufficient, but incorporating cues into conversation was challenging. | Test timing, meaning, and conversational flow together; investigate design changes as well as training. |

Understanding an icon and using it in conversation are different tasks. A participant may recognise a coffee preference but be unsure when to mention it. The feedback connects shorter icons (Section 5.3.2) with relevant selection (Section 5.3.3): staff need information that fits the current interaction.

This non-staff study did not compare profile lookup or measure gaze and attention, so it cannot establish improved service or reduced distraction.

### 6.2 Design requirements and whole-system testing {#requirements-check}

Testing covers **tap → guest selection → recognition → profile retrieval → display**. Conversation-to-approved-update and next-employee use remain incomplete. Findings map to Chapter 3's requirements.

On 3 November, 13 live activations included quick repeat taps while capture was already running. Five produced a recognised name and icons in the app's drawing process; four also recorded an Android frame commit, confirming a completed frame was submitted for display. These four averaged **1,180 ms**, median **1,198.5 ms**, range **974–1,349 ms**. [P4](#p4)

| Measured stage, four completed frames | Mean |
|---|---:|
| Tap handled → selected image sent: camera, face selection, image preparation, scheduling | 693 ms |
| Request sent → server response read, including recognition | 302 ms |
| Response read → app draws name and icons | 101.3 ms |
| Drawing → Android confirms frame submitted | 83.8 ms |
| Total | **1,180 ms** |

Server recognition took 177.5 ms within the 302 ms request stage; it is not an additional delay. The largest delay was before sending the image, so optimisation must address capture and selection as well as server speed. Another activation took 4,412 ms to draw information without a completed frame recorded before the next tap; eight had no accepted name/icon output before another tap. Repeat taps can interrupt processing, so these counts do not establish a success rate. Independent starts from idle and physical on-lens timing still need testing.

| Requirement | Current evidence | Assessment and next verification |
|---|---|---|
| **DR1 · On-time support:** proposed 1.0 s trigger-to-correct-visible-cue target | Four successful warm commits averaged 1.18 s; this does not establish the end-to-end 1.0 s target, include cold starts, or include every interrupted attempt. | **Target attainment not established.** Repeat independent cold/warm trials and count all failures; report p50/p95 and the proportion of valid attempts meeting the 1.0 s target. |
| **DR2 · Low effort:** single tap and automatic silence expiry | All 10 participants found activation easy; checks verify timeout and camera/microphone shutdown. | **Early support.** Test staff task interference and stopping behaviour in realistic noise. |
| **DR3 · Glanceability:** concise cues during conversation | Icons are implemented; 70% reported needing only a quick glance, but natural conversational use remained difficult. | **Partially achieved.** Compare comprehension, attention shifts, and conversational flow with a baseline. |
| **DR4 · Preference continuity:** approved update reaches another employee | Stored profiles are retrieved; new facts are not consistently extracted and profile changes require restart. | **Incomplete.** Test captured statement → review → updated record → next employee's action. |
| **Cross-cutting safeguard · Correct association:** hide uncertain/outdated details | Tests check unrecognised guests, tracking changes, expired results, and cancellation. | **Safeguards implemented; real-world error rates unknown.** Count wrong guest details and missed matches in new, crowded test scenes. |
| **Cross-cutting safeguard · Appropriate information:** relevant fields and distinct allergy handling | Two-cue limit and fictional allergy markers exist; irrelevant content was reported. | **Partially achieved in demo data.** Validate contextual selection, interpretation, permissions, and fallback. |

Retrieval and display work; the service benefit and complete handover still need evaluation. The photo benchmark and four live frame measurements cover different stages and must be reported separately.

### 6.3 Limitations and guest acceptance {#guest-acceptance}

In an exploratory survey, **40.7%** rated hotel preference storage 4 or 5. The denominator and recruitment method are unavailable, so this is not a representative acceptance estimate. Comfort with storing preferences does not establish acceptance of facial images or recorded conversations; a lounge entry tap is not permission for every proposed use. Real-person studies need an approved purpose, notice, access, and retention protocol with the hotel and university. The PDPC biometric guide is a reference for review, not approval for this hospitality use. [P1](#p1), [R10](#r10)

The current microphone uses local activity detection only. Audio transcription and an external model would require separate review. Recognition safeguards and fictional allergy icons have not been evaluated for representative error rates or food safety. These limits define the next study; the present prototype remains useful for finding usability and integration problems.

### 6.4 Next development and validation steps {#next-development}

Chapter 7 sets out the next-stage work plan; Appendix B gives a comparative evaluation protocol.

## 7. Limitations, responsible use, and next-stage plan {#next-stage}

The recognition-and-display prototype is the strongest interim outcome; the full handover from a guest statement to another employee's service action remains unvalidated.

**Next-stage controls.** Suppress personal cues for uncertain matches. Save only source-supported preferences after staff confirms the guest, stay, and scope. Verify allergy details against an authorised record and food-safety source. Obtain hotel and university approval for guest and employee data collection; a lounge tap does not authorise face or audio capture. Keep LQA output evidence-linked and human-reviewed, not a staff ranking. [P2](#p2), [P8](#p8), [R10](#r10)

| Window | Work | Evidence or decision |
|---|---|---|
| **Weeks 1–2** | Agree one lounge task, staff roles, profile path, permissions, and study protocol. | Approved workflow and baseline task. |
| **Weeks 2–4** | Label extraction examples, including corrections, ambiguity, and multiple speakers. | Supported/unsupported facts and attribution errors. |
| **Weeks 3–5** | Add staff correction and contextual retrieval for one F&B task. | Confirmed update reaches the next employee. |
| **Weeks 4–6** | Test recognition edge cases, cold/warm latency, and longer battery use. | Count all activations, misses, false reveals, and failures. |
| **Weeks 6–8** | If approved, compare phone and glasses with 6–8 hotel staff. | Correct action, cue comprehension, task time, interruption, and feedback. |
| **Weeks 9–10** | Refine failures and demonstrate the complete same-stay handover. | Requirements check and decision on the wearable direction. |

**Proposed acceptance gates:** no wrong-profile reveals in the defined test set; source-supported approved preferences; reliable no-match fallback; and improved task performance without poorer comprehension or conversation flow. A zero-error result remains limited to the tested sample. Cost and return on investment need later evidence on hardware, infrastructure, integration, maintenance, and training.

## 8. Team contributions {#contributions}

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
| Slide 23 shows a **<1 s** cue target; an earlier speaker-script draft said **1.5 s** | This report adopts **1.0 s** as the proposed target, and the revised speaker script uses the one-second target. The value is informed only by analogy to a communication-robot response study, not an LQA rule or a direct smart-glasses standard. The supplied slide's **<1 s** label expresses the same one-second goal. Four successful warm frame commits averaging 1.18 s do not establish end-to-end target attainment, p95, failures, cold-start performance, or physical lens visibility. |
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

**Battery and latency evaluation.** Repeat balanced conditions from comparable charge levels with the same brightness, network, gallery, capture policy, and workload. Include camera, microphone/VAD, inference, transfer, and display. Measure trigger-to-first-visible-cue latency across all attempts; report p50 and p95 only with enough independent observations, separate cold starts from warm retaps, and count misses, cancellations, and interruptions. Distinguish wall-clock duration, active time, traffic, battery percentage points, and measured energy. Software frame submission does not prove physical lens presentation.

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



## Appendix D. Prototype recognition and extraction detail {#technical-detail}

**Selective photo-recognition benchmark.** Fifteen warm probes per mode used the same enrolled 800 × 800 image, five gallery identities, CPU execution, and 0.50/0.10 score and margin settings. Offline testing disabled Wi-Fi and stopped the laptop server. [P5](#p5)

| Warm photo-recognition path | Mean | Median | Observed range |
|---|---:|---:|---:|
| Glasses → Wi-Fi → laptop → parsed response | 1,350.6 ms | 1,311.6 ms | 1,220.1–1,513.7 ms |
| Entire recognition on glasses | 1,927.9 ms | 1,896.0 ms | 1,848.6–2,379.7 ms |

On-device component means were **1,268.7 ms** for SCRFD preparation, inference, and postprocessing; **639.1 ms** for alignment, ArcFace inference, and matching; and **20.1 ms** for JPEG decoding. The offloaded path was faster in this small warm test; it does not establish identity accuracy or complete touch-to-cue performance. [P5](#p5)

**Text-only extraction test.** Three local models processed two invented, speaker-labelled conversations containing three expected guest facts. A fixed JSON format recorded category, value, and supporting quote; automated checks compared outputs with the guest's words. Testing ran on an M1 Mac. [P13](#p13)

| Model | Valid JSON | Expected guest facts matched | Mean time per transcript |
|---|---:|---:|---:|
| `llama3.2:3b` | 2/2 | 1/3 | 76.1 s |
| `qwen3:4b-instruct` | 2/2 | 2/3 | 67.2 s |
| `gemma4:e2b` | 2/2 | 2/3 | 86.4 s |

Qwen is provisional: it matched Gemma's fact count and ran fastest. Gemma interpreted “too sweet” as a preference and a dessert-safety question as dietary information, despite valid JSON. The sample is too small to establish general accuracy; test negation, corrections, speaker attribution, ambiguity, and repeatability before integration. No outputs changed guest records. [P1](#p1), [P13](#p13)
