import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = "/Users/wongwh/Desktop/NUS/Y4S1/CDE4301/CDE4301-Hotel-Hospitality";
const sourcePath = path.join(workspaceDir, "deliverables/hotel-slides-7-13.pptx");
const finalPath = path.join(workspaceDir, "deliverables/hotel-slides-7-11-canva.pptx");
const buildDir = path.join(workspaceDir, ".build/hotel-slides-7-11");
const skillDir = "/Users/wongwh/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11618/skills/presentations";

const presentation = await PresentationFile.importPptx(await FileBlob.load(sourcePath));
while (presentation.slides.items.length > 5) {
  presentation.slides.items.at(-1).delete();
}

const replaceNamedText = (slide, name, value) => {
  const shape = slide.shapes.items.find((item) => item.name === name);
  if (!shape) throw new Error(`Missing expected shape ${name}`);
  shape.text.set(value);
};

replaceNamedText(presentation.slides.items[0], "slide-7-title", "MORPH CHART");
replaceNamedText(presentation.slides.items[0], "slide-7-subtitle", "Possible ways to capture, link, share and retrieve a guest insight.");
replaceNamedText(presentation.slides.items[0], "slide-7-bundle-text", "BUNDLE TO EVALUATE: staff checks the note, links it to the guest/stay, then shares a short cue.");
replaceNamedText(presentation.slides.items[1], "slide-8-title", "COMPETITOR ANALYSIS");
replaceNamedText(presentation.slides.items[1], "slide-8-subtitle", "Existing products cover different parts of the guest information workflow.");
replaceNamedText(presentation.slides.items[2], "slide-9-title", "WHAT TO PERSONALISE");
replaceNamedText(presentation.slides.items[2], "slide-9-primary-copy", "A guest says “I prefer oat milk.” Later, F&B staff offers a suitable drink and checks that the preference still applies.");
replaceNamedText(presentation.slides.items[3], "slide-10-title", "USER JOURNEY");

const addShape = (slide, name, geometry, x, y, width, height, fill, lineColor = "none", lineWidth = 0) =>
  slide.shapes.add({
    geometry,
    name,
    position: { left: x, top: y, width, height },
    fill,
    line: { style: "solid", fill: lineColor, width: lineWidth },
  });

const addText = (slide, name, value, x, y, width, height, style = {}) => {
  const shape = addShape(slide, name, "textbox", x, y, width, height, "none");
  shape.text.set(value);
  shape.text.style = {
    typeface: "Helvetica Neue",
    fontSize: 20,
    color: "#26344A",
    alignment: "left",
    verticalAlignment: "middle",
    wrap: true,
    ...style,
  };
  return shape;
};

const addCard = (slide, name, x, y, width, height, title, body, palette = "blue") => {
  const colors = palette === "gold"
    ? { fill: "#FFFFFF", border: "#B9892A", title: "#81580D" }
    : palette === "teal"
      ? { fill: "#F5FBFA", border: "#65A7A3", title: "#24635F" }
      : { fill: "#F3F6FC", border: "#88A6D7", title: "#193F84" };
  addShape(slide, `${name}-box`, "roundRect", x, y, width, height, colors.fill, colors.border, 2);
  addText(slide, `${name}-title`, title, x + 14, y + 10, width - 28, 34, {
    fontSize: 21,
    color: colors.title,
    bold: true,
    alignment: "center",
  });
  addText(slide, `${name}-body`, body, x + 16, y + 48, width - 32, height - 56, {
    fontSize: 17,
    color: "#34465E",
    alignment: "center",
  });
};

const addArrow = (slide, name, x, y, width = 46) =>
  addShape(slide, name, "rightArrow", x, y, width, 26, "#2453A6", "#2453A6", 0);

const architecture = presentation.slides.items[4];
architecture.shapes.deleteAll();
architecture.background.fill = "#F7F7F7";

addText(architecture, "slide-11-title", "SYSTEM ARCHITECTURE", 100, 40, 1720, 96, {
  fontSize: 58,
  color: "#2453A6",
  bold: true,
  alignment: "center",
});
addText(architecture, "slide-11-subtitle", "A proposed guest-approved note can feed the lounge profile retrieval path.", 150, 139, 1620, 58, {
  fontSize: 27,
  color: "#5D6878",
  alignment: "center",
});

