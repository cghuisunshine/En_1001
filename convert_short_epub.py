#!/usr/bin/env python3
"""Convert short.epub to a single, offline-readable HTML file."""

from __future__ import annotations

import base64
import html
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "short.epub"
OUTPUT = ROOT / "short.html"
XHTML = "{http://www.w3.org/1999/xhtml}"
OPF = "{http://www.idpf.org/2007/opf}"
DC = "{http://purl.org/dc/elements/1.1/}"


def convert_node(node: ET.Element, archive: ZipFile) -> str:
    tag = node.tag.removeprefix(XHTML)
    if tag == "img":
        path = "OEBPS/" + node.attrib["src"]
        data = base64.b64encode(archive.read(path)).decode("ascii")
        alt = html.escape(node.attrib.get("alt", ""), quote=True)
        return f'<img src="data:image/jpeg;base64,{data}" alt="{alt}" loading="lazy">'
    if tag == "div" and node.attrib.get("id", "").startswith("page-"):
        page = node.attrib["id"].removeprefix("page-")
        return f'<div class="page-marker" id="page-{page}"><span>Page {page}</span></div>'
    if tag not in {"div", "p"}:
        raise ValueError(f"Unexpected EPUB element: {tag}")
    attributes = []
    for key in ("class", "id"):
        value = node.attrib.get(key)
        if value and value != "pages":
            attributes.append(f'{key}="{html.escape(value, quote=True)}"')
    opening = f"<{tag}{(' ' + ' '.join(attributes)) if attributes else ''}>"
    parts = [opening, html.escape(node.text or "")]
    for child in node:
        parts.append(convert_node(child, archive))
        parts.append(html.escape(child.tail or ""))
    parts.append(f"</{tag}>")
    return "".join(parts)


with ZipFile(SOURCE) as archive:
    opf = ET.fromstring(archive.read("OEBPS/content.opf"))
    title = opf.findtext(f"{OPF}metadata/{DC}title") or "Short fiction anthology"
    creator = opf.findtext(f"{OPF}metadata/{DC}creator") or ""
    manifest = {
        item.attrib["id"]: item.attrib["href"]
        for item in opf.findall(f"{OPF}manifest/{OPF}item")
    }
    spine = [
        manifest[item.attrib["idref"]]
        for item in opf.findall(f"{OPF}spine/{OPF}itemref")
    ]

    sections = []
    page_count = 0
    paragraph_count = 0
    for filename in spine:
        root = ET.fromstring(archive.read("OEBPS/" + filename))
        body = root.find(f"{XHTML}body")
        if body is None:
            raise ValueError(f"Missing body in {filename}")
        section_id = filename.removesuffix(".html")
        label = filename.removesuffix(".html")
        sections.append(f'<section class="book-section" id="{section_id}" aria-label="{label}">')
        for child in body:
            sections.append(convert_node(child, archive))
        sections.append("</section>")
        page_count += sum(
            1 for node in body.iter() if node.attrib.get("id", "").startswith("page-")
        )
        paragraph_count += sum(1 for node in body.iter() if node.tag == f"{XHTML}p")

page_max = 1597
document = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
  :root {{ color-scheme: light dark; --paper: #fbf8f1; --ink: #24211e; --muted: #665f55; --line: #d9d1c4; --accent: #4b5740; }}
  * {{ box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; scroll-padding-top: 5rem; }}
  body {{ margin: 0; background: var(--paper); color: var(--ink); font: 1.13rem/1.68 Georgia, "Palatino Linotype", Palatino, serif; }}
  .toolbar {{ position: sticky; top: 0; z-index: 10; display: flex; flex-wrap: wrap; align-items: center; gap: .55rem 1rem; padding: .7rem max(1rem, calc((100vw - 82rem)/2)); background: #f5f0e6; border-bottom: 1px solid var(--line); font: .9rem/1.3 system-ui, sans-serif; }}
  .toolbar a {{ color: var(--accent); text-decoration: none; }}
  .toolbar a:hover {{ text-decoration: underline; }}
  .toolbar strong {{ margin-right: auto; max-width: 25rem; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }}
  .toolbar form {{ display: flex; gap: .3rem; align-items: center; }}
  .toolbar input {{ width: 5rem; padding: .35rem; font: inherit; border: 1px solid var(--line); border-radius: .25rem; background: white; color: #24211e; }}
  .toolbar button {{ padding: .38rem .65rem; border: 1px solid var(--line); border-radius: .25rem; background: white; color: #24211e; cursor: pointer; }}
  main {{ max-width: 49rem; margin: auto; padding: 2rem 1.25rem 6rem; }}
  .intro-note {{ font: .9rem/1.5 system-ui, sans-serif; color: var(--muted); margin-bottom: 2rem; }}
  p {{ margin: 0 0 .8em; overflow-wrap: break-word; }}
  img {{ display: block; max-width: 100%; height: auto; margin: 1.5rem auto; }}
  .book-section {{ margin-bottom: 2rem; }}
  .page-marker {{ margin: 2.1rem 0 1rem; border-top: 1px solid var(--line); padding-top: .3rem; scroll-margin-top: 5rem; color: var(--muted); font: .75rem/1.4 system-ui, sans-serif; }}
  .page-marker span {{ background: var(--paper); padding-right: .45rem; }}
  .page-marker:target {{ color: var(--accent); border-color: var(--accent); font-weight: 700; }}
  @media (prefers-color-scheme: dark) {{ :root {{ --paper: #201f1c; --ink: #e8e2d7; --muted: #b1a99d; --line: #4a463f; --accent: #c6d0b2; }} .toolbar {{ background: #292722; }} }}
  @media print {{ .toolbar, .intro-note {{ display: none; }} body {{ color: black; background: white; }} main {{ max-width: none; }} .page-marker {{ break-before: auto; }} }}
</style>
</head>
<body>
<nav class="toolbar" aria-label="Book navigation">
  <strong>{html.escape(title)}</strong>
  <a href="#leaf0001">Cover</a>
  <a href="#part0001">Contents</a>
  <a href="#page-2">Text</a>
  <form id="page-form"><label for="page-number">Page</label><input id="page-number" type="number" min="2" max="{page_max}" inputmode="numeric" required><button type="submit">Go</button></form>
</nav>
<main>
  <p class="intro-note">{html.escape(creator)} · Converted from short.epub · {page_count:,} page markers · Use your browser’s Find command to search the text.</p>
  {''.join(sections)}
</main>
<script>
document.getElementById('page-form').addEventListener('submit', function (event) {{
  event.preventDefault();
  const page = Number(document.getElementById('page-number').value);
  const target = document.getElementById('page-' + page);
  if (target) {{ location.hash = 'page-' + page; target.scrollIntoView(); }}
  else alert('Page ' + page + ' is not present in this EPUB.');
}});
</script>
</body>
</html>
'''
OUTPUT.write_text(document, encoding="utf-8")
print(f"Wrote {OUTPUT.name}: {len(document.encode('utf-8')):,} bytes, {len(spine)} sections, {paragraph_count:,} paragraphs, {page_count:,} pages")
