#!/usr/bin/env python3
"""Build the text and audio reader from the checked photograph transcription."""

import html
import json
import re
from pathlib import Path
from apply_mobile_heading_menu import add_menu_assets


ROOT = Path(__file__).resolve().parent


def render(data):
    assert [p["page"] for p in data["pages"]] == list(range(57, 80))
    sections = []
    text = ["Sonny’s Blues — James Baldwin", "Transcribed from sonny_blues_img; printed pages 57–79.", "", "Author biography", data["biography"], ""]
    for page in data["pages"]:
        number = page["page"]
        assert page["paragraphs"] and all(p.strip() for p in page["paragraphs"])
        heading = ""
        if number == 57:
            heading = '<header class="story-heading"><h1>Sonny’s Blues</h1><p class="author">James Baldwin · 1924–1987</p><p class="source-note">Transcribed from your 23 photographs, preserving printed pages 57–79.</p></header><details class="biography"><summary>Author biography from the first page</summary><p>' + html.escape(data["biography"]) + '</p></details>'
        paragraphs = []
        for paragraph in page["paragraphs"]:
            escaped = html.escape(paragraph)
            escaped = re.sub(r"\[(\d+)\]", lambda match: '<sup><a href="#notes-' + str(number) + '" aria-label="Footnote ' + match[1] + '">' + match[1] + '</a></sup>', escaped)
            paragraphs.append('<p class="story-paragraph">' + escaped + "</p>")
        notes = '<aside class="note" id="notes-' + str(number) + '" aria-label="Page footnotes">' + html.escape(page["notes"]) + '</aside>' if page["notes"] else ""
        date = '<p class="date">' + html.escape(page["date"]) + '</p>' if "date" in page else ""
        sections.append(f'''<section class="reader-page" id="page-{number}" aria-label="Printed page {number}"{'' if number == 57 else ' hidden'}>
<div class="page-heading">Printed page {number} · {number - 56} / 23</div>
<div class="text-view">{heading}{''.join(paragraphs)}{date}{notes}</div>
</section>''')
        text.extend([f"—— Printed page {number} ——", "", "\n\n".join(page["paragraphs"]), page.get("date", ""), ("Footnotes: " + page["notes"]) if page["notes"] else "", ""])
    (ROOT / "sonny_blues_img.txt").write_text("\n".join(text), encoding="utf-8")
    page_html = add_menu_assets(TEMPLATE.replace("__SECTIONS__", "\n".join(sections)))
    for filename in ("sonnys_blues.html", "sonny_blues_img.html"):
        output = ROOT / filename
        output.write_text(page_html, encoding="utf-8")
        print(f"Built {output.name}: 23 pages, {output.stat().st_size:,} bytes.")


