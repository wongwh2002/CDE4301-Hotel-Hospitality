# Hotel Smart-Glasses POC — Working Context

**Status:** Concept under investigation. A proposed architecture is documented; the team has not adopted it.

## Problem framing

The project explores whether smart glasses can help hotel workers use guest information already collected by the hotel during service. Relevant guest information may include preferences and allergies, stored separately from guest photographs. The intended benefit is to connect useful information with the worker serving the guest at the right moment; access rules and displayed fields are unresolved.

## Initial lounge scenario

- The proof of concept is intended for a hotel lounge.
- A guest taps a room or access card to enter.
- Staff may need to recognize guests while moving through the lounge, where several guests may be present.
- The current concept is to use the card-tap event to define which guests are currently in the lounge, then use computer vision on smart glasses to match a visible guest against that group and show relevant guest information.

## Current direction

- The proof of concept should help a worker use relevant guest context at the point of service. A measurable success target is still to be chosen.
- The on-glasses presentation should be concise and easy to scan.
- The intended normal flow should be seamless: automatically show cues for stable, high-confidence matches without asking staff to confirm each match.
- Emojis and colors are being considered as visual cues; meanings and accessibility still need evaluation on the selected display.
- Face matching is a hypothesis to evaluate; other smart-glasses capabilities or interaction methods may help connect workers with guest context.
- The team has a physical Rokid Glasses RV101 available. Meta remains a comparative option; do not assume Glass3 Enterprise SDK capabilities apply to RV101.
- Current integration hypothesis: RV101 → paired Android phone → local laptop Docker services. The phone is the vendor-SDK endpoint and forwards camera data to the laptop; the laptop runs the first CV implementation and sends cues back through the phone.
- This phone-bridge path is still a proposal. Validate whether the RV101 CXR-L path exposes continuous camera frames, and whether cues can be returned with acceptable latency.

## Preliminary display research

These are design leads, not settled requirements:

- Google Glass Enterprise design guidance recommends glanceable, timely, short information with a clear hierarchy.
- A controlled study found that a single word on Google Glass disrupted concurrent visual-search tasks across five experiments. The tasks were laboratory visual-search tasks, not hotel work; use this as a reason to test interruption and timing, not as proof that every current display is unsuitable.
- Proposed starting pattern: show a cue only when relevant to a service moment or when the worker asks; keep the first view to one identity cue and one task-relevant note; reveal additional details only after a deliberate action. This is a prototype heuristic, not a universal text-count standard.
- If identity is uncertain or there are multiple plausible matches, show no personal profile data and provide a manual fallback. Do not let an unconfirmed face match be the sole basis for acting on allergy information.
- Consider voice, button/ring input, or a staff phone as alternatives or complements to on-lens text. Avoid speaking names or sensitive details where other guests can hear them.
- Evaluate false profile reveals, missed matches, time to retrieve useful context, worker comprehension, and interruption of the service task.

## Hardware research leads (checked 2026-10-06)

- Meta's developer FAQ says the Device Access Toolkit supports its display and displayless product families, with capabilities varying by device. Its current supported-country page does not list Singapore, so full toolkit capabilities and local support should be confirmed before using Meta as the POC platform.
- Rokid's Open Platform documents image, audio, display, and command channels through its CXR-L SDK, plus a CXR-S path for standalone on-device apps. These are different development paths and need validation on the exact glasses SKU.
- The public CXR-L sample code located for RV101 demonstrates a still-photo request (`takePhoto`) and an image callback. It does not establish a continuous camera-frame API. Treat live frame delivery as an unresolved integration gate until confirmed with Rokid's current SDK documentation or a device spike. ([CXR-L sample mirror](https://github.com/e7naq3y/CXR-L-SDK), [photo sample source](https://github.com/e7naq3y/CXR-L-SDK/blob/main/cxrlsample101/app/src/main/java/com/rokid/cxrlsample/activities/photo/PhotoUsageViewModel.kt))
- Rokid's separate Glass3 Enterprise product manual describes offline face watchlists, with a note that offline face recognition is not currently available on the public network. Do not assume that capability exists on consumer Rokid Glasses or is available to this project.
- Compare exact SKUs for camera access, display, where inference can run, temporary gallery/watchlist support, developer access in Singapore, and the data path. Do not select by brand alone.

References:

- [Google Glass Enterprise design guidelines](https://developers.google.com/glass-enterprise/guides/design-guidelines)
- [Lewis and Neider, “Through the Google Glass: The impact of heads-up displays on visual attention”](https://link.springer.com/article/10.1186/s41235-016-0015-6)
- [Meta Wearables Device Access Toolkit](https://developers.meta.com/wearables/device-access-toolkit/)
- [Meta Wearables FAQ](https://developers.meta.com/wearables/faq/)
- [Meta AI glasses supported countries](https://www.meta.com/en-gb/help/ai-glasses/4961066940605960/)
- [Rokid Open Platform](https://open.rokid.com/)
- [Rokid Glass3 Enterprise SDK](https://x-docs.rokid.com/docs/en/terminal-sdk/glasses/)
- [Rokid Glass3 Enterprise product manual](https://x-docs.rokid.com/docs/en/terminal-sdk/resources/%E4%BA%A7%E5%93%81%E6%89%8B%E5%86%8C.html)
- [Singapore PDPC guide on biometric data in security applications](https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/other-guides/guide-to-biometric_17may2022.pdf)

See `docs/architecture/hotel-lounge-smart-glasses-poc.md` for the current local-laptop architecture proposal.

## Open design questions

- Whether testing uses real guests and hotel records or controlled participants and synthetic records.
- Which staff roles may see which guest fields.
- How lounge presence begins and ends, including missed exit events.
- Which lounge service task the prototype will support first.
- Whether on-lens text is required in the target deployment market.
- What measurable outcome will define a successful proof of concept.