// Proposed preference capture extension.
addShape(architecture, "slide-11-write-lane", "roundRect", 90, 218, 1740, 220, "#FFF9ED", "#D2AD66", 2);
addText(architecture, "slide-11-write-label", "PROPOSED NOTE WRITE PATH", 120, 231, 700, 38, {
  fontSize: 25,
  color: "#81580D",
  bold: true,
});
const writeCards = [
  [110, "Guest shares", "One preference for this stay"],
  [530, "Staff phone form", "Enter, edit and review the note"],
  [950, "Confirm guest and stay", "Keep source, time and expiry"],
  [1370, "mock-hotel profile API", "SQLite: synthetic profile + stay note"],
];
for (let i = 0; i < writeCards.length; i++) {
  const [x, title, body] = writeCards[i];
  addCard(architecture, `slide-11-write-${i + 1}`, x, 285, 330, 118, title, body, "gold");
  if (i < writeCards.length - 1) addArrow(architecture, `slide-11-write-arrow-${i + 1}`, x + 350, 331, 54);
}
addText(architecture, "slide-11-write-status", "Staff saves only after checking the wording and its guest/stay link.", 120, 405, 1580, 25, {
  fontSize: 17,
  color: "#765817",
  alignment: "center",
});

// Existing lounge read architecture and its integration boundaries.
addShape(architecture, "slide-11-read-lane", "roundRect", 90, 460, 1740, 425, "#FFFFFF", "#D7DDE7", 2);
addText(architecture, "slide-11-read-label", "LOUNGE READ PATH: proposed architecture with simulated main POC pieces", 120, 475, 1550, 38, {
  fontSize: 24,
  color: "#2453A6",
  bold: true,
});

addText(architecture, "slide-11-tap-lane-label", "ENTRY + PROFILE CONTEXT", 120, 523, 500, 27, {
  fontSize: 17,
  color: "#5D6878",
  bold: true,
});
addCard(architecture, "slide-11-tap-reader", 120, 555, 300, 100, "Card reader", "Entry / exit event", "blue");
addCard(architecture, "slide-11-control", 555, 555, 440, 100, "lounge-control", "Tap API · profile lookup · expiring active cohort", "blue");
addCard(architecture, "slide-11-mock-profile", 1130, 555, 560, 100, "mock-hotel API", "Synthetic profile + proposed stay-scoped note", "blue");
addArrow(architecture, "slide-11-tap-arrow-1", 455, 592, 70);
addText(architecture, "slide-11-tap-arrow-label", "tap", 455, 565, 70, 22, {
  fontSize: 14,
  color: "#5D6878",
  alignment: "center",
});
addArrow(architecture, "slide-11-profile-arrow", 1017, 576, 80);
addText(architecture, "slide-11-profile-arrow-label", "profile read", 1000, 550, 115, 22, {
  fontSize: 14,
  color: "#5D6878",
  alignment: "center",
});

addText(architecture, "slide-11-frame-lane-label", "CAMERA FRAMES + CUE", 120, 671, 500, 27, {
  fontSize: 17,
  color: "#5D6878",
  bold: true,
});
addCard(architecture, "slide-11-rv101", 120, 704, 300, 112, "Rokid RV101", "Camera input + lens display", "blue");
addCard(architecture, "slide-11-android", 555, 704, 340, 112, "Android phone", "Vendor SDK bridge · sampled frames", "blue");
addCard(architecture, "slide-11-local-services", 1025, 704, 380, 112, "Local laptop · Docker", "lounge-control + face-worker match only within active cohort", "blue");
addCard(architecture, "slide-11-cue", 1515, 704, 250, 112, "Glasses cue", "Short note; no cue when match is uncertain", "teal");
addArrow(architecture, "slide-11-frame-arrow-1", 455, 748, 68);
addText(architecture, "slide-11-frame-arrow-label", "frames", 450, 722, 80, 22, {
  fontSize: 14,
  color: "#5D6878",
  alignment: "center",
});
addArrow(architecture, "slide-11-frame-arrow-2", 925, 748, 68);
addText(architecture, "slide-11-frame-arrow-label-2", "frame API", 918, 722, 82, 22, {
  fontSize: 14,
  color: "#5D6878",
  alignment: "center",
});
addArrow(architecture, "slide-11-frame-arrow-3", 1440, 748, 52);
addText(architecture, "slide-11-frame-arrow-label-3", "cue via phone", 1428, 722, 91, 22, {
  fontSize: 14,
  color: "#5D6878",
  alignment: "center",
});

addShape(architecture, "slide-11-status-strip", "roundRect", 90, 900, 1740, 82, "#E5E9EF", "#E5E9EF", 0);
addText(architecture, "slide-11-status-copy", "Main hotel POC simulates taps/cohort, synthetic profiles, matching and cues. Separate Rokid demo uses a local gallery for name/status and is not integrated. RV101 frame delivery and hotel data access remain validation gates.", 118, 911, 1684, 60, {
  fontSize: 18,
  color: "#26344A",
  alignment: "center",
});
addShape(architecture, "slide-11-footer-rule", "rect", 90, 1017, 1740, 2, "#D7DDE7", "#D7DDE7", 0);
addText(architecture, "slide-11-footer", "CDE4301  |  HOTEL PERSONALISATION", 96, 1024, 820, 30, {
  fontSize: 17,
  color: "#5D6878",
});
addText(architecture, "slide-11-page", "11", 1740, 1024, 84, 30, {
  fontSize: 18,
  color: "#2453A6",
  bold: true,
  alignment: "right",
});

