"""Rebuild the report page from this folder's Markdown and HTML template.

Requires Markdown (also listed in ../requirements.txt).
"""

from html import escape, unescape
import hashlib
import json
from pathlib import Path
import re

import markdown


HERE = Path(__file__).resolve().parent
NAV_PAGES = (
    ('index.html', 'Home'),
    ('about.html', 'About Us'),
    ('report.html', 'Report'),
    ('presentation.html', 'Presentation'),
    ('prototype.html', 'Prototype'),
)


def navigation(page_name):
    active_page = 'report.html' if page_name == 'main-report-tables.html' else page_name
    links = []
    for href, label in NAV_PAGES:
        current = ''
        if href == active_page:
            state = 'page' if page_name == href else 'location'
            current = f' class="active" aria-current="{state}"'
        links.append(f'<a href="{href}"{current}>{label}</a>')
    return ('<nav class="nav" aria-label="Main navigation">'
            '<a class="brand" href="index.html">CDE4301 / IS-432</a>'
            '<button class="menu" type="button" aria-label="Toggle navigation" '
            'aria-controls="site-navigation" aria-expanded="false">Menu &#9776;</button>'
            '<div class="navlinks" id="site-navigation">' + ''.join(links) + '</div></nav>')


def with_navigation(page, page_name):
    if '{{SITE_NAVIGATION}}' in page:
        return page.replace('{{SITE_NAVIGATION}}', navigation(page_name))
    page, count = re.subn(r'<nav\b[^>]*class="nav"[^>]*>.*?</nav>', navigation(page_name), page, count=1, flags=re.S)
    if count != 1:
        raise ValueError(f'Expected one main navigation in {page_name}.')
    return page

# Keep links from the other website pages and older report bookmarks usable.
ALIASES = {
    'requirements': '3-aim-scope-and-requirements',
    'concepts': '34-concept-generation-and-selection',
    'prototype': '4-system-architecture-and-prototype-development',
    'initial-concept': '41-solution-overview-and-staff-journey',
    'capture': '42-capture',
    'activation': '421-temple-touch-activation',
    'processing': '422-selective-server-processing',
    'preference-extraction': '423-independent-preference-extraction-testing',
    'display': '43-display',
    'display-position': '431-positioning-information-beside-the-guest',
    'display-content': '432-replacing-descriptions-with-concise-icons',
    'contextual-retrieval': '433-retrieving-contextually-relevant-preferences',
    'system-architecture': '44-complete-system-architecture',
    'testing': '5-user-validation-system-evaluation',
    'user-validation': '51-user-validation',
    'requirements-check': '52-design-requirements-and-whole-system-testing',
    'guest-acceptance': '53-limitations-guest-acceptance-and-pdpa-considerations',
    'next-stage': '6-next-steps-and-validation-plan',
    'contributions': '8-team-contributions',
    'evidence-notes': 'appendix-j',
    'evaluation-protocol': 'appendix-k',
    'technical-detail': 'appendix-l',
}


def section_links(tokens):
    for token in tokens:
        if token['level'] in (2, 3):
            label = escape(unescape(token['name']))
            yield f'<a class="toc-level-{token["level"]}" href="#{escape(token["id"])}">{label}</a>'
        yield from section_links(token.get('children', []))


def build_report():
    source = (HERE / 'interim-report.md').read_text(encoding='utf-8')
    template = (HERE / 'report.template.html').read_text(encoding='utf-8')
    table_source = HERE / 'main-report-tables.md'
    if table_source.exists():
        manifest = json.loads((HERE / 'assets/tables/manifest.json').read_text(encoding='utf-8'))
        digest = hashlib.sha256(table_source.read_text(encoding='utf-8').encode('utf-8')).hexdigest()
        if manifest['source_sha256'] != digest:
            raise ValueError('Table images need refreshing. Run render_tables.py, then build.py.')
    renderer = markdown.Markdown(extensions=['tables', 'attr_list', 'toc', 'fenced_code'])
    body = renderer.convert(source)
    for alias, target in ALIASES.items():
        pattern = rf'(<h[1-6] id="{re.escape(target)}")'
        if not re.search(pattern, body):
            raise ValueError(f'Missing section for bookmark {alias}: {target}')
        body = re.sub(pattern, f'<span id="{alias}" class="section-alias" aria-hidden="true"></span>\\1', body, count=1)
    body = re.sub(r'(<table>.*?</table>)', r'<div class="table-scroll">\1</div>', body, flags=re.S)
    page = template.replace('{{REPORT_TOC}}', ''.join(section_links(renderer.toc_tokens)))
    page = page.replace('{{REPORT_BODY}}', body)
    page = with_navigation(page, 'report.html')
    (HERE / 'report.html').write_text(page, encoding='utf-8')
    if table_source.exists():
        build_table_text_page(table_source.read_text(encoding='utf-8'), template)
    (HERE / 'report (1).html').write_text('''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="0; url=report.html">
<link rel="canonical" href="report.html">
<title>CDE4301 interim report</title>
<script>location.replace('report.html' + location.search + location.hash);</script>
</head>
<body><p>The report is available at <a href="report.html">CDE4301 Hospitality: interim report</a>.</p></body>
</html>
''', encoding='utf-8')
    for filename, _ in NAV_PAGES:
        if filename != 'report.html':
            path = HERE / filename
            path.write_text(with_navigation(path.read_text(encoding='utf-8'), filename), encoding='utf-8')
    print('Built report.html and the redirect from report (1).html.')


def build_table_text_page(source, template):
    renderer = markdown.Markdown(extensions=['tables', 'attr_list', 'toc', 'fenced_code'])
    body = renderer.convert(source)
    body = re.sub(r'(<table>.*?</table>)', r'<div class="table-scroll">\1</div>', body, flags=re.S)
    page = template.replace('{{REPORT_TOC}}', ''.join(section_links(renderer.toc_tokens)))
    page = page.replace('{{REPORT_BODY}}', body)
    page = page.replace('<title>Report |', '<title>Table text |')
    page = re.sub(r'(<h1 class="page-title">).*?(</h1>)', r'\1Main Report Tables\2', page)
    page = page.replace('Interim capstone report · Team IS-432 · References and Appendices A–L', 'Text versions of Tables 1–9 from the interim report')
    page = page.replace('href="interim-report.md"', 'href="main-report-tables.md"')
    page = page.replace('href="#references"', 'href="report.html#references"')
    page = page.replace('href="#appendix-a"', 'href="report.html#appendix-a"')
    page = with_navigation(page, 'main-report-tables.html')
    (HERE / 'main-report-tables.html').write_text(page, encoding='utf-8')


if __name__ == '__main__':
    build_report()
