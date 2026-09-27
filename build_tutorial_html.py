#!/usr/bin/env python3
"""Build a standalone HTML study page from the ENGL 1001 Markdown guide."""

from __future__ import annotations

import html
import re
import subprocess
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "ENGL1001_7_day_exam_tutorial.md"
OUTPUT = ROOT / "ENGL1001_7_day_exam_tutorial.html"


def main() -> None:
    result = subprocess.run(
        ["pandoc", "-f", "gfm+raw_html", "-t", "html5", str(SOURCE)],
        check=True,
        capture_output=True,
        text=True,
    )
    body = result.stdout
    body = re.sub(r"^<h1\b[^>]*>.*?</h1>\s*", "", body, count=1, flags=re.S)

    sections = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body, flags=re.S)
    toc = "\n".join(
        f'<a href="#{html.escape(sid)}">{re.sub(r"<[^>]+>", "", title)}</a>'
        for sid, title in sections
    )
    modules = "\n".join(
        f'<a href="{quote(path.name)}">Module {n}</a>'
        for n, path in enumerate(sorted(ROOT.glob("Overview _ Module *.mhtml")), 1)
    )

    page = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>ENGL 1001 · Seven-day exam tutorial</title>
<style>
  :root { --bg:#f5f2ec; --paper:#fffefa; --ink:#263238; --muted:#627079; --line:#ddd7cc; --accent:#174f50; --accent-soft:#e4f1ed; --warm:#bd7746; --shadow:0 12px 30px #202b2911; }
  :root[data-theme="dark"] { --bg:#182123; --paper:#233032; --ink:#eef2ed; --muted:#b1c0bd; --line:#3e5050; --accent:#8bd1c3; --accent-soft:#294a48; --warm:#e6aa7d; --shadow:0 12px 30px #0003; }
  * { box-sizing:border-box; }
  html { scroll-behavior:smooth; }
  body { margin:0; background:var(--bg); color:var(--ink); font:16px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
  a { color:var(--accent); text-underline-offset:3px; }
  a:hover { text-decoration-thickness:2px; }
  button,input { font:inherit; }
  button { cursor:pointer; }
  :focus-visible { outline:3px solid var(--warm); outline-offset:3px; }
  .skip { position:absolute; left:-9999px; top:10px; z-index:100; background:var(--paper); padding:8px 12px; }
  .skip:focus { left:10px; }
  .shell { display:grid; grid-template-columns:260px minmax(0,1fr); max-width:1500px; margin:auto; }
  .sidebar { position:sticky; top:0; height:100vh; overflow:auto; padding:28px 18px 32px; border-right:1px solid var(--line); }
  .brand { font-size:.76rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; color:var(--warm); }
  .sidebar h2 { font-size:1.45rem; line-height:1.2; margin:10px 0 18px; }
  .sidebar nav { display:grid; gap:2px; margin:24px 0; }
  .sidebar nav a { display:block; padding:7px 10px; border-radius:8px; color:var(--muted); text-decoration:none; font-size:.89rem; line-height:1.3; }
  .sidebar nav a:hover,.sidebar nav a[aria-current="true"] { color:var(--accent); background:var(--accent-soft); }
  .sidebar label { display:block; font-size:.79rem; font-weight:750; margin-bottom:6px; }
  .sidebar input[type="search"] { width:100%; padding:9px 10px; border:1px solid var(--line); border-radius:9px; background:var(--paper); color:var(--ink); }
  .side-actions { display:flex; gap:8px; flex-wrap:wrap; margin-top:16px; }
  .side-actions button { border:1px solid var(--line); border-radius:8px; padding:7px 10px; color:var(--ink); background:var(--paper); font-size:.82rem; }
  .sidebar .tip { color:var(--muted); font-size:.78rem; margin-top:20px; }
  .main { min-width:0; padding:0 clamp(20px,4vw,70px) 70px; }
  .hero { padding:42px 0 25px; border-bottom:1px solid var(--line); }
  .eyebrow { margin:0 0 9px; font-size:.78rem; font-weight:800; letter-spacing:.13em; text-transform:uppercase; color:var(--warm); }
  h1 { max-width:900px; margin:0; font:700 clamp(2rem,4.2vw,3.5rem)/1.09 Georgia,"Times New Roman",serif; letter-spacing:-.025em; }
  .hero p { max-width:860px; margin:15px 0 0; color:var(--muted); }
  .stats { display:flex; flex-wrap:wrap; gap:10px; margin-top:24px; }
  .stat { border:1px solid var(--line); border-radius:999px; padding:6px 11px; background:var(--paper); font-size:.82rem; font-weight:700; }
  .tracker { margin:25px 0 30px; padding:20px 22px; background:var(--paper); border:1px solid var(--line); border-radius:15px; box-shadow:var(--shadow); }
  .tracker-head { display:flex; align-items:baseline; justify-content:space-between; gap:14px; }
  .tracker h2 { margin:0; font-size:1.12rem; }
  .tracker #progressText { color:var(--muted); font-size:.85rem; }
  .progress { height:8px; margin:13px 0 17px; border-radius:99px; background:var(--line); overflow:hidden; }
  .progress span { display:block; width:0%; height:100%; background:var(--accent); transition:width .2s; }
  .day-checks { display:flex; flex-wrap:wrap; gap:8px; }
  .day-checks label { display:flex; gap:7px; align-items:center; padding:7px 10px; border:1px solid var(--line); border-radius:9px; font-size:.85rem; cursor:pointer; }
  .day-checks label:has(input:checked) { border-color:var(--accent); background:var(--accent-soft); }
  input[type="checkbox"] { accent-color:var(--accent); width:1rem; height:1rem; }
  .resources { margin:0 0 26px; padding:17px 20px; border-left:4px solid var(--warm); background:var(--paper); border-radius:0 12px 12px 0; }
  .resources strong { display:block; margin-bottom:7px; }
  .module-links { display:flex; flex-wrap:wrap; gap:8px 13px; }
  .module-links a { font-size:.88rem; }
  .content { max-width:1020px; }
  .content > h2 { scroll-margin-top:25px; margin:43px 0 17px; padding-bottom:8px; border-bottom:1px solid var(--line); font:700 clamp(1.5rem,2.3vw,2rem)/1.2 Georgia,"Times New Roman",serif; }
  .content h2:first-child { margin-top:24px; }
  .content h3 { margin:30px 0 10px; color:var(--accent); font-size:1.22rem; line-height:1.3; }
  .content h4 { margin:22px 0 8px; font-size:1.03rem; line-height:1.35; }
  .content p { margin:0 0 15px; }
  .content ul,.content ol { padding-left:1.45rem; margin:0 0 19px; }
  .content li { margin:5px 0; }
  .content table { display:block; overflow-x:auto; width:100%; margin:18px 0 23px; border:1px solid var(--line); border-radius:12px; border-spacing:0; background:var(--paper); box-shadow:var(--shadow); }
  .content thead { background:var(--accent-soft); }
  .content th,.content td { min-width:180px; padding:12px 14px; border-right:1px solid var(--line); border-bottom:1px solid var(--line); text-align:left; vertical-align:top; font-size:.91rem; line-height:1.48; }
  .content th:last-child,.content td:last-child { border-right:0; }
  .content tr:last-child td { border-bottom:0; }
  .content th { font-weight:800; color:var(--accent); }
  .content table:nth-of-type(1) th:first-child,.content table:nth-of-type(1) td:first-child { min-width:155px; }
  .content table:nth-of-type(2) th:first-child,.content table:nth-of-type(2) td:first-child { min-width:245px; }
  .content details { margin:14px 0 20px; padding:12px 16px; background:var(--accent-soft); border-radius:10px; }
  .content summary { cursor:pointer; font-weight:750; color:var(--accent); }
  .content details p { margin:12px 0 0; }
  .content code { padding:2px 4px; background:var(--accent-soft); border-radius:4px; }
  .content strong { font-weight:750; }
  .content li input[type="checkbox"] { margin-right:8px; vertical-align:-2px; }
  .content li label { cursor:pointer; }
  .content li:has(input:checked) { color:var(--muted); }
  .footer { margin-top:50px; padding:20px 0; border-top:1px solid var(--line); color:var(--muted); font-size:.84rem; }
  [hidden] { display:none !important; }
  @media (max-width:850px) { .shell { display:block; } .sidebar { position:relative; height:auto; overflow:visible; border-right:0; border-bottom:1px solid var(--line); padding:15px 20px; } .sidebar h2,.sidebar .tip { display:none; } .sidebar nav { display:flex; overflow-x:auto; gap:4px; margin:12px 0 0; white-space:nowrap; } .sidebar nav a { flex:none; } .side-actions { position:absolute; top:10px; right:20px; margin:0; } .sidebar label { display:none; } .sidebar input[type="search"] { max-width:330px; } .hero { padding-top:30px; } .main { padding-bottom:35px; } }
  @media (max-width:480px) { .sidebar input[type="search"] { max-width:170px; } .side-actions button { padding:7px; } .hero p { font-size:.94rem; } .tracker { padding:16px; } .content th,.content td { min-width:230px; } }
  @media print { :root { --bg:#fff; --paper:#fff; --ink:#000; --muted:#333; --line:#bbb; --accent:#000; --accent-soft:#eee; } .sidebar,.tracker,.resources,.skip { display:none !important; } .shell { display:block; } .main { padding:0; } .hero { padding:0 0 10px; } .content > h2 { break-after:avoid; margin-top:25px; } .content table { box-shadow:none; overflow:visible; } .content tr { break-inside:avoid; } .content details:not([open]) > *:not(summary) { display:block; } a { color:#000; text-decoration:none; } }
</style>
</head>
<body>
<a class="skip" href="#main">Skip to tutorial</a>
<div class="shell">
  <aside class="sidebar" aria-label="Tutorial navigation">
    <div class="brand">TRU · ENGL 1001</div>
    <h2>Study guide</h2>
    <label for="search">Find a topic or story</label>
    <input id="search" type="search" placeholder="Search this page…" autocomplete="off">
    <nav id="toc" aria-label="Sections">__TOC__</nav>
    <div class="side-actions"><button id="themeBtn" type="button" aria-label="Switch colour theme">◐ Theme</button><button id="printBtn" type="button">Print</button></div>
    <p class="tip">Tip: use the seven-day tracker to save your progress on this device.</p>
  </aside>
  <main class="main" id="main">
    <header class="hero">
      <p class="eyebrow">One-week intensive · final exam prep</p>
      <h1>ENGL 1001<br>Seven-day tutorial</h1>
      <p>Read the stories and novel, learn the seven literary concepts, then practise the three exam parts under the clock.</p>
      <div class="stats"><span class="stat">7 study days</span><span class="stat">13 short stories</span><span class="stat">1 novel</span><span class="stat">3-hour practice exam</span></div>
    </header>
    <section class="tracker" aria-label="Seven-day progress tracker">
      <div class="tracker-head"><h2>Daily progress</h2><span id="progressText">0 of 7 days complete</span></div>
      <div class="progress" role="progressbar" aria-label="Study progress" aria-valuemin="0" aria-valuemax="7" aria-valuenow="0"><span id="progressFill"></span></div>
      <div class="day-checks">__DAY_CHECKS__</div>
    </section>
    <aside class="resources"><strong>Course module overviews</strong><div class="module-links">__MODULES__</div></aside>
    <aside class="resources" aria-label="Writing examples"><strong>Writing examples</strong><a href="heic_essays.html">Read 14 transcribed essays and passage commentaries</a></aside>
    <article class="content" id="tutorial">__BODY__</article>
    <footer class="footer">Based on the local course overviews, exam instructions, practice exam, answer key, and story readers. Check Moodle for current assignment prompts and exam arrangements.</footer>
  </main>
</div>
<script>
(() => {
  const store = {
    get(key) { try { return localStorage.getItem(key); } catch { return null; } },
    set(key, value) { try { localStorage.setItem(key, value); } catch {} }
  };
  const root = document.documentElement;
  const themeBtn = document.getElementById('themeBtn');
  const savedTheme = store.get('engl1001-theme');
  if (savedTheme === 'dark' || savedTheme === 'light') root.dataset.theme = savedTheme;
  themeBtn.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    store.set('engl1001-theme', root.dataset.theme);
  });
  document.getElementById('printBtn').addEventListener('click', () => window.print());

  const days = [...document.querySelectorAll('.day-checks input')];
  const checklist = [...document.querySelectorAll('.content input[type="checkbox"]')];
  [...days, ...checklist].forEach((box, index) => {
    const key = 'engl1001-check-' + index;
    box.checked = store.get(key) === '1';
    box.addEventListener('change', () => { store.set(key, box.checked ? '1' : '0'); updateProgress(); });
  });
  function updateProgress() {
    const done = days.filter(box => box.checked).length;
    document.getElementById('progressText').textContent = `${done} of 7 days complete`;
    document.getElementById('progressFill').style.width = `${done / 7 * 100}%`;
    document.querySelector('.progress').setAttribute('aria-valuenow', String(done));
  }
  updateProgress();

  const search = document.getElementById('search');
  const article = document.getElementById('tutorial');
  const headings = [...article.querySelectorAll('h2')];
  const sections = headings.map((heading, index) => {
    const nodes = [];
    let node = heading;
    const next = headings[index + 1];
    while (node && node !== next) { nodes.push(node); node = node.nextElementSibling; }
    return { heading, nodes, text: nodes.map(n => n.textContent).join(' ').toLowerCase() };
  });
  search.addEventListener('input', () => {
    const query = search.value.trim().toLowerCase();
    sections.forEach(section => {
      const show = !query || section.text.includes(query);
      section.nodes.forEach(node => { node.hidden = !show; });
      const nav = document.querySelector(`#toc a[href="#${section.heading.id}"]`);
      if (nav) nav.hidden = !show;
    });
  });
  search.addEventListener('keydown', event => {
    if (event.key === 'Escape') { search.value = ''; search.dispatchEvent(new Event('input')); search.blur(); }
  });
  document.addEventListener('keydown', event => {
    if (event.key === '/' && event.target.tagName !== 'INPUT' && event.target.tagName !== 'TEXTAREA') {
      event.preventDefault(); search.focus();
    }
  });
  document.querySelectorAll('a[href^="http"]').forEach(link => {
    link.target = '_blank'; link.rel = 'noopener noreferrer';
  });
})();
</script>
</body>
</html>
'''
    checks = "\n".join(
        f'<label><input type="checkbox" aria-label="Day {n} complete">Day {n}</label>'
        for n in range(1, 8)
    )
    page = page.replace("__TOC__", toc)
    page = page.replace("__DAY_CHECKS__", checks)
    page = page.replace("__MODULES__", modules)
    page = page.replace("__BODY__", body)
    OUTPUT.write_text(page, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
