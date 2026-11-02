"""Convert the shared SVG cue catalog into bundled native Android vector resources."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from server.guest_preferences import CATALOG, ICON_DIR, MARKERS

ANDROID = 'http://schemas.android.com/apk/res/android'
ET.register_namespace('android', ANDROID)


def path_data(element):
    tag = element.tag.rsplit('}', 1)[-1]
    attr = element.attrib
    n = lambda key, default=0: float(attr.get(key, default))
    if tag == 'path':
        return attr['d']
    if tag in ('circle', 'ellipse'):
        x, y = n('cx'), n('cy')
        rx = n('r') if tag == 'circle' else n('rx')
        ry = n('r') if tag == 'circle' else n('ry')
        return f'M{x-rx},{y}a{rx},{ry} 0 1,0 {2*rx},0a{rx},{ry} 0 1,0 {-2*rx},0z'
    if tag == 'rect':
        x, y, w, h = n('x'), n('y'), n('width'), n('height')
        rx = min(n('rx'), w/2)
        ry = min(n('ry', rx), h/2)
        return (f'M{x+rx},{y}H{x+w-rx}Q{x+w},{y} {x+w},{y+ry}V{y+h-ry}'
                f'Q{x+w},{y+h} {x+w-rx},{y+h}H{x+rx}Q{x},{y+h} {x},{y+h-ry}'
                f'V{y+ry}Q{x},{y} {x+rx},{y}z')
    raise ValueError(f'Unsupported SVG element: {tag}')


def convert(source, target):
    svg = ET.parse(source).getroot()
    _, _, width, height = svg.attrib['viewBox'].split()
    vector = ET.Element('vector', {f'{{{ANDROID}}}width': f'{width}dp',
        f'{{{ANDROID}}}height': f'{height}dp', f'{{{ANDROID}}}viewportWidth': width,
        f'{{{ANDROID}}}viewportHeight': height})
    def visit(element, inherited):
        attrs = dict(inherited)
        attrs.update(element.attrib)
        if element.tag.rsplit('}', 1)[-1] in ('g', 'svg'):
            for child in element:
                visit(child, attrs)
            return
        path = {f'{{{ANDROID}}}pathData': path_data(element)}
        for svg_key, android_key, default in (
            ('fill','fillColor','#000000'), ('stroke','strokeColor','none'),
            ('stroke-width','strokeWidth','1'), ('stroke-linecap','strokeLineCap','butt'),
            ('stroke-linejoin','strokeLineJoin','miter')):
            value = attrs.get(svg_key, default)
            if value == 'none':
                value = '#00000000'
            path[f'{{{ANDROID}}}{android_key}'] = value
        ET.SubElement(vector, 'path', path)
    visit(svg, {})
    ET.indent(vector)
    target.write_text('<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(vector, encoding='unicode') + '\n', encoding='utf-8')


def main():
    resources = ROOT / 'app/src/main/res/drawable'
    resources.mkdir(parents=True, exist_ok=True)
    icons, markers = [], []
    for code, _, _, icon in CATALOG:
        name = f'cue_{code}'
        convert(ICON_DIR / icon, resources / f'{name}.xml')
        icons.append(f'        "{code}" to R.drawable.{name}')
    for sentiment, marker in MARKERS.items():
        name = f'cue_marker_{sentiment}'
        convert(ICON_DIR / marker['icon_file'], resources / f'{name}.xml')
        markers.append(f'        "{sentiment}" to R.drawable.{name}')
    code = ('package com.example.rokid_app\n\n'
            '// Generated from the shared SVG catalog by server/generate_android_cue_icons.py.\n'
            'object GuestCueIcons {\n    private val icons = mapOf(\n' + ',\n'.join(icons) + '\n    )\n'
            '    private val markers = mapOf(\n' + ',\n'.join(markers) + '\n    )\n'
            '    fun icon(code: String): Int? = icons[code]\n'
            '    fun marker(sentiment: String): Int? = markers[sentiment]\n}\n')
    (ROOT / 'app/src/main/java/com/example/rokid_app/GuestCueIcons.kt').write_text(code, encoding='utf-8')
    print(f'Generated {len(icons)} main icons and {len(markers)} markers for Android')


if __name__ == '__main__':
    main()
