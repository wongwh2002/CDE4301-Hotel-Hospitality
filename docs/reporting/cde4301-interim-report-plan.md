# CDE4301 Interim Report — Planning Brief

- **Status:** Working plan for discussion with the project supervisor
- **Project direction:** Design-led investigation with an early prototype and simulated user evaluation
- **Case setting:** PARKROYAL club lounge; wider hospitality and restaurant research informs the context

**Filled-in working draft:** [CDE4301 interim report draft](cde4301-interim-report-working-draft.md). This companion draft uses the research below and marks unverified local workflow, permission, and evaluation details for follow-up.

## TL;DR

Relevant personalization can make hospitality service feel more fitting to an individual guest. Some hotels record preferences and service history, but collection does not guarantee that the right employee can access accurate, authorized context at the service moment or use it in a way the guest welcomes. Research and one local hotel visit make this a credible issue to investigate; they do not establish the same gap at PARKROYAL. The project will map the club-lounge workflow and prototype whether a staff-facing cue can make one relevant preference actionable during food-and-drink service.

The proposed proof of concept starts when a guest taps a lounge card at the entrance. The tap identifies the guest and adds them to a temporary active-lounge set. During a food-or-drink interaction, a staff-facing interface could show a relevant preference and an allergy alert. Face recognition is one candidate way to associate a visible guest with that set; it remains a design hypothesis alongside simpler alternatives. The first evaluation should use synthetic or consenting demo data and a simulated service task.

## What we have agreed so far

- **Problem area:** Turning recorded guest context into relevant, authorized, guest-facing service.
- **Context:** Use hotel and restaurant research where it informs high-contact hospitality and food service; keep the field case and prototype at PARKROYAL's club lounge.
- **Local case:** PARKROYAL visit notes record stakeholder interest in smart glasses for VIP recognition and possible name, allergy, and preference cues. They do not document its current profile system or the lounge's food-and-drink workflow.
- **Problem mechanism to investigate:** Context may be inaccurate, inaccessible to a staff role, poorly timed, or not translated into an appropriate service action. Do not assume which mechanism applies at PARKROYAL before mapping its workflow.
- **Project type:** Mixed research and design, weighted toward design, concept refinement, and testing initial prototypes.
- **Primary interaction to prototype:** Food/drink service, with a current preference as the first personalization example. A welcome/arrival cue is a possible secondary scenario.
- **Initial data boundary:** Synthetic or consenting demo profiles and images. Do not assume access to live hotel records or guests.
- **Length:** The interim brief specifies up to 6,000 words for a four-person group; word allocation can be decided later.

## Provisional problem statement

> Some hospitality providers collect guest preferences and service history to support tailored service, but the presence of data does not guarantee that it reaches frontline staff in an accurate, usable form or results in service guests experience as relevant. Existing research and project visits make this a credible issue to investigate; the current PARKROYAL lounge workflow and its specific barriers are not yet established. This project will map that workflow and prototype a staff-facing way to make one authorized guest cue actionable during food-and-drink service.

This keeps the core problem solution-neutral. Face matching and smart glasses are candidate ways to connect a visible guest with relevant context, not established requirements.

## Provisional HMW and research question

**How might we:**

> How might we help PARKROYAL lounge staff use relevant, authorized guest context during food-and-drink service so the interaction feels more fitting to the guest?

**Research question:**

> How can a staff-facing prototype make a current guest preference actionable during a PARKROYAL lounge interaction, and how well can participants understand and use the cue in a simulated scenario?

Possible sub-questions:

1. At what point in the lounge workflow do staff currently learn about a guest and access relevant context?
2. Which guest details are useful and appropriate for the first service interaction?
3. Can a prototype surface the right cue with sufficient accuracy and at a useful moment?
4. In a simulated service task, how do staff understand and act on the cue, and what interruptions or errors occur?

## Proposed workflow to validate

1. Guest taps their lounge card at the reader outside the lounge.
2. The tap event resolves a hotel guest reference and adds that guest to a temporary active-lounge set.
3. Inside the lounge, a staff device attempts to associate the guest with an entry in that set. Face matching is the current example; manual selection or another interaction may be a better fit.
4. At a food/drink service moment, show a compact, relevant preference cue and, where applicable, a clearly worded allergy alert.
5. Staff use the cue as a prompt to provide or verify service. An uncertain identity match must not be treated as the basis for an allergy decision.
6. The guest is removed from the active set on exit or after a defined expiry/fallback rule.

Steps 3–6 need workflow and safety validation with PARKROYAL. The existing visit summary does not document how lounge staff receive an arrival event, retrieve profile details, verify allergies, or record exits.

## Initial cue framework

