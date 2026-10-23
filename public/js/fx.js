(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = window.matchMedia('(hover:hover) and (pointer:fine)').matches;

  // Footer year
  document.querySelectorAll('[data-year]').forEach(function (n) { n.textContent = new Date().getFullYear(); });

  // Scroll reveal
  var els = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    els.forEach(function (el) { io.observe(el); });
  } else { els.forEach(function (el) { el.classList.add('in'); }); }

  // Header hides on scroll down, returns on scroll up
  var hdr = document.querySelector('.site-header'), last = window.scrollY, tick = false;
  window.addEventListener('scroll', function () {
    if (tick) return; tick = true;
    requestAnimationFrame(function () {
      var y = window.scrollY, open = document.documentElement.classList.contains('menu-open');
      hdr.classList.toggle('is-hidden', !open && y > last && y > 160);
      last = y; tick = false;
    });
  }, { passive: true });
  hdr.addEventListener('focusin', function () { hdr.classList.remove('is-hidden'); });

  // Hero parallax word
  var word = document.querySelector('.hero-word');
  if (word && !reduce) {
    window.addEventListener('scroll', function () {
      document.documentElement.style.setProperty('--py', Math.min(window.scrollY / 600, 1.5).toFixed(3));
    }, { passive: true });
  }

  if (!fine || reduce) return;

  // Magnetic buttons
  document.querySelectorAll('.btn').forEach(function (b) {
    b.addEventListener('mousemove', function (e) {
      var r = b.getBoundingClientRect();
      b.style.transform = 'translate(' + ((e.clientX - r.left - r.width / 2) * 0.18).toFixed(1) + 'px,' + ((e.clientY - r.top - r.height / 2) * 0.28).toFixed(1) + 'px)';
    });
    b.addEventListener('mouseleave', function () { b.style.transform = ''; });
  });

  // Custom cursor with contextual label
  var c = document.createElement('div'); c.className = 'cursor'; c.setAttribute('aria-hidden', 'true'); c.innerHTML = '<span></span>';
  document.body.appendChild(c);
  var lab = c.firstChild, x = 0, y = 0, cx = 0, cy = 0;
  document.addEventListener('mousemove', function (e) { x = e.clientX; y = e.clientY; c.classList.add('on'); });
  document.addEventListener('mouseleave', function () { c.classList.remove('on'); });
  (function loop() { cx += (x - cx) * 0.2; cy += (y - cy) * 0.2; c.style.transform = 'translate(' + cx.toFixed(1) + 'px,' + cy.toFixed(1) + 'px)'; requestAnimationFrame(loop); })();
  document.addEventListener('mouseover', function (e) {
    var t = e.target.closest && e.target.closest('[data-cursor]');
    if (t) { lab.textContent = t.getAttribute('data-cursor'); c.classList.add('big'); } else c.classList.remove('big');
  });

  // Hover-to-preview project videos
  document.querySelectorAll('.project video').forEach(function (v) {
    var li = v.closest('.project');
    li.addEventListener('mouseenter', function () { v.play().catch(function () {}); });
    li.addEventListener('mouseleave', function () { v.pause(); v.currentTime = 0; });
  });
})();
