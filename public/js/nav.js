(function () {
  var b = document.querySelector('.menu-btn'), h = document.documentElement;
  if (!b) return;
  var mq = window.matchMedia('(min-width:769px)');
  function set(open, restoreFocus) {
    h.classList.toggle('menu-open', open);
    b.setAttribute('aria-expanded', String(open));
    b.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.body.style.overflow = open ? 'hidden' : '';
    if (!open && restoreFocus) b.focus();
  }
  b.addEventListener('click', function () { set(!h.classList.contains('menu-open')); });
  document.querySelectorAll('.nav a').forEach(function (a) { a.addEventListener('click', function () { set(false); }); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && h.classList.contains('menu-open')) set(false, true);
  });
  mq.addEventListener('change', function () { set(false); });
})();
