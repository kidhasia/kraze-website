"""Generates the static site in public/ from content/*.json and one shared header/footer.

Usage:  python3 build.py
Env overrides (handy for staging/tests, nothing secret):
  KRAZE_SITE_URL        production origin, e.g. https://example.lk
  KRAZE_FORM_ENDPOINT   form-service URL that accepts a JSON POST
"""
import json
import os
import sys
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).parent
PUB = ROOT / "public"
SITE = json.loads((ROOT / "content/site.json").read_text())
PROJECTS = json.loads((ROOT / "content/projects.json").read_text())["projects"]

NAME = SITE["name"]
SITE_URL = os.environ.get("KRAZE_SITE_URL", SITE["site_url"]).rstrip("/")
ENDPOINT = os.environ.get("KRAZE_FORM_ENDPOINT", SITE["form"]["endpoint"]).strip()
TURNSTILE = SITE["form"]["turnstile_site_key"].strip()
MIN_SECONDS = int(SITE["form"]["min_seconds"])
CONTACT = SITE["contact"]
SOCIALS = [s for s in SITE["socials"] if s["url"].strip()]
CATEGORIES = ["Video production", "Social media", "Branding & design"]

NAV = [("index.html", "Home"), ("work.html", "Work"), ("services.html", "Services"), ("about.html", "About")]
LOGO_ALT = NAME


def logo(cls="", eager=True):
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<span class="logo {cls}"><img src="images/kraze-logo.jpg" width="1080" height="1080" '
            f'alt="{e(LOGO_ALT)}" {load}></span>')


def contact_lines():
    out = []
    if CONTACT["email"]:
        out.append(f'<li><a href="mailto:{e(CONTACT["email"])}">{e(CONTACT["email"])}</a></li>')
    if CONTACT["phone"]:
        out.append(f'<li><a href="tel:{e(CONTACT["phone"])}">{e(CONTACT["phone"])}</a></li>')
    if CONTACT["whatsapp"]:
        out.append(f'<li><a href="{e(CONTACT["whatsapp"])}" rel="noopener">WhatsApp</a></li>')
    if CONTACT["location"]:
        out.append(f'<li>{e(CONTACT["location"])}</li>')
    return out


def social_links():
    return "".join(f'<li><a href="{e(s["url"])}" rel="noopener me" target="_blank">{e(s["label"])}'
                   f'<span class="sr-only"> (opens in a new tab)</span></a></li>' for s in SOCIALS)


