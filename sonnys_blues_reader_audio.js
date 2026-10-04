/* Per-page narration and synchronized word highlighting for printed pages 57–79. */
'use strict';
window.initSonnysBluesAudio = function ({ getCurrentPage, showPage, lastPage }) {
  const audio = document.getElementById('story-audio');
  const checkbox = document.getElementById('highlight-words');
  const status = document.getElementById('audio-status');
  const data = window.SONNYS_BLUES_AUDIO || {};
  const prepared = new Map();
  let audioPage = null, words = [], active = null, frame = 0;
  try { checkbox.checked = localStorage.getItem('sonny-blues-img-highlight') !== 'false'; } catch {}

  function clear() {
    if (active) active.classList.remove('is-speaking');
    active = null;
  }

  function prepare(number) {
    if (prepared.has(number)) return prepared.get(number);
    const paragraphs = [...document.getElementById('page-' + number).querySelectorAll('.story-paragraph')];
    const timings = data[number];
    if (!timings || paragraphs.length !== timings.length) throw new Error('Missing page timings');
    // Superscript note links stay intact and are excluded from narration offsets.
    const sources = paragraphs.map(paragraph => {
      const nodes = [];
      const walker = document.createTreeWalker(paragraph, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walker.nextNode())) if (!node.parentElement.closest('sup')) nodes.push(node);
      return { nodes, text:nodes.map(item => item.textContent).join('') };
    });
    if (sources.some((source, index) => source.text !== timings[index].text)) throw new Error('Page text and narration differ');
    const result = [];
    timings.forEach((timing, index) => {
      const timedWords = timing.words.map(([start, end, first, last]) => ({start, end, first, last, elements:[]}));
      let offset = 0;
      sources[index].nodes.forEach(node => {
        const text = node.textContent;
        const fragment = document.createDocumentFragment();
        let cursor = 0;
        for (const word of timedWords) {
          const first = Math.max(0, word.first - offset), last = Math.min(text.length, word.last - offset);
          if (first >= last) continue;
          if (first < cursor) throw new Error('Overlapping word timings');
          fragment.append(document.createTextNode(text.slice(cursor, first)));
          const span = document.createElement('span');
          span.className = 'tts-word';
          span.textContent = text.slice(first, last);
          fragment.append(span);
          word.elements.push(span);
          cursor = last;
        }
        fragment.append(document.createTextNode(text.slice(cursor)));
        node.replaceWith(fragment);
        offset += text.length;
      });
      result.push(...timedWords);
    });
    prepared.set(number, result);
    return result;
  }

  function paint() {
    if (audio.paused || audio.ended || !checkbox.checked || audioPage !== getCurrentPage()) { clear(); return; }
    const time = audio.currentTime;
    let low = 0, high = words.length;
    while (low < high) {
      const middle = (low + high) >> 1;
      if (words[middle].start <= time) low = middle + 1;
      else high = middle;
    }
    const word = words[low - 1];
    const next = word && time <= word.end + .06 ? word.elements[0] : null;
    if (next === active) return;
    clear();
    if (!next) return;
    active = next;
    active.classList.add('is-speaking');
    const bounds = active.getBoundingClientRect();
    const viewport = document.getElementById('page-' + audioPage).getBoundingClientRect();
    if (bounds.top < viewport.top + 24 || bounds.bottom > viewport.bottom - 24) {
      active.scrollIntoView({block:'center', behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'});
    }
  }

  function tick() {
    paint();
    if (!audio.paused && !audio.ended) frame = requestAnimationFrame(tick);
  }

  function setPage(number) {
    if (number === audioPage) return;
    const resume = audioPage !== null && !audio.paused && !audio.ended;
    audio.pause();
    cancelAnimationFrame(frame);
    clear();
    audioPage = number;
    status.textContent = '';
    try { words = prepare(number); }
    catch (error) { words = []; status.textContent = 'Word highlighting is unavailable for this page.'; console.warn(error); }
    audio.setAttribute('aria-label', 'Read printed page ' + number + ' aloud');
    audio.src = 'sonnys_blues_audio/page-' + number + '.mp3';
    audio.load();
    if (resume) audio.play().catch(() => {});
  }

  audio.addEventListener('play', () => {
    cancelAnimationFrame(frame);
    tick();
  });
  audio.addEventListener('pause', () => { cancelAnimationFrame(frame); clear(); });
  audio.addEventListener('timeupdate', paint);
  audio.addEventListener('seeked', paint);
  audio.addEventListener('error', () => { clear(); status.textContent = 'Audio for page ' + audioPage + ' could not load. Keep the sonnys_blues_audio folder beside this HTML file.'; });
  audio.addEventListener('ended', () => {
    cancelAnimationFrame(frame);
    clear();
    if (getCurrentPage() < lastPage) { showPage(getCurrentPage() + 1); audio.play().catch(() => {}); }
  });
  checkbox.addEventListener('change', () => {
    try { localStorage.setItem('sonny-blues-img-highlight', String(checkbox.checked)); } catch {}
    paint();
  });
  return {setPage};
};
