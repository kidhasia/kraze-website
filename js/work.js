(function () {
  var chips = document.querySelectorAll('.chip'), items = document.querySelectorAll('.project');
  var status = document.getElementById('filter-status'), empty = document.getElementById('empty');
  function apply(cat) {
    var n = 0;
    items.forEach(function (li) {
      var show = cat === 'all' || li.getAttribute('data-category') === cat;
      li.hidden = !show; if (show) n++;
    });
    chips.forEach(function (c) { c.setAttribute('aria-pressed', String(c.getAttribute('data-filter') === cat)); });
    empty.hidden = n !== 0;
    status.textContent = n + (n === 1 ? ' project' : ' projects') + ' shown' + (cat === 'all' ? '' : ' in ' + cat);
  }
  chips.forEach(function (c) { c.addEventListener('click', function () { apply(c.getAttribute('data-filter')); }); });

  // Video player dialog
  var dlg = document.getElementById('player');
  if (!dlg || !dlg.showModal) return;
  var vid = dlg.querySelector('video'), opener = null;
  document.querySelectorAll('.media-hit.play').forEach(function (b) {
    b.addEventListener('click', function () {
      opener = b; vid.src = b.getAttribute('data-video'); vid.poster = b.getAttribute('data-poster') || '';
      dlg.setAttribute('aria-label', 'Video: ' + b.getAttribute('data-title'));
      dlg.showModal(); vid.play().catch(function () {});
    });
  });
  function stop() { vid.pause(); vid.removeAttribute('src'); vid.load(); if (opener) opener.focus(); }
  dlg.addEventListener('close', stop);
  dlg.querySelector('.player-close').addEventListener('click', function () { dlg.close(); });
  dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
})();
