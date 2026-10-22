# CDE4301 interim report research synthesis

- **Prepared:** 2026-10-22
- **Purpose:** A report-ready synthesis to support the interim report and a discussion with the professor. It builds on the project's existing research notes and hotel-visit records.
- **Scope:** A hotel-service problem hypothesis with a design-led proof of concept (POC) in the PARKROYAL club lounge. The evidence below does not establish that this problem is universal or that facial recognition is the right solution.

## Executive summary

The most defensible project question is whether guest context that a hotel has recorded can be turned into a relevant, authorized service action at the point where staff serve the guest. Personalization can support perceived service fit and professional rapport, but a name or profile display alone is not the outcome. Hotel systems and local visit notes show that some properties collect preferences and route guest requests; broader evidence also identifies data-access, system-integration, and guest-experience gaps. None of this proves that the same barrier occurs at PARKROYAL.

Use a hotel-service design problem, informed by broader hospitality, restaurant, and food-service research. Keep discovery, prototyping, and evaluation bounded to the PARKROYAL club lounge, which the team has permission to use as the POC test setting. The Novotel ACDC example is a separate Accor property and cannot stand in for PARKROYAL's workflow. Permission to use the lounge as a test setting does not itself establish approval for live guest records, images, biometric processing, or every participant/device arrangement.

For the interim report, define personalization as an employee using relevant, permitted guest knowledge to adapt the interaction or service. Keep four stages separate: recognition, context access, service adaptation, and the guest's perceived fit. The POC can explore whether a staff-facing cue makes one current food or drink preference actionable, with a separate verification path for allergy information. A successful early prototype would show a functioning path and that participants can interpret and use the cue in a simulation. It would not by itself prove improved guest satisfaction, safe food service, or commercial impact.

## 1. From recorded guest information to service action

### The service pathway

A useful way to frame the design problem is as a sequence:

1. **Capture:** A guest shares a preference or a staff member records relevant context.
2. **Store and govern:** The information is kept in an appropriate system, with access limited by purpose, role, and accuracy requirements.
3. **Make available:** The employee serving the guest can retrieve the current, relevant detail at a useful moment.
4. **Adapt:** The employee uses judgment to change an offer, interaction, or service step.
5. **Check fit:** The guest experiences the action as relevant, respectful, and welcome.

A break at any stage can mean that having data does not lead to personalized service. Recognition is only an identification step; it does not establish that staff found the right context or adapted service.

### What hotel service systems already do

Hotels use guest-facing preference capture and internal records to support service. Piccoli, Lui, and Grün's mixed-method study examined one independent 122-room four-star hotel. Its traditional process recorded guest requests in PMS traces and routed them to the responsible department; the hotel later added a personalized web page with 57 preference options. In 98,330 reservation records, the IT-enabled process was associated with more recorded preferences and higher service/value rating categories among linked reviews. This shows one way data capture and routing can support service, but it is a single-property observational study and does not test a live staff cue in a lounge. [Piccoli et al., *Tourism Management*](https://doi.org/10.1016/j.tourman.2016.08.015) · [Open manuscript](https://dds.cct.lsu.edu/ddslab/pdf/piccoliLuiGruen.pdf)