| Cue | First-version treatment | Rationale / guardrail |
|---|---|---|
| Food or drink preference | Show one current, task-relevant preference, such as a preferred coffee | Demonstrates adaptation in the selected service scenario; confirm that the source is current and staff are authorized to see it |
| Allergy | High-visibility alert with an emoji **and explicit text**, e.g. `⚠️ PEANUT ALLERGY` | Emoji alone is ambiguous. A match or profile cue must not replace the hotel's allergy verification process |
| Name | Optional, only if accurate and natural in the interaction | May support recognition and rapport, but using a name by itself is not personalization |
| Room, meeting schedule, prior conversation | Exclude from the first prototype unless PARKROYAL confirms a specific need and authorized source | Avoid irrelevant or intrusive detail; prior-conversation information needs provenance, recency, and relevance |

The design question is what to show, to whom, and at which service moment—not how many profile fields can fit on a display.

## Initial prototype and evaluation

**Already implemented:** The main local prototype can simulate lounge tap events, maintain a temporary candidate set, match test images or a laptop-camera feed against synthetic guest records, and display diagnostic match cards. Separately, the repository now contains a standalone Rokid face-identification demo with a Kotlin Android app and a laptop FastAPI server. Its README reports 30 capture requests over Wi-Fi on 2026-10-22: average capture-request-to-response time was 944 ms, with a 1,114 ms p95; 11 samples contained a detected face. This is a latency result, not an accuracy result, and excludes the wait for the next capture and physical display presentation.

**Not yet demonstrated:** The Rokid demo is separate from the main hotel POC. It compares against a local gallery and displays names/status text; it does not use lounge entry/exit events or the active lounge set, connect to `lounge-control`, `face-worker`, or `mock-hotel`, or show allergy/preference cues. The physical card-reader connection, live hotel-profile connection, integrated glasses-to-lounge flow, and employee-facing food/drink interaction are not demonstrated. The exact glasses SKU used in the latency run and its relationship to the team's RV101 need confirmation. Neither demo's match thresholds have been validated for a real lounge environment.

**Next prototype target:** Demonstrate the chain from simulated lounge-card tap, to temporary guest-set membership, to a match or explicit manual selection, to a concise staff cue in a simulated food/drink task. Use a small set of synthetic profiles.

**Two kinds of evidence to keep separate:**

- **Technical feasibility:** Whether the prototype associates an active guest with the correct synthetic profile and displays the intended cue. Record correct matches, missed matches, false reveals, cue delay, and cases where the system abstains.
- **Design usefulness:** Whether participants understand the cue, choose an appropriate service action, complete the service task, and experience interruption or extra mental effort. A simulated comparison with the current/manual information path could help, subject to supervisor approval.

Do not claim improved guest satisfaction, safe food service, or commercial impact unless those outcomes are directly measured. Do not use real guest data or test with hotel guests until the permitted data, participants, and procedures are confirmed.

## Privacy, safety, and device gates

