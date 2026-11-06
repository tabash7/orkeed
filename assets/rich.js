// Rich articles: reveal on scroll and saved checklist ticks. No dependencies.
(function () {
  const root = document.documentElement;
  const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function setupReveal() {
    const items = Array.from(document.querySelectorAll('.rich-reveal'));
    const showAll = () => items.forEach((item) => item.classList.add('is-visible'));
    if (reduced || !('IntersectionObserver' in window)) {
      showAll();
      root.classList.add('rich-js');
      return;
    }
    // Items on screen or already scrolled past (e.g. opened at #faq) stay visible.
    items.forEach((item) => {
      const box = item.getBoundingClientRect();
      if (box.top < window.innerHeight) item.classList.add('is-visible');
    });
    root.classList.add('rich-js');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting && entry.boundingClientRect.top > 0) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
    items.forEach((item) => {
      if (!item.classList.contains('is-visible')) observer.observe(item);
    });
  }

  function setupChecklists() {
    const boxes = Array.from(document.querySelectorAll('input[data-rich-check]'));
    if (!boxes.length) return;
    const key = 'rich-checklist:' + window.location.pathname;
    let saved = {};
    try {
      saved = JSON.parse(window.localStorage.getItem(key) || '{}') || {};
    } catch (error) {
      saved = {};
    }
    boxes.forEach((box, index) => {
      if (saved[index]) box.checked = true;
      box.addEventListener('change', () => {
        if (box.checked) saved[index] = true;
        else delete saved[index];
        try {
          window.localStorage.setItem(key, JSON.stringify(saved));
        } catch (error) {
          // Storage can be blocked (private mode); ticking still works for this visit.
        }
      });
    });
  }

  function start() {
    setupReveal();
    setupChecklists();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
