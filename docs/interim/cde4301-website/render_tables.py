"""Render the editable main-body tables to PNGs with their original text intact.

Requires Markdown, Playwright, and Google Chrome. Run before build.py after
editing main-report-tables.md. The published website needs none of these tools.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re

import markdown


HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'main-report-tables.md'
OUTPUT = HERE / 'assets/tables'
WIDTHS = {1: 1280, 2: 1440, 3: 1600, 4: 1440, 5: 1000, 6: 1440, 7: 1100, 8: 1440, 9: 1440}
COLUMNS = {
    1: [25, 75], 2: [24, 24, 52], 3: [16, 21, 21, 21, 21],
    4: [23, 37, 40], 5: [42, 22, 36], 6: [29, 31, 40],
    7: [78, 22], 8: [25, 33, 42], 9: [27, 18, 55],
}
STYLE = '''
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff;color:#162b48}
body{font-family:Arial,Helvetica,sans-serif;font-size:22px;line-height:1.45}
.table-card{padding:20px;width:100%}
table{width:100%;border-collapse:collapse;table-layout:fixed}
th,td{border:1px solid #c9d5e5;padding:16px 18px;text-align:left;vertical-align:top;overflow-wrap:break-word}
th{background:#142d52;color:#fff;font-weight:700}
tbody tr:nth-child(even){background:#f0f4fa}
strong{font-weight:700}
a{color:#154c94;text-decoration:underline;text-underline-offset:3px}
'''


def read_tables(source):
    sections = re.findall(r'^## Table (\d+)\. (.*?) \{#table-\d+\}\s*\n(.*?)(?=^## |\Z)', source, re.M | re.S)
    tables = []
    for number, title, section in sections:
        rendered = markdown.markdown(section, extensions=['tables'])
        match = re.search(r'<table>.*?</table>', rendered, re.S)
        if not match:
            raise ValueError(f'Table {number} is missing a Markdown table.')
        tables.append((int(number), title, match[0]))
    if [number for number, _, _ in tables] != list(range(1, 10)):
        raise ValueError('Expected Tables 1–9, in order, in main-report-tables.md.')
    return tables


def render_tables(channel='chrome'):
    from playwright.sync_api import sync_playwright

    source = SOURCE.read_text(encoding='utf-8')
    tables = read_tables(source)
    OUTPUT.mkdir(exist_ok=True)
    manifest = {'source': SOURCE.name, 'source_sha256': hashlib.sha256(source.encode('utf-8')).hexdigest(), 'scale': 2, 'tables': []}
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=channel, headless=True)
        page = browser.new_page(device_scale_factor=2)
        for number, title, content in tables:
            width = WIDTHS[number]
            page.set_viewport_size({'width': width, 'height': 1000})
            cols = '<colgroup>' + ''.join(f'<col style="width:{percent}%">' for percent in COLUMNS[number]) + '</colgroup>'
            content = content.replace('<table>', '<table>' + cols, 1)
            page.set_content(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><style>{STYLE}</style></head><body><main class="table-card">{content}</main></body></html>')
            page.evaluate('document.fonts.ready')
            if not page.locator('th,td').evaluate_all('(cells)=>cells.every(c=>c.scrollWidth<=c.clientWidth+1)'):
                raise ValueError(f'Text overflows a cell in Table {number}.')
            bounds = page.locator('.table-card').bounding_box()
            height = round(bounds['height'])
            filename = f'table-{number:02}.png'
            page.locator('.table-card').screenshot(path=str(OUTPUT / filename))
            manifest['tables'].append({'number': number, 'title': title, 'file': f'assets/tables/{filename}', 'width': width, 'height': height})
            print(f'Table {number}: {width * 2} x {height * 2} pixels -> {filename}', flush=True)
        browser.close()
    (OUTPUT / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', default='chrome', help='Playwright browser channel (default: chrome).')
    render_tables(parser.parse_args().browser)
