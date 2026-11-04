#!/usr/bin/env python3
"""Build artwork galleries from image folders, with short display titles.

Image filenames and paths are preserved; only the captions are simplified.
When shop-links.json includes an exact normalized title match, its title is used
for consistency with the Print / Original shop buttons.
"""

import json
import re
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


def simple_title(filename_stem):
    """Remove size / framing information at the END of an artwork filename."""
    title = re.sub(r'\s+', ' ', filename_stem.replace('_', ' ')).strip()

    # Run repeatedly to accommodate e.g. "Lionfish 29 x 39 matted".
    while True:
        before = title
        # Unwanted closing and opening parentheses/brackets around dimensions.
        title = re.sub(
            r'\s*[\(\[]\s*\d+(?:\.\d+)?\s*[x×]\s*\d+(?:\.\d+)?\s*[\)\]]\s*$',
            '', title, flags=re.IGNORECASE,
        )
        # e.g. "Lionfish 29 x 39", "Utopia 41x17", "Visionary 13.5 x 18.5".
        title = re.sub(
            r'\s*[-–—,]?\s+\d+(?:\.\d+)?\s*(?:["”″]|in(?:ches?)?\.?)*\s*[x×]\s*'
            r'\d+(?:\.\d+)?\s*(?:["”″]|in(?:ches?)?\.?)*\s*$',
            '', title, flags=re.IGNORECASE,
        )
        # e.g. "Patch reef matted 15\"", "Watchful Eyes framed".
        title = re.sub(
            r'\s+(?:matted|framed)(?:\s+\d+(?:\.\d+)?\s*(?:["”″]|in(?:ches?)?\.?))?\s*$',
            '', title, flags=re.IGNORECASE,
        )
        # e.g. "No Escape 15\"", "Reef Hunter 15 inches".
        title = re.sub(
            r'\s+\d+(?:\.\d+)?\s*(?:["”″]|in(?:ches?)?\.?)\s*$',
            '', title, flags=re.IGNORECASE,
        )
        title = title.strip(' -–—_,')
        if title == before:
            break

    return title or filename_stem.strip()


def match_key(title):
    """Match display titles without making guesses about different artworks."""
    return re.sub(r'[^\w]+', ' ', title.casefold()).strip()


def shop_titles():
    """Optional exact titles from the shop-links.json mapping."""
    shop_file = ROOT / 'shop-links.json'
    if not shop_file.is_file():
        return {}
    try:
        catalog = json.loads(shop_file.read_text(encoding='utf-8'))
        return {
            section: {match_key(title): title for title in entries}
            for section, entries in catalog.items()
            if isinstance(entries, dict)
        }
    except (ValueError, OSError) as error:
        print(f'Ignoring unreadable shop-links.json: {error}')
        return {}


def main():
    titles = shop_titles()
    manifest = {}
    for section_id, folder in FOLDERS.items():
        directory = ROOT / 'images' / folder
        if not directory.is_dir():
            raise SystemExit(f'Missing gallery folder: {directory}')
        pictures = sorted(
            (p for p in directory.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONS),
            key=lambda p: p.name.casefold(),
        )
        section_titles = titles.get(section_id, {})
        manifest[section_id] = [
            {
                'path': p.relative_to(ROOT).as_posix(),
                'caption': section_titles.get(
                    match_key(simple_title(p.stem)), simple_title(p.stem)
                ),
            }
            for p in pictures
        ]

    output = ROOT / 'gallery-manifest.json'
    output.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + '\n',
        encoding='utf-8',
    )
    print(f'Generated {output.name} with {sum(map(len, manifest.values()))} images')


if __name__ == '__main__':
    main()
