# CDE4301 Interim Report — Working Draft

- **Project:** Guest-context cues for the PARKROYAL club lounge
- **Status:** Research-backed draft for supervisor discussion; not a final submission
- **Project direction:** Design-led mixed project, focused on refining and testing an initial prototype
- **Word limit:** Up to 6,000 words for a four-person group, excluding appendices, according to the [interim assessment brief](../rubrics/CDE4301%20assessment%20brief%20and%20rubrics%20-%20AY2026%20-%20interim%20assessment.md).

**Planning brief:** [CDE4301 interim report plan](cde4301-interim-report-plan.md).

> **Drafting note:** This draft fills the report skeleton with current research and project notes. Items marked **To confirm** need evidence from PARKROYAL, the supervisor, or prototype evaluation. Do not convert them into findings without collecting that evidence. The linked [research synthesis](../research/cde4301-interim-report-research-synthesis.md) contains the fuller source audit and limitations.

## Executive summary

Hotel employees balance time-sensitive operational work with guest-facing service. During busy service periods, they may have less opportunity to retrieve and use recorded guest context. Existing hotel research supports investigating workload pressure and competing demands, but it does not show that check-in universally takes priority over personalization or that the same access problem has been confirmed at PARKROYAL. A local Novotel visit provides one example of food-and-beverage staff potentially lacking time to check recorded profiles; this is a separate property and cannot establish PARKROYAL's workflow.

This project will investigate the lounge workflow at PARKROYAL and design a low-disruption way to surface one useful guest cue during food-or-drink service. The proposed proof of concept begins with a guest tapping a lounge card at the entrance. A simulated tap adds the guest to a temporary active-lounge set. A staff-facing device could then associate a visible guest with that set, using face matching or a simpler selection method, and show one current preference plus an explicit allergy alert where relevant. An allergy cue would prompt staff to verify the current information and the food item; it would not make the decision for them.

The main local prototype can simulate entry events, maintain a candidate set, match test images or a laptop-camera feed against synthetic profiles, and show diagnostic match cards. The repository also contains a separate Rokid Android/laptop face-identification demo. Its README reports 30 capture requests over Wi-Fi on 2026-10-22, with 944 ms average and 1,114 ms p95 capture-request-to-response latency; 11 samples contained a detected face. This is a latency measurement, not a recognition-accuracy result, and excludes the wait for the next capture and physical display presentation. The standalone demo is not connected to lounge entry, the active guest set, hotel profiles, or allergy/preference cues; the exact glasses SKU used still needs confirmation. A physical reader, live hotel data, and an employee service interaction are not demonstrated. The next phase should connect the relevant components, validate the workflow, compare face matching with a manual alternative, and run a small simulated evaluation using synthetic or appropriately consenting demo data. Current evidence supports a bounded design investigation, not a claim of reduced real-shift workload, improved guest satisfaction, or safer food service.

## 1. Hotel-service context and why personalization matters

