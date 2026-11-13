# CDE4301 interim assessment report

Open [index.html](index.html) for the report or [transcript.html](transcript.html) for the searchable presentation transcript.

The report was prepared on 10 November 2026 from the 5 November presentation, supplied slides and recording, repository implementation and benchmark records, project research, hotel-visit notes, and the team's clarifications about contributions and the battery test. It contains approximately 5,981 words before the appendices, including references, within the 6,000-word limit for a four-person group.

Chapter 4 introduces the solution's models, database setup, operating assumptions, and intended staff journey, then illustrates each activation, processing, display, and contextual-retrieval iteration before presenting the full architecture. The journey includes updating the shared preference database as a normal solution step; implementation readiness is assessed separately. Chapter 5 covers user validation, the requirements/system check, limitations and guest acceptance, and next steps. Both chapters stand independently of the presentation. Current testing is framed as problem finding and prototyping, with hotel-staff and broader system validation planned for the next stage.

Pipeline SVGs redraw the presentation's capture, server allocation, display, and contextual-retrieval flows. The three before/after comparisons use unchanged generated images from `rokid/output/slide-20-ui/screenshots`, copied into `assets/ui/` for Pages. These illustrate UI choices, not measured device performance. The report's full architecture figure uses a general local-detector label; the original architecture assets remain unchanged.

Section 4.2 groups capture activation, selective offloading, and independent preference extraction as Sections 4.2.1–4.2.3, using measured battery, timing, and extraction results. Section 4.3 groups display positioning, icons, and contextual retrieval as Sections 4.3.1–4.3.3, guided by user feedback. Section 4.4 presents the complete architecture. Qwen is the provisional preference-extraction choice based on guest facts and runtime, rather than staff assessment labels.

The complete icon figure is copied unchanged from `rokid/output/guest-preferences/icon-reference.svg` and its PNG. The team-supplied extraction testing image is transcribed in `evidence/preference-extraction-test-summary.md`; it is a reported-results summary, not raw experiment logs.

## Files

| File | Purpose |
|---|---|
| `index.html` | Ready-to-serve report with navigation, figures, evidence links, and print styling |
| `interim-report.md` | Editable report source |
| `transcript.html` | Searchable transcript with recording playback and timestamp links |
| `Recording.transcript.md` / `.txt` | Readable timestamped transcript downloads |
| `Recording.vtt` | English caption track using the speech model's approximate segment boundaries |
| `Recording.transcript.json` | Transcript source, segment times, source fingerprint, and original ASR wording for edited segments |
| `Slides.pdf` / `Recording.mp4` | Original supplied materials, unchanged |
| `assets/` | Local styling, JavaScript, architecture and pipeline diagrams, generated UI comparisons, and prototype icons |
| `build.py` | Optional rebuild helper; the published site does not run Python |
| `preview.py` | Local preview server with byte-range support for video seeking |

The transcript was generated locally with Whisper large-v3-turbo and checked against a second large-v3 pass and the slide terminology. It is machine-generated and lightly edited, without reliable speaker diarisation. Indistinct setup/demo speech is marked; timestamps are approximate. The file ends during the opening of Q&A. The transcript preserves spoken claims, while the report discusses their evidence separately.

## GitHub Pages

These are static files, with relative resource links and no external JavaScript, fonts, or build service. They work with the repository's documented Pages arrangement: deploy the `main` branch's `/docs` directory. Once these files are committed and that deployment is enabled, the report path is:

`https://wongwh2002.github.io/CDE4301-Hotel-Hospitality/interim/`

Creating these files does not enable Pages, commit changes, or publish the report.

For local video playback and caption testing, run the preview helper from the repository root:

```text
python docs/interim/preview.py
```

Then open `http://127.0.0.1:8000/interim/`. The helper supports video byte-range requests; Python's basic `http.server` may not support seeking to transcript timestamps. The report itself can also be opened directly in a browser. Use **Print / save PDF** for a print layout.

## Editing and rebuilding

Edit `interim-report.md` for report changes. Edit segment `text` values in `Recording.transcript.json` for transcript corrections; retain the original `asr_text` where present. Rebuild the generated HTML, transcript downloads, and captions from the repository root:

```text
python -m pip install -r docs/interim/requirements.txt
python docs/interim/build.py
```

The source marker `<!-- APPENDICES -->` defines the start of the appendices for the approximate word count; references are included in that count. Do not edit only the generated HTML if the change needs to survive a rebuild.

## Presentation references

The supplied example reports informed the document organisation: context and requirements, concept selection, implementation, evaluation, future work, references, and appendices. Their project findings were not used as evidence for this hotel prototype.

- [ASI-401 indoor-search report](https://cde-4301-asi-401.github.io/final-report/)
- [ASI-403 science mission](https://gulatis14.github.io/ASI403/)
- [AUV battery-management report](https://teohxuen.github.io/website/report/final_report/)
- [Team META GolfVision report](https://rexyyong.github.io/CDE4301_Final_Report/)
