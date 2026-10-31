# CDE4301 Personalization Argument and Presentation Q&A

- **Purpose:** Pressure-test the report and presentation rationale before supervisor review.
- **Project case:** PARKROYAL club lounge, with a first use case in food-and-beverage service.
- **Working stance:** Hospitality-wide background; a bounded PARKROYAL lounge investigation. The current lounge workflow and problem still need local validation.

## The short verdict

Use a problem-to-solution chain: **personalized service matters → guests do not always experience it as highly personalized → a possible barrier is guest knowledge not reaching staff → improve continuity at the point of service → test the first use case and whether glasses help.**

> Personalized service can make a hotel interaction feel more relevant to the guest. Yet high personalization is not consistently reported: in one U.S. survey, 23% of hotel guests rated a recent stay 9–10 for personalization. That result does not explain why; a possible barrier is that relevant preferences and needs are not consistently captured, shared, or accessible to frontline staff in the moment. When context does not carry across employees or service moments, staff may rely on memory and guests may have to repeat themselves. This project will test whether that information gap exists in the PARKROYAL lounge and whether making guest-approved context usable during service can help. The first use case and the added value of smart glasses remain open.

## Scope: widen the context, keep the case bounded

It is sensible to discuss personalization across **hospitality, hotels, restaurants, and food service**. Restaurants and lounges offer directly relevant evidence about remembered orders, dietary inclusion, names, and service encounters.

Frame the design problem at the **hotel-service level**, then keep discovery, prototyping, and evaluation bounded to the **PARKROYAL club lounge**. The team has permission to use the lounge as a POC test setting. Treat restaurants as a literature and comparison context, not as a second field site. This lets the report discuss a hotel-level design opportunity without implying that one lounge test represents every hotel.

Do not describe ACDC as PARKROYAL's system. The visit notes place ACDC at **Novotel Singapore on Stevens**, an Accor property. PARKROYAL's notes record interest in lounge recognition and possible name, allergy, and preference cues; they do not document its current profile system or full lounge-service workflow.

## Six-slide problem-to-solution flow

