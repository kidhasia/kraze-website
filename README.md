# KrazE website

Plain HTML/CSS/JS. Pages in `public/` are **generated** by `build.py` from `content/*.json`; do not edit the generated `.html` files by hand.

## Commands
    python3 build.py                      # regenerate pages, sitemap.xml, robots.txt
    python3 check.py                      # links, assets, ids, tags, SEO tags, image attributes
    cd public && python3 -m http.server 8000   # preview at http://localhost:8000

## What to edit
- `content/site.json`: domain (`site_url`), email/phone/WhatsApp, social links, services, workflow steps, form settings. Empty values are hidden or shown as marked placeholders.
- `content/projects.json`: portfolio. Put real images in `public/images/projects/` and set `cover`, `cover_width`, `cover_height`, optional `video`, and `placeholder: false`.
- `build.py`: page copy and layout. `public/css/style.css`: styling.

## Before launch
1. Set `site_url` (or `KRAZE_SITE_URL=https://yourdomain python3 build.py`). Canonical, Open Graph and sitemap URLs use it.
2. Contact form: create a form-service endpoint that accepts a JSON POST (e.g. Formspree or Web3Forms), put its public URL in `form.endpoint`, and rebuild. Until then the form tells visitors it is not connected. Keep any secret keys in the service dashboard, never in this repo. Optional: add a Cloudflare Turnstile **site** key in `form.turnstile_site_key` (enable Turnstile verification in your form service).
3. Add real contact details, social links, projects and About copy; confirm the draft service/workflow copy is accurate.

`public/images/kraze-logo.jpg` is the original logo, unmodified. The favicon/apple-touch PNGs are resized crops of its "K".

## Portfolio videos
Source videos are large, so `public/media/` holds web versions: `<slug>.mp4` (720px wide, H.264), `<slug>-preview.mp4` (muted 6 s hover clip) and `<slug>.jpg` (poster). Re-create them from an original with ffmpeg:

    ffmpeg -i original.mp4 -vf "scale=720:-2,fps=30" -c:v libx264 -preset veryfast -crf 27 -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 96k public/media/<slug>.mp4
    ffmpeg -ss 0.5 -t 6 -i original.mp4 -an -vf "scale=400:-2,fps=24" -c:v libx264 -crf 30 -pix_fmt yuv420p -movflags +faststart public/media/<slug>-preview.mp4
    ffmpeg -ss 1.5 -i original.mp4 -frames:v 1 -vf "scale=720:-2" -q:v 4 public/media/<slug>.jpg

Then add the project to `content/projects.json` and rebuild. Interactive effects (scroll reveal, hiding header, marquee, cursor label, magnetic buttons, hover previews) live in `public/js/fx.js` and `public/css/style.css`; all are disabled under `prefers-reduced-motion` and the site works without JS.
