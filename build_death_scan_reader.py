#!/usr/bin/env python3
"""Build a faithful single-file image reader for the scanned Atwood story."""

from __future__ import annotations

import base64
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Death by Landscape.pdf"
OUTPUT = ROOT / "death_by_landscape.html"


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="death-landscape-") as directory:
        prefix = Path(directory) / "scan"
        subprocess.run(
            [
                "pdftoppm", "-f", "4", "-l", "23", "-scale-to", "1600",
                "-jpeg", "-jpegopt", "quality=84", str(SOURCE), str(prefix),
            ],
            check=True,
        )
        scans = sorted(Path(directory).glob("scan-*.jpg"))
        if len(scans) != 20:
            raise ValueError(f"Expected 20 story scans, found {len(scans)}")
        image_urls = [
            "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode("ascii")
            for path in scans
        ]

    page = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Death by Landscape — Margaret Atwood</title>
<style>
  :root { --bg:#e9e3d8; --paper:#fffdf8; --ink:#28241e; --muted:#6d665d; --line:#d8d0c4; --accent:#69543d; }
  * { box-sizing:border-box; }
  body { margin:0; min-height:100dvh; background:var(--bg); color:var(--ink); font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif; }
  a { color:var(--accent); text-underline-offset:3px; }
  button,input { font:inherit; }
  button { cursor:pointer; }
  :focus-visible { outline:3px solid var(--accent); outline-offset:3px; }
  .top { display:flex; flex-wrap:wrap; align-items:center; gap:10px 20px; padding:12px clamp(12px,3vw,30px); background:var(--paper); border-bottom:1px solid var(--line); }
  .title { margin:0 auto 0 0; font:700 1.13rem/1.2 Georgia,"Times New Roman",serif; }
  .tools { display:flex; flex-wrap:wrap; align-items:center; gap:8px; }
  .tools form { display:flex; align-items:center; gap:6px; }
  .tools input { width:4.3rem; padding:5px; border:1px solid var(--line); border-radius:6px; background:var(--paper); color:var(--ink); }
  button { border:1px solid var(--line); border-radius:7px; padding:7px 11px; background:var(--paper); color:var(--ink); }
  button:hover { border-color:var(--accent); }
  button:disabled { opacity:.45; cursor:not-allowed; }
  .intro { max-width:980px; margin:18px auto 12px; padding:0 15px; }
  .intro p { margin:5px 0; color:var(--muted); font-size:.88rem; }
  .stage { width:min(100%,1040px); height:calc(100dvh - 210px); min-height:430px; margin:0 auto; overflow:auto; background:var(--paper); box-shadow:0 10px 32px #0002; text-align:center; }
  .stage img { display:block; width:min(100%,1040px); height:auto; margin:0 auto; }
  .stage.actual img { width:1600px; max-width:none; }
  .bottom { display:flex; flex-wrap:wrap; justify-content:center; align-items:center; gap:12px; padding:13px; }
  .bottom span { min-width:12rem; text-align:center; font-weight:700; }
  @media(max-width:650px) { .top { gap:10px; } .title { width:100%; } .stage { height:calc(100dvh - 245px); } }
  @media print { .top,.bottom,.intro { display:none; } .stage { width:auto; height:auto; overflow:visible; box-shadow:none; } .stage img { width:100%; } }
</style>
</head>
<body>
<header class="top">
  <h1 class="title">Death by Landscape <small>· Margaret Atwood</small></h1>
  <div class="tools">
    <form id="pageForm"><label for="pageInput">Printed page</label><input id="pageInput" type="number" min="99" max="118" required><button type="submit">Go</button></form>
    <button id="zoom" type="button" aria-pressed="false">Actual size</button>
    <a id="pdfLink" href="Death%20by%20Landscape.pdf#page=4">Original PDF</a>
  </div>
</header>
<div class="intro">
  <p>Complete story from printed pages 99–118. These are the scanned page images, so the wording remains faithful to the PDF. Use “Actual size” to zoom and scroll.</p>
</div>
<main class="stage" id="stage"><img id="scan" src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=" alt="Scanned story page 99"></main>
<nav class="bottom" aria-label="Page turns">
  <button id="previous" type="button">← Previous</button>
  <span id="status" role="status" aria-live="polite">Page 99 of 118</span>
  <button id="next" type="button">Next →</button>
</nav>
<script>
const pageImages = __PAGES_JSON__;
const firstPage = 99;
const lastPage = 118;
const image = document.getElementById('scan');
const stage = document.getElementById('stage');
const input = document.getElementById('pageInput');
const status = document.getElementById('status');
const previous = document.getElementById('previous');
const next = document.getElementById('next');
const pdfLink = document.getElementById('pdfLink');
let current = firstPage;
function loadPage() { try { return Number(localStorage.getItem('death-landscape-page')); } catch { return 0; } }
function savePage(n) { try { localStorage.setItem('death-landscape-page', String(n)); } catch {} }
function showPage(n) {
  if (!Number.isInteger(n) || n < firstPage || n > lastPage) return;
  current = n;
  image.src = pageImages[n - firstPage];
  image.alt = 'Scanned printed page ' + n + ' of Death by Landscape';
  stage.scrollTop = 0; stage.scrollLeft = 0;
  input.value = String(n);
  status.textContent = 'Page ' + n + ' of ' + lastPage;
  previous.disabled = n === firstPage;
  next.disabled = n === lastPage;
  pdfLink.href = 'Death%20by%20Landscape.pdf#page=' + (n - 95);
  savePage(n);
  try { history.replaceState(null, '', '#page-' + n); } catch {}
}
previous.addEventListener('click', () => showPage(current - 1));
next.addEventListener('click', () => showPage(current + 1));
document.getElementById('pageForm').addEventListener('submit', event => { event.preventDefault(); showPage(Number(input.value)); });
document.getElementById('zoom').addEventListener('click', event => {
  const enabled = stage.classList.toggle('actual');
  event.currentTarget.setAttribute('aria-pressed', String(enabled));
  event.currentTarget.textContent = enabled ? 'Fit width' : 'Actual size';
});
document.addEventListener('keydown', event => {
  if (event.target.closest('input,textarea,select') || event.altKey || event.ctrlKey || event.metaKey) return;
  if (event.key === 'ArrowRight' || event.key === 'PageDown') { event.preventDefault(); showPage(current + 1); }
  if (event.key === 'ArrowLeft' || event.key === 'PageUp') { event.preventDefault(); showPage(current - 1); }
});
const hashPage = Number((location.hash.match(/^#page-([0-9]+)$/) || [])[1]);
const savedPage = loadPage();
showPage(hashPage >= firstPage && hashPage <= lastPage ? hashPage : savedPage >= firstPage && savedPage <= lastPage ? savedPage : firstPage);
</script>
</body>
</html>'''
    page = page.replace("__PAGES_JSON__", json.dumps(image_urls))
    OUTPUT.write_text(page, encoding="utf-8")
    print(f"Built {OUTPUT.name}: {len(image_urls)} scanned pages, {OUTPUT.stat().st_size:,} bytes.")


if __name__ == "__main__":
    main()