1. **Why personalized service matters.** Show how tailoring service to guest needs can improve perceived relevance and value. Use hotel evidence, while distinguishing perceived personalization from actual service behavior. ([Piccoli et al., 2017](https://doi.org/10.1016/j.tourman.2016.08.015); [Lei et al., 2024](https://doi.org/10.1016/j.tourman.2023.104818).)
2. **Where hotel personalization falls short.** Give the guest-side signal: Medallia found 23% of surveyed U.S. hotel guests rated their recent stay 9–10 for personalization; average recall of listed personalization elements during the stay was 46%. Explain that this is perceived rating and recall, not an objective count of personalized stays or an explanation of the cause. ([Medallia report and methodology](https://www.medallia.com/press-release/medallia-research-finds-61-percent-of-consumers-are-willing-to-spend-more-for-personalized-experiences/).)
3. **A possible barrier: guest knowledge may not reach staff.** Introduce the mechanism to investigate: information may not be recorded, handed over, easy to retrieve, or actionable during face-to-face service. Hotel studies and operator surveys describe data access or integration challenges in some settings, but do not prove this caused the Medallia result or exists at PARKROYAL. ([Sigala, 2005](https://doi.org/10.1016/j.ijhm.2004.08.008); [Hapi/Revinate, 2025](https://www.revinate.com/press-releases/the-future-of-hotel-data-report-reveals-nearly-50-of-hoteliers-struggle-to-access-critical-data/); [Novotel visit notes](../../hotel-visit/novotel-formatted.md).)
4. **The design need: continuity from guest context to service action.** Explain who and when: new guests may share a preference that needs to carry from check-in to breakfast; returning guests may have existing information that staff still need to retrieve and apply. The possible outcome is fewer repeated explanations and more consistent, attentive service. Validate these effects locally.
5. **How might staff use guest-approved context in the moment?** State the design question: “How might we enable hotel staff to capture and access relevant, guest-approved information across interactions, so they can provide personalized service while remaining naturally engaged with the guest?”
6. **The first use case and value of glasses remain open.** Prioritize between remembering requirements, following up on concerns, or supporting personalized conversations. Then compare the chosen interaction with existing tools to see whether glasses improve access without disrupting engagement. The direction has broad alignment; the local problem and feature set are not yet fully validated.

**Short spoken version:** “Personalized service matters because it helps a hotel respond to what is relevant to each guest. But guests do not always experience hotel stays as highly personalized. One possible reason is that the knowledge staff need does not consistently reach them during service. A preference shared at check-in may not carry through to breakfast, and a returning guest's existing record may be difficult to use in the moment. We need to validate this information gap in the PARKROYAL lounge. Our design question is how staff can use guest-approved context while staying engaged with the guest. We still need to choose the first use case and test whether glasses work better than existing tools.”

## Why personalization can matter

### Guest relevance and perceived service value

Personalization is useful when it changes a service action to fit a guest's current need or preference. In a hotel field study, a guest-facing preference system was associated with higher service and value ratings. The study analyzed 98,330 reservations at one 122-room independent four-star hotel; it is useful evidence that structured preferences can support service, but it is observational, single-property research and does not test an in-lounge wearable cue. [Piccoli, Lui, and Grün (2017), article and author manuscript](https://dds.cct.lsu.edu/ddslab/pdf/piccoliLuiGruen.pdf)

A separate hotel study found that actual attempts to tailor service and guests' perceptions of personalization can diverge. Its sequence included manager interviews, an online experiment with 919 participants, and a survey of 214 respondents. This supports measuring whether an interaction feels relevant to the guest rather than counting how many profile fields the prototype displays. [Lei et al. (2024), Tourism Management](https://doi.org/10.1016/j.tourman.2023.104818)

Guest-side survey evidence points to continuity and responsiveness: in Medallia's November 2023 survey of 1,749 U.S. hotel guests, common recalled examples included staff having stay details ready, following up after a service issue, and offering choices. Guests recalled fewer listed personalization elements during the stay itself (46% average recall) than at several other journey stages. This is self-reported vendor research; it does not identify why personalization was less often recalled or show that a staff-facing cue would fix it. [Medallia report and methodology](https://www.medallia.com/press-release/medallia-research-finds-61-percent-of-consumers-are-willing-to-spend-more-for-personalized-experiences/)

### Why names and being remembered can feel meaningful

The “friend who keeps asking your name” analogy is a useful way to introduce the feeling of being recognized. For the academic explanation, use **customer–employee rapport**: Gremler and Gwinner describe rapport as a service relationship construct and report links with satisfaction, loyalty intention, and word of mouth. Rapport concerns an enjoyable interaction and personal connection; it does not require that the hotel employee and guest literally be friends. [Gremler and Gwinner (2000), Journal of Service Research](https://journals.sagepub.com/doi/10.1177/109467050031006)

Hospitality scholars also study **commercial friendship**. It can develop in some repeated host–guest relationships, but it involves more than recognizing a name; research describes dimensions such as shared activities, self-disclosure, and social support. Use this as a possible deeper form of relationship, not the expected baseline for every hotel stay. [Commercial friendships in Dutch pubs (2024)](https://www.sciencedirect.com/science/article/pii/S0278431924002445)

There is direct evidence that name use can support rapport, with limits. A 2026 restaurant field experiment and three online experiments found that employee-initiated name use could improve satisfaction through rapport, while excessive or awkward use could create discomfort. It is restaurant evidence, not proof that all hotel guests want to be addressed by their first name. [Raja, Cheng, and Danaher (2026), Monash research record](https://research.monash.edu/en/publications/call-me-by-my-name-the-effects-of-addressing-customers-by-their-n/)

**Presentation wording:** “Being remembered can signal personal attention and support rapport. But a name is only one possible cue: the useful outcome is service that fits the guest, and familiarity should remain natural and welcome.”

### Which examples belong in the first use case?

| Guest context | Fit with the lounge prototype | Reasoning and guardrail |
| --- | --- | --- |
| Preferred coffee or repeat order | Strong | A current preference could change what staff offer. Present it as a prompt—“Would you like your usual?”—and allow the guest to choose. |
| Food allergy or dietary restriction | Strong, with a separate safety pathway | It can change what staff recommend or prepare. Show clear words, source/freshness where possible, and require the normal guest and ingredient verification. A face match or screen must never be the sole safety check. |
| Name | Optional, secondary | Can support a natural greeting and rapport, but can feel overfamiliar or intrusive. Do not count name display alone as successful personalization. |
| Preferred room type | Relevant to accommodation and booking moments | It is not a good first cue for a lounge food-and-drink task unless staff can identify a concrete action it changes there. |
| Previous conversation or meeting schedule | Defer | Could support continuity when recent and relevant, but raises questions of provenance, staleness, privacy, and relevance. Do not put it in the first prototype without a validated need. |

There is no evidence-backed universal ranking of these examples. Choose the first one by asking: would this information change a specific service action in the selected lounge scenario?

## What hotels currently do, and where the gap may be

Hotels use a mix of guest-facing preference capture and internal guest-service systems. One hotel study describes requests recorded as PMS “traces” and routed to the responsible department; the same hotel later offered an online page with 57 options for guests to specify preferences. Across seven Swiss hotels, a separate longitudinal study analyzed 118,647 reservations and examined an IT-enabled customer-service system for eliciting and using preferences. These are examples of established capture and routing practices, not proof of a single standard used by every hotel. [Piccoli et al. (2017)](https://doi.org/10.1016/j.tourman.2016.08.015) · [Bonaretti et al. (2020)](https://www.sciencedirect.com/science/article/pii/S0378720620302846)

Hotel technology adoption is uneven. A 2025 study developed a measure of personalization-supporting technology and surveyed 105 hotels from a population of 458; it found variation in which practices were established. This is provider-reported capability, not a direct audit of a front-line employee retrieving a profile at a particular service moment. [Hiezl and Gyurácz-Németh (2025)](https://doi.org/10.1002/jsc.2663)

The project visit to Novotel documented the Accor Customer Digital Card (ACDC): guest preferences and observations are recorded, some profiles are reviewed before arrival, and access is described as role-dependent. The same visit notes say F&B staff may rely on memory or a physical VIP board and may not consult ACDC during service. These are interview and visit notes from one property, not measured usage data and not evidence about PARKROYAL. [Novotel visit notes](../../hotel-visit/novotel-formatted.md)

Two external signals make a broader data-to-service gap plausible:

- Hapi and Revinate surveyed nearly 200 hospitality professionals in 2025; their release reports that 49% struggled to access data for broad operational or revenue decisions and 40% cited disconnected systems as their biggest data obstacle. It is a vendor-sponsored, self-reported survey with limited public sampling detail; these percentages are not frontline guest-profile lookup rates. [Survey findings and method](https://www.revinate.com/press-releases/the-future-of-hotel-data-report-reveals-nearly-50-of-hoteliers-struggle-to-access-critical-data/)
- Medallia's guest survey found lower recall of listed personalization elements during the stay than at several other touchpoints. That is a guest-experience signal, not evidence that the cause was staff access or data systems. [Report and methodology](https://www.medallia.com/press-release/medallia-research-finds-61-percent-of-consumers-are-willing-to-spend-more-for-personalized-experiences/)

Therefore, the gap to investigate is not simply “hotels need more data.” It is whether **accurate, authorized, relevant guest context reaches the employee who can act on it, at the service moment when it matters, and leads to an interaction the guest experiences as a fit**.

## Recommended problem framing

> Some hotels collect guest preferences and service history to support personalized experiences, but having the information does not guarantee that frontline staff can use relevant, current, authorized context to adapt service at the right moment. Research makes this a credible hotel-service design question, but does not prove the same gap exists in every hotel or at PARKROYAL. We will investigate it through a bounded test in PARKROYAL's club lounge, where the team has permission to use the lounge as the POC test setting, and prototype whether a staff-facing cue can make one guest preference actionable during food-and-drink service.

**How might we:**

> How might we help hotel frontline staff use relevant, authorized guest context to adapt a service interaction in a way that feels fitting to the guest?

The empirical work will explore this hotel-level design question through the permitted PARKROYAL club-lounge test setting.

**Research question:**

> How can a staff-facing prototype make a current guest preference actionable during a PARKROYAL lounge service interaction, and how well can participants understand and use the cue in a simulated scenario?

These questions leave open whether face recognition, a manual active-guest list, or another method is most appropriate.

## Questions the presentation is likely to attract

### “Why does personalization matter?”

It can make an interaction more relevant and support perceived service value or rapport. Hotel research links preference-system use with better service/value ratings in one property and shows that guest-perceived fit can differ from a provider's attempt. The case is contextual: do not claim every guest wants the same degree of familiarity or that a prototype guarantees satisfaction.

### “Why use a friend analogy?”

It makes the idea of recognition intuitive, but it is not evidence. The theory to cite is customer–employee rapport. Friendship is a stronger and more reciprocal relationship; commercial-friendship research shows it can emerge in some hospitality relationships, not that it is the standard a hotel should promise.

### “What are hotels already doing?”

Some hotels capture preferences through booking or guest-facing forms and store or route them through PMS/CRM/guest-service systems. The Novotel visit offers a local example with ACDC, role-based access, pre-arrival review, and an F&B VIP board/memory practice. We do not yet know PARKROYAL's system or the lounge's current lookup process.

### “If hotels already collect preferences, what is the problem?”

Collection is only one step. Information can be stale, unavailable to a role, split across systems, or presented at the wrong time. Staff still need to make a suitable service choice, and the guest needs to experience it as relevant. External surveys make this a credible industry question; local workflow research must confirm the PARKROYAL case.

### “Why study restaurants and lounges if the partner is a hotel?”

The lounge is hotel hospitality and food service. Restaurant studies directly inform order memory, name use, and dietary inclusion. Use them to explain the interaction; keep observation, prototype, and evaluation at PARKROYAL's lounge so the project does not become a study of the entire restaurant industry.

### “Why face recognition if the guest already tapped a room card?”

The card tap may identify who entered, but it does not automatically tell a staff member which visible person in the lounge is that guest. Face matching is useful only if that identity-to-person gap exists in the actual service workflow and alternatives are less suitable. Validate that need and compare face matching with staff selection or another lower-risk interaction. If staff already know the guest or can use the tap event directly, face recognition may add little value.

### “Why show allergies on the same cue as a favorite drink?”

They are different information types. A drink preference can prompt an offer; an allergy is a safety-relevant flag requiring a current source and verification with the guest and food item. The prototype may show both to test hierarchy, but the allergy path needs stronger accuracy, authorization, and staff-process safeguards.

### “How will you know personalization worked?”

Separate the stages: correct guest association; correct and current context; participant comprehension; appropriate service action; and guest-perceived fit/comfort. A simulated staff test can assess the first four only. Do not claim actual guest satisfaction without an approved guest study.

### “Does the proof of concept prove the hotel needs facial recognition or smart glasses?”

No. It can test whether an end-to-end cue flow is technically feasible and understandable. Whether it is needed, welcome, safe, and better than a manual alternative remains an evaluation question.

## Key evidence to cite in the report

| Claim | Useful source | Keep the limitation visible |
| --- | --- | --- |
| Rapport can matter in service relationships | Gremler & Gwinner (2000) | General service research; not a PARKROYAL or biometric study |
| Being remembered can contribute to luxury guest experience | Buehring & O’Mahony (2019), 25 frequent luxury-hotel guest interviews | Small, purposive sample |
| Names can support rapport but may be uncomfortable if overused | Raja et al. (2026), restaurant field and online experiments | Not a hotel lounge; context and formality vary |
| Guests may perceive less personalization during the stay | Medallia (2024), 1,749 U.S. hotel guests | Self-reported vendor survey; does not identify cause |
| Preference systems can support service and value ratings | Piccoli et al. (2017), 98,330 reservations at one hotel | Observational, single property, preference page not a smart-glasses cue |
| Hotels report data-access/integration barriers | Hapi/Revinate (2025), nearly 200 hospitality professionals | Vendor-sponsored, broad data rather than frontline guest-profile access |
| Hotel personalization-supporting technology varies by practice | Hiezl & Gyurácz-Németh (2025), 105 surveyed hotels | Provider-reported capability, not a live workflow audit |
| Guest-specific cues need to feel like a fit | Lei et al. (2024), three sequential studies | Experiments/survey, not a live lounge field test |

## Sources

- [Gremler & Gwinner (2000), “Customer-Employee Rapport in Service Relationships”](https://journals.sagepub.com/doi/10.1177/109467050031006)
- [Price & Arnould (1999), “Commercial Friendships: Service Provider–Client Relationships in Context”](https://journals.sagepub.com/doi/full/10.1177/002224299906300405)
- [“Commercial friendships in pubs: Defining the quality, levels, and process” (2024)](https://www.sciencedirect.com/science/article/pii/S0278431924002445)
- [Buehring & O’Mahony (2019), “Designing memorable guest experiences”](https://doi.org/10.1108/JHTI-11-2018-0077)
- [Raja, Cheng, & Danaher (2026), “Call me by my name”](https://doi.org/10.1016/j.jretai.2026.03.008)
- [Lei et al. (2024), “Recipe for perceived personalization in hotels”](https://doi.org/10.1016/j.tourman.2023.104818)
- [Piccoli, Lui, & Grün (2017), hotel preference system field study](https://doi.org/10.1016/j.tourman.2016.08.015)
- [Bonaretti et al. (2020), preference elicitation across seven Swiss hotels](https://doi.org/10.1016/j.im.2020.103346)
- [Medallia (2024), hotel personalization survey and method](https://www.medallia.com/press-release/medallia-research-finds-61-percent-of-consumers-are-willing-to-spend-more-for-personalized-experiences/)
- [Hapi/Revinate (2025), hotel data survey and method](https://www.revinate.com/press-releases/the-future-of-hotel-data-report-reveals-nearly-50-of-hoteliers-struggle-to-access-critical-data/)
- Project records: [PARKROYAL visit](../../hotel-visit/parkroyal-main-points.md) and [Novotel visit](../../hotel-visit/novotel-formatted.md)