presentation.slides.items[0].speakerNotes.text = "Use the chart to show functional alternatives before comparing complete workflows. The selected bundle remains a candidate to evaluate. Face matching is an optional guest-association method, not a way to capture the preference. Staff-triggered capture and explicit guest/stay selection are proposed additions. Internal references: docs/reporting/hotel_presentation_outline.md; docs/agents/hotel-smart-glasses-poc.md; docs/architecture/hotel-lounge-smart-glasses-poc.md.";
presentation.slides.items[1].speakerNotes.text = "Commercial capabilities come from vendor materials and are not independent performance evaluations. Oracle OPERA Cloud profile notes: https://docs.oracle.com/en/industries/hospitality/opera-cloud/26.2/ocsuh/t_create_manage_adding_notes_to_a_profile.htm ; mobile profiles: https://docs.oracle.com/en/industries/hospitality/opera-cloud/26.2/ocsuh/t_managing_profiles_mobile_app_pwa.htm . hotelkit Collaboration: https://hotelkit.net/products/collaboration/ . Alliants Core Platform: https://www.alliants.com/products/core-platform . SoftServe Hands-Free Face ID demo: https://www.softserveinc.com/en-us/resources/hands-free-face-id-demo . Public materials do not provide comparable project pricing. The selected glasses workflow is a candidate for evaluation, not a validated winner.";
presentation.slides.items[2].speakerNotes.text = "The oat-milk example is synthetic and does not describe a verified PARKROYAL workflow or guest preference. Ask the partner which guest-approved detail staff can act on in the lounge and share across roles. Preferences and allergies have different operational meanings. Allergy details require verification against the authoritative hotel source and food-safety process; a face match alone cannot support an allergy decision. W3C use-of-color guidance: https://www.w3.org/WAI/WCAG21/Understanding/use-of-color.html .";
presentation.slides.items[3].speakerNotes.text = "The steps describe a proposed service journey. The main hotel POC and standalone Rokid demo are separate systems. The main POC simulates taps, an active lounge cohort, synthetic records, matching and a cue path. The standalone demo uses a local gallery and displays a name/status; it does not capture a preference or integrate with the hotel profile. New preference capture and cross-staff sharing are proposed, not demonstrated.";
architecture.speakerNotes.text = "This slide adds a proposed guest-approved write path to the separate lounge retrieval architecture. Staff enters and reviews a short note, confirms the guest and current stay, and saves a stay-scoped record with source/time/expiry metadata. The mock-hotel API and SQLite are synthetic POC components. lounge-control handles tap events, active cohort and profile lookup; face-worker matches against the current candidate set; Android is the RV101 vendor bridge. The main hotel POC simulates core flow components. The standalone Rokid demo is separate and does not use this profile path. RV101 continuous/sufficiently frequent frames, hotel data access, role permissions, retention, recognition reliability and cue readability need validation. Internal sources: docs/agents/hotel-smart-glasses-poc.md; docs/architecture/hotel-lounge-smart-glasses-poc.md; docs/research/hotel-presentation-slides-7-13-research-plan.md.";

await fs.mkdir(buildDir, { recursive: true });
const previews = [];
for (const [index, slide] of presentation.slides.items.entries()) {
  const image = await presentation.export({ slide, format: "png", scale: 1 });
  const previewPath = path.join(buildDir, `final-slide-${index + 7}.png`);
  await fs.writeFile(previewPath, new Uint8Array(await image.arrayBuffer()));
  previews.push(previewPath);
}

const { finalizePresentation } = await import(pathToFileURL(
  path.join(skillDir, "container_tools/artifact_tool_utils.mjs"),
).href);
const stagingDir = path.join(workspaceDir, ".codex-finalizer");
await fs.mkdir(stagingDir, { recursive: true });
await fs.mkdir(path.dirname(finalPath), { recursive: true });
const candidatePath = path.join(stagingDir, "hotel-slides-7-11-canva-candidate.pptx");
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);
const result = await finalizePresentation({
  explicitTotalSlideCount: 5,
  requiredNativeTableOwnerSlides: [1, 3],
  workspaceDir,
  candidatePath,
  finalPath,
  pythonExecutable: "/Users/wongwh/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3",
  integrityValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_layout_geometry.py"),
  layoutArgs: [
    "--expected-slide-size-emu", "18288000,10287000",
    "--validate-bullet-geometry",
    "--validate-heading-fit",
    "--require-native-table-slide", "1",
    "--require-native-table-slide", "3",
  ],
  fontPolicy: { basis: "design", families: ["Helvetica Neue"] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(stagingDir, "hotel-slides-7-11-canva-validation.json"),
});
console.log(JSON.stringify({ finalPath, previews, result }, null, 2));
