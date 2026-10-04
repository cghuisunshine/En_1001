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
  function reflect() {
    const expanded = menu.open;
    toggle.setAttribute('aria-expanded', String(expanded));
    icon.textContent = expanded ? '×' : '☰';
  }
  function restoreHeadings() { origins.forEach(({node, marker}) => marker.after(node)); }
  function layout() {
    if (mobile.matches) origins.forEach(({node}) => panel.append(node));
    else restoreHeadings();
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
    if (!menu.contains(event.target)) close();
  });
  window.addEventListener('beforeprint', () => { restoreHeadings(); menu.open = true; reflect(); });
  window.addEventListener('afterprint', layout);
  layout();
})();
