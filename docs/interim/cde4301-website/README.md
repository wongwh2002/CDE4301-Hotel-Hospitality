# CDE4301 Hospitality website

Static HTML/CSS/JavaScript website generated from the supplied `interim-report.md`.

## Pages
- `index.html` — Home
- `about.html` — Team and project framing
- `report.html` — Full report with linked table of contents, references and appendices
- `prototype.html` — Prototype overview and status

## Preview
Open `index.html` in a browser, or from this folder run `python3 -m http.server 8000` and visit `http://localhost:8000`.

## GitHub Pages deployment
**Easiest:** Put the files in the repository root of a deployment branch, then go to Settings → Pages → Deploy from a branch → choose the deployment branch and `/ (root)`. If the repository already has a Pages site, changing the publishing source may replace it. Alternatively use a separate repository for the website.

## Assets and supporting files
The user uploaded only the Markdown file. Original report figures and attachments are **not bundled**. Image URLs point to `raw.githubusercontent.com/wongwh2002/CDE4301-Hotel-Hospitality/main/docs/interim/assets/...`; supporting files link to their original GitHub paths. Ensure these files exist on the published branch, or copy the original `assets/`, PDF, video and transcript files into the website and update links to local paths. Some links to external files may be inaccessible if the repository is private.

## Content
The report is included verbatim in `interim-report.md`; HTML generated from it preserves section structure and citations. The homepage and prototype overview are shorter editorial summaries.