TEMPLATE = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sonny’s Blues — Photographed pages 57–79</title>
<style>
:root { color-scheme:light; --bg:#e9e3d8; --paper:#fffdf8; --ink:#28241e; --muted:#6d665d; --line:#d8d0c4; --accent:#69543d; --reader-size:19px; }
:root[data-theme="night"] { color-scheme:dark; --bg:#161615; --paper:#24231f; --ink:#e9e2d6; --muted:#b6ad9e; --line:#4b473f; --accent:#d8bd98; }
* { box-sizing:border-box; }
html { height:100%; }
body { display:flex; flex-direction:column; height:100dvh; min-height:350px; margin:0; overflow:hidden; background:var(--bg); color:var(--ink); font:var(--reader-size)/1.75 Georgia,Palatino,serif; }
a { color:var(--accent); text-underline-offset:3px; }
h1 { margin:0; font:600 clamp(2rem,5vw,3.2rem)/1.1 Georgia,Palatino,serif; }
p { margin:0 0 .82em; }
.author { margin:.5rem 0 0; font:.95rem/1.5 system-ui,sans-serif; letter-spacing:.08em; text-transform:uppercase; color:var(--accent); }
.source-note { margin:.7rem 0 1.5rem; color:var(--muted); font:.8rem/1.45 system-ui,sans-serif; }
.story-heading { margin:1rem 0 1.5rem; text-align:center; }
.biography { margin:0 0 1.5rem; padding:.6rem .8rem; border:1px solid var(--line); border-radius:.3rem; font:.88em/1.6 Georgia,Palatino,serif; }
.biography summary { cursor:pointer; font:.8rem/1.5 system-ui,sans-serif; color:var(--accent); }
.biography p { margin:.7rem 0 0; }
.reader-stage { position:relative; flex:1; min-height:0; width:min(54rem,calc(100% - 2rem)); margin:1rem auto; perspective:1600px; touch-action:pan-y; }
.reader-page { position:absolute; inset:0; overflow-y:auto; overscroll-behavior:contain; padding:2rem clamp(1.25rem,7vw,5rem) 3rem; background:var(--paper); box-shadow:0 10px 32px #00000019; scrollbar-color:var(--line) transparent; }
.reader-page[hidden] { display:none; }
.reader-page.turn-next { transform-origin:left center; animation:turn-next .3s ease-out both; }
.reader-page.turn-previous { transform-origin:right center; animation:turn-previous .3s ease-out both; }
@keyframes turn-next { from { opacity:.45; transform:rotateY(18deg) translateX(18px); } to { opacity:1; transform:none; } }
@keyframes turn-previous { from { opacity:.45; transform:rotateY(-18deg) translateX(-18px); } to { opacity:1; transform:none; } }
.page-heading { margin:0 0 1.5rem; border-bottom:1px solid var(--line); padding-bottom:.4rem; color:var(--muted); font:.75rem/1.3 system-ui,sans-serif; text-transform:uppercase; letter-spacing:.08em; }
.note { margin-top:1.6rem; font:.78em/1.5 Georgia,Palatino,serif; color:var(--muted); padding-left:1rem; border-left:2px solid var(--line); }
.date { text-align:right; color:var(--muted); }
sup { line-height:0; font-size:.65em; }
.reader-bar { z-index:2; display:flex; flex:none; flex-wrap:wrap; justify-content:center; align-items:center; gap:.55rem 1rem; padding:.55rem 1rem; background:var(--paper); border-bottom:1px solid var(--line); box-shadow:0 2px 8px #0000000d; font:.85rem/1.3 system-ui,sans-serif; }
.reader-bar strong { margin-right:auto; white-space:nowrap; }
.reader-bar form,.reader-controls { display:flex; align-items:center; gap:.4rem; margin:0; }
.reader-controls { border-left:1px solid var(--line); padding-left:.7rem; }
.reader-bar input { width:4.3rem; padding:.35rem; border:1px solid var(--line); border-radius:.3rem; background:var(--paper); color:var(--ink); font:inherit; }
button { min-height:2rem; padding:.35rem .65rem; border:1px solid var(--line); border-radius:.3rem; background:var(--paper); color:var(--ink); font:inherit; cursor:pointer; }
button:hover:not(:disabled),button[aria-pressed="true"] { border-color:var(--accent); background:var(--accent); color:var(--paper); }
button:disabled { opacity:.45; cursor:not-allowed; }
:focus-visible { outline:2px solid var(--accent); outline-offset:2px; }
#font-size-display { min-width:2.7rem; text-align:center; font-variant-numeric:tabular-nums; }
.audio-controls audio { width:min(15rem,55vw); height:2rem; }
.audio-controls label { display:inline-flex; align-items:center; gap:.3rem; white-space:nowrap; cursor:pointer; }
.audio-controls input { width:auto; accent-color:var(--accent); }
.tts-word.is-speaking { border-radius:.15em; background:#ffe08a; color:#28241e; }
:root[data-theme="night"] .tts-word.is-speaking { background:#c7923b; color:#161615; }
#audio-status:empty { display:none; }
#audio-status { width:100%; color:var(--muted); font-size:.78rem; text-align:center; }
.page-turn-bar { display:flex; flex:none; justify-content:center; align-items:center; gap:1rem; padding:.45rem 1rem .6rem; background:var(--paper); border-top:1px solid var(--line); font:.9rem/1.2 system-ui,sans-serif; }
.page-turn-bar button { min-width:7rem; padding:.6rem 1rem; }
#page-status { min-width:8rem; text-align:center; color:var(--muted); font-variant-numeric:tabular-nums; }
.noscript { margin:0; text-align:center; font:1rem/1.5 system-ui,sans-serif; }
@media(max-width:700px) { .reader-bar strong { width:100%; text-align:center; } .reader-controls { padding-left:.5rem; } .reader-stage { width:100%; margin:0; } .reader-page { box-shadow:none; } .page-turn-bar { gap:.4rem; } .page-turn-bar button { min-width:5rem; padding:.6rem .7rem; } }
@media(prefers-reduced-motion:reduce) { .reader-page.turn-next,.reader-page.turn-previous { animation:none; } }
@media print { body { display:block; height:auto; overflow:visible; color:black; background:white; } .reader-bar,.page-turn-bar { display:none; } .reader-stage { display:block; width:auto; margin:0; } .reader-page,.reader-page[hidden] { position:static; display:block; overflow:visible; box-shadow:none; padding:1rem 0; break-after:page; background:white; } .tts-word.is-speaking { background:transparent; color:inherit; } }
</style>
</head>
<body>
<nav class="reader-bar" aria-label="Reader settings">
<strong>Sonny’s Blues</strong>
<form id="page-form"><label for="page-number">Page</label><input id="page-number" type="number" min="57" max="79" value="57" inputmode="numeric" required><button type="submit">Go</button></form>
<div class="reader-controls" role="group" aria-label="Color theme"><button id="day-button" type="button" aria-pressed="true">Day</button><button id="night-button" type="button" aria-pressed="false">Night</button></div>
<div class="reader-controls" role="group" aria-label="Font size"><button id="font-smaller" type="button" aria-label="Decrease font size">A−</button><output id="font-size-display" aria-live="polite">19px</output><button id="font-larger" type="button" aria-label="Increase font size">A+</button></div>
<div class="reader-controls audio-controls" role="group" aria-label="Story narration"><audio id="story-audio" controls preload="none" aria-label="Read the current page aloud"></audio><label for="highlight-words"><input id="highlight-words" type="checkbox" checked>Highlight words</label></div>
<button id="print-button" type="button">Print text</button>
<span id="audio-status" role="status" aria-live="polite"></span>
</nav>
<noscript><p class="noscript">Enable JavaScript for page navigation. All text is available in <a href="sonny_blues_img.txt">the extracted text file</a>.</p></noscript>
<main class="reader-stage" id="reader-stage">
__SECTIONS__
</main>
<nav class="page-turn-bar" aria-label="Page navigation">
<button id="previous" type="button" disabled>← Previous</button>
<span id="page-status" role="status" aria-live="polite">Page 57 · 1 / 23</span>
<button id="next" type="button">Next →</button>
</nav>
<script src="sonnys_blues_audio/timings.js"></script>
<script src="sonnys_blues_reader_audio.js"></script>
<script>
(() => {
'use strict';
const first = 57, last = 79, prefix = 'sonny-blues-img-';
const root = document.documentElement;
const pages = Array.from(document.querySelectorAll('.reader-page'));
const input = document.getElementById('page-number');
const previous = document.getElementById('previous'), next = document.getElementById('next');
let current = first, fontSize = 19;
const narration = window.initSonnysBluesAudio({
  getCurrentPage:() => current,
  showPage,
  lastPage:last
});
const get = (key) => { try { return localStorage.getItem(prefix + key); } catch { return null; } };
const save = (key,value) => { try { localStorage.setItem(prefix + key,String(value)); } catch {} };
const validPage = (number) => Number.isInteger(number) && number >= first && number <= last;
function showPage(number,animate = true) {
  if (!validPage(number)) return;
  const direction = number >= current ? 'turn-next' : 'turn-previous';
  pages.forEach(page => { page.hidden = page.id !== 'page-' + number; page.classList.remove('turn-next','turn-previous'); });
  const active = pages[number - first];
  active.scrollTop = 0;
  if (animate && number !== current) active.classList.add(direction);
  current = number;
  narration.setPage(number);
  input.value = String(number);
  previous.disabled = number === first;
  next.disabled = number === last;
  document.getElementById('page-status').textContent = 'Page ' + number + ' · ' + (number - first + 1) + ' / 23';
  save('page',number);
  try { history.replaceState(null,'','#page-' + number); } catch {}
}
function setTheme(theme) {
  root.dataset.theme = theme;
  document.getElementById('day-button').setAttribute('aria-pressed',String(theme === 'day'));
  document.getElementById('night-button').setAttribute('aria-pressed',String(theme === 'night'));
  save('theme',theme);
}
function setFont(size) {
  fontSize = Math.min(30,Math.max(16,Number.isFinite(size) ? size : 19));
  root.style.setProperty('--reader-size',fontSize + 'px');
  document.getElementById('font-size-display').textContent = fontSize + 'px';
  document.getElementById('font-smaller').disabled = fontSize === 16;
  document.getElementById('font-larger').disabled = fontSize === 30;
  save('font',fontSize);
}
previous.addEventListener('click',() => showPage(current - 1));
next.addEventListener('click',() => showPage(current + 1));
document.getElementById('page-form').addEventListener('submit',event => { event.preventDefault(); showPage(Number(input.value)); });
document.getElementById('day-button').addEventListener('click',() => setTheme('day'));
document.getElementById('night-button').addEventListener('click',() => setTheme('night'));
document.getElementById('font-smaller').addEventListener('click',() => setFont(fontSize - 1));
document.getElementById('font-larger').addEventListener('click',() => setFont(fontSize + 1));
document.getElementById('print-button').addEventListener('click',() => window.print());
document.addEventListener('keydown',event => {
  if (event.target.closest('input,textarea,select,audio,[contenteditable="true"]') || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
  if (event.key === 'ArrowRight' || event.key === 'PageDown') { event.preventDefault(); showPage(current + 1); }
  if (event.key === 'ArrowLeft' || event.key === 'PageUp') { event.preventDefault(); showPage(current - 1); }
});
let touchStart = null;
document.getElementById('reader-stage').addEventListener('touchstart',event => {
  touchStart = event.touches.length === 1 ? {x:event.touches[0].clientX,y:event.touches[0].clientY} : null;
}, {passive:true});
document.getElementById('reader-stage').addEventListener('touchend',event => {
  if (!touchStart || !event.changedTouches.length) return;
  const dx = event.changedTouches[0].clientX - touchStart.x, dy = event.changedTouches[0].clientY - touchStart.y;
  touchStart = null;
  if (Math.abs(dx) > 70 && Math.abs(dx) > Math.abs(dy) * 1.6 && !String(window.getSelection())) showPage(current + (dx < 0 ? 1 : -1));
}, {passive:true});
document.getElementById('reader-stage').addEventListener('touchcancel',() => { touchStart = null; }, {passive:true});
const pageFromHash = () => Number((location.hash.match(/^#page-(\\d+)$/) || [])[1]);
window.addEventListener('hashchange',() => { const number = pageFromHash(); if (validPage(number)) showPage(number); });
setTheme(get('theme') === 'night' ? 'night' : 'day');
const savedFont = Number(get('font'));
setFont(savedFont >= 16 && savedFont <= 30 ? savedFont : 19);
const hashPage = pageFromHash(), savedPage = Number(get('page'));
showPage(validPage(hashPage) ? hashPage : validPage(savedPage) ? savedPage : first,false);
})();
</script>
</body>
</html>
'''


def main():
    data = json.loads((ROOT / "sonny_blues_img_transcription.json").read_text(encoding="utf-8"))
    render(data)


if __name__ == "__main__":
    main()
