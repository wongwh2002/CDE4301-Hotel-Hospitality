# CDE4301 Interim Report — Working Draft

- **Project:** Guest-context cues for the PARKROYAL club lounge
- **Status:** Research-backed draft for supervisor discussion; not a final submission
- **Project direction:** Design-led mixed project, focused on refining and testing an initial prototype
- **Word limit:** Up to 6,000 words for a four-person group, excluding appendices, according to the [interim assessment brief](../rubrics/CDE4301%20assessment%20brief%20and%20rubrics%20-%20AY2026%20-%20interim%20assessment.md).

**Planning brief:** [CDE4301 interim report plan](cde4301-interim-report-plan.md).

> **Drafting note:** This draft fills the report skeleton with current research and project notes. Items marked **To confirm** need evidence from PARKROYAL, the supervisor, or prototype evaluation. Do not convert them into findings without collecting that evidence. The linked [research synthesis](../research/cde4301-interim-report-research-synthesis.md) contains the fuller source audit and limitations.

## Executive summary

Some hotels collect guest preferences and service history to support more personalized experiences, but having the information does not guarantee that frontline staff can use relevant, current, authorized context to adapt service at the right moment. Research makes this a credible hotel-service design question; it does not prove the same gap exists in every hotel or at PARKROYAL.

This project will investigate the question through a bounded test in PARKROYAL's club lounge, where the team has permission to use the lounge as a POC test setting. It will map the current workflow and design a low-disruption way to surface one useful guest cue during food-or-drink service. The proposed proof of concept begins with a guest tapping a lounge card at the entrance. A simulated tap adds the guest to a temporary active-lounge set. A staff-facing device could then associate a visible guest with that set, using face matching or a simpler selection method, and show one current preference plus an explicit allergy alert where relevant. An allergy cue would prompt staff to verify the current information and the food item; it would not make the decision for them.

The main local prototype can simulate entry events, maintain a candidate set, match test images or a laptop-camera feed against synthetic profiles, and show diagnostic match cards. The repository also contains a separate Rokid Android/laptop face-identification demo. Its README reports 30 capture requests over Wi-Fi on 2026-10-22, with 944 ms average and 1,114 ms p95 capture-request-to-response latency; 11 samples contained a detected face. This is a latency measurement, not a recognition-accuracy result, and excludes the wait for the next capture and physical display presentation. The standalone demo is not connected to lounge entry, the active guest set, hotel profiles, or allergy/preference cues; the exact glasses SKU used still needs confirmation. A physical reader, live hotel data, and an employee service interaction are not demonstrated. The next phase should map the workflow, compare face matching with a manual alternative, and run a small simulated evaluation using synthetic or appropriately consenting demo data. Current evidence supports a bounded design investigation, not a claim of improved guest satisfaction, safer food service, or commercial return.

## 1. Hotel-service context and why personalization matters

For this project, **guest-context personalization** means an employee uses relevant, permitted knowledge about an individual guest to adapt the service or interaction. Recognition, context access, service adaptation, and the guest's perception that the service fits are separate stages. A name or profile display by itself is not enough. Lei et al. found that a hotel's attempt to tailor service and a guest's perception of that effort can differ, so the report should measure whether the action seems relevant rather than assume that intent guarantees a good guest experience. [Lei et al. (2024)](https://doi.org/10.1016/j.tourman.2023.104818)

