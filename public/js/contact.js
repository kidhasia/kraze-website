(function () {
  var wrap = document.getElementById('form-wrap'), form = document.getElementById('contact-form');
  if (!wrap || !form) return;
  var endpoint = wrap.getAttribute('data-endpoint'), minSeconds = +wrap.getAttribute('data-min-seconds') || 0;
  var status = document.getElementById('form-status'), btn = document.getElementById('f-submit');
  var loaded = Date.now(), sending = false;
  var fields = { name: 'Please enter your name.', email: 'Please enter a valid email address.', message: 'Please enter a message of at least 10 characters.' };

  function err(el) { return document.getElementById(el.id + '-err'); }
  function setErr(el, msg) {
    var s = err(el);
    s.textContent = msg || ''; s.hidden = !msg;
    if (msg) el.setAttribute('aria-invalid', 'true'); else el.removeAttribute('aria-invalid');
  }
  function check(el) {
    var v = el.value.trim(), bad = false;
    if (el.name === 'email') bad = !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
    else if (el.name === 'message') bad = v.length < 10;
    else bad = !v;
    setErr(el, bad ? fields[el.name] : '');
    return !bad;
  }
  function show(msg, kind) {
    status.hidden = false; status.className = 'status status--' + kind; status.textContent = msg;
    status.setAttribute('role', kind === 'error' ? 'alert' : 'status');
  }
  ['name', 'email', 'message'].forEach(function (n) {
    var el = form.elements[n];
    el.addEventListener('blur', function () { if (el.value) check(el); });
    el.addEventListener('input', function () { if (el.hasAttribute('aria-invalid')) check(el); });
  });

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    if (sending) return;
    var first = null;
    ['name', 'email', 'message'].forEach(function (n) { var el = form.elements[n]; if (!check(el) && !first) first = el; });
    if (first) { show('Please fix the highlighted fields and try again.', 'error'); first.focus(); return; }
    if (form.elements.website.value) { status.hidden = true; return; } // honeypot: bots only, no request sent
    if (!endpoint) { show('The contact form is not connected yet, so your message was not sent. Please use another way to reach us.', 'error'); return; }
    if ((Date.now() - loaded) / 1000 < minSeconds) { show('Please wait a moment and press send again.', 'error'); return; }

    sending = true; btn.disabled = true; btn.textContent = 'Sending…'; form.setAttribute('aria-busy', 'true');
    show('Sending your message…', 'info');
    var data = {};
    new FormData(form).forEach(function (v, k) { if (k !== 'website') data[k] = v; });
    var ctl = new AbortController(), t = setTimeout(function () { ctl.abort(); }, 12000);
    fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(data), signal: ctl.signal })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (o) {
        if (!o.ok || o.j.success === false || o.j.error) throw new Error('rejected');
        form.hidden = true;
        show('Thank you. Your message has been sent.', 'success');
        status.focus();
      })
      .catch(function () {
        show('Sorry, your message could not be sent. Please check your connection and try again.', 'error');
      })
      .then(function () {
        clearTimeout(t); sending = false; form.removeAttribute('aria-busy');
        btn.disabled = false; btn.textContent = 'Send message';
      });
  });
})();