Frontline hotel work includes both guest-facing service and operational responsibilities. In an observational, multilevel study, Vashdi, Katz–Navon, and Delegach examined 245 employees in 39 departments across 13 hotels in one luxury chain. Their results indicate that workload pressure can condition the relationship between service-priority climate, emotional-labour strategies, and manager-rated service performance. The study does not compare check-in with personalization, measure guest-profile retrieval, or show that workload caused a particular service failure. It provides a reason to investigate competing demands, not proof of the specific problem proposed here. [Vashdi et al. (2022)](https://doi.org/10.1177/19389655211029912)

Related research also connects performance pressure with discretionary extra-role service among frontline hospitality employees. “Extra-role service” is broader than personalization, so this evidence should remain background context rather than be presented as a finding about guest profiles. [Rescalvo-Martin et al. (2022)](https://doi.org/10.1016/j.tmp.2022.101030)

For this project, **guest-context personalization** means an employee uses relevant, permitted knowledge about an individual guest to adapt the service or interaction. Recognition, access to context, adaptation, and the guest’s perception that the service fits are different steps. Recognizing a name or displaying a profile does not, by itself, demonstrate personalization. Lei et al. find that a hotel's attempt to tailor service and a guest's perception of that effort can differ; their studies support measuring whether an action feels relevant, not assuming that intent guarantees a good guest experience. [Lei et al. (2024)](https://doi.org/10.1016/j.tourman.2023.104818)

Guest surveys suggest that continuity and responsive service are meaningful examples of personalization. Medallia surveyed 1,749 U.S. hotel guests about recent stays; commonly recalled experiences included having stay details ready, follow-up after a service issue, and being offered a choice in resolving it. These are self-reported recollections from a vendor-produced U.S. survey, not objective service rates or evidence about PARKROYAL. [Medallia (2024)](https://www.medallia.com/wp-content/uploads/pdf/resources/Medallia-Understanding-Personalization-Efforts-in-the-Hospitality-and-Retail-Industries-Report.pdf)

Oracle Hospitality and Skift reported that many surveyed consumers were conditionally open to data-assisted hotel service when they had willingly provided the data for that purpose. This is stated interest in a hypothetical scenario; it is not blanket consent to biometric identification. [Oracle/Skift (2022)](https://www.oracle.com/news/announcement/oracle-hospitality-in-2025-consumer-research-study-2022-06-01/)

Food and drink is a bounded first use case because a current preference can change what an employee offers, while allergy information can prompt a necessary verification step. A guest's name may support a natural greeting, but it is secondary to adapting service. Previous conversations, meeting schedules, and broader profile details are excluded from the first prototype unless discovery establishes a specific, authorized need.

## 2. Problem framing and local evidence

### Working problem statement

> Hotel lounge employees may have limited opportunity to retrieve and apply relevant guest preferences during busy service periods. This project will investigate the PARKROYAL lounge workflow and prototype a low-disruption way to surface an authorized, task-relevant cue at the point of service.

This statement treats workload pressure and missed profile use as a hypothesis. The current evidence does not establish high cognitive load at PARKROYAL, show that staff rank check-in above personalization, or indicate that employees do not value personalization.

### What the local notes support

| Evidence | What it supports | What it does not establish |
|---|---|---|
| Novotel Singapore on Stevens visit notes | A local lead: F&B staff may not have time to consult ACDC during service, may rely on memory or a physical VIP board, and preferences may not transfer consistently between shifts. The notes also mention a three-minute check-in brand standard and peak-period queues. | A measured time-use comparison, that check-in causes missed profile checks, or the same workflow at PARKROYAL. ACDC is an Accor system and must not be attributed to PARKROYAL. |
| PARKROYAL visit notes | Stakeholder interest in VIP recognition in the club lounge; possible fields include name, allergies, and preferences; room-card entry and privacy/access concerns are relevant to the concept. | The full in-lounge F&B workflow, a finding that staff lack time for personalization, or the exact scope of permission for devices, real guest data, or staff testing. |

The team reports that PARKROYAL's General Manager allowed a proof of concept. The visit notes record stakeholder interest but do not specify the permission boundaries. **To confirm:** whether the permission covers synthetic-data demonstration only, staff observation or testing, device use in the lounge, or any real guest information.

## 3. Project aim, research question, and scope

**Aim:** Investigate how guest context currently reaches lounge staff at PARKROYAL and test whether a concise service cue can help staff use one relevant food-or-drink preference during a simulated service interaction.

**Research question:**

> How might a concise, timely guest-context cue help lounge staff use a relevant food or drink preference during service while remaining understandable, useful, and low-disruption?

**Supporting questions:**

1. When and how do lounge staff learn that a guest has arrived and access relevant information?
2. Which guest details are useful, current, and appropriate for the first food-or-drink interaction?
3. How should the prototype connect the lounge-entry event to a guest cue, and is face matching preferable to a manual alternative?
4. In a simulated task, can participants interpret the cue and take an appropriate service action without unacceptable confusion or interruption?

**Initial scope:** One lounge food-or-drink scenario; synthetic profiles or explicitly consenting demo participants; one current preference; a clearly worded allergy alert where applicable; and a manual fallback. The project will not claim to solve hotel staffing, validate a live hotel deployment, or prove a commercial return. Face matching remains a concept to compare, not a fixed requirement.

## 4. User workflow and design requirements

### Proposed journey to validate

1. A guest taps a lounge card at the entrance; in the target workflow, the existing reader opens the door and resolves the guest identity.
2. The system adds the guest reference to a temporary active-lounge set. In the current proof of concept this is simulated; physical reader integration has not been shown.
3. During service, a staff device associates the visible guest with the active set, using face matching or a lower-complexity method such as staff selection.
4. If the association is sufficiently reliable and authorized, the interface shows a concise, task-relevant cue.
5. Staff use the preference as a conversation prompt and verify allergy details against the current authoritative source and food item.
6. A guest leaves the active set on an exit event or after a defined expiry rule. If identity is uncertain, the interface shows no personal guest details and staff use the normal workflow.

Steps 3–6 are design proposals. **To confirm with PARKROYAL:** staff roles, arrival notification, current lookup process, allergy verification, authorized profile fields, and how departures are recorded.

### Initial requirements

| Requirement | First-version treatment | How to assess it |
|---|---|---|
| Support one actual service moment | Focus on food or drink; show one current preference such as a preferred coffee | Staff can explain how the cue would change or support a service action |
| Keep profile data relevant and authorized | Show only fields confirmed as current and accessible to the staff role | Confirm fields and source with the hotel; test whether any displayed detail is unnecessary |
| Make allergy information explicit | Use warning icon plus plain text, e.g. `⚠️ PEANUT ALLERGY`; prompt verification | Participants correctly identify the alert and describe the verification step |
| Prevent uncertain identity from revealing a profile | Suppress all guest-specific details when the match is uncertain; offer manual fallback | Include no-match and ambiguous-match scenarios |
| Avoid overloading or interrupting staff | Use an event-timed, glanceable cue with one preference; no persistent profile stream | Observe reading time, task completion, confusion, and interruption |
| Keep the demo safe and feasible | Use synthetic or consented demo data; avoid live hotel records until permissions are clear | Document the data source, participant notice, and limits of the demo |

### Alternatives to compare

| Concept | Potential benefit | Main trade-off to investigate |
|---|---|---|
| Staff manually select a guest from the active lounge list | Avoids biometric matching; can be prototyped with a phone or tablet | Adds a deliberate lookup step and may be awkward when several guests are present |
| Match a visible guest against the active set | Could reduce repeated lookup actions during service | Identity error can reveal another guest's information; biometric governance and device feasibility are unresolved |
| Use the card tap only, with no in-lounge identification | Simplest data and device path | Does not associate a guest with a staff member at the service moment |

The interim prototype can compare manual selection with face matching in a controlled demonstration. Select a final concept only after the workflow, staff burden, privacy constraints, and hardware path are better understood.

## 5. Concept and prototype status

The current proof of concept supports simulated lounge-entry events, a temporary candidate set, matching of test images or a laptop-camera feed against synthetic guest records, and diagnostic match cards. This establishes a technical starting point for demonstrating candidate association; it does not establish that employees can use the output in service.

The next design increment is a staff-facing cue for one food-or-drink scenario. A possible first view is:

```text
 ALEX (optional)
 ⚠️ PEANUT ALLERGY — confirm with guest and check item
 Coffee: oat milk, no sugar
```

The name is optional. The allergy line must use explicit text; emoji or color alone is ambiguous. A displayed allergy is a prompt to verify, not an instruction to serve or withhold an item. If identity is uncertain, suppress the profile. Keep previous conversations, schedules, and unrelated fields out of the first view.

The current project notes do not show a physical card-reader connection, live hotel-profile connection, or completed staff-facing food-and-drink interaction. The repository's separate Rokid demo captures images about every two seconds and returns recognition names/status, but it is not connected to the hotel POC's active guest set or profile cues. Its README labels the device “Rokid Glass3”; do not assume it validates the available RV101. The integrated glasses path in the architecture document remains a proposal. A phone or tablet interface is a viable evaluation fallback if the target glasses path cannot be confirmed in time.

## 6. Method and evaluation plan

The project uses a design-led, mixed approach: discover and bound the service problem; translate it into requirements; compare concepts; prototype a cue; and run a small formative evaluation. These are proposed next steps unless results are added below.

### Discovery

Walk through the lounge service journey with the supervisor and, if permitted, lounge employees. Ask staff to describe a recent food-or-drink interaction in which guest context was useful or unavailable. Record the role, moment, information source, decision, handoff, and any interruption. This should establish the actual information path before assuming that the entry card tap is available to the service employee.

### Formative prototype evaluation

Use synthetic profiles and a simulated lounge scenario. If feasible and approved, compare the current/manual lookup path with the cue prototype using matched scenarios. Participants, sample size, task order, location, consent process, and supervisor approval must be specified before conducting the study.

Suggested scenarios are: (1) a guest's usual drink preference; (2) an allergy alert that requires staff verification; and (3) an ambiguous identity, no-match, or stale preference. Keep identity-matching outcomes separate from service outcomes.

| Evaluation question | Minimal measures |
|---|---|
| Did the system associate the right guest? | Correct associations, misses, false associations, abstentions, and cue delay |
| Did the participant understand the cue? | Correct interpretation of the preference and allergy wording; clarification requests or errors |
| Did the cue support service? | Whether the participant offered or confirmed an appropriate option and followed the allergy-check step |
| Did it disrupt the task? | Task or retrieval time, interruptions, visible hesitation, and brief usefulness/distraction feedback |
| Did perceived workload change? | Optional NASA-TLX after matched scenarios; exploratory only and not a measure of a real shift |

### Initial outcomes available for this draft

Two technical starting points are recorded. The main local prototype can simulate entry and candidate matching against synthetic profiles and display diagnostic cards. Separately, the Rokid demo's 30-capture run gives preliminary request-to-response timing but does not test the hotel workflow or recognition accuracy. No controlled staff or participant service-evaluation results are included in the current report materials. Add the following only after running and recording the test:

- **Build and date:** `[insert]`
- **Participants and setting:** `[insert or state that no participant study was run]`
- **Tasks and order:** `[insert]`
- **Technical results:** `[main POC: correct / missed / false / abstained associations; delay; failures]`
- **Rokid demo interpretation:** The recorded average was 944 ms and p95 was 1,114 ms from capture request to response on the tested setup. These numbers do not include the next two-second capture interval or display presentation and cannot establish matching accuracy. `[Confirm exact device SKU and repeat only if this demo is part of the evaluation.]`
- **Interaction results:** `[cue interpretation; service action; task time; interruption; participant feedback]`
- **Changes made after testing:** `[insert]`

If no participant evaluation is completed before the interim deadline, report the technical demonstration as an initial outcome and present the service evaluation as a detailed, viable plan. Do not describe a planned test as completed.

## 7. Discussion, limitations, and responsible use

The strongest current rationale is that relevant guest context can support a more fitting service interaction, while workload pressure and information access are worth investigating. The evidence does not establish that PARKROYAL staff currently miss preferences, that check-in is the competing task in the lounge, or that a display reduces workload. A correct face match would establish identification performance only; personalization additionally requires a suitable staff action and, ideally, evidence that the guest experiences the action as relevant.

The local workflow evidence is limited to hotel-visit notes. The Novotel notes provide an F&B example of possible profile-access friction, but one property cannot establish PARKROYAL practice. The PARKROYAL notes support the lounge as a useful bounded case and record interest in the concept, but they do not map the current F&B workflow or the exact POC permission. This report should identify which findings are literature-based, which come from local notes, and which remain design hypotheses.

Biometric identification linked to a guest profile and allergy information require careful purpose, access, accuracy, retention, and participant handling. The [Singapore PDPA](https://sso.agc.gov.sg/Act/PDPA2012) and the [PDPC biometric-data guide](https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/other-guides/guide-to-biometric_17may2022.pdf) provide official reference points, but the PDPC guide focuses on security applications and is not blanket approval for service personalization. Before any real-guest trial, confirm the project purpose, notice/consent or other reviewed basis, authorized roles, bystander treatment, retention/deletion, and correction or withdrawal route with the hotel and university reviewers. A lounge-card tap for access does not by itself demonstrate that a guest agreed to camera capture for personalization.

Allergy information must come from a current, authorized source. A face match must never infer an allergy, and an uncertain match must never reveal the profile. The cue should prompt staff to confirm the guest's current need and check the relevant food item. For early testing, use synthetic or explicitly consenting demo data and provide a normal manual service path.

The glasses path is a separate feasibility risk. Public project documentation does not yet establish continuous camera frames from the exact RV101/phone SDK configuration or reliable cue return to the display. Validate the exact device before promising a live glasses demo; if needed, test the service interaction on a phone/tablet first. A laboratory study found that single-word heads-up-display interruptions slowed visual-search tasks across five experiments; it does not predict hotel-service effects, but supports testing cue timing and distraction rather than assuming a display is unobtrusive. [Lewis & Neider (2016)](https://doi.org/10.1186/s41235-016-0015-6)

## 8. Next steps and conclusion

| Step | Decision or work | Evidence to retain |
|---|---|---|
| 1. Confirm the local problem and permission | Validate the staff role, current information path, one service moment, and the General Manager's POC scope | Workflow map; interview/observation notes; approved data and participant boundary |
| 2. Finalize requirements and concept | Confirm the fields, compare manual selection with face matching, and define no-match and allergy behavior | Requirements matrix; alternative rationale; cue and fallback sketches |
| 3. Complete one end-to-end demo | Connect simulated tap, active set, association or selection, cue, and expiry | Demo record; synthetic data description; known failure cases |
| 4. Check device feasibility | Test the exact glasses camera/display path only if it is needed for the chosen evaluation | Camera-frame and cue-return observations; fallback decision |
| 5. Run a small formative task | Use the approved participant/data setup and preference, allergy, and no-match scenarios | Protocol, participant description, result table, limitations |
| 6. Iterate and report | Fix the most important issue and state remaining risks and responsibilities | Updated prototype, next milestones, individual contribution statement |

The interim project will be strongest if it demonstrates one complete, honest path from a lounge-entry event to a relevant staff cue and evaluates that interaction in a bounded simulation. Its contribution is a tested design direction and a clear account of what remains unresolved—not a claim that facial recognition or smart glasses have already improved hotel service.

## Selected references and project records

- Alfataftah, M. (2026). *Sorry to Interrupt…: How Work Interruptions Relate to Performance of Hotel Front Office Staff*. Auburn University thesis. [Repository record](https://auetd.auburn.edu/handle/10415/10452). Emerging thesis evidence; not a PARKROYAL study.
- Hart, S. G., & Staveland, L. E. (1988). “Development of NASA-TLX.” [NASA-hosted paper](https://human-factors.arc.nasa.gov/groups/TLX/downloads/Hart_Staveland_ORIGINAL_1.pdf).
- Lei, S. S. I., Wang, D., Fong, L. H. N., & Ye, S. (2024). “Recipe for perceived personalization in hotels.” *Tourism Management*, 100, 104818. [DOI](https://doi.org/10.1016/j.tourman.2023.104818).
- Lewis, J. E., & Neider, M. B. (2016). “Through the Google Glass: The impact of heads-up displays on visual attention.” [DOI](https://doi.org/10.1186/s41235-016-0015-6).
- Medallia Market Research (2024). *Understanding Personalization Efforts in the Hospitality and Retail Industries*. [Report](https://www.medallia.com/wp-content/uploads/pdf/resources/Medallia-Understanding-Personalization-Efforts-in-the-Hospitality-and-Retail-Industries-Report.pdf).
- Oracle Hospitality & Skift (2022). *Hospitality in 2025*. [Methodology](https://www.oracle.com/news/announcement/oracle-hospitality-in-2025-consumer-research-study-2022-06-01/).
- Personal Data Protection Commission Singapore. *Guide on Responsible Use of Biometric Data in Security Applications* (2022). [Guide](https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/other-guides/guide-to-biometric_17may2022.pdf).
- Rescalvo-Martin, E., Gutiérrez, L., & Llorens-Montes, F. J. (2022). “Extra-role service under pressure in the hospitality industry.” [DOI](https://doi.org/10.1016/j.tmp.2022.101030).
- Rokid standalone face-identification demo and latency notes. [Repository README](../../rokid/README.md). The run reports timing, not recognition accuracy or hotel-workflow performance.
- Vashdi, D. R., Katz–Navon, T., & Delegach, M. (2022). “Service Priority Climate and Service Performance Among Hospitality Employees.” *Cornell Hospitality Quarterly*, 63(4), 504–518. [DOI](https://doi.org/10.1177/19389655211029912).
- CDE4301 project records: [PARKROYAL visit notes](../../hotel-visit/parkroyal-main-points.md), [Novotel visit notes](../../hotel-visit/novotel-formatted.md), [problem framing](../agents/hotel-smart-glasses-poc.md), and [proposed architecture](../architecture/hotel-lounge-smart-glasses-poc.md).
- Fuller source audit: [CDE4301 interim report research synthesis](../research/cde4301-interim-report-research-synthesis.md).