Customer–employee rapport offers a useful theory for the interpersonal side of recognition. Gremler and Gwinner linked rapport dimensions with satisfaction, loyalty intention, and word of mouth in two service contexts. This supports the idea that personal connection and an enjoyable interaction can matter in service; it does not mean a hotel employee and guest are literally friends or that every guest wants familiarity. [Gremler & Gwinner (2000)](https://journals.sagepub.com/doi/10.1177/109467050031006)

The “friend who keeps asking your name” example is a relatable presentation hook, not evidence. A 2026 restaurant study found that name use can support satisfaction through rapport, but overuse or awkward use can create discomfort. Frequent luxury-hotel guests interviewed by Buehring and O'Mahony also described being acknowledged and remembered as a valued experience, although their sample of 25 cannot represent all hotel guests. Use a name as an optional, natural recognition cue; test the guest's comfort and do not treat a name alone as personalized service. [Raja et al. (2026)](https://research.monash.edu/en/publications/call-me-by-my-name-the-effects-of-addressing-customers-by-their-n/) · [Buehring & O'Mahony (2019)](https://doi.org/10.1108/JHTI-11-2018-0077)

Guest surveys suggest that continuity and responsive service are meaningful examples of personalization. Medallia surveyed 1,749 U.S. hotel guests about recent stays; commonly recalled experiences included having stay details ready, follow-up after a service issue, and being offered a choice in resolving it. Guests recalled fewer listed personalization elements during the stay itself than at several other journey stages. These are self-reported recollections from a vendor-produced U.S. survey, not objective service rates or evidence of the cause. [Medallia (2024)](https://www.medallia.com/press-release/medallia-research-finds-61-percent-of-consumers-are-willing-to-spend-more-for-personalized-experiences/)

Hotels use guest-facing preference capture and internal systems to store or route service requests. In one hotel field study, preferences entered through an IT-enabled system were associated with higher service and value ratings; it was a single-property observational study, not a test of a lounge cue. The Novotel visit notes separately describe ACDC and role-based profile access. These examples show that recorded context exists in some hotel workflows; they do not establish one industry-wide system or prove that PARKROYAL uses ACDC. [Piccoli et al. (2017)](https://doi.org/10.1016/j.tourman.2016.08.015) · [Novotel visit notes](../../hotel-visit/novotel-formatted.md)

Food and drink is a bounded first use case because a current preference can change what an employee offers. A dietary restriction may affect inclusion or safety and needs a distinct verification path. A guest's preferred room type is more relevant to booking or room assignment, while previous conversations or meeting schedules should remain outside the first prototype unless discovery establishes a specific, authorized need.

## 2. Problem framing and local evidence

### Working problem statement

> Some hotels collect guest preferences and service history to support personalized experiences, but having the information does not guarantee that frontline staff can use relevant, current, authorized context to adapt service at the right moment. Research makes this a credible hotel-service design question, but does not prove the same gap exists in every hotel or at PARKROYAL. We will investigate it through a bounded test in PARKROYAL's club lounge and prototype whether a staff-facing cue can make one guest preference actionable during food-and-drink service.

This statement distinguishes an evidence-supported industry question from a locally confirmed problem. The current evidence does not establish PARKROYAL's profile system, staff access path, or the exact point where relevant guest context does or does not change service.

### What the local notes support

| Evidence | What it supports | What it does not establish |
|---|---|---|
| Novotel Singapore on Stevens visit notes | A local lead about ACDC, role-dependent access, pre-arrival profile review, and reported F&B reliance on memory or a physical VIP board. | A measured rate of profile use, a causal explanation for any gap, or the same workflow at PARKROYAL. ACDC is an Accor system and must not be attributed to PARKROYAL. |
| PARKROYAL visit notes | Stakeholder interest in VIP recognition in the club lounge; possible fields include name, allergies, and preferences; room-card entry and privacy/access concerns are relevant to the concept. | The full in-lounge F&B workflow, a finding that staff lack time for personalization, or detailed conditions for staff testing, devices, live guest records, images, or biometric processing. |

The team has permission from PARKROYAL to use the club lounge as the POC test setting. This establishes the case location, not blanket approval for every test method. **To confirm:** conditions for dates and device use, staff observation or testing, customer presence, and any use of real guest records, images, or biometric processing. Use synthetic profiles and consenting demo participants until the relevant boundaries are agreed.

## 3. Project aim, research question, and scope

**Aim:** Map how guest context currently reaches lounge staff at PARKROYAL and test whether a staff-facing cue can make one relevant food-or-drink preference actionable during a simulated service interaction.

**How might we:**

> How might we help hotel frontline staff use relevant, authorized guest context to adapt a service interaction in a way that feels fitting to the guest?

The project will explore this hotel-level design question through the permitted PARKROYAL club-lounge test setting.

**Research question:**

> How can a staff-facing prototype make a current guest preference actionable during a PARKROYAL lounge interaction, and how well can participants understand and use the cue in a simulated scenario?

**Supporting questions:**

1. When and how do lounge staff learn that a guest has arrived and access relevant information?
2. Which guest details are useful, current, and appropriate for the first food-or-drink interaction?
3. How should the prototype connect the lounge-entry event to a guest cue, and is face matching preferable to a manual alternative?
4. In a simulated task, can participants interpret the cue and take an appropriate service action without unacceptable confusion or interruption?

**Initial scope:** Hotel and restaurant research for context; one PARKROYAL lounge food-or-drink scenario for discovery and prototype evaluation; synthetic profiles or explicitly consenting demo participants; one current preference; a clearly worded allergy alert where applicable; and a manual fallback. The project will not claim to validate a live hotel deployment or prove a commercial return. Face matching remains a concept to compare, not a fixed requirement.

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
| Fit the cue to the service moment | Use an event-timed, glanceable cue with one preference; no persistent profile stream | Observe whether the participant sees it at the right moment, understands it, and can continue the interaction naturally |
| Keep the demo safe and feasible | Use synthetic or consented demo data; avoid live hotel records until permissions are clear | Document the data source, participant notice, and limits of the demo |

### Alternatives to compare

| Concept | Potential benefit | Main trade-off to investigate |
|---|---|---|
| Staff manually select a guest from the active lounge list | Avoids biometric matching; can be prototyped with a phone or tablet | Adds a deliberate lookup step and may be awkward when several guests are present |
| Match a visible guest against the active set | Could reduce repeated lookup actions during service | Identity error can reveal another guest's information; biometric governance and device feasibility are unresolved |
| Use the card tap only, with no in-lounge identification | Simplest data and device path | Does not associate a guest with a staff member at the service moment |

The interim prototype can compare manual selection with face matching in a controlled demonstration. Select a final concept only after the workflow, privacy constraints, and hardware path are better understood.

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
| Did the cue fit the service flow? | Task or retrieval time, interruptions, visible hesitation, and brief usefulness feedback |

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

The strongest current rationale is that relevant guest context can support a more fitting service interaction, while the path from recorded information to a staff action is worth investigating. The evidence does not establish PARKROYAL's profile system, lounge staff access path, or exact local barrier. A correct face match would establish identification performance only; personalization additionally requires a suitable staff action and, ideally, evidence that the guest experiences the action as relevant.

The local workflow evidence is limited to hotel-visit notes. The Novotel notes provide an F&B example of possible profile-access friction, but one property cannot establish PARKROYAL practice. The team has permission to use PARKROYAL's lounge as the POC test setting; that gives the project a bounded case, but does not establish the current F&B workflow or approval for live guest records, images, biometric processing, or every participant/device arrangement. This report should identify which findings are literature-based, which come from local notes, and which remain design hypotheses.

Biometric identification linked to a guest profile and allergy information require careful purpose, access, accuracy, retention, and participant handling. The [Singapore PDPA](https://sso.agc.gov.sg/Act/PDPA2012) and the [PDPC biometric-data guide](https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/other-guides/guide-to-biometric_17may2022.pdf) provide official reference points, but the PDPC guide focuses on security applications and is not blanket approval for service personalization. Before any real-guest trial, confirm the project purpose, notice/consent or other reviewed basis, authorized roles, bystander treatment, retention/deletion, and correction or withdrawal route with the hotel and university reviewers. A lounge-card tap for access does not by itself demonstrate that a guest agreed to camera capture for personalization.

Allergy information must come from a current, authorized source. A face match must never infer an allergy, and an uncertain match must never reveal the profile. The cue should prompt staff to confirm the guest's current need and check the relevant food item. For early testing, use synthetic or explicitly consenting demo data and provide a normal manual service path.

The glasses path is a separate feasibility risk. Public project documentation does not yet establish continuous camera frames from the exact RV101/phone SDK configuration or reliable cue return to the display. Validate the exact device before promising a live glasses demo; if needed, test the service interaction on a phone/tablet first. A laboratory study found that single-word heads-up-display interruptions slowed visual-search tasks across five experiments; it does not predict hotel-service effects, but supports testing cue timing and distraction rather than assuming a display is unobtrusive. [Lewis & Neider (2016)](https://doi.org/10.1186/s41235-016-0015-6)

## 8. Next steps and conclusion

| Step | Decision or work | Evidence to retain |
|---|---|---|
| 1. Map the local workflow and test conditions | Validate the staff role, current information path, one service moment, and the conditions attached to using the lounge as the test setting | Workflow map; interview/observation notes; agreed data and participant boundary |
| 2. Finalize requirements and concept | Confirm the fields, compare manual selection with face matching, and define no-match and allergy behavior | Requirements matrix; alternative rationale; cue and fallback sketches |
| 3. Complete one end-to-end demo | Connect simulated tap, active set, association or selection, cue, and expiry | Demo record; synthetic data description; known failure cases |
| 4. Check device feasibility | Test the exact glasses camera/display path only if it is needed for the chosen evaluation | Camera-frame and cue-return observations; fallback decision |
| 5. Run a small formative task | Use the approved participant/data setup and preference, allergy, and no-match scenarios | Protocol, participant description, result table, limitations |
| 6. Iterate and report | Fix the most important issue and state remaining risks and responsibilities | Updated prototype, next milestones, individual contribution statement |

The interim project will be strongest if it demonstrates one complete, honest path from a lounge-entry event to a relevant staff cue and evaluates that interaction in a bounded simulation. Its contribution is a tested design direction and a clear account of what remains unresolved—not a claim that facial recognition or smart glasses have already improved hotel service.

## Selected references and project records

- Gremler, D. D., & Gwinner, K. P. (2000). “Customer-Employee Rapport in Service Relationships.” *Journal of Service Research*, 3(1), 82–104. [DOI](https://doi.org/10.1177/109467050031006).
- Lei, S. S. I., Wang, D., Fong, L. H. N., & Ye, S. (2024). “Recipe for perceived personalization in hotels.” *Tourism Management*, 100, 104818. [DOI](https://doi.org/10.1016/j.tourman.2023.104818).
- Lewis, J. E., & Neider, M. B. (2016). “Through the Google Glass: The impact of heads-up displays on visual attention.” [DOI](https://doi.org/10.1186/s41235-016-0015-6).
- Medallia Market Research (2024). *Understanding Personalization Efforts in the Hospitality and Retail Industries*. [Report](https://www.medallia.com/wp-content/uploads/pdf/resources/Medallia-Understanding-Personalization-Efforts-in-the-Hospitality-and-Retail-Industries-Report.pdf).
- Piccoli, G., Lui, T.-W., & Grün, B. (2017). “The impact of IT-enabled customer service systems on service personalization, customer service perceptions, and hotel performance.” *Tourism Management*, 59, 349–362. [DOI](https://doi.org/10.1016/j.tourman.2016.08.015).
- Raja, S. V. S., Cheng, Y., & Danaher, T. S. (2026). “Call me by my name: The effects of addressing customers by their names, the underlying mechanisms, and the boundary conditions.” *Journal of Retailing*. [DOI](https://doi.org/10.1016/j.jretai.2026.03.008).
- Hapi and Revinate (2025). *The Future of Hotel Data*. [Survey findings and method](https://www.revinate.com/press-releases/the-future-of-hotel-data-report-reveals-nearly-50-of-hoteliers-struggle-to-access-critical-data/).
- Oracle Hospitality & Skift (2022). *Hospitality in 2025*. [Methodology](https://www.oracle.com/news/announcement/oracle-hospitality-in-2025-consumer-research-study-2022-06-01/).
- Personal Data Protection Commission Singapore. *Guide on Responsible Use of Biometric Data in Security Applications* (2022). [Guide](https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/other-guides/guide-to-biometric_17may2022.pdf).
- Rokid standalone face-identification demo and latency notes. [Repository README](../../rokid/README.md). The run reports timing, not recognition accuracy or hotel-workflow performance.
- Buehring, J. H., & O'Mahony, B. (2019). “Designing memorable guest experiences: Development of constructs and value generating factors in luxury hotels.” *Journal of Hospitality and Tourism Insights*, 2(4), 358–376. [DOI](https://doi.org/10.1108/JHTI-11-2018-0077).
- CDE4301 project records: [PARKROYAL visit notes](../../hotel-visit/parkroyal-main-points.md), [Novotel visit notes](../../hotel-visit/novotel-formatted.md), [problem framing](../agents/hotel-smart-glasses-poc.md), and [proposed architecture](../architecture/hotel-lounge-smart-glasses-poc.md).
- [Personalization argument and presentation Q&A](cde4301-personalization-argument-and-qa.md) — expanded reasoning and likely oral-defense questions.
- Fuller source audit: [CDE4301 interim report research synthesis](../research/cde4301-interim-report-research-synthesis.md).
