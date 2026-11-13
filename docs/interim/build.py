"""Rebuild the static report and transcript pages. Requires Markdown >= 3.5."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import json
import re

import markdown

HERE = Path(__file__).resolve().parent
TITLE = 'Guest-context cues for personalised hotel service'


def timestamp(seconds, milliseconds=False):
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    if milliseconds:
        return f'{h:02}:{m:02}:{s:02}.{ms:03}'
    return f'{h:02}:{m:02}:{s:02}' if h else f'{m:02}:{s:02}'


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def word_count(source):
    parsed = PlainText()
    parsed.feed(markdown.markdown(source, extensions=['tables', 'attr_list']))
    return len(re.findall(r"\b\w+(?:[’'-]\w+)*\b", ' '.join(parsed.parts)))


def frame(title, nav, hero, content, transcript=False):
    return f'''<!doctype html>
<html lang="en-SG">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="CDE4301 Team IS-432 interim report: guest-context capture, recognition and concise smart-glasses cues for hotel service. Includes technical evidence, formative testing and a timestamped presentation transcript.">
<meta name="theme-color" content="#192e35">
<title>{escape(title)} · CDE4301 IS-432</title>
<link rel="stylesheet" href="assets/report.css">
<script src="assets/report.js" defer></script>
</head>
<body{' class="transcript-layout"' if transcript else ''}>
<a class="skip-link" href="#main">Skip to content</a>
<aside class="rail" id="navigation" aria-label="Document navigation">
<a class="brand" href="index.html">CDE4301 · IS-432<small>Hotel & hospitality<br>Semester 1 · Interim assessment</small></a>
<p class="rail-label">{'Recording chapters' if transcript else 'In this report'}</p>
<nav aria-label="{'Recording chapters' if transcript else 'Report contents'}">{nav}</nav>
<div class="resources"><a href="index.html">Interim report</a><a href="transcript.html">Presentation transcript</a><a href="Slides.pdf">Presentation slides ↗</a><a href="interim-report.md" download>Report Markdown ↓</a></div>
<div class="rail-foot">Presentation · 5 Nov 2026<br>Prepared · 10 Nov 2026<div class="progress" aria-hidden="true"><span></span></div></div>
</aside>
<main class="page" id="main">
<div class="topbar"><button class="menu-toggle" aria-expanded="false" aria-controls="navigation">Contents</button><span class="desktop-label">NUS · Innovation & Design Capstone</span><span class="tag">{'Source transcript' if transcript else 'Interim report'}</span><button type="button" data-print>Print / save PDF</button></div>
{hero}
<article class="article">{content}</article>
<footer class="footer"><span>IS-432 · Neha Rajan · Tan Ping Hui · Wong Weng Hong · Nigel Yeo Tong Wei</span><span>10 November 2026 · <a href="https://github.com/wongwh2002/CDE4301-Hotel-Hospitality">Project repository ↗</a></span></footer>
</main>
</body>
</html>
'''


def build_report():
    source = (HERE / 'interim-report.md').read_text(encoding='utf-8')
    body = source.split('<!-- REPORT_BODY -->', 1)[1]
    count = word_count(body.split('<!-- APPENDICES -->', 1)[0])
    md = markdown.Markdown(extensions=['tables', 'attr_list', 'toc', 'fenced_code'])
    rendered = md.convert(body)
    rendered = re.sub(r'(<table>.*?</table>)', r'<div class="table-wrap">\1</div>', rendered, flags=re.S)
    nav = ''.join(f'<a href="#{escape(t["id"])}">{escape(t["name"])}</a>' for t in md.toc_tokens if t['level'] == 2)
    hero = f'''<header class="hero">
<p class="eyebrow">Hotel & hospitality · Team IS-432</p>
<h1>{TITLE}</h1>
<p class="standfirst">Helping hotel staff carry useful guest knowledge from one encounter to the next. A Semester 1 investigation into capture, recognition, and concise cues.</p>
<p class="byline">Neha Rajan · Tan Ping Hui · Wong Weng Hong · Nigel Yeo Tong Wei<br>Interim presentation: 5 November 2026 &nbsp; / &nbsp; Report prepared: 10 November 2026 &nbsp; / &nbsp; Revised: 13 November 2026<br>Approximately {count:,} words in the main report · Four-person group limit: 6,000 words excluding appendices</p>
<div class="hero-links"><a class="button primary" href="#executive-summary">Read the report ↓</a><a class="button" href="transcript.html">Read the transcript</a><a class="button" href="Slides.pdf">View the slides ↗</a></div>
</header>
<div class="overview" aria-label="Interim evidence at a glance">
<div><span class="big">1.18 s</span><span class="label">Mean warm rendering latency</span><small>Four successful Android frame commits.<br>Independent cold starts remain to be measured.</small></div>
<div><span class="big">10</span><span class="label">Formative walkthrough participants</span><small>Non-hotel staff; activation was easy.<br>Natural cue use needs further work.</small></div>
<div><span class="big">28 → 9</span><span class="label">Battery drop, percentage points</span><small>Team-confirmed 20-minute comparison.<br>Battery gauge depletion, not measured power.</small></div>
</div>'''
    (HERE / 'index.html').write_text(frame(TITLE, nav, hero, rendered), encoding='utf-8')
    print(f'Report built: approximately {count:,} words before appendices, including references.')


def build_transcript():
    data = json.loads((HERE / 'Recording.transcript.json').read_text(encoding='utf-8'))
    chapters = data['chapters']
    caption_segments = data['segments']
    segments = []
    for segment in caption_segments:
        if segments and segment['start'] - segments[-1]['end'] < 2 and segment['end'] - segments[-1]['start'] <= 28:
            segments[-1]['end'] = segment['end']
            segments[-1]['text'] += ' ' + segment['text']
        else:
            segments.append({key: segment[key] for key in ['start', 'end', 'text']})
    note = data['editorial_note']
    source_note = (
        'Source: Recording.mp4. Duration: 29 minutes 18 seconds. '
        'Presentation date: 5 November 2026. Transcribed locally on 10 November 2026.'
    )
    md = ['# Recording.mp4 — presentation transcript', '', source_note, '', note, '', '## Chapters', '']
    txt = ['RECORDING.MP4 — PRESENTATION TRANSCRIPT', '', source_note, '', note, '', 'CHAPTERS', '']
    for ch in chapters:
        md.append(f'- **{timestamp(ch["start"])}** — {ch["title"]}')
        txt.append(f'{timestamp(ch["start"])} — {ch["title"]}')
    md += ['', '## Transcript', '']
    txt += ['', 'TRANSCRIPT', '']
    vtt = ['WEBVTT', '', 'NOTE Machine-generated transcript with editorial terminology checks; not speaker-diarised.', '']
    entries = []
    for segment in segments:
        start = timestamp(segment['start'])
        end = timestamp(segment['end'])
        text = segment['text']
        md += [f'### {start}–{end}', '', text, '']
        txt += [f'[{start}–{end}]', text, '']
        entries.append(f'<section class="transcript-entry" id="t-{int(segment["start"])}"><a class="timestamp" href="Recording.mp4#t={segment["start"]}" data-seek="{segment["start"]}" aria-label="Play recording from {start}">{start}<br><span aria-hidden="true">↗</span></a><p>{escape(text)}</p></section>')
    for i, segment in enumerate(caption_segments):
        # Preserve ASR boundaries rather than inventing word-level alignment.
        vtt += [str(i + 1), f'{timestamp(segment["start"], True)} --> {timestamp(segment["end"], True)}', segment['text'], '']
    (HERE / 'Recording.transcript.md').write_text('\n'.join(md), encoding='utf-8')
    (HERE / 'Recording.transcript.txt').write_text('\n'.join(txt), encoding='utf-8')
    (HERE / 'Recording.vtt').write_text('\n'.join(vtt), encoding='utf-8')
    nav = ''.join(f'<a href="Recording.mp4#t={ch["start"]}" data-seek="{ch["start"]}">{timestamp(ch["start"])} · {escape(ch["title"])}</a>' for ch in chapters)
    hero = '''<header class="hero"><p class="eyebrow">Presentation source · 29 min 18 s</p><h1>Presentation transcript</h1><p class="standfirst">A timestamped record of the interim presentation and live demonstration, with playback links and searchable passages.</p><div class="hero-links"><a class="button primary" href="index.html">← Return to the report</a><a class="button" href="Recording.transcript.md" download>Markdown ↓</a><a class="button" href="Recording.transcript.txt" download>Plain text ↓</a><a class="button" href="Recording.vtt" download>Captions ↓</a></div></header>'''
    content = f'''<div class="note"><strong>Transcript method.</strong> {escape(note)}</div>
<div class="transcript-video"><video id="recording" controls preload="metadata" aria-label="Interim presentation recording"><source src="Recording.mp4" type="video/mp4"><track kind="captions" src="Recording.vtt" srclang="en" label="English — machine transcript"><a href="Recording.mp4">Open the recording</a></video><div class="video-controls-note">Select a timestamp to seek in the recording. Caption timing follows transcription passages, without word-level alignment.</div></div>
<div class="transcript-tools"><label for="transcript-search">Find in transcript</label><input id="transcript-search" type="search" placeholder="Search a word or phrase" autocomplete="off"><output id="search-count" aria-live="polite">{len(segments)} of {len(segments)} passages</output></div>
<p id="no-results" class="no-results" hidden>No matching passages. Try another word or phrase.</p>
{''.join(entries)}
<p class="footnote">Source SHA-256: <code>{data['source_sha256']}</code><br>Model output was checked against the presentation terminology. Technical and business claims remain the speakers' claims; the report assesses their supporting evidence separately. The file ends during the opening Q&A response.</p>'''
    (HERE / 'transcript.html').write_text(frame('Presentation transcript', nav, hero, content, transcript=True), encoding='utf-8')
    print(f'Transcript built: {len(segments)} timestamped passages.')


if __name__ == '__main__':
    build_transcript()
    build_report()