Bonaretti and colleagues studied a customer-service system across seven independently run Swiss hotels using 118,647 reservations over 26 months. The study examined digital preference representations and their use in eliciting and delivering personalized service. The results support the role of systems in helping employees apply guest preferences, but do not imply that every hotel uses the same workflow or that a glasses interface is needed. [Bonaretti et al., *Information & Management*](https://doi.org/10.1016/j.im.2020.103346)

The Novotel Singapore on Stevens visit notes describe ACDC as a guest-information system containing preferences and observations, with access limited by role and operational need. They report that managers review some profiles before arrival and that food-and-beverage staff may rely on memory or a physical VIP board instead of consulting the system during service. These are local visit/interview notes, not usage measurements, and they apply to Novotel rather than PARKROYAL. [Novotel visit notes](../../hotel-visit/novotel-formatted.md)

### Why the data-to-service gap is plausible

Hapi and Revinate's 2025 survey of nearly 200 hospitality professionals reported that 49% struggled to access data for broad operational or revenue decisions and 40% identified disconnected systems as their biggest data obstacle. It is a vendor-sponsored, self-reported survey with limited public sampling detail; these figures are not frontline guest-profile lookup rates. [Survey findings and method](https://www.revinate.com/press-releases/the-future-of-hotel-data-report-reveals-nearly-50-of-hoteliers-struggle-to-access-critical-data/)

Hiezl and Gyurácz-Németh (2025) developed a measure of personalization-supporting technology and surveyed **105 hotels from a population of 458**. Their results indicate variation in which practices were established, with some higher-tech capabilities less developed. This adds a hotel-technology perspective, but it is provider-reported capability rather than a direct observation of staff retrieving a profile during a specific service moment. [Hiezl & Gyurácz-Németh, *Strategic Change*](https://doi.org/10.1002/jsc.2663)

Medallia's November 2023 survey of 1,749 U.S. hotel guests found lower recall of listed personalization elements during the stay than at several other stages. This is a guest-experience signal, not evidence that the cause was staff access or system integration. [Report and method](https://www.medallia.com/press-release/medallia-research-finds-61-percent-of-consumers-are-willing-to-spend-more-for-personalized-experiences/)

A 2025 qualitative study interviewed 33 managers and frontline employees at hotels in Accra and described customer knowledge as distributed across PMS/CRM systems, shared tools, and employee memory. This supports investigating both technology and team practices; it cannot estimate how common these issues are in Singapore. [Wavei, Lo, and Gedecho, *International Journal of Hospitality & Tourism Administration*](https://doi.org/10.1080/15256480.2025.2549991)

Together, these sources make a data-to-service problem credible enough to investigate. They do not establish that PARKROYAL lounge staff lack profile access, that such a gap affects guests, or that face recognition or smart glasses would solve it.

### Scope and local evidence

Broaden the literature review to hospitality, hotels, restaurants, and food service where the evidence concerns guest relevance, recognition, dietary inclusion, or service interaction. Frame the design problem at the hotel-service level, while keeping discovery, design, and evaluation bounded to PARKROYAL's club lounge. The team has permission from PARKROYAL to use the lounge as the POC test setting. The project visit notes record stakeholder interest in VIP recognition and possible name, allergy, and preference cues; they do not document the current in-lounge workflow or profile system. Confirm the conditions for staff observation/testing, device use, customer presence, and any live guest records, images, or biometric processing. [PARKROYAL visit notes](../../hotel-visit/parkroyal-main-points.md)

A defensible problem framing is:

> Some hotels collect guest preferences and service history to support personalized experiences, but having the information does not guarantee that frontline staff can use relevant, current, authorized context to adapt service at the right moment. Research makes this a credible hotel-service design question, but does not prove the same gap exists in every hotel or at PARKROYAL. We will investigate it through a bounded test in PARKROYAL's club lounge, where the team has permission to use the lounge as the POC test setting, and prototype whether a staff-facing cue can make one guest preference actionable during food-and-drink service.

The main discovery task is to find what actually happens at PARKROYAL: which employee serves the guest, what information is available, how a guest is linked to the profile, what action the cue would change, and what the guest can choose or decline. Do not use ACDC as if it were PARKROYAL's system.

## 2. Why useful personalization can matter—and limits on loyalty or profit claims

### Guest value is about relevance and response, not just displaying a name

Medallia Market Research surveyed **1,749 U.S. hotel guests** about a recent stay in November 2023 using a CheckMarket/Sense360 panel; results were weighted by age and gender. Frequently recalled examples included having stay details ready when an interaction began (**65%**), following up on a service issue (**66%**), and offering a choice in how to resolve an issue (**65%**). These figures indicate what respondents remembered experiencing, not an objective service rate or a ranked measure of importance. The same report found that only **23%** rated their recent stay 9–10 out of 10 for personalization; that is a single self-reported rating and does not reveal why a guest did not notice personalization. The report is vendor-produced and U.S.-only. [Medallia, *Understanding Personalization Efforts in the Hospitality and Retail Industries*](https://www.medallia.com/wp-content/uploads/pdf/resources/Medallia-Understanding-Personalization-Efforts-in-the-Hospitality-and-Retail-Industries-Report.pdf)

Oracle Hospitality and Skift surveyed **5,266 consumers and 633 hotel executives** in nine global markets in 2022. About **74%** of consumers were very or somewhat interested in hotels using AI to analyze travel information for better service during a trip when they had willingly provided the data for that purpose. This supports conditional openness to data-based service, not blanket demand for profiling or facial recognition. It is a vendor-sponsored survey of stated interest in a hypothetical use, not a consent study or observed guest behavior. [Oracle/Skift, *Hospitality in 2025*](https://www.oracle.com/asean/a/ocom/docs/industries/hospitality/hospitality-industry-trends-for-2025.pdf) · [Oracle methodology](https://www.oracle.com/news/announcement/oracle-hospitality-in-2025-consumer-research-study-2022-06-01/)

For a lounge food-and-beverage moment, dietary context is a useful candidate because it can change what staff recommend or prepare. Norris et al. used a sequential mixed-method design: interviews with people with dietary restrictions, a conjoint analysis of menu cues, and an empirical test. The publisher's accessible abstract says availability of menu modifications was the most valued inclusion cue in the conjoint and that inclusive cues influenced emotional, attitudinal, and purchase-intention responses. This is directly relevant to diners with restrictions, not a ranking of all hotel guests' preferences. The accessible abstract does not provide the sample sizes or geography, and the study tests menu design rather than a staff-facing allergy display. [Norris et al., *International Journal of Hospitality Management*](https://doi.org/10.1016/j.ijhm.2025.104425)

Lei et al. examined the difference between a hotel's **actual attempt** to personalize service and the guest's **perception** that the service was personalized. The three sequential studies included qualitative interviews with hotel senior managers, a between-subject online experiment with **919 participants**, and a survey of **214 respondents** evaluating hotel personalization practices. Their findings indicate that perceived personalization depends partly on how much effort the guest sees and whether the act feels surprising; a hotel can make a tailoring attempt that the guest does not experience as a fit. The experiment and survey are not observation of a real lounge encounter or evidence of financial return. [Lei et al., *Tourism Management*](https://doi.org/10.1016/j.tourman.2023.104818)

The case for remembering a guest's name is narrower. Name use can signal that an employee sees a person rather than an anonymous order and can support rapport. A study of **25 frequent luxury-hotel guests** found that being acknowledged and remembered was a meaningful experience theme, but a small purposive sample cannot establish how often all hotel guests want this. In Lei et al.'s hotel-practice survey, greeting guests by name was rated as perceived personalization at **4.94/7**, close to anticipating needs from previous records (**4.96/7**) and several other practices. The close ratings do not establish a priority ranking. Other studies on natural name exchange are from cafes and restaurants, not hotels; they suggest name use can be context-sensitive and may feel uncomfortable if repeated or used to sell. For this POC, a name can be a secondary rapport cue, not the main service outcome. [Buehring & O’Mahony, open manuscript](https://ira.lib.polyu.edu.hk/bitstream/10397/92274/1/JHTI_Memorable_Experiences_Buehring_OMahony_Apr_2019.pdf) · [Lei et al.](https://doi.org/10.1016/j.tourman.2023.104818)

### Repeat business and commercial impact need careful wording

Piccoli, Lui, and Grün studied a **122-room independent four-star hotel** with a large business-traveller segment. Their mixed-method study combined staff interviews and observation with **98,330 reservations from 2010–2014**, PMS traces, and **4,706 linked Booking.com reviews**. A guest-facing preference page elicited more preference items than the traditional request process; use of the system was associated with higher service and value rating categories. Among guests who had already returned, first-stay preference-system use was associated with a shift toward the hotel's website as booking channel. This is useful evidence that structured preference capture and fulfilment can support service perceptions. It is a single-property observational study with guest self-selection, and it mainly changes preference capture before arrival. It does not isolate a staff-facing in-service cue, prove that personalization caused a return, or measure net hotel profit. Channel choice among people who returned is not the same outcome as whether a guest returned. [Piccoli et al., *Tourism Management*](https://doi.org/10.1016/j.tourman.2016.08.015) · [Open author manuscript](https://dds.cct.lsu.edu/ddslab/pdf/piccoliLuiGruen.pdf)

Luxury-specific survey evidence also reports associations rather than realized return. Baloglu and Bai's conference paper surveyed **220 U.S. consumers aged 25–54** who had recently stayed at a U.S. luxury hotel; perceived personalization was associated with stated loyalty intentions and willingness-to-pay-more. The study was cross-sectional and did not observe actual bookings, paid price premiums, or profit. Use it, if needed, as evidence of stated intent, not proof of revenue impact. [Baloglu & Bai, EuroCHRIE 2024 proceedings](https://eurochrie.org/2024/wp-content/uploads/2025/02/EuroCHRIE-2024-Conference-Proceedings.pdf)

The broader hotel literature further warns against attributing loyalty to one service feature. Hu et al. analyzed **521,083 TripAdvisor reviews across 7,031 hotels**, tracking reviewers who returned to the same property. Their observational review analysis considers service attributes and re-patronage; it does not isolate personalization, and the reviewer sample is not all hotel guests. Therefore the interim report can say that useful personalization **may** support service continuity or guest-perceived fit. It should not say it will increase loyalty, repeat stays, spending, or GOP. [Hu et al., *Tourism Management*](https://doi.org/10.1016/j.tourman.2019.04.010)

## 3. Define personalization separately from recognition and data access

There is no single universal definition of hotel personalization. For this project, a practical definition synthesized from hotel and service research is:

> **Guest-context personalization occurs when a frontline employee uses relevant, permitted knowledge about an individual guest's needs, preferences, or circumstances to adapt the service or interaction being delivered. The guest's perception that the adaptation fits them is a separate outcome.**

This definition gives the report four things to observe separately:

1. **Recognition:** Did staff identify or remember the guest?
2. **Context access:** Could staff retrieve relevant, current information in time?
3. **Adaptation:** Did the employee change an interaction or service based on that information?
4. **Perceived fit:** Did the guest notice and experience the change as relevant?

A face match or displayed name only demonstrates a recognition step. A profile card can improve context access without causing any change in service. A personalized action can still be inaccurate, unwanted, or not perceived as personal. Hotel scale-development and experimental work includes interpersonal dimensions such as responsiveness, intimacy, empathy, and attention to personal interests, but these overlap with good service more generally; the project should state its own operational definition rather than imply a universal taxonomy. [Choo, hotel service-personalization scale](https://journal.kci.go.kr/JTS/archive/articleView?artiId=ART001697043) · [Project definition note](defining-hotel-service-personalization.md)

Personalization also differs from **customization**. In one common marketing distinction, personalization is a provider tailoring a service using what it knows about the guest; customization is the guest actively selecting or requesting an option. A guest choosing oat milk is customization. A server using a current, guest-provided oat-milk preference to ask whether the guest wants it again is personalization. The distinction helps avoid calling every choice or good service moment personalization. [Arora et al., *Marketing Letters*](https://doi.org/10.1007/s11002-008-9056-z)

### Which context should the first prototype show?

The initial cue should be limited to information that is **current, reliable, relevant to the service task, actionable, and authorized for the staff member**. Possible fields differ in usefulness and risk:

| Context | Possible lounge use | Initial POC treatment |
| --- | --- | --- |
| Food allergy | Could prevent an unsuitable suggestion and prompt an appropriate check | Prominent, explicit text such as `⚠️ PEANUT ALLERGY`; use only from an authorized, current profile, and ask staff to verify with the guest and food source. Never rely on color or emoji alone; facial recognition must not infer an allergy. |
| Food or drink preference | Could make a current recommendation or order smoother | One concise, task-relevant item, e.g. `Coffee: oat milk, no sugar`, if the source and recency are clear. Invite confirmation rather than assume the guest still wants it. |
| Guest name | Can support natural greeting and rapport | Optional and secondary. Do not treat correct name display as the personalization outcome. Avoid repeated or scripted name use. |
| Previous conversational context | Could avoid asking a guest to repeat a current request or interest | Do not include in the first version unless it is clearly guest-approved, recent, relevant, and actionable. A raw conversation log is too broad for a compact staff cue. |
| Room type, meeting schedule, broader profile | May matter in other workflows | Exclude from the first lounge F&B cue unless discovery demonstrates a direct need. Avoid showing more personal data simply because it exists. |

For allergy information, use text plus a warning symbol and, if validated on the device, an emoji as a supporting visual. The project's allergy cue note recommends explicit text and says the model identifies a possible person; the profile supplies the allergy. An uncertain identity match must not attach personal fields to a visible guest. [Face enrollment and allergy cue note](face-enrollment-and-allergy-cue.md) · [W3C: do not use color alone](https://www.w3.org/WAI/tips/designing/)

## 4. Design-led PARKROYAL lounge POC and evaluation

### POC hypothesis and boundary

The design question is whether a concise staff cue can help an employee use a relevant guest preference during a lounge food-or-drink interaction, while making an allergy note visible enough to prompt a safe verification step. Facial recognition is one possible way to associate the cue with a returning guest after their lounge-card tap; the evidence reviewed here does not show that it is necessary or better than a manual lookup, staff-selected guest card, or another lower-friction approach.

The known entry concept is: a guest taps a lounge card at a reader outside the lounge; the tap opens the door, resolves an identity, and adds the guest to the lounge's active set. The in-lounge service steps remain a discovery question: who serves the guest, when they need to know the guest's identity, how a preference is currently retrieved, and what should happen if the guest cannot be matched. Model the after-entry flow with lounge staff before treating the entry signal as an accurate record of who is present or what staff should see. The proposed architecture remains a proposal until the team adopts it. [PARKROYAL visit notes](../../hotel-visit/parkroyal-main-points.md) · [POC architecture proposal](../architecture/hotel-lounge-smart-glasses-poc.md)

Use synthetic or explicitly consenting participants and demo profiles for early prototype work unless the hotel confirms that the POC approval covers the specific information and device workflow. Begin with one service moment, such as a guest asking for coffee or a snack, and one or two fields. A cue should not expose a guest's allergies or profile on an uncertain match; if no reliable match exists, show no personal data. The research and current project notes do not validate facial recognition on the intended staff device, the live card-reader integration, or a full lounge service workflow.

### Privacy, data quality, and device feasibility gates

These are design and project-scope gates, not legal advice. The Singapore PDPC's biometric guide says that biometric samples or templates linked to an identified person are personal data. The Personal Data Protection Act (PDPA) sets consent and purpose-notification/limitation requirements and also includes obligations concerning accuracy, protection, retention, access, and correction. The PDPC biometric guide focuses on security applications; security-camera or building-access examples should not be treated as blanket authorization for using facial recognition to personalize a service interaction. A room/lounge-card tap verifies an entry credential for its existing purpose; it does not by itself demonstrate that the guest was told about or agreed to face identification and staff display of allergy/preferences. Before any live-data trial, confirm purpose, notice/consent or other applicable legal basis, bystander handling, role-based access, retention/deletion, and correction/withdrawal process with the hotel's data-protection officer. [PDPC, *Guide on Responsible Use of Biometric Data in Security Applications*](https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/other-guides/guide-to-biometric_17may2022.pdf) · [Singapore PDPA, §§13, 18, 20–25](https://sso.agc.gov.sg/Act/PDPA2012) · [PDPC Advisory Guidelines on Key Concepts](https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/advisory-guidelines/ag-on-key-concepts/advisory-guidelines-on-key-concepts-in-the-pdpa-17-may-2022.pdf)

Allergy data needs its own accuracy path: the cue should display the source and freshness where practical, come only from an authorized profile, and prompt staff to confirm the guest's current need and the food item's ingredients. A face match must never infer an allergy. If the identity is uncertain, suppress all guest-specific fields. In formative tests, include stale/unknown values and a no-match case so staff can show what they would do safely.

The smart-glasses hardware path is also only partly proven for the intended property and device. The current architecture document is a proposal for a Rokid RV101 phone bridge. Rokid's CXR-L material describes phone-app access to image, audio, display, and command channels, but the current project evidence does not prove the specific RV101/phone/app integration needed by the hotel POC. Do not assume features demonstrated in a CXR-M, Glass3, or separate livestream workflow transfer to RV101 through CXR-L. A hardware spike must confirm camera frame delivery, display updates, indicator/notice behavior, and any SDK/cloud telemetry before building the service workflow around it. [Rokid Open Platform](https://open.rokid.com/) · [POC architecture proposal](../architecture/hotel-lounge-smart-glasses-poc.md)

The repository now also contains a **separate Rokid face-identification demo**: a Kotlin Android app captures images about every two seconds and sends them over Wi-Fi to a laptop FastAPI server running YuNet/SFace recognition. The [demo README](../../rokid/README.md) reports 30 capture requests on 2026-10-22: average request-to-response time was 944 ms, median 943 ms, and p95 1,114 ms; 11 of the samples contained a detected face. These timings end when the response is parsed on the glasses, excluding the wait until the next capture and physical display presentation. They do not measure recognition accuracy. The README labels the demo “Rokid Glass3”; confirm the exact SKU used and do not treat this measurement as validation of the team's RV101. This demo is not integrated with `lounge-control`, `face-worker`, or `mock-hotel`; it matches a local gallery and shows names/status, without lounge entry/exit, an active guest cohort, or allergy/preference cues. It demonstrates a separate technical path, not the proposed hotel-service workflow.

Meta's Wearables Device Access Toolkit provides an alternative documented phone-to-glasses path with camera capabilities, including streaming, but that does not validate the Rokid RV101 path or prove availability for a particular model, display, phone, or Singapore deployment. If comparing devices, check the exact supported SKU and market and test the same privacy, latency, and display requirements. [Meta Wearables Device Access Toolkit](https://developers.meta.com/wearables/device-access-toolkit/) · [Meta device and market FAQ](https://developers.meta.com/wearables/faq/)

Finally, a heads-up display can itself create a distraction. Lewis and Neider ran **five laboratory experiments**, with reported samples of **90, 72, 72, 72, and 57 participants**; participants performed a computer visual-search task while a single word appeared on Google Glass. Secondary HUD information slowed the primary visual task, including when participants were told to ignore it. These experiments do not predict the size of an effect during hospitality service, but they make it important to test whether cue timing and frequency interrupt staff attention or guest conversation. The interface should be sparse and event-triggered, not a persistent stream of guest data. [Lewis & Neider, *Cognitive Research: Principles and Implications*](https://doi.org/10.1186/s41235-016-0015-6)

### A compact cue framework

Use an **identity gate → immediate service need → one helpful preference → confirm/act** sequence:

| Cue layer | Display principle | Example |
| --- | --- | --- |
| Identity gate | Show personal details only after an authorized, sufficiently reliable match; name can be omitted if not useful | `ALEX` (optional) |
| Safety-critical context | Make a current allergy impossible to miss; use words and an icon, not color or emoji alone | `⚠️ PEANUT ALLERGY — confirm with guest and check item` |
| Current-task preference | Show at most one relevant preference, with clear wording and its source/recency available if staff need to check it | `Coffee: oat milk, no sugar` |
| Action / confirmation | Leave the employee in control; the cue informs a conversation rather than silently placing an order | `Ask: “Would you like your usual coffee?”` |

The interface should have a safe no-match state, a way to clear or dismiss stale information, and a simple route back to the hotel's normal service process. Do not show prior conversation, schedules, or unrelated profile fields by default. The display is a prompt for a human interaction, not an automated decision about what a guest can consume.

### What to test in the interim phase

Compare the current/manual information-retrieval workflow with one or more cue prototypes in matched, simulated lounge scenarios. The exact test can be small and formative; report the participants, scenarios, task order, and limitations. A useful scenario set would include a regular drink preference, an allergy alert that requires verification, and a no-match or stale-information case. If possible, ask staff to walk through a recent real example before designing the scenarios.

Measure the stages separately:

| Question | Example outcome |
| --- | --- |
| Did the system associate the cue with the right guest? | Correct matches, unknown/no-match behavior, and false personal-data associations. Report match results separately from service success. |
| Could staff understand the cue? | Correct interpretation of allergy wording and preference; time to read; errors or requests for clarification. |
| Did the cue change the service action? | Whether staff offered or prepared a relevant option, confirmed a preference, or used the correct allergy-check step. |
| Did it help the interaction? | Repeated questions, time to retrieve context, interruptions, perceived distraction, and staff-reported usefulness. |
| Did the guest experience a fit? | In a consented simulation or later field test, ask whether the action felt relevant, respectful, and comfortable; do not infer this from the staff action alone. |

For the interim report, a credible early result is an end-to-end prototype that turns a lounge-entry event into a cue and a formative test showing whether participants can understand and use that cue in a simulated food-and-beverage interaction. That result supports technical and interaction feasibility only. It cannot establish improved guest satisfaction, safer allergy outcomes, more repeat stays, or hotel profit. Those require additional property access, appropriate participant/data approvals, baselines, and a stronger comparison design.

## Evidence map and key limitations

| Evidence source | Method and sample | Useful for | Important limitation |
| --- | --- | --- | --- |
| Gremler & Gwinner (2000) [publisher](https://doi.org/10.1177/109467050031006) | Customer and employee interviews; rapport tested in banking and dental services | Professional rapport and its relationship with satisfaction, loyalty intention, and word of mouth | Not a hotel study; effects vary by service context |
| Buehring & O’Mahony (2019) [publisher](https://doi.org/10.1108/JHTI-11-2018-0077) | Luxury-hotel experience research including interviews with 25 frequent guests | Guest accounts of acknowledgement and recognition | Small, purposive sample; mostly recalled luxury-stay experiences |
| Raja et al. (2026) [research record](https://research.monash.edu/en/publications/call-me-by-my-name-the-effects-of-addressing-customers-by-their-n/) | Restaurant field experiment and three online experiments | Name use, rapport, and discomfort boundaries | Not a hotel lounge; name use can backfire if overused or awkward |
| Novotel visit notes [local record](../../hotel-visit/novotel-formatted.md) | One local hotel visit and interview notes | ACDC, role-based access, pre-arrival review, and F&B memory/VIP-board practices | Applies to Novotel only; self-reported, not measured usage |
| PARKROYAL visit notes [local record](../../hotel-visit/parkroyal-main-points.md) | One local hotel visit and stakeholder discussion | Lounge setting, stakeholder interest, possible guest-context fields, privacy concerns | Does not document the profile system or full F&B workflow |
| Piccoli et al. (2017) [DOI](https://doi.org/10.1016/j.tourman.2016.08.015) | Mixed-method study at one four-star hotel; 98,330 reservations, PMS traces, 4,706 reviews | Preference capture, request routing, service and value ratings | Single hotel; observational; not a live staff cue |
| Bonaretti et al. (2020) [publisher](https://doi.org/10.1016/j.im.2020.103346) | Longitudinal field study of 118,647 reservations across seven Swiss hotels | Digital preference records supporting elicitation and service use | Swiss hotel sample; not an in-lounge recognition system |
| Wavei et al. (2025) [publisher](https://doi.org/10.1080/15256480.2025.2549991) | 33 manager and frontline interviews in Accra hotels | Guest knowledge across formal systems, shared tools, and staff memory | Small, purposive, geographically specific qualitative study |
| Hapi/Revinate (2025) [survey release](https://www.revinate.com/press-releases/the-future-of-hotel-data-report-reveals-nearly-50-of-hoteliers-struggle-to-access-critical-data/) | Vendor survey of nearly 200 hospitality professionals worldwide | Broad hotel data-access and integration barriers | Limited public sampling details; not frontline guest-profile lookup |
| Hiezl & Gyurácz-Németh (2025) [publisher](https://doi.org/10.1002/jsc.2663) | Technology measure and provider survey; 105 hotels from a population of 458 | Variation in hotel personalization-supporting technology | Provider-reported capability; not a point-of-service access audit |
| Medallia (2024) [report](https://www.medallia.com/wp-content/uploads/pdf/resources/Medallia-Understanding-Personalization-Efforts-in-the-Hospitality-and-Retail-Industries-Report.pdf) | U.S. panel; 1,749 recent hotel guests; recall and stated-preference questions | Guest-recalled continuity, issue follow-up, and stage differences | Vendor-produced, self-reported, U.S.-only; does not identify cause |
| Oracle/Skift (2022) [methodology](https://www.oracle.com/news/announcement/oracle-hospitality-in-2025-consumer-research-study-2022-06-01/) | Survey of 5,266 consumers and 633 hotel executives in nine markets | Conditional stated openness to data-based service when data was willingly provided | Vendor-sponsored, hypothetical; not biometric consent or observed behavior |
| Lei et al. (2024) [publisher](https://doi.org/10.1016/j.tourman.2023.104818) | Manager interviews, online experiment with 919 participants, survey of 214 respondents | Actual versus perceived personalization and why fit should be measured | Not a live lounge field trial; does not establish financial impact |
| Norris et al. (2026) [publisher](https://doi.org/10.1016/j.ijhm.2025.104425) | Interviews, conjoint analysis, and empirical test with diners with dietary restrictions | Menu modification as an inclusion cue in food service | Specific dietary-restriction segment; not a staff-facing hotel cue |
| Lewis & Neider (2016) [publisher](https://doi.org/10.1186/s41235-016-0015-6) | Five laboratory visual-search experiments with Google Glass | Possible attention cost from heads-up display cues | Lab tasks, not hotel service; use as a design risk to test |
| PDPC and Singapore PDPA [PDPC guide](https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/other-guides/guide-to-biometric_17may2022.pdf) · [PDPA](https://sso.agc.gov.sg/Act/PDPA2012) | Official regulator guidance and statute | Governance for linked biometric and guest data | Biometric guide focuses on security applications; confirm the service-purpose review |
| Rokid / Meta device documentation [Rokid](https://open.rokid.com/) · [Meta](https://developers.meta.com/wearables/device-access-toolkit/) | Vendor SDK/product documentation, not an evaluated hotel deployment | What must be validated for camera/display paths | Capabilities vary by device, SDK, phone, app, country, and release |

## Existing project research to consult

These notes contain the fuller source audits and should be used when writing the literature review or reference list:

- [Defining hotel service personalization](defining-hotel-service-personalization.md)
- [Hotel personalization project review](hotel-personalization-project-review.md)
- [Guest-data access evidence](hotel-personalization-guest-data-access-evidence.md)
- [What hotel guests value](what-hotel-guests-value-in-personalization.md)
- [Guest-name recognition, experience, and profit](hotel-guest-name-recognition-experience-and-profit.md)
- [Additional evidence on personalization, repeat choice, and business travel](hotel-personalization-additional-evidence.md)
- [Face enrollment and allergy cue](face-enrollment-and-allergy-cue.md)
- [Face-recognition model landscape](cv-face-models-sota.md)
- [Smart-glasses camera and model feasibility](smart-glasses-scrfd-feasibility.md)

## Core references

- Gremler, D. D., & Gwinner, K. P. (2000). “Customer-Employee Rapport in Service Relationships.” *Journal of Service Research*, 3(1), 82–104. [DOI](https://doi.org/10.1177/109467050031006).
- Price, L. L., & Arnould, E. J. (1999). “Commercial Friendships: Service Provider–Client Relationships in Context.” *Journal of Marketing*, 63(4), 38–56. [DOI](https://doi.org/10.1177/002224299906300405).
- Buehring, J. H., & O’Mahony, B. (2019). “Designing memorable guest experiences: Development of constructs and value generating factors in luxury hotels.” *Journal of Hospitality and Tourism Insights*, 2(4), 358–376. [DOI](https://doi.org/10.1108/JHTI-11-2018-0077).
- Raja, S. V. S., Cheng, Y., & Danaher, T. S. (2026). “Call me by my name: The effects of addressing customers by their names, the underlying mechanisms, and the boundary conditions.” *Journal of Retailing*. [DOI](https://doi.org/10.1016/j.jretai.2026.03.008).
- Lei, S. S. I., Wang, D., Fong, L. H. N., & Ye, S. (2024). “Recipe for perceived personalization in hotels.” *Tourism Management*, 100, 104818. [DOI](https://doi.org/10.1016/j.tourman.2023.104818).
- Piccoli, G., Lui, T.-W., & Grün, B. (2017). “The impact of IT-enabled customer service systems on service personalization, customer service perceptions, and hotel performance.” *Tourism Management*, 59, 349–362. [DOI](https://doi.org/10.1016/j.tourman.2016.08.015).
- Bonaretti, D., Bartosiak, M., Lui, T.-W., Piccoli, G., & Marchesani, D. (2020). “What can I(S) do for you? How technology enables service providers to elicit customers’ preferences and deliver personalized service.” *Information & Management*, 57(6), 103346. [DOI](https://doi.org/10.1016/j.im.2020.103346).
- Wavei, E. B., Lo, A., & Gedecho, E. K. (2025). “Understanding Frontline Employees’ Knowledge Management in Key Aspects of Customer Relationship Management: Insights from Contemporary Hotels.” *International Journal of Hospitality & Tourism Administration*. [DOI](https://doi.org/10.1080/15256480.2025.2549991).
- Hiezl, K., & Gyurácz-Németh, P. (2025). “Is High-Touch Enough? Personalization-Supporting Technology in Hotel Service: A Data-Driven Approach.” *Strategic Change*, 34(4), 609–630. [DOI](https://doi.org/10.1002/jsc.2663).
- Medallia Market Research (2024). *Understanding Personalization Efforts in the Hospitality and Retail Industries*. [Report](https://www.medallia.com/wp-content/uploads/pdf/resources/Medallia-Understanding-Personalization-Efforts-in-the-Hospitality-and-Retail-Industries-Report.pdf).
- Hapi and Revinate (2025). *The Future of Hotel Data*. [Survey findings and method](https://www.revinate.com/press-releases/the-future-of-hotel-data-report-reveals-nearly-50-of-hoteliers-struggle-to-access-critical-data/).
- Norris, C. L., Slevitch, L., Bauman, M. J., Park, S., Lee, J., & Gamor, E. (2026). “A seat at the table: Designing menus that signal inclusion.” *International Journal of Hospitality Management*, 133, 104425. [DOI](https://doi.org/10.1016/j.ijhm.2025.104425).
- Lewis, J. E., & Neider, M. B. (2016). “Through the Google Glass: The impact of heads-up displays on visual attention.” *Cognitive Research: Principles and Implications*, 1, 13. [DOI](https://doi.org/10.1186/s41235-016-0015-6).
- Personal Data Protection Commission Singapore. *Guide on Responsible Use of Biometric Data in Security Applications* (2022). [Guide](https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/other-guides/guide-to-biometric_17may2022.pdf).
- Singapore. *Personal Data Protection Act 2012*, especially sections 13, 18, and 20–25. [Singapore Statutes Online](https://sso.agc.gov.sg/Act/PDPA2012).
- Arora, N., Drèze, X., Ghose, A., Hess, J. D., Iyengar, R., Jing, B., et al. (2008). “Putting One-to-one Marketing to Work: Personalization, Customization, and Choice.” *Marketing Letters*, 19, 305–321. [DOI](https://doi.org/10.1007/s11002-008-9056-z).
- Choo, S.-W. (2012). “A Study on the Development of a Service Personalization Scale for Hotel Enterprises.” *Journal of Tourism Sciences*, 36(8), 11–24. [Journal record](https://journal.kci.go.kr/JTS/archive/articleView?artiId=ART001697043).
