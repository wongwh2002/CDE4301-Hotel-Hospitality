# CDE4301 Hospitality website

Static HTML/CSS/JavaScript website generated from the supplied `interim-report.md`.

## Pages
- `index.html` — Home
- `about.html` — Team and project framing
- `report.html` — Full report with linked table of contents, references and appendices
- `report (1).html` — Redirect preserving the previous report URL and section bookmarks
- `presentation.html` — Supplied presentation PDF
- `prototype.html` — Prototype overview and status

## Preview
Open `index.html` in a browser, or from this folder run `python3 -m http.server 8000` and visit `http://localhost:8000`.

## GitHub Pages deployment
**Easiest:** Put the files in the repository root of a deployment branch, then go to Settings → Pages → Deploy from a branch → choose the deployment branch and `/ (root)`. If the repository already has a Pages site, changing the publishing source may replace it. Alternatively use a separate repository for the website.

## Assets and supporting files
Figures, interface comparisons, portraits, the survey PDF, and presentation PDF are bundled in `assets/`. Prototype images use these local copies. Reference links to research, the assessment rubric, architecture documentation, and extraction evidence use paths to the existing parent `docs` folders; keep the website at `docs/interim/cde4301-website/` when publishing the repository's `/docs` tree. If deploying this folder alone, copy those supporting documents and update their relative paths. Implementation records continue to link to GitHub.

## Content
Edit `interim-report.md` for report content and `report.template.html` for its page frame. Rebuild from the repository root:

```text
python -m pip install Markdown
python docs/interim/cde4301-website/build.py
```

The build produces `report.html`, its linked contents, and the redirect from the previous filename. It preserves older bookmarks such as `#prototype`, `#testing`, and `#contributions`. The homepage and prototype overview are shorter editorial summaries.

The response-time requirement is **1.0 second** from activation to the first correct visible cue. The current prototype does not meet it; stronger server hardware is an optimisation to evaluate. Section 3.5 restores the visual/audio literature comparison and references R68–R72.

Link maintenance on 15 November 2026 repaired report navigation, section bookmarks, supporting-document paths, and the legacy magazine-viewer URL. Local files and anchors were checked; external sources were checked with HTTP requests and publisher/institutional pages. Some publishers return access restrictions to automated requests, so these responses cannot be treated as missing pages or guaranteed anonymous full-text access.