def head(fname, title, desc):
    full_title = f"{title} | {NAME}" if fname != "index.html" else f"{NAME} | Creative production and digital marketing for DJs and artists"
    url = f"{SITE_URL}/{'' if fname == 'index.html' else fname}"
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#000000">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(NAME)}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{e(SITE_URL)}/images/kraze-logo.jpg">
<meta property="og:image:width" content="1080">
<meta property="og:image:height" content="1080">
<meta property="og:image:alt" content="{e(LOGO_ALT)}">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" sizes="32x32" href="images/favicon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="images/favicon-192.png">
<link rel="apple-touch-icon" href="images/apple-touch-icon.png">
<script>document.documentElement.className+=" js"</script>
<link rel="stylesheet" href="css/style.css">
</head>'''


def page(fname, title, desc, body, scripts=()):
    links = "".join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == fname else "", t) for h, t in NAV)
    cur = ' aria-current="page"' if fname == "contact.html" else ""
    flinks = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in NAV + [("contact.html", "Contact")])
    extra = ""
    cl = contact_lines()
    if cl:
        extra += f'<ul class="footer-list" aria-label="Contact details">{"".join(cl)}</ul>'
    if SOCIALS:
        extra += f'<ul class="footer-list" aria-label="Social media">{social_links()}</ul>'
    js = "".join(f'<script src="js/{s}" defer></script>' for s in ("nav.js", "fx.js") + tuple(scripts))
    return f'''{head(fname, title, desc)}
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap">
<a href="index.html" class="logo-link" aria-label="{e(NAME)}, home">{logo()}</a>
<button class="menu-btn" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="nav"><span></span></button>
<nav class="nav" id="nav" aria-label="Main">{links}<a class="btn"{cur} href="contact.html">Contact</a></nav>
</div></header>
<main id="main" tabindex="-1">
{body}
</main>
<footer class="site-footer"><div class="wrap">
<div class="footer-grid">
<div class="footer-brand"><a href="index.html" class="logo-link" aria-label="{e(NAME)}, home">{logo("logo--footer", eager=False)}</a><p>Creative production and digital marketing for {e(SITE["audience"])}.</p></div>
<nav aria-label="Footer"><ul class="footer-list">{flinks}</ul></nav>
{extra}
</div>
<div class="copy">&copy; 2026 {e(NAME)}. All rights reserved.</div>
</div></footer>
{js}
</body>
</html>
'''


# ---------- shared blocks ----------
def cta_band(heading="Ready to build your visual presence?", text="Tell us about your music and where you want to take it."):
    return (f'<section class="band"><div class="wrap reveal"><h2>{e(heading)}</h2><p class="lead">{e(text)}</p>'
            f'<div class="actions"><a class="btn" href="contact.html">Start a project</a></div></div></section>')


def workflow():
    items = "".join(f'<li class="step reveal" style="--d:{(i-1)*0.1:.1f}s"><span class="step-n" aria-hidden="true">{i}</span><h3>{e(s["title"])}</h3><p>{e(s["text"])}</p></li>'
                    for i, s in enumerate(SITE["workflow"], 1))
    return f'<section aria-labelledby="flow-h"><div class="wrap"><p class="eyebrow">How it works</p><h2 class="reveal" id="flow-h">Four simple steps</h2><ol class="steps">{items}</ol></div></section>'


def service_cards(detail=False):
    out = []
    for n, s in enumerate(SITE["services"]):
        pts = f'<ul class="ticks">{"".join(f"<li>{e(p)}</li>" for p in s["points"])}</ul>' if detail else ""
        out.append(f'<article class="card reveal" style="--d:{n*0.1:.1f}s"><h3>{e(s["title"])}</h3><p>{e(s["summary"])}</p>{pts}</article>')
    return f'<div class="grid">{"".join(out)}</div>'


def project_card(p, link=None, delay=0):
    cat = e(p["category"])
    ext = p["video"].startswith("http")
    dims = f' width="{int(p["cover_width"])}" height="{int(p["cover_height"])}"' if p["cover_width"] else ""
    if p["cover"]:
        media = f'<img src="{e(p["cover"])}"{dims} alt="Cover frame from {e(p["title"])}" loading="lazy">'
    else:
        media = '<div class="ph-media" role="img" aria-label="Placeholder cover image"><span>Cover image<br>placeholder</span></div>'
    if p.get("preview"):
        media += f'<video class="preview" src="{e(p["preview"])}" muted loop playsinline preload="none" aria-hidden="true" tabindex="-1"></video>'
    badge = '<span class="badge">Placeholder</span>' if p["placeholder"] else ""
    if link:
        media += f'<a class="media-hit" href="{link}" data-cursor="View" aria-label="See {e(p["title"])} on the Work page"></a>'
    elif p["video"] and not ext:
        media += (f'<button type="button" class="media-hit play" data-video="{e(p["video"])}" data-poster="{e(p["cover"])}" data-title="{e(p["title"])}" '
                  f'data-cursor="Play" aria-label="Play video: {e(p["title"])}"><span class="play-icon" aria-hidden="true"></span></button>')
    ext_link = (f'<a class="text-link" href="{e(p["video"])}" target="_blank" rel="noopener">Watch video'
                f'<span class="sr-only"> for {e(p["title"])} (opens in a new tab)</span></a>') if ext else ""
    return (f'<li class="project reveal" style="--d:{delay}s" data-category="{cat}"><article><div class="project-media">{media}{badge}</div>'
            f'<p class="tag">{e(p.get("client",""))}{" &middot; " if p.get("client") else ""}{cat}</p><h3>{e(p["title"])}</h3><p>{e(p["description"])}</p>{ext_link}</article></li>')


# ---------- pages ----------
def marquee():
    words = [x["title"] for x in SITE["services"]] + ["360\u00b0 service"]
    run = "".join(f"<span>{e(w)}</span>" for w in words)
    return f'<div class="marquee" aria-hidden="true"><div class="marquee-track">{run}{run}{run}{run}</div></div>'


def featured():
    real = [p for p in PROJECTS if not p["placeholder"]][:3] or PROJECTS[:3]
    cards = "".join(project_card(p, link="work.html", delay=i * 0.12) for i, p in enumerate(real))
    return (f'<section aria-labelledby="feat-h"><div class="wrap"><p class="eyebrow">Selected work</p><h2 class="reveal" id="feat-h">Recent video work</h2>'
            f'<ul class="projects projects--feat">{cards}</ul><p class="more"><a class="text-link" href="work.html">See all work</a></p></div></section>')


def home():
    return f'''<section class="hero"><span class="hero-word" aria-hidden="true">KRAZE</span><div class="wrap">
