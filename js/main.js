/* ============================================================
   THE INQUISITIVECYNIC — main.js
   Light theme only · Scroll animations · Sticky header
   ============================================================ */

(function () {
  'use strict';

  /* ─── FORCE LIGHT THEME (dark mode removed) ─── */
  document.documentElement.setAttribute('data-theme', 'light');

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
  const revealSelectors = [
    '.about-text',
    '.about-accent',
    '.focus-card',
    '.note-card',
    '.connect-inner'
  ];

  revealSelectors.forEach((selector) => {
    document.querySelectorAll(selector).forEach((el, i) => {
      el.classList.add('reveal');
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
