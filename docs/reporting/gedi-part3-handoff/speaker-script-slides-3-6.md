# Speaker script: sequence slides 3–6

These are the speaker notes Wong supplied for the four solution slides. Their sequence numbers map to GEDI source slides 22–25 as shown in [README.md](README.md).

## Slide 3 — Important functions

“Slides 1 and 2 showed the problems in the current first-time guest journey and what the system needs to improve. We’ve grouped the solution into two functions: capture and process guest context, then display the information staff need for the current service moment.

Capture and processing would collect guest-stated preferences or requests, associate the interaction with a likely guest when possible, and prepare the information in a consistent format. Display would select the relevant detail and show it as a short cue on the glasses. The aim is to help staff use useful context during service and carry confirmed information forward.”

**Transition:** “We then turned those functions into criteria we can evaluate.”

## Slide 4 — Design criteria for the service

“Slide 2 identified three needs: recognise and find guest context quickly, capture information naturally, and keep it reliable between staff. These four criteria translate those needs into things we can test.

On-time service support and glanceable interaction address the need to find information quickly without disrupting the conversation. Low-effort capture addresses the difficulty of gathering information while serving guests. Preference continuity addresses delayed or inconsistent notes that can be lost before another staff member uses them.

We linked the criteria to LQA service behaviours such as timely service, natural engagement, active listening and personalisation. The less-than-one-second cue target is our proposed engineering target; it isn’t an LQA timing requirement. We can measure whether the cue arrives in time, whether staff can glance at it comfortably, how long capture takes, and whether a confirmed preference reaches the next staff member.”

**Transition:** “With the criteria in place, we compared different ways to support the same functions.”

## Slide 5 — Morphological matrix

“We compared the current profile-and-phone workflow with smart glasses and an audio badge with earpiece. The current workflow relies on staff finding a profile and entering information manually. The audio option supports hands-free capture and audio cues. The glasses concept combines hands-free capture with a visual cue and vision-assisted guest matching.

We selected smart glasses as the concept to prototype because they appear to fit the service moment and our criteria. The criteria will help us check whether that choice works in practice.”

**Transition:** “Here’s how the proposed glasses workflow could look during a guest interaction.”

## Slide 6 — Proposed staff journey

“The staff member sees a guest and taps the glasses to start the interaction. The system checks for a likely guest match and, when it has one, surfaces relevant preferences or allergy information.

The staff member uses that context in the conversation. For an allergy-related request, they verify the information against the appropriate food or kitchen source before explaining the issue and offering a suitable alternative. If there’s no confident guest match, the system should not show a profile cue; staff can continue with the usual greeting and ask the guest directly.

The interaction can then become a draft for staff review and saving, so useful information can be available to the next staff member.”

**Transition to video:** “The flowchart summarises the steps. The video shows how that interaction might feel in practice.”

## Reconciliation note

The supplied GEDI slide 23 and revised speaker script use a proposed less-than-one-second cue target. This is an engineering target, not an LQA requirement; [Shiwa et al. (2009)](https://doi.org/10.1007/s12369-009-0012-8) is an analogy from communication-robot timing, not direct smart-glasses evidence. The earlier script draft used 1.5 seconds. Four successful warm frame commits averaged 1.18 seconds and do not establish end-to-end target attainment, p95, failure rate, or physical lens visibility. Do not present the target as demonstrated.
