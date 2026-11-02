# Interim presentation modules 11–17: evidence and open questions

Research date: 2026-11-01. Numbering follows the reorganized presentation outline, which describes content modules rather than a mandatory count of projected slides.

## 11 — What to personalize

- The outline attributes coffee, sweetener and breakfast-egg examples to the Novotel interview and allergy/preference access to PARKROYAL. These are reported interview findings; use the original notes to confirm exact wording and do not present them as findings from every hotel.
- Research on hotels describes using individual guest information to tailor service, including both preferences and requirements. Knowing a name or storing information does not itself establish that service was adapted or that the guest appreciated it. [Piccoli et al., author manuscript](https://dds.cct.lsu.edu/ddslab/pdf/piccoliLuiGruen.pdf); [Lei et al., study record](https://research.polyu.edu.hk/en/publications/recipe-for-perceived-personalization-in-hotels/).
- Suggested example: guest tells one employee they prefer black coffee; another employee uses the shared context to offer black coffee and confirms the preference. The example illustrates the proposed mechanism, not a measured outcome. Allergy information requires established verification and food-service procedures.
- The outline cites Wilkins (2010) for importance 7.37/10 and performance 6.76/10 for remembering requirements, based on 664 guests at eight Queensland hotels. Check the original article's question wording, scale and numbers before putting these on a slide; the DOI alone does not verify the values. [Article](https://doi.org/10.1080/19368623.2010.514554).

## 12 — Select a pilot setting

The club lounge, restaurant, reception and concierge are candidate contexts. A lounge may offer repeated contact and handovers, but the outline does not establish comparative encounter counts, access or superiority. Label the selection a hypothesis informed by interviews and feasibility, not an experiment. Validate with hotel staff: expected relevant encounters, who learns and uses preferences, frequency of handovers, disruption, privacy constraints, and access for testing. Document the reasoning behind any matrix scores instead of implying measurements exist.

## 13 — Requirements

The outline derives requirements for capture, sharing, correct association, timely retrieval, low effort, clear presentation and appropriate guest control. Convert each to a measurable test only when the team agrees a target: e.g., observe time from needing context to finding it, count correct and incorrect associations, check if the next staff member can act on the right preference, and ask staff how disruptive the interface felt. These are proposed measures, not completed test results.

The Singapore PDPC's guide for biometric data in **security applications** advises notification, consent unless an exception applies, restricted access and minimizing retention. It is useful design guidance, but is not a complete determination of legal requirements for this hospitality scenario. Check the actual use, consent approach, bystanders, access and retention with the appropriate project advisers. [PDPC biometric guide](https://www.pdpc.gov.sg/-/media/Files/PDPC/PDF-Files/Other-Guides/Guide-to-Biometric_17May2022.ashx?la=en).

## 14–15 — Generate and compare concepts

Separate **information infrastructure** from the **access interface**. Accor's own 2018 report describes ACDC as a group-wide guest-data system intended to support personalization using previous stays and consumption patterns. It is historical evidence about ACDC, not proof of its present capabilities or the partner hotel's current workflow. [Accor 2018 interim report, section 1.3.1.1](https://assets.group.accor.com/yrj0orc8tx24/5rOI9WTkd4fRibpd6MoRX8/8b3d87f6c855f55cf2b0b90c80119d81/AccorHotels_Interim-Financial-report_30062018_def.pdf).

Compare complete alternatives on the same task: shared profile plus manual lookup; phone or tablet; earpiece; smart-glasses cue. Specify how each captures updates and identifies a guest, rather than treating the device alone as a complete system. Any weighted scores are team judgments until tested. The potential benefit of hands-free access must be balanced against display distraction, recognition errors, privacy and device integration.

Google's AI-glasses guidance recommends concise, glanceable and transient interface elements because a transparent display competes with the real world. This is a platform design recommendation, not proof that the proposed prototype improves hotel service. [Android AI-glasses design principles](https://developer.android.com/design/ui/ai-glasses/guides/foundations/design-principles).

## 16–17 — Journey and architecture

The end-to-end journey in the outline—capture and check a preference, update a record, then retrieve it for another employee—is a **proposed** service workflow. Distinguish it from the narrower recognition-and-display POC: `docs/agents/hotel-smart-glasses-poc.md` describes an intended lounge card tap, candidate matching and cue, with continuous camera access and return-to-display on the actual RV101 still integration questions. `docs/architecture/hotel-lounge-smart-glasses-poc.md` is a proposal with some implemented services; verify actual implementation and demo configuration before labelling individual boxes implemented. No source found establishes that conversation capture, automatic preference extraction, or a hotel production integration is operational.

Face recognition requires separate checks for false matches and missed matches. NIST reports that error rates vary between algorithms and can vary by demographic group; capture conditions affect false negatives. Its benchmarks do not give this prototype's error rate. Test the actual configuration and prevent uncertain results from exposing a profile. [NIST demographic effects](https://pages.nist.gov/frvt/html/frvt_demographics.html); [NIST 1:N identification](https://pages.nist.gov/frvt/html/frvt1N.html).

## Questions to resolve with the team

1. Are modules 11–17 the actual slide numbers or material to combine, and how much speaking time is available?
2. What system components actually work today, which are mocked, and will there be a live demo?
3. Is the immediate scope capturing new preferences, retrieving existing data, or both? How is consent obtained?
4. Which hotel partner, staff interview evidence and test access can be named? Are survey data and interview notes available?
5. Has the team made a documented use-case or concept selection? If not, what criteria are reasonable to present as provisional?