- A lounge-card tap identifies an access event; it does not by itself establish that the guest agreed to camera capture or biometric identification for service personalization. Use synthetic records or clearly informed, consenting participants for initial testing, and keep ordinary lounge access available to nonparticipants.
- Treat face images/templates linked to a profile as personal data. Before any real-guest trial, confirm purpose, notice/consent or a specifically reviewed exception, authorized roles, bystander handling, retention/deletion, and the responsible hotel/university reviewer. [Singapore PDPA](https://sso.agc.gov.sg/Act/PDPA2012) · [PDPC biometric-data guide](https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/other-guides/guide-to-biometric_17may2022.pdf)
- Use an allergy cue only as a prompt for staff to check the current authoritative source and verify with the guest/food process. Pair emoji or color with explicit text and a manual path for uncertain identity.
- The exact glasses path is unresolved. The standalone Rokid demo shows a separate camera-to-laptop recognition loop, but it is not integrated with the hotel POC and does not establish the available RV101's camera/display path. Validate the target SKU, repeated capture, laptop delivery, and cue rendering before promising an integrated glasses demo. [Standalone Rokid demo](../../rokid/README.md) · [Rokid developer documentation](https://developerdoc.rokid.com/sdk?lang=en) · [Rokid Open Platform](https://open.rokid.com/)

## Suggested interim report skeleton

1. **Executive summary** — problem, approach, initial evidence, and next steps.
2. **Hospitality context and rationale** — why guest-relevant personalization can matter in hotels and restaurants, how hotels capture guest context, and the possible data-to-service gap.
3. **Problem framing and evidence gap** — what is supported, what remains a hypothesis, and why the lounge is a useful bounded case.
4. **Users and current workflow** — staff roles, guest journey, existing information flow, and points of friction.
5. **Requirements and alternatives** — information needs, privacy and safety constraints, and alternatives to face matching.
6. **Concept and interaction design** — tap-to-active-set flow, cue selection, timing, display, and fallback behavior.
7. **Prototype** — what is implemented, what is simulated, and what remains a proposal.
8. **Evaluation plan and initial results** — tasks, participants, measures, findings, and observed failures.
9. **Discussion and limitations** — evidence limits, risks, design trade-offs, and what cannot be concluded yet.
10. **Next steps** — workflow confirmation, device feasibility, prototype iteration, and further testing.

This structure follows the interim rubric's emphasis on context and value, methods and alternatives, prototype development, testing, analysis, problems, and the next plan. Treat this as a working skeleton rather than a fixed final table of contents.

## Working milestones

| Milestone | Work and decision | Evidence / output |
|---|---|---|
| 1. Confirm the service problem | Walk through the lounge workflow with the supervisor and, if permitted, lounge staff; identify one recent example where recorded guest context did or did not change a food/drink interaction | Validated problem statement, staff role, target service moment, data source, access path, and service action |
| 2. Set requirements and compare concepts | Specify what context is useful, who can see it, when it appears, and how the system handles uncertainty; compare face matching with a staff-selected or otherwise lower-complexity alternative | Requirements and rationale for the selected concept |
| 3. Design the cue and fallback | Sketch and review cue hierarchy, allergy wording, timing, expiry, and manual fallback | Reviewed interaction flow and cue prototypes |
| 4. Complete technical feasibility checks | Use synthetic profiles to exercise tap, active-set, matching/selection, cue, and expiry; separately verify the exact glasses camera/display path if it is needed | Prototype demonstration plus a record of match, abstention, false-reveal, and delay cases |
| 5. Run an initial simulated service evaluation | Ask suitable participants to complete a short food/drink scenario using the manual information path and the cue prototype, if comparison is feasible | Correct guest association, cue comprehension, appropriate service action, perceived fit in a guest simulation, and workflow fit |
| 6. Iterate and report | Fix the main design issues, summarize what the prototype supports, document limitations, and identify the next validation step | Interim report, demonstration, and a viable continuation plan |

These are sequence gates, not date commitments. The supervisor should confirm whether access to staff or a representative testing environment is realistic before Milestone 5 is treated as an approved study plan.

## Questions to take to the supervisor / PARKROYAL

1. **Problem validation:** Which guest information, if any, is difficult to turn into a relevant lounge service action? What specifically prevents its use?
2. **Workflow:** Who serves lounge guests, how do they learn a guest has arrived, what information can they access, and when does it affect service?
3. **Use case:** Is food/drink service the right first moment? Which preference would change an actual service action?
4. **Allergy practice:** What is the authoritative allergy record and required verification procedure? Could an alert be shown in a student prototype without creating a safety-critical reliance?
5. **Data and access:** Which fields can a lounge employee access, from what source, and under what consent, retention, and role rules?
6. **Identification:** Does the card tap give staff enough information to connect a profile to a visible guest? If not, is face recognition necessary, or is a staff-selected guest, table/seat cue, or other lower-complexity method more appropriate?
7. **Prototype permission:** What did the general manager's POC approval cover—synthetic-data demonstration, staff observation, staff testing, device use in the lounge, or any real guest data?
8. **Device path:** Can the available glasses deliver the camera/display interaction needed for the prototype, or should the first prototype use a phone/tablet display?
9. **Evaluation:** Which participants can be recruited, what scenarios are realistic, and which outcomes matter most to the course and hotel stakeholder?

## Existing material to build on

- [Personalization argument and presentation Q&A](cde4301-personalization-argument-and-qa.md) — revised rationale, theory, scope, and likely challenge questions.
- [Definition of hotel-service personalization](../research/defining-hotel-service-personalization.md) — separates recognizing a guest from adapting service.
- [What hotel guests value in personalization](../research/what-hotel-guests-value-in-personalization.md) and [hotel guest-name research](../research/hotel-guest-name-recognition-experience-and-profit.md) — guest-value and name-use evidence, with limits.
- [Profile access evidence](../research/hotel-personalization-guest-data-access-evidence.md) and [allergy cue research](../research/face-enrollment-and-allergy-cue.md) — data-access and cue-design issues.
- [PARKROYAL visit summary](../../hotel-visit/parkroyal-main-points.md) — local stakeholder and lounge context.
- [POC problem framing](../agents/hotel-smart-glasses-poc.md) and [architecture proposal](../architecture/hotel-lounge-smart-glasses-poc.md) — current project context; architecture remains unadopted.
- [Interim assessment brief and rubric (searchable Markdown)](../rubrics/CDE4301%20assessment%20brief%20and%20rubrics%20-%20AY2026%20-%20interim%20assessment.md) — structured reading copy; see the [original PDF](../rubrics/CDE4301%20assessment%20brief%20and%20rubrics%20-%20AY2026%20-%20interim%20assessment.pdf) for authoritative wording.
