"""Static checks on public/: links, assets, ids, tags, SEO and image attributes. Usage: python3 check.py"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

PUB = Path(__file__).parent / "public"
VOID = {"meta", "link", "img", "input", "br", "hr"}
problems = []


class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.stack = []; s.ids = []; s.refs = []; s.imgs = []; s.meta = {}; s.title = ""; s.in_title = False; s.h1 = 0; s.labels = []; s.inputs = []

    def handle_starttag(s, tag, a):
        a = dict(a)
        if tag not in VOID: s.stack.append(tag)
        if "id" in a: s.ids.append(a["id"])
        if tag == "title": s.in_title = True
        if tag == "h1": s.h1 += 1
        if tag == "meta":
            k = a.get("name") or a.get("property")
            if k: s.meta[k] = a.get("content", "")
        for k in ("href", "src"):
            if k in a and tag != "meta": s.refs.append((tag, a[k]))
        if tag == "img": s.imgs.append(a)
        if tag == "label" and "for" in a: s.labels.append(a["for"])
        if tag in ("input", "textarea") and a.get("type") != "hidden" and "id" in a: s.inputs.append(a["id"])

    def handle_endtag(s, tag):
        if tag == "title": s.in_title = False
        if tag in VOID: return
        if not s.stack or s.stack[-1] != tag: problems.append(f"{s.name}: unbalanced </{tag}> (open: {s.stack[-3:]})")
        else: s.stack.pop()

    def handle_data(s, d):
        if s.in_title: s.title += d


titles, descs = {}, {}
for f in sorted(PUB.glob("*.html")):
    p = P(); p.name = f.name; p.feed(f.read_text())
    if p.stack: problems.append(f"{f.name}: unclosed tags {p.stack}")
    if len(p.ids) != len(set(p.ids)): problems.append(f"{f.name}: duplicate ids")
    if p.h1 != 1: problems.append(f"{f.name}: expected one h1, found {p.h1}")
    for k in ("description", "og:title", "og:description", "og:url", "og:image"):
        if not p.meta.get(k): problems.append(f"{f.name}: missing {k}")
    titles.setdefault(p.title, []).append(f.name); descs.setdefault(p.meta.get("description"), []).append(f.name)
    for tag, ref in p.refs:
        if re.match(r"(https?:|mailto:|tel:|#)", ref): 
            if ref.startswith("#") and ref[1:] not in p.ids: problems.append(f"{f.name}: dead anchor {ref}")
            continue
        if not (PUB / ref.split("#")[0]).exists(): problems.append(f"{f.name}: broken {tag} -> {ref}")
    for i in p.imgs:
        if "alt" not in i: problems.append(f"{f.name}: img without alt {i.get('src')}")
        if not (i.get("width") and i.get("height")) and not i.get("src", "").startswith("images/projects"): problems.append(f"{f.name}: img without dimensions {i.get('src')}")
    for i in p.inputs:
        if i not in p.ids or False: pass
    for l in p.labels:
        if l not in p.ids: problems.append(f"{f.name}: label for={l} has no target")
for k, v in {**titles, **{"desc:" + str(d): n for d, n in descs.items()}}.items():
    if len(v) > 1: problems.append(f"duplicate title/description {k!r}: {v}")
for need in ("sitemap.xml", "robots.txt", "images/favicon-32.png", "images/apple-touch-icon.png", "images/kraze-logo.jpg"):
    if not (PUB / need).exists(): problems.append(f"missing {need}")
print("\n".join(problems) or "OK: %d pages, no problems found" % len(list(PUB.glob("*.html"))))
sys.exit(1 if problems else 0)
