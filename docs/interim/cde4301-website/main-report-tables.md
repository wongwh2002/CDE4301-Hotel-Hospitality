# Main Report Tables

Editable source for Tables 1–9 in the [interim report](report.html). The report displays an image of each table in its original position; this file preserves the complete table text.

## Table 1. Functional Requirements {#table-1}

| Function | Required behaviour and boundary |
|---|---|
| **Capture and process** | Record a guest-stated preference, request, or concern with its source and time. Keep explicit statements distinct from staff observations and model inferences; retain enough supporting wording for staff to check a draft. |
| **Associate and prepare** | Link the draft to a likely guest and current stay only when the association is sufficiently confident. Keep scope, source, timestamp, and review state with the draft. If identity or meaning is uncertain, ask staff to resolve it or leave it unlinked. |
| **Review and carry forward** | Let staff correct the draft, confirm the guest and stay, and approve the record before it becomes shared context. A confirmed detail should be available to the next employee; a single visit-specific request must not silently become a permanent preference. |
| **Select and display** | Choose the smallest task-relevant detail and show it as a brief, actionable cue. Do not surface a raw transcript or unrelated profile fields. An uncertain match suppresses personal cues and leaves normal greeting or manual profile lookup available. |

[Return to Table 1 in the report](report.html#table-1).

## Table 2. Design Requirements DR1–DR6 {#table-2}

| Criterion | Service behaviour | Requirement and proposed measure |
|---|---|---|
| **DR1 · On-time service support** | Timely acknowledgement and offer of service. | Show the first correct, readable cue within **1.0 s** of deliberate activation. Measure the complete trigger-to-visible-cue path and count late, missing, or incorrect cues as failures to meet the target. Assess unknown-guest suppression separately; time entry/seating to the staff action as a separate service measure. |
| **DR2 · Low-effort capture** | Active listening and natural engagement. | Start capture with one deliberate action and avoid lengthy note-taking. Measure capture time, staff actions, correction effort, and disruption to conversation. |
| **DR3 · Glanceable interaction** | Natural, friendly engagement and discreet use of the guest's name. | Keep the cue short and understandable during conversation. Measure correct comprehension, glance duration, attention shifts, and interruption. |
| **DR4 · Preference continuity** | Use confirmed context to personalise service. | Preserve source, time, scope, and review status. Measure whether the correct approved preference reaches the next employee in time and whether that employee interprets it correctly. |
| **DR5 · Correct guest association** | No personal details for unknown, ambiguous, stale, or lost matches. | Suppress cues on uncertain identity and provide manual lookup. Count false reveals, missed matches, stale results, and fallback use in multi-guest scenarios. |
| **DR6 · Appropriate, safe information** | Present task-relevant information while distinguishing allergy alerts from preferences. | Limit displayed fields, test cue relevance and interpretation, and verify allergy details through authorised records and food-safety procedures. |

[Return to Table 2 in the report](report.html#table-2).

## Table 3. Concept Comparison {#table-3}

| Comparison row | Phone/PMS baseline | Audio badge + earpiece | Camera-free glasses hybrid | Vision-assisted smart glasses |
|---|---|---|---|---|
| **Capture** | Staff enters a note in the existing profile after or during the interaction; familiar, but screen use and delayed entry may interrupt or lose detail. | A deliberate push-to-talk action captures speech hands-free; noise, speaker attribution, and correction needs require testing. | The microphone captures speech after a deliberate trigger; a companion interface selects or confirms the guest. | Triggered microphone capture adds visual context from the camera, with greater collection and battery demands. |
| **Guest and stay association** | Staff selects the guest and stay in the profile; the step is visible and correctable but takes time. | Staff still selects or confirms the guest and stay in a companion interface; speech does not identify its speaker by itself. | The same explicit selection avoids face matching and helps isolate the display's value. | Vision can suggest a guest match and reduce lookup when correct; ambiguous or unstable matches must not reveal profile details. |
| **Processing and review** | The existing profile workflow handles the note; the staff member checks what they entered. | A transcript can become a structured draft, but staff checks the wording and confirms the guest and stay before saving. | Use the same processing and staff-review path as the audio concept, so the display can be compared separately. | Use the same draft and review path; recognition is an association aid, not approval to save or act on an inferred preference. |
| **Cue delivery** | The phone offers profile detail but requires staff to look down and navigate. | A short earpiece cue can be private and hands-free; audibility, comfort, and comprehension in a noisy lounge need testing. | A concise in-lens cue keeps information near the line of sight without a camera. | A concise in-lens cue can follow a visual match, but may draw attention from the guest or affect eye contact. |
| **Staff effort** | Manual navigation and note entry add steps, though the workflow uses familiar equipment. | Capture is hands-free, but guest selection and companion-interface review remain. | Capture and glanceable display may reduce device switching; fitting, controls, and review still take effort. | It may combine capture, association, and cue delivery, while confirmation and camera/display setup add work. |
| **Privacy and comfort** | No new wearable sensor is needed, but viewing a profile in front of the guest may feel intrusive. | No camera is used; recorded speech still needs clear purpose, access, retention, and guest-notice decisions. | A microphone and display still affect privacy and comfort; removing the camera reduces visual collection. | Camera, microphone, and display create the greatest face-data, recording, comfort, and acceptance questions. |
| **Integration and fallback** | Uses the current profile and phone path, with manual lookup as the baseline. | Needs a reliable mic, speech processing, and earpiece; use phone/PMS if capture fails. | Also needs a working microphone, display, companion selection, and device link; fall back to phone/PMS. | Needs a validated camera/display link and safe matching against the active guest set; on uncertainty or device failure, suppress cues and use phone/PMS. |

[Return to Table 3 in the report](report.html#table-3).

## Table 4. Literature-Based Comparison of Visual and Audio Cues {#table-4}

| Benchmark consideration | Published evidence | Implication for the lounge concept |
|---|---|---|
| **Listening during conversation** | Competing spoken phrases interfered with target-speech recognition. [R69](report.html#r69) | Prefer a short visual fact while the guest speaks; test spoken cues on request or between turns. |
| **Attention and workload** | HUD information disrupted visual search; both head-mounted and audible words interfered with tracking. [R9](report.html#r9), [R72](report.html#r72) | Keep either cue brief and relevant. Measure missed guest information and service interruption alongside comprehension. |
| **Placement during social interaction** | Notification position and alignment affected perception during face-to-face communication. [R70](report.html#r70) | Assess whether staff can consult a face-relative cue naturally while engaging the guest. |
| **Visually demanding tasks** | Visual icon alerts disrupted continuous visual tracking more than auditory tones. [R71](report.html#r71) | Retain audio as a comparator when visual attention is occupied; distinguish a simple tone from a spoken factual message. |

[Return to Table 4 in the report](report.html#table-4).

## Table 5. Activation and Battery Comparison {#table-5}

| Activation comparison | Continuous | Temple touch + silence timeout |
|---|---:|---:|
| Scheduled duty cycle | 100% | 25% |
| Reported traffic count | 705 | 170 |
| Battery-level drop | 28 percentage points | 9 percentage points |

[Return to Table 5 in the report](report.html#table-5).

## Table 6. Formative Walkthrough Findings {#table-6}

| Walkthrough question | Reported finding | Design implication |
|---|---|---|
| Is starting capture/display easy? | All 10 described activation as easy. | Retain single-tap activation; test it during realistic staff tasks. |
| Could cues help serve guests? | 70% saw potential usefulness, but some icons were unrelated to the conversation. | Develop contextual retrieval and assess whether it enables a specific service action. |
| Can cues be used naturally? | Most described a quick glance as sufficient, but incorporating cues into conversation was challenging. | Test timing, meaning, and conversational flow together; investigate design changes as well as training. |

[Return to Table 6 in the report](report.html#table-6).

## Table 7. Live Frame-Commit Timing {#table-7}

| Measured stage, four completed frames | Mean |
|---|---:|
| Tap handled → selected image sent: camera, face selection, image preparation, scheduling | 693 ms |
| Request sent → server response read, including recognition | 302 ms |
| Response read → app draws name and icons | 101.3 ms |
| Drawing → Android confirms frame submitted | 83.8 ms |
| Total | **1,180 ms** |

[Return to Table 7 in the report](report.html#table-7).

## Table 8. Design Requirements Evaluation {#table-8}

| Requirement | Current evidence | Assessment and next verification |
|---|---|---|
| **DR1 · On-time support:** 1.0 s from activation to a correct, visible cue | Four successful warm frame commits averaged 1.18 s, above the target; physical lens timing, cold starts, and all interrupted attempts are not established. | **Requirement not met.** Test a more powerful server and optimise capture/scheduling, then repeat independent complete-path trials, count failures, and report p50/p95 and the share meeting 1.0 s. |
| **DR2 · Low effort:** single tap and automatic silence expiry | All 10 participants found activation easy; checks verify timeout and camera/microphone shutdown. | **Early support.** Test staff task interference and stopping behaviour in realistic noise. |
| **DR3 · Glanceability:** concise cues during conversation | Icons are implemented; 70% reported needing only a quick glance, but natural conversational use remained difficult. | **Partially achieved.** Compare comprehension, attention shifts, and conversational flow with a baseline. |
| **DR4 · Preference continuity:** approved update reaches another employee | Stored profiles are retrieved; new facts are not consistently extracted and profile changes require restart. | **Incomplete.** Test captured statement → review → updated record → next employee's action. |
| **DR5 · Correct association:** hide uncertain/outdated details | Tests check unrecognised guests, tracking changes, expired results, and cancellation. | **Safeguards implemented; real-world error rates unknown.** Count wrong guest details and missed matches in new, crowded test scenes. |
| **DR6 · Appropriate information:** relevant fields and distinct allergy handling | Two-cue limit and fictional allergy markers exist; irrelevant content was reported. | **Partially achieved in demo data.** Validate contextual selection, interpretation, permissions, and fallback. |

[Return to Table 8 in the report](report.html#table-8).

## Table 9. January–May Development Roadmap {#table-9}

| Workstream | Planned Window | Intended Deliverable |
|---|---|---|
| Subsystem refinement | January–February | More reliable activation, display and recognition components. |
| Real-time capture and processing | January–February | Integrated capture, transcription/extraction experiments and staff review of proposed facts. |
| Retrieval and recognition integration | February–March | Correct guest/stay association and context-sensitive retrieval of approved information. |
| End-to-end system integration | March–April | Guest statement → checked update → next employee's actionable cue. |
| Internal functional testing | March–April | Repeatable checks for all six design requirements, including failure and privacy cases. |
| Hotel-staff usability pilot | April | Approved comparative pilot against ordinary phone/PMS lookup; assess cue use and workflow fit. |
| Iteration and reliability improvements | April–May | Resolve failures and refine response time, robustness, cue relevance and usability. |
| Final evaluation and documentation | May | Requirements evidence, limitations, final demonstration and report. |

[Return to Table 9 in the report](report.html#table-9).
