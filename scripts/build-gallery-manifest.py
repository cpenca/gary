#!/usr/bin/env python3
"""List artwork images in category folders, for GitHub Pages galleries."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = {
    'botanicals': 'Botanicals',
    'balloons': 'Balloons',
    'fish-out-of-water': 'Fish Out of Water',
    'reefscapes': 'Reefscapes',
    'conceptual-art': 'Conceptual Art',
    'under-the-pier': 'Under the Pier',
}
EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif'}

manifest = {}
for section_id, folder in FOLDERS.items():
    directory = ROOT / 'images' / folder
    if not directory.is_dir():
        raise SystemExit(f'Missing gallery folder: {directory}')
    pictures = sorted(
        (p for p in directory.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONS),
        key=lambda p: p.name.casefold(),
    )
    manifest[section_id] = [
        {'path': p.relative_to(ROOT).as_posix(), 'caption': p.stem.strip().replace('_', ' ')}
        for p in pictures
    ]

output = ROOT / 'gallery-manifest.json'
output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f'Generated {output.name} with {sum(map(len, manifest.values()))} images')
