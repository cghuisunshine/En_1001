#!/usr/bin/env python3
"""Build a local paged reader for Amy Tan's story from the supplied school PDF."""

from __future__ import annotations

import html
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Rules-of-the-Game.pdf"
TEMPLATE = ROOT / "hills_like_white_elephants.html"
OUTPUT = ROOT / "rules_of_the_game.html"


def paragraphs() -> list[str]:
    raw = subprocess.check_output(["pdftotext", "-layout", str(SOURCE), "-"], text=True)
    pages = raw.split("\f")[:6]
    if len(pages) != 6 or "Rules of The Game" not in pages[0]:
        raise ValueError("The expected six-page Amy Tan story was not found.")
    result: list[str] = []
    current = ""
    previous_line = ""
    for page in pages:
        for line in page.splitlines():
            text = line.strip()
            if not text or "Rules of The Game" in text and "Amy Tan" in text:
                continue
            indent = len(line) - len(line.lstrip())
            begins_new = indent >= 3
            if not begins_new and current and previous_line.endswith(('.', '?', '!', '"')):
                begins_new = bool(re.match(r'^[A-Z"“]', text))
            if begins_new and current:
                result.append(current.strip())
                current = ""
            if current.endswith("-") and text and text[0].islower():
                current += text
            else:
                current += (" " if current else "") + text
            previous_line = text
    if current:
        result.append(current.strip())
    cleaned = []
    for item in result:
        item = item.replace("Each morn ing", "Each morning")
        item = item.replace("We lived in. San Francisco's", "We lived in San Francisco's")
        item = item.replace("Chinese people.do", "Chinese people do")
        item = item.replace("My bother Winston", "My brother Winston")
        item = item.replace("'Who say this word?\"", '"Who say this word?"')
        cleaned.append(item)
    return cleaned


def split_into_parts(items: list[str], count: int = 6) -> list[list[str]]:
    total_words = sum(len(item.split()) for item in items)
    target = total_words / count
    parts: list[list[str]] = [[]]
    words = 0
    for item in items:
        if len(parts) < count and parts[-1] and words >= target:
            parts.append([])
            words = 0
        parts[-1].append(item)
        words += len(item.split())
    while len(parts) < count:
        parts.append([])
    return parts


def main() -> None:
    items = paragraphs()
    parts = split_into_parts(items)
    page = TEMPLATE.read_text(encoding="utf-8")
    page = page.replace("Hills Like White Elephants", "Rules of the Game")
    page = page.replace("hills-like-white-elephants", "rules-of-the-game")
    page = page.replace("Ernest Hemingway", "Amy Tan")
    sections = ['<main class="reader-stage" id="reader-stage">']
    for n, group in enumerate(parts, 1):
        sections.append(f'<section class="reader-page" id="page-{n}" aria-label="Part {n}"' + (' hidden>' if n > 1 else '>'))
        sections.append(f'<div class="page-heading">Part {n} of 6</div>')
        if n == 1:
            sections.append(
                '<div class="story-heading"><h1>Rules of the Game</h1><p class="author">Amy Tan</p>'
                '<p class="source-note">Text from <a href="Rules-of-the-Game.pdf">the school PDF</a>. '
                'The source has some transcription errors; consult your course anthology for exact quotations.</p></div>'
            )
        sections.extend(f'<p>{html.escape(item, quote=False)}</p>' for item in group)
        sections.append('</section>')
    sections.append('</main>')
    page, replacements = re.subn(
        r'<main class="reader-stage" id="reader-stage">.*?</main>',
        "\n".join(sections),
        page,
        count=1,
        flags=re.S,
    )
    if replacements != 1:
        raise ValueError("Could not replace template story pages.")
    page = page.replace('PDF page 1 of 6', 'Part 1 of 6')
    page = page.replace('>Page</label>', '>Part</label>')
    page = page.replace("pageStatus.textContent = 'PDF page ' + number", "pageStatus.textContent = 'Part ' + number")
    OUTPUT.write_text(page, encoding="utf-8")
    print(f"Built {OUTPUT.name}: {len(items)} paragraphs, {sum(len(x.split()) for x in items)} words.")


if __name__ == "__main__":
    main()
