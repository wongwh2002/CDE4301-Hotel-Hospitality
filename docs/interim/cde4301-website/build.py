"""Rebuild the report page from this folder's Markdown and HTML template.

Requires Markdown (also listed in ../requirements.txt).
"""

from html import escape, unescape
from pathlib import Path
import re

import markdown


HERE = Path(__file__).resolve().parent

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
    (HERE / 'report.html').write_text(page, encoding='utf-8')
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
    print('Built report.html and the redirect from report (1).html.')


if __name__ == '__main__':
    build_report()