<p class="eyebrow">Creative production &amp; digital marketing</p>
<h1>Your sound deserves a screen presence to match.</h1>
<p class="lead">KrazE builds the video, content and brand around your music for {e(SITE["audience"])}, delivered as one joined-up 360&deg; service.</p>
<div class="actions"><a class="btn" href="contact.html">Start a project</a><a class="btn btn--ghost" href="work.html">See the work</a></div>
</div></section>
{marquee()}
<section aria-labelledby="s360-h"><div class="wrap">
<p class="eyebrow">The 360&deg; service</p>
<h2 class="reveal" id="s360-h">One team for everything people see</h2>
<p class="lead">Most artists juggle a videographer, a designer and someone to post. KrazE brings video production, social media management and artist branding together, so every release, set and announcement looks and feels like you.</p>
{service_cards()}
<p class="more"><a class="text-link" href="services.html">Explore the services</a></p>
</div></section>
{featured()}
{workflow()}
{cta_band()}'''


def work():
    used = [c for c in CATEGORIES if any(p["category"] == c for p in PROJECTS)]
    chips = "".join(f'<button type="button" class="chip" data-filter="{e(c)}" aria-pressed="false">{e(c)}</button>' for c in CATEGORIES)
    cards = "".join(project_card(p) for p in PROJECTS)
    note = ""
    if any(p["placeholder"] for p in PROJECTS):
        note = ('<p class="notice"><strong>Placeholder content.</strong> Items marked "Placeholder" are sample slots, not real client work. '
                'Add genuine projects in <code>content/projects.json</code>.</p>')
    return f'''<section class="hero hero--sm"><div class="wrap">
<p class="eyebrow">Work</p><h1>Selected work</h1>
<p class="lead">Video work for DJs and music artists.</p>
{note}
{('<div class="filters" role="group" aria-label="Filter projects by category"><button type="button" class="chip" data-filter="all" aria-pressed="true">All</button>' + chips + '</div>') if len(used) > 1 else ""}
<p class="sr-only" id="filter-status" role="status" aria-live="polite"></p>
<ul class="projects" id="projects">{cards}</ul>
<p class="empty" id="empty" hidden>No projects in this category yet.</p>
</div></section>
<dialog id="player" aria-label="Video player"><button type="button" class="player-close" aria-label="Close video">&times;</button><video controls playsinline preload="none"></video></dialog>
{cta_band("Want to see your music here?", "Start a project and we will plan it together.")}'''


def services():
    return f'''<section class="hero hero--sm"><div class="wrap">
<p class="eyebrow">Services</p><h1>Everything your music needs to be seen</h1>
<p class="lead">Three core services that work best together, built for {e(SITE["audience"])}.</p>
{service_cards(detail=True)}
</div></section>
<section aria-labelledby="pk-h"><div class="wrap">
<p class="eyebrow">360&deg; service</p><h2 id="pk-h">All of it, coordinated</h2>
<p class="lead">Choose one service or combine all three. In a 360&deg; engagement the video, the content calendar and the brand design are planned together, so everything points the same way. Tell us what you need and we will shape a plan around it.</p>
<div class="actions"><a class="btn" href="contact.html">Ask about a 360&deg; plan</a></div>
</div></section>
{workflow()}
{cta_band()}'''


def about():
    return f'''<section class="hero hero--sm"><div class="wrap">
