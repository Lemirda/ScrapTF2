// Main JS for demo site
// - Theme toggle with persistence
// - Copy to clipboard helper
// - Smooth in-page anchor scrolling
// - Dynamic footer year

(function() {
  const $ = (sel, ctx=document) => ctx.querySelector(sel);
  const $$ = (sel, ctx=document) => Array.from(ctx.querySelectorAll(sel));

  // Theme toggle
  const root = document.documentElement;
  const toggleBtn = $('#themeToggle');

  function applyTheme(next) {
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch(_) {}
  }

  toggleBtn?.addEventListener('click', () => {
    const current = root.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
  });

  // Config-driven links (assets/config.json)
  async function loadConfig() {
    try {
      const res = await fetch('./assets/config.json');
      if (!res.ok) return;
      const cfg = await res.json();
      const nodes = $$('[data-config]');
      for (const el of nodes) {
        const key = el.getAttribute('data-config');
        const val = cfg?.[key];
        if (!val) continue;
        if (el.tagName === 'A' || el.hasAttribute('href')) {
          el.setAttribute('href', val);
        } else {
          el.textContent = val;
        }
      }
    } catch (e) {
      console.warn('Config load failed:', e);
    }
  }
  loadConfig();

  // Smooth anchor scroll for same-page links
  $$('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const href = a.getAttribute('href');
      if (!href || href.length <= 1) return;
      const id = href.slice(1);
      const el = document.getElementById(id);
      if (el) {
        e.preventDefault();
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        history.pushState(null, '', `#${id}`);
      }
    });
  });

  // Reveal all immediately (no IntersectionObserver optimizations)
  try {
    const els = $$('.reveal');
    els.forEach(el => el.classList.add('in-view'));
  } catch (_) {}

  // Footer year
  const y = $('#year');
  if (y) y.textContent = String(new Date().getFullYear());
})();
