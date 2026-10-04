#!/usr/bin/env python3
"""Add the shared mobile heading menu to local HTML pages, idempotently."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
VERSION = '20261004-iphone-player'
ASSETS = f'<link rel="stylesheet" href="mobile_heading_menu.css?v={VERSION}">\n<script src="mobile_heading_menu.js?v={VERSION}" defer></script>\n'


def add_menu_assets(page):
    if re.search(r'src="mobile_heading_menu\.js(?:\?[^"\s]*)?"', page):
        return re.sub(r'(?:mobile_heading_menu\.(?:js|css))(?:\?[^"\s]*)?(?=")', lambda match: match.group(0).split('?')[0] + '?v=' + VERSION, page)
    return page.replace('</head>', ASSETS + '</head>', 1)


def main():
    updated = []
    for path in sorted(ROOT.glob('*.html')):
        before = path.read_text(encoding='utf-8')
        after = add_menu_assets(before)
        if after != before:
            path.write_text(after, encoding='utf-8')
            updated.append(path.name)
    print(f'Updated {len(updated)} HTML pages.')


if __name__ == '__main__':
    main()
