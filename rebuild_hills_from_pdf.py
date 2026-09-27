#!/usr/bin/env python3
"""Replace the incomplete OCR reader with the six story pages in May-Short-Stories.pdf."""

from __future__ import annotations

import html
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PDF = ROOT / "May-Short-Stories.pdf"
PAGE = ROOT / "hills_like_white_elephants.html"


def story_pages() -> list[list[str]]:
    raw = subprocess.check_output(["pdftotext", "-layout", str(PDF), "-"], text=True)
    pages = raw.split("\f")[:6]
    if len(pages) != 6 or "HILLS LIKE WHITE ELEPHANTS" not in pages[0]:
        raise ValueError("The expected six-page Hemingway story was not found at the start of the PDF.")
    result: list[list[str]] = []
    for page_index, page in enumerate(pages):
        if page_index == 5:
            page = page.split(
                "“Hills Like White Elephants” by Ernest Hemingway was originally published",
                1,
            )[0]
        paragraphs: list[str] = []
        current: list[str] = []
        for line in page.splitlines():
            stripped = line.strip()
            if not stripped or stripped.isdigit() or stripped.startswith("HILLS LIKE WHITE ELEPHANTS"):
                continue
            if stripped.startswith("* River in the north of Spain") or stripped == "1927":
                continue
            indent = len(line) - len(line.lstrip())
            new_paragraph = indent >= 5 or stripped.startswith('"')
            if new_paragraph and current:
                paragraphs.append(" ".join(current))
                current = []
            current.append(stripped)
        if current:
            paragraphs.append(" ".join(current))
        result.append([re.sub(r'^" +', '"', text) for text in paragraphs])
    return result


def main() -> None:
    pages = story_pages()
    old = PAGE.read_text(encoding="utf-8")
    parts: list[str] = ['<main class="reader-stage" id="reader-stage">']
    for n, paragraphs in enumerate(pages, 1):
        hidden = " hidden" if n > 1 else ""
        parts.extend([
            f'<section class="reader-page" id="page-{n}" aria-label="PDF page {n}"{hidden}>',
            f'<div class="page-heading">PDF page {n} of 6</div>',
        ])
        if n == 1:
            parts.append(
                '<div class="story-heading"><h1>Hills Like White Elephants</h1>'
                '<p class="author">Ernest Hemingway</p>'
                '<p class="source-note">Complete story text from '
                '<a href="May-Short-Stories.pdf">May-Short-Stories.pdf</a>, pages 1–6.</p></div>'
            )
        parts.extend(f"<p>{html.escape(paragraph, quote=False)}</p>" for paragraph in paragraphs)
        if n == 1:
            parts.append('<p class="note">* Ebro: river in the north of Spain.</p>')
        parts.append('</section>')
    parts.append('</main>')
    revised = re.sub(
        r'<main class="reader-stage" id="reader-stage">.*?</main>',
        "\n".join(parts),
        old,
        count=1,
        flags=re.S,
    )
    if revised == old:
        raise ValueError("Could not locate the old reader pages.")
    revised = revised.replace('min="641" max="645"', 'min="1" max="6"')
    revised = revised.replace('Page 641 of 645', 'PDF page 1 of 6')
    revised = revised.replace('const firstPage = 641;', 'const firstPage = 1;')
    revised = revised.replace('const lastPage = 645;', 'const lastPage = 6;')
    revised = revised.replace("pageStatus.textContent = 'Page ' + number + ' of ' + lastPage;", "pageStatus.textContent = 'PDF page ' + number + ' of ' + lastPage;")
    PAGE.write_text(revised, encoding="utf-8")
    print(f"Updated {PAGE.name}: {len(pages)} PDF pages, {sum(map(len,pages))} paragraphs.")


if __name__ == "__main__":
    main()