<p class="eyebrow">About</p><h1>About KrazE</h1>
<p class="lead">Visuals by KrazE is a creative production and digital marketing service for {e(SITE["audience"])}. We turn music into video, content and branding that people remember.</p>
</div></section>
<section aria-labelledby="ab-h"><div class="wrap">
<h2 id="ab-h">What we believe</h2>
<div class="grid">
<article class="card"><h3>Music first</h3><p>Everything we make starts from the artist&rsquo;s sound and story.</p></article>
<article class="card"><h3>Consistent by design</h3><p>Video, social and branding are planned together so the whole presence feels like one.</p></article>
<article class="card"><h3>Clear communication</h3><p>A simple process, so you always know what is happening and what comes next.</p></article>
</div>
<p class="notice"><strong>Placeholder:</strong> add the KrazE story, team and background here once supplied.</p>
</div></section>
{cta_band("Let us talk about your music.", "Tell us where you are and where you want to go.")}'''


def contact():
    cl = contact_lines()
    if cl or SOCIALS:
        aside = '<h2 class="h3">Other ways to reach us</h2>'
        if cl:
            aside += f'<ul class="plain">{"".join(cl)}</ul>'
        if SOCIALS:
            aside += f'<ul class="plain">{social_links()}</ul>'
    else:
        aside = ('<p class="notice"><strong>Placeholder:</strong> business email, phone and social links have not been supplied yet. '
                 'Add them in <code>content/site.json</code>.</p>')
    action = f' action="{e(ENDPOINT)}" method="post"' if ENDPOINT else ""
    turnstile = ""
    if TURNSTILE:
        turnstile = (f'<div class="cf-turnstile" data-sitekey="{e(TURNSTILE)}"></div>'
                     '<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>')
    return f'''<section class="hero hero--sm"><div class="wrap contact-grid">
<div>
<p class="eyebrow">Contact</p><h1>Let&rsquo;s talk</h1>
<p class="lead">Tell us about your music and what you would like to create. Fields marked * are required.</p>
<div id="form-wrap" data-endpoint="{e(ENDPOINT)}" data-min-seconds="{MIN_SECONDS}">
<form id="contact-form" novalidate{action}>
<label for="f-name">Name *<input id="f-name" name="name" autocomplete="name" required aria-describedby="f-name-err"><span class="err" id="f-name-err" hidden></span></label>
<label for="f-email">Email *<input id="f-email" name="email" type="email" autocomplete="email" required aria-describedby="f-email-err"><span class="err" id="f-email-err" hidden></span></label>
<label for="f-msg">Message *<textarea id="f-msg" name="message" rows="6" required minlength="10" aria-describedby="f-msg-err"></textarea><span class="err" id="f-msg-err" hidden></span></label>
<div class="hp" aria-hidden="true"><label>Leave this field empty<input name="website" tabindex="-1" autocomplete="off"></label></div>
{turnstile}
<button class="btn" type="submit" id="f-submit">Send message</button>
<noscript><p class="notice">JavaScript is needed to send this form.</p></noscript>
</form>
<div id="form-status" class="status" role="status" aria-live="polite" tabindex="-1" hidden></div>
</div>
</div>
<aside aria-label="Contact details">{aside}</aside>
</div></section>'''


PAGES = {
    "index.html": ("Home", f"KrazE builds video, social media and branding for {SITE['audience']}, as one coordinated 360-degree creative service.", home, ()),
    "work.html": ("Work", "Video, social media and design projects from Visuals by KrazE for DJs and music artists in Sri Lanka.", work, ("work.js",)),
    "services.html": ("Services", "Video production, social media management and artist branding for DJs and music artists in Sri Lanka, delivered as a 360-degree service.", services, ()),
    "about.html": ("About", "About Visuals by KrazE, a creative production and digital marketing service for DJs and music artists in Sri Lanka.", about, ()),
    "contact.html": ("Contact", "Contact Visuals by KrazE to start a video, social media or branding project for your music.", contact, ("contact.js",)),
}

for f, (t, d, fn, js) in PAGES.items():
    (PUB / f).write_text(page(f, t, d, fn(), js))

urls = "".join(f"<url><loc>{SITE_URL}/{'' if f == 'index.html' else f}</loc></url>" for f in PAGES)
(PUB / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
(PUB / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")

print("built", ", ".join(PAGES), "+ sitemap.xml, robots.txt")
if "YOUR-DOMAIN" in SITE_URL:
    print("WARNING: site_url is still the placeholder; canonical, Open Graph and sitemap URLs need the real domain.", file=sys.stderr)
if not ENDPOINT:
    print("WARNING: form.endpoint is empty; the contact form will report that it is not connected.", file=sys.stderr)
