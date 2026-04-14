/* ============================================================
   THE INQUISITIVECYNIC — main.js
   Theme toggle · Scroll animations · Sticky header
   ============================================================ */

(function () {
  'use strict';

  /* ─── THEME TOGGLE ─── */
  const html = document.documentElement;
  const toggle = document.querySelector('[data-theme-toggle]');

  // Determine initial theme from system preference
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  let currentTheme = prefersDark ? 'dark' : 'light';
  html.setAttribute('data-theme', currentTheme);

  const moonIcon = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
  const sunIcon  = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>`;

  if (toggle) {
    // Set initial icon
    toggle.innerHTML = currentTheme === 'dark' ? sunIcon : moonIcon;
    toggle.setAttribute('aria-label', `Switch to ${currentTheme === 'dark' ? 'light' : 'dark'} mode`);

    toggle.addEventListener('click', () => {
      currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', currentTheme);
      toggle.innerHTML = currentTheme === 'dark' ? sunIcon : moonIcon;
      toggle.setAttribute('aria-label', `Switch to ${currentTheme === 'dark' ? 'light' : 'dark'} mode`);
    });
  }

  /* ─── STICKY HEADER SHADOW ON SCROLL ─── */
  const header = document.querySelector('.site-header');
  if (header) {
    const onScroll = () => {
      if (window.scrollY > 20) {
        header.classList.add('is-scrolled');
      } else {
        header.classList.remove('is-scrolled');
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ─── SCROLL REVEAL ─── */
  // Add reveal class to target elements
  const revealSelectors = [
    '.about-text',
    '.about-accent',
    '.focus-card',
    '.note-card',
    '.connect-inner'
  ];

  revealSelectors.forEach((selector, selectorIndex) => {
    document.querySelectorAll(selector).forEach((el, i) => {
      el.classList.add('reveal');
      // Stagger cards within same type
      if (i === 1) el.classList.add('reveal-delay-1');
      if (i === 2) el.classList.add('reveal-delay-2');
      if (i === 3) el.classList.add('reveal-delay-3');
    });
  });

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.08, rootMargin: '0px 0px -40px 0px' }
  );

  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

  /* ─── SMOOTH SCROLL FOR NAV LINKS ─── */
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
      const targetId = link.getAttribute('href');
      if (targetId === '#') return;
      const target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

})();
