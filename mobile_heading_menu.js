/* Preserve existing controls and their event listeners while folding headings. */
(() => {
  'use strict';
  if (document.querySelector('.mobile-heading-menu')) return;
  let primary, companions = [], mobileOnly = [];
  const readerBar = document.querySelector('.reader-bar');
  const sidebar = document.querySelector('.sidebar');
  const topbar = document.querySelector('.wrap > .topbar');
  if (readerBar) {
    primary = readerBar;
    document.body.classList.add('mobile-menu-page-reader');
    mobileOnly = [...document.querySelectorAll('.reader-page .story-heading')];
  } else if (sidebar) {
    primary = sidebar;
    mobileOnly = [...document.querySelectorAll('.main > .hero')];
  } else if (topbar) {
    primary = topbar;
    let node = topbar.nextElementSibling;
    while (node && !node.classList.contains('bar') && node.tagName !== 'SECTION') {
      companions.push(node);
      node = node.nextElementSibling;
    }
  } else if (document.querySelector('body > .top')) {
    primary = document.querySelector('body > .top');
    const intro = document.querySelector('body > .intro');
    if (intro) companions.push(intro);
    document.body.classList.add('mobile-menu-scroll-reader');
  } else if (document.querySelector('.page > .page-nav')) {
    primary = document.querySelector('.page > .page-nav');
    mobileOnly = [...document.querySelectorAll('main > .article-header')];
  } else {
    primary = document.querySelector('body > header, main > header, .wrap > .hero, .page > .article-header');
    if (primary) {
      const next = primary.nextElementSibling;
      if (next && (next.tagName === 'NAV' || next.classList.contains('summary'))) companions.push(next);
    }
  }
  if (!primary) return;

  const title = document.querySelector('h1')?.innerText.replace(/\s+/g, ' ').trim()
    || primary.querySelector('strong')?.textContent.trim()
    || document.title.split('—')[0].trim();
  const menu = document.createElement('details');
  menu.className = 'mobile-heading-menu';
  menu.open = true;
  const toggle = document.createElement('summary');
  toggle.className = 'mobile-heading-toggle';
  toggle.setAttribute('aria-controls', 'mobile-heading-panel');
  const icon = document.createElement('span');
  icon.className = 'mobile-heading-icon';
  icon.setAttribute('aria-hidden', 'true');
  const label = document.createElement('span');
  label.className = 'mobile-heading-title';
  label.textContent = title;
  toggle.setAttribute('aria-label', 'Menu for ' + title);
  toggle.append(icon, label);
  const panel = document.createElement('div');
  panel.className = 'mobile-heading-panel';
  panel.id = 'mobile-heading-panel';
  primary.before(menu);
  menu.append(toggle, panel);
  panel.append(primary, ...companions);
  // Return first-page headings and tutorial introductions to their exact desktop
  // positions. Story paragraphs, audio controls, IDs and handlers stay intact.
  const origins = mobileOnly.map(node => {
    const marker = document.createComment('mobile heading position');
    node.before(marker);
    return {node, marker};
  });
  const mobile = matchMedia('(max-width:700px)');
  const audioControls = panel.querySelector('.audio-controls');
  const audio = audioControls?.querySelector('audio');
  let audioDock, audioOrigin, shell, mobilePlayer;
  if (audio) {
    audioOrigin = document.createComment('desktop audio controls position');
    audioControls.before(audioOrigin);
    shell = document.createElement('div');
    shell.className = 'mobile-heading-shell';
    audioDock = document.createElement('div');
    audioDock.className = 'mobile-audio-dock';
    menu.before(shell);
    shell.append(menu, audioDock);
    // Use ordinary HTML controls on phones. iOS native media controls can lose
    // their rendering when the containing menu or scrolling layout changes.
    mobilePlayer = document.createElement('div');
    mobilePlayer.className = 'mobile-audio-player';
    const playButton = document.createElement('button');
    playButton.type = 'button';
    const seek = document.createElement('input');
    seek.type = 'range';
    seek.min = '0'; seek.max = '1000'; seek.value = '0'; seek.step = '1';
    seek.setAttribute('aria-label', 'Narration position');
    const speed = document.createElement('select');
    speed.setAttribute('aria-label', 'Playback speed');
    for (const rate of [0.5, 0.75, 1, 1.25, 1.5, 2]) {
      const option = document.createElement('option');
      option.value = String(rate); option.textContent = rate + '×';
      speed.append(option);
    }
    const time = document.createElement('span');
    time.className = 'mobile-audio-time';
    const message = document.createElement('span');
    message.className = 'mobile-audio-message';
    message.setAttribute('role', 'status');
    mobilePlayer.append(playButton, seek, speed, time, message);
    audioControls.append(mobilePlayer);
    function clock(seconds) {
      if (!Number.isFinite(seconds)) return '–:––';
      return Math.floor(seconds / 60) + ':' + String(Math.floor(seconds % 60)).padStart(2, '0');
    }
    function updatePlayer() {
      const playing = !audio.paused && !audio.ended;
      playButton.textContent = playing ? '❚❚' : '▶';
      playButton.setAttribute('aria-label', playing ? 'Pause narration' : 'Play narration');
      const duration = audio.duration;
      seek.disabled = !Number.isFinite(duration) || duration <= 0;
      seek.value = seek.disabled ? '0' : String(Math.round(1000 * audio.currentTime / duration));
      seek.setAttribute('aria-valuetext', clock(audio.currentTime) + ' of ' + clock(duration));
      time.textContent = clock(audio.currentTime) + ' / ' + clock(duration);
      speed.value = String(audio.playbackRate);
    }
    playButton.addEventListener('click', () => {
      message.textContent = '';
      if (!audio.paused && !audio.ended) audio.pause();
      else {
        // Call play directly in the tap handler to retain iOS user activation.
        const request = audio.play();
        request?.catch(() => { message.textContent = 'Unable to play. Tap Play to try again.'; updatePlayer(); });
      }
    });
    seek.addEventListener('input', () => {
      if (!seek.disabled) audio.currentTime = Number(seek.value) * audio.duration / 1000;
      updatePlayer();
    });
    speed.addEventListener('change', () => { audio.playbackRate = Number(speed.value); });
    for (const event of ['play', 'playing', 'pause', 'ended', 'emptied', 'loadedmetadata', 'durationchange', 'timeupdate', 'seeked', 'ratechange']) {
      audio.addEventListener(event, updatePlayer);
    }
    audio.addEventListener('play', () => {
      close();
    });
    updatePlayer();
  }
  function reflect() {
    const expanded = menu.open;
    toggle.setAttribute('aria-expanded', String(expanded));
    icon.textContent = expanded ? '×' : '☰';
  }
  function restoreHeadings() { origins.forEach(({node, marker}) => marker.after(node)); }
  function restoreAudio() {
    if (audioOrigin) { audioOrigin.after(audioControls); audio.controls = true; }
  }
  function layout() {
    if (mobile.matches) origins.forEach(({node}) => panel.append(node));
    else restoreHeadings();
    if (audioDock) {
      if (mobile.matches) { audioDock.append(audioControls); audio.controls = false; }
      else restoreAudio();
    }
    menu.open = !mobile.matches;
    reflect();
  }
  function close(restoreFocus = false) {
    if (!mobile.matches || !menu.open) return;
    menu.open = false;
    reflect();
    if (restoreFocus) toggle.focus();
  }
  menu.addEventListener('toggle', reflect);
  mobile.addEventListener('change', layout);
  panel.addEventListener('submit', () => close(true));
  panel.addEventListener('play', () => close(true), true);
  panel.addEventListener('click', event => {
    if (event.target.closest('a, [data-part]')) close();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && mobile.matches && menu.open) { event.preventDefault(); close(true); }
  });
  document.addEventListener('pointerdown', event => {
    if (!menu.contains(event.target) && !audioDock?.contains(event.target)) close();
  });
  window.addEventListener('beforeprint', () => { restoreHeadings(); restoreAudio(); menu.open = true; reflect(); });
  window.addEventListener('afterprint', layout);
  layout();
})();
