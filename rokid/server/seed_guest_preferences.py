"""Seed demo preferences from gallery filenames and export a standalone icon preview."""
import argparse
import html
import json
from pathlib import Path
import sys
import sqlite3
from datetime import datetime, timezone
from contextlib import closing

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from server.guest_preferences import CATALOG, DEFAULT_DATABASE, GuestPreferenceStore, ICON_DIR, MARKERS


def export_preview(profiles, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "profiles.json").write_text(json.dumps(profiles, indent=2), encoding="utf-8")
    def tile(label, icon_file, sentiment=None):
        svg = (ICON_DIR / icon_file).read_text(encoding="utf-8")
        marker = ''
        if sentiment:
            marker_svg = (ICON_DIR / MARKERS[sentiment]['icon_file']).read_text(encoding='utf-8')
            marker = f'<span class="corner-marker">{marker_svg}</span>'
        return f'<div class="tile"><span class="cue-icon">{svg}{marker}</span><span>{html.escape(label)}</span></div>'
    cards = []
    for guest in profiles:
        groups = []
        for sentiment, heading in (('prefer','Prefers'), ('dislike','Dislikes'), ('allergy','Fictional demo allergies')):
            cues = [cue for cue in guest['cues'] if cue['sentiment'] == sentiment]
            if cues:
                tiles = ''.join(tile(c['label'], c['icon_file'], sentiment) for c in cues)
                groups.append(f'<div class="cue-group"><h3>{heading}</h3><div class="tiles">{tiles}</div></div>')
        content = ''.join(groups) or '<p class="empty">No demo cues assigned.</p>'
        cards.append(f'<article><h2>{html.escape(guest["name"])}</h2>{content}</article>')
    legend = ''.join(tile(label, icon) for _, _, label, icon in CATALOG)
    marker_legend = ''.join(tile(marker['label'], marker['icon_file']) for marker in MARKERS.values())
    examples = tile('Prefers twin room', 'twin-beds.svg', 'prefer')
    examples += tile('Dislikes smoking rooms', 'smoking-room.svg', 'dislike')
    examples += tile('Demo shellfish allergy', 'shellfish.svg', 'allergy')
    icon_catalog = {'schema_version': 2,
                    'items': [{"code": code, "category": category, "label": label, "icon_file": icon}
                              for code, category, label, icon in CATALOG],
                    'markers': MARKERS,
                    'overlay': {'anchor': 'bottom_right', 'size_ratio': 0.36}}
    (destination / "icon-catalog.json").write_text(json.dumps(icon_catalog, indent=2), encoding="utf-8")
    page = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Demo guest preferences</title><style>
*{box-sizing:border-box}body{margin:0;background:#090e0b;color:#edf6ef;font:16px system-ui,sans-serif}
main{max-width:1120px;margin:auto;padding:40px 24px}h1{font-size:30px;margin:0 0 10px}
p{color:#aabdaf;line-height:1.6}h2{color:#39ff64;font-weight:600;font-size:24px;margin:0 0 22px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px;margin:28px 0 40px;align-items:start}
article{border:1px solid #29452e;border-radius:20px;background:#101a13;padding:24px}
.tiles{display:flex;flex-wrap:wrap;gap:18px}.tile{display:flex;align-items:center;flex-direction:column;gap:10px;text-align:center;font-size:13px;width:100px}
.cue-icon{position:relative;display:block;width:88px;height:88px;flex:none}.cue-icon>svg{width:100%;height:100%}
.corner-marker{position:absolute;right:-2px;bottom:-2px;width:36%;height:36%}.corner-marker svg{display:block;width:100%;height:100%}
.legend{display:flex;flex-wrap:wrap;gap:24px;padding:12px 0 28px}h3{font-size:12px;color:#aabdaf;font-weight:500;margin:0 0 12px}
.cue-group{margin-top:24px}.empty{font-size:14px;margin-bottom:0}.examples{border-bottom:1px solid #29452e;margin-top:20px}
footer{color:#aabdaf;border-top:1px solid #29452e;padding-top:20px;font-size:14px}
 </style><main><h1>Guest preferences &amp; allergy cues</h1><p>Fictional demo data for the current gallery. Each guest has 1-2 cues in this demo.<br>
All preferences and allergy labels shown here are fabricated examples, not verified personal or medical information.</p>
<section class="legend examples">EXAMPLES</section>
<section class="cards">CARDS</section><h2>Main icons</h2><section class="legend">LEGEND</section>
<h2>Separate corner markers</h2><section class="legend">MARKERS</section>
<footer>The main icon and marker are separate SVG assets, layered at the bottom-right corner.
Heart = prefer; crossed-out heart = dislike; warning triangle = fictional demo allergy.</footer></main></html>'''
    (destination / "index.html").write_text(page.replace('CARDS', ''.join(cards)).replace('LEGEND', legend)
                                           .replace('MARKERS', marker_legend).replace('EXAMPLES', examples), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gallery", type=Path, default=ROOT / "server/faces")
    parser.add_argument("--db", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--output", type=Path, default=ROOT / "output/guest-preferences")
    parser.add_argument('--regenerate-demo', action='store_true', help='Back up the DB and replace generated demo cues only')
    args = parser.parse_args()
    for _, _, _, icon in CATALOG:
        if not (ICON_DIR / icon).is_file():
            parser.error(f"Missing preference icon: {icon}")
    for icon in [marker['icon_file'] for marker in MARKERS.values()]:
        if not (ICON_DIR / icon).is_file():
            parser.error(f"Missing marker icon: {icon}")
    if args.regenerate_demo and args.db.is_file():
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        backup = Path(str(args.db) + '.before-cues-' + stamp)
        with closing(sqlite3.connect(args.db)) as source, closing(sqlite3.connect(backup)) as target:
            source.backup(target)
        print(f'Previous database backed up: {backup}')
    store = GuestPreferenceStore(args.db)
    profiles = store.seed_gallery(args.gallery, regenerate_demo=args.regenerate_demo)
    export_preview(profiles, args.output)
    print(f"Database: {store.path}")
    print(f"Preview: {args.output / 'index.html'}")
    for guest in profiles:
        print(guest['name'] + ': ' + (', '.join(f"{p['sentiment']} {p['label']}" for p in guest['cues']) or 'No demo cues assigned'))


if __name__ == "__main__":
    main()
