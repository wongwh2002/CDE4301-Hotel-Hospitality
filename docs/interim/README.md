# CDE4301 interim assessment report

Open [index.html](index.html) for the report or [transcript.html](transcript.html) for the searchable presentation transcript.

The report was prepared on 10 November 2026 from the 5 November presentation, supplied slides and recording, repository implementation and benchmark records, project research, hotel-visit notes, and the team's clarifications about contributions and the battery test. It contains approximately 4,167 words in the main body, within the 6,000-word limit for a four-person group. References and appendices follow the main report.

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
| `assets/` | Local styling, JavaScript, architecture figure, and reused prototype icons |
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

The source marker `<!-- APPENDICES -->` defines the end of the main body for the approximate word count. Do not edit only the generated HTML if the change needs to survive a rebuild.

## Presentation references

The supplied example reports informed the document organisation: context and requirements, concept selection, implementation, evaluation, future work, references, and appendices. Their project findings were not used as evidence for this hotel prototype.

- [ASI-401 indoor-search report](https://cde-4301-asi-401.github.io/final-report/)
- [ASI-403 science mission](https://gulatis14.github.io/ASI403/)
- [AUV battery-management report](https://teohxuen.github.io/website/report/final_report/)
- [Team META GolfVision report](https://rexyyong.github.io/CDE4301_Final_Report/)
