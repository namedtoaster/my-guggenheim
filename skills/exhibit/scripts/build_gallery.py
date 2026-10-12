#!/usr/bin/env python3
"""Builds the exhibition: a gallery page and images to post.

    python3 build_gallery.py EXHIBIT_FOLDER [--linked]

Reads EXHIBIT_FOLDER/manifest.json (from inspect_photos.py) and
EXHIBIT_FOLDER/exhibition.json (the wall texts, written by the curator), and writes:

    EXHIBIT_FOLDER/gallery/index.html   the exhibition, one file you can open or send
    EXHIBIT_FOLDER/share/*.png          a carousel and a story cover sized for social posts
    EXHIBIT_FOLDER/share/caption.txt    a caption to paste with them

Every image is re-saved without its camera data, so no location or device details
leave with the gallery. With --linked the page points to images in gallery/images/
instead of carrying them inside, which suits hosting on GitHub Pages. No network.
"""

import argparse
import base64
import datetime
import html
import io
import re
import sys
from pathlib import Path

from common import (
    accent_color, wall_colors,
    ACCENT, INK, SOFT_INK, WALL, Image, ImageDraw, clamp_lines, draw_lines, first_sentences, fit_sentences,
    fit_inside, font, hex_to_rgb, load_json, open_photo, tombstone_artist, wrap,
)

REPO_URL = "https://github.com/namedtoaster/my-guggenheim"


# ---------------------------------------------------------------- checking

def check(exhibition, manifest):
    """Return a list of problems in exhibition.json, worded for whoever fixes it."""
    problems = []
    for key in ("title", "statement", "works"):
        if not exhibition.get(key):
            problems.append(f'exhibition.json needs "{key}"')
    known = {w["id"] for w in manifest["works"]}
    for i, work in enumerate(exhibition.get("works", [])):
        wid = work.get("id")
        if wid not in known:
            problems.append(f'works[{i}] has id "{wid}", which is not in manifest.json')
        for key in ("title", "label"):
            if not work.get(key):
                problems.append(f'works[{i}] ("{wid}") needs "{key}"')
    for i, entry in enumerate((exhibition.get("timeline") or {}).get("entries", [])):
        for wid in entry.get("works", []):
            if wid not in known:
                problems.append(f'timeline entry {i} names work "{wid}", which is not in manifest.json')
    text = repr(exhibition)
    if "\u2014" in text or "\u2013" in text:
        problems.append("exhibition.json has a long dash; use a comma, a period or parentheses")
    return problems


# ---------------------------------------------------------------- images

def jpeg_bytes(im, quality=84):
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    return buf.getvalue()


def web_copy(im, long_side):
    im = im.copy()
    im.thumbnail((long_side, long_side), Image.LANCZOS)
    return im


# ---------------------------------------------------------------- page

# White walls follow the viewer's light or dark setting. Shows that choose their
# own walls (a mood asking for a black box room, say) keep them in both.
WHITE_WALL_CSS = """:root {
  --wall: #efeeea; --ink: #1c1c1c; --soft: #5c5c5c; --rule: #d9d7d0; --accent: ACCENT;
  --shadow: 0 1px 2px rgba(0,0,0,.08), 0 18px 40px -12px rgba(0,0,0,.28);
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { --wall: #1d1d1b; --ink: #eceae4; --soft: #a5a39c; --rule: #3a3936;
    --shadow: 0 18px 40px -12px rgba(0,0,0,.7); color-scheme: dark; }
}
:root[data-theme="dark"] { --wall: #1d1d1b; --ink: #eceae4; --soft: #a5a39c; --rule: #3a3936;
  --shadow: 0 18px 40px -12px rgba(0,0,0,.7); color-scheme: dark; }"""

def inline(text):
    """Escape text, then allow *italics* for titles of works."""
    out = html.escape(text)
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", out)


def paragraphs(value):
    if isinstance(value, str):
        value = [p for p in value.split("\n\n") if p.strip()]
    return "".join(f"<p>{inline(p.strip())}</p>" for p in value)


def dimensions(meta):
    return f"{meta['width']:,} × {meta['height']:,} pixels"


def build_page(ex, manifest, srcs, thumbs):
    meta = {w["id"]: w for w in manifest["works"]}
    accent = "#%02x%02x%02x" % accent_color(ex)
    wall, ink, soft = ("#%02x%02x%02x" % c for c in wall_colors(ex))
    custom_walls = (ex.get("walls") or "white").strip().lower() != "white"
    artist = ex.get("artist") or {}
    artist_line = html.escape(tombstone_artist(artist))
    kicker = html.escape(ex.get("kicker") or "Collection in Focus")
    title = html.escape(ex["title"])

    # Room panels: each timeline entry with a room_text opens a section of the
    # gallery, the way a museum introduces each room before its works.
    sections = {}
    for g, entry in enumerate((ex.get("timeline") or {}).get("entries", []), 1):
        if entry.get("room_text") and entry.get("works"):
            first = next((w["id"] for w in ex["works"] if w["id"] in entry["works"]), None)
            if first and first not in sections:
                sections[first] = (g, entry)
    year = datetime.date.today().year

    rooms = []
    for n, work in enumerate(ex["works"], 1):
        m = meta[work["id"]]
        if work["id"] in sections:
            g, entry = sections[work["id"]]
            rooms.append(f"""
<section class="section-panel">
  <p class="kicker">Gallery {g}{' &middot; ' + html.escape(entry['when']) if entry.get('when') else ''}</p>
  <h2>{inline(entry.get('heading', ''))}</h2>
  {paragraphs(entry['room_text'])}
</section>""")
        tomb = [f'<p class="artist">{artist_line}</p>',
                f'<p class="work-title"><em>{html.escape(work["title"].replace("*", ""))}</em>'
                + (f', {html.escape(work["date"])}' if work.get("date") else "") + "</p>"]
        if work.get("medium"):
            tomb.append(f'<p>{html.escape(work["medium"])}</p>')
        tomb.append(f"<p>{dimensions(m)}</p>")
        tomb.append(f'<p>{html.escape(work.get("credit") or "Collection of the artist")}</p>')
        tomb.append(f'<p class="acc">{html.escape(work.get("accession") or f"{year}.{n}")}</p>')
        rooms.append(f"""
<section class="room {m['orientation']}" id="{html.escape(work['id'])}">
  <figure><img src="{srcs[work['id']]}" alt="{html.escape(work.get('alt') or work['title'])}"
    width="{m['width']}" height="{m['height']}"></figure>
  <aside class="label">
    <p class="number">{n}</p>
    <div class="tombstone">{''.join(tomb)}</div>
    <div class="text">{paragraphs(work['label'])}</div>
  </aside>
</section>""")

    timeline_html = ""
    tl = ex.get("timeline") or {}
    if tl.get("entries"):
        items = []
        for entry in tl["entries"]:
            pics = "".join(
                f'<a href="#{html.escape(w)}"><img src="{thumbs[w]}" alt=""></a>' for w in entry.get("works", []) if w in thumbs
            )
            items.append(f"""
  <li>
    <p class="when">{html.escape(entry.get('when', ''))}</p>
    <h3>{inline(entry.get('heading', ''))}</h3>
    {paragraphs(entry.get('text', ''))}
    <div class="thumbs">{pics}</div>
  </li>""")
        timeline_html = f"""
<section class="timeline" id="timeline">
  <p class="kicker">Chronology</p>
  <h2>{inline(tl.get('title') or "The Artist's Life")}</h2>
  <ol>{''.join(items)}</ol>
</section>"""

    note = ex.get("visitor_note") or "You do not have to read everything. Look at what you like. Get what you get."
    description = html.escape(first_sentences(" ".join(ex["statement"]) if isinstance(ex["statement"], list) else ex["statement"], 180))
    share_text = html.escape(f'{ex["title"]}, an exhibition by {artist.get("name") or "me"}')

    if custom_walls:
        dark = wall_colors(ex)[1][0] > 128
        wall_css = (f":root {{ --wall: {wall}; --ink: {ink}; --soft: {soft}; --rule: {'#3a3936' if dark else '#bdbbb4'}; "
                    f"--accent: {accent}; --shadow: 0 18px 40px -12px rgba(0,0,0,{'.7' if dark else '.3'}); "
                    f"color-scheme: {'dark' if dark else 'light'}; }}")
    else:
        wall_css = WHITE_WALL_CSS.replace("ACCENT", accent)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta name="generator" content="My Guggenheim">
<style>
{wall_css}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{ margin: 0; background: var(--wall); color: var(--ink);
  font: 17px/1.55 Inter, "Helvetica Neue", -apple-system, "Segoe UI", Arial, sans-serif; -webkit-font-smoothing: antialiased; }}
.wrap {{ max-width: 1180px; margin: 0 auto; padding: 0 16px; }}
.panel {{ min-height: 92vh; display: flex; flex-direction: column; justify-content: center; max-width: 820px; padding: 12vh 0; }}
.kicker {{ font-size: clamp(18px, 2.4vw, 26px); margin: 0 0 .1em; font-weight: 500; }}
h1 {{ color: var(--accent); font-size: clamp(40px, 7.4vw, 84px); line-height: 1.02; margin: 0 0 .6em; font-weight: 500; letter-spacing: -.02em; }}
.panel p {{ font-size: clamp(17px, 2vw, 21px); margin: 0 0 1.1em; }}
.byline {{ color: var(--soft); font-size: 15px !important; }}
.room {{ display: grid; grid-template-columns: minmax(0, 1fr) 400px; gap: 56px; align-items: start;
  min-height: 88vh; padding: 9vh 0; border-top: 1px solid var(--rule); }}
.room.portrait {{ grid-template-columns: minmax(0, .85fr) 420px; }}
figure {{ position: sticky; top: 6vh; }}
.tombstone .acc {{ color: var(--soft); font-size: 13px; margin-top: .4em; }}
.section-panel {{ border-top: 1px solid var(--rule); padding: 14vh 0 10vh; max-width: 760px; }}
.section-panel h2 {{ color: var(--accent); font-size: clamp(30px, 4.6vw, 52px); font-weight: 500; margin: 0 0 .7em; letter-spacing: -.01em; }}
.section-panel p {{ font-size: clamp(17px, 1.9vw, 20px); margin: 0 0 1em; }}
.section-panel .kicker {{ font-size: 15px; color: var(--soft); letter-spacing: .04em; text-transform: uppercase; }}
figure {{ margin: 0; display: flex; justify-content: center; }}
figure img {{ max-width: 100%; max-height: 78vh; width: auto; height: auto; box-shadow: var(--shadow); background: #ccc; }}
.label {{ font-size: 16px; line-height: 1.6; padding-top: 2vh; }}
.label .number {{ color: var(--soft); font-size: 13px; margin: 0 0 1em; }}
.tombstone p {{ margin: 0; }}
.tombstone .artist {{ font-weight: 600; }}
.tombstone {{ margin-bottom: 1.2em; }}
.text p {{ margin: 0 0 .9em; }}
.timeline {{ border-top: 1px solid var(--rule); padding: 12vh 0; }}
.timeline h2 {{ color: var(--accent); font-size: clamp(32px, 5vw, 56px); font-weight: 500; margin: 0 0 1em; letter-spacing: -.01em; }}
.timeline ol {{ list-style: none; margin: 0; padding: 0 0 0 28px; border-left: 2px solid var(--rule); max-width: 760px; }}
.timeline li {{ position: relative; padding: 0 0 2.6em; }}
.timeline li::before {{ content: ""; position: absolute; left: -36px; top: .45em; width: 14px; height: 14px; border-radius: 50%; background: var(--accent); }}
.timeline .when {{ color: var(--soft); margin: 0; font-size: 14px; letter-spacing: .04em; text-transform: uppercase; }}
.timeline h3 {{ margin: .1em 0 .4em; font-size: 22px; font-weight: 600; }}
.timeline p {{ margin: 0 0 .8em; }}
.thumbs {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.thumbs img {{ height: 64px; width: auto; display: block; box-shadow: 0 1px 4px rgba(0,0,0,.2); }}
footer {{ border-top: 1px solid var(--rule); padding: 10vh 0 14vh; max-width: 680px; }}
footer .note {{ font-size: 21px; margin: 0 0 1.4em; }}
footer small {{ color: var(--soft); display: block; margin-top: 2em; font-size: 13px; }}
footer a {{ color: inherit; }}
button {{ font: inherit; font-size: 15px; padding: .55em 1.1em; border-radius: 999px; border: 1px solid var(--ink);
  background: transparent; color: var(--ink); cursor: pointer; }}
button:hover {{ background: var(--ink); color: var(--wall); }}
@media (max-width: 820px) {{
  .room, .room.portrait {{ grid-template-columns: minmax(0, 1fr); gap: 28px; min-height: 0; padding: 8vh 0; }}
  figure {{ position: static; }}
  figure img {{ max-height: 72vh; }}
  body {{ font-size: 16px; }}
}}
@media print {{ .room {{ break-inside: avoid; min-height: 0; }} button {{ display: none; }} }}
</style>
</head>
<body>
<main class="wrap">
<header class="panel">
  <p class="kicker">{kicker}</p>
  <h1>{title}</h1>
  {paragraphs(ex['statement'])}
  <p class="byline">{len(ex['works'])} works by {artist_line}. Collection of the artist.</p>
</header>
{''.join(rooms)}
{timeline_html}
<footer>
  <p class="note">{inline(note)}</p>
  <button type="button" id="share">Share this exhibition</button>
  <small>Made with <a href="{REPO_URL}">My Guggenheim</a>. A personal exhibition,
  not affiliated with the Solomon R. Guggenheim Foundation or any museum.</small>
</footer>
</main>
<script>
document.getElementById('share').addEventListener('click', async () => {{
  const data = {{ title: document.title, text: "{share_text}", url: location.href }};
  try {{
    if (navigator.share && !location.protocol.startsWith('file')) {{ await navigator.share(data); return; }}
    await navigator.clipboard.writeText(location.protocol.startsWith('file') ? data.text : data.url);
    document.getElementById('share').textContent = 'Copied';
  }} catch (e) {{}}
}});
</script>
</body>
</html>
"""


# ---------------------------------------------------------------- share cards

def paste_with_shadow(canvas, im, xy):
    from PIL import ImageFilter

    x, y = xy
    pad = 40
    shadow = Image.new("L", (im.width + pad * 2, im.height + pad * 2), 0)
    ImageDraw.Draw(shadow).rectangle((pad, pad + 14, pad + im.width, pad + im.height + 14), fill=95)
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    canvas.paste((0, 0, 0), (x - pad, y - pad), shadow)
    canvas.paste(im, (x, y))


def card_wall_text(ex, accent, size=(1080, 1350)):
    W, H = size
    c = Image.new("RGB", size, WALL)
    d = ImageDraw.Draw(c)
    m = 96
    y = 150
    d.text((m, y), ex.get("kicker") or "Collection in Focus", font=font("medium", 40), fill=INK)
    y += 60
    tf = font("medium", 96)
    lines = wrap(ex["title"], tf, W - 2 * m)
    y = draw_lines(d, (m, y), lines, tf, accent, 104) + 50
    statement = ex["statement"] if isinstance(ex["statement"], list) else [ex["statement"]]
    bf = font("regular", 36)
    room = (H - 190 - y) // 52
    for para in statement:
        if room <= 1:
            break
        lines = fit_sentences(para, bf, W - 2 * m, room, clip=False)
        if not lines:
            break
        y = draw_lines(d, (m, y), lines, bf, INK, 52) + 26
        room -= len(lines) + 1
    d.text((m, H - 120), tombstone_artist(ex.get("artist")), font=font("semibold", 30), fill=INK)
    d.text((m, H - 78), "Collection of the artist", font=font("regular", 28), fill=SOFT_INK)
    return c


def card_work(ex, work, meta, photo, number, size=(1080, 1350)):
    W, H = size
    c = Image.new("RGB", size, WALL)
    d = ImageDraw.Draw(c)
    m = 96
    pic = fit_inside(photo, (W - 2 * m, int(H * 0.56)))
    px = (W - pic.width) // 2
    py = 90 + (int(H * 0.56) - pic.height) // 2
    paste_with_shadow(c, pic, (px, py))
    y = 90 + int(H * 0.56) + 64
    d.text((m, y), tombstone_artist(ex.get("artist")), font=font("semibold", 30), fill=INK)
    y += 42
    title = work["title"].replace("*", "")
    tl = wrap(title + (f", {work['date']}" if work.get("date") else ""), font("italic", 30), W - 2 * m)
    y = draw_lines(d, (m, y), clamp_lines(tl, 2), font("italic", 30), INK, 40) + 22
    bf = font("regular", 29)
    room = max(1, (H - 70 - y) // 42)
    lines = fit_sentences(work["label"].replace("*", "").replace("\n\n", " "), bf, W - 2 * m, room)
    draw_lines(d, (m, y), lines, bf, INK, 42)
    d.text((W - m, 44), f"{number}/{len(ex['works'])}", font=font("regular", 24), fill=SOFT_INK, anchor="ra")
    return c


def card_timeline(ex, accent, size=(1080, 1350)):
    W, H = size
    tl = ex.get("timeline") or {}
    c = Image.new("RGB", size, WALL)
    d = ImageDraw.Draw(c)
    m = 96
    d.text((m, 130), "Chronology", font=font("medium", 36), fill=INK)
    hf = font("medium", 78)
    y = draw_lines(d, (m, 180), wrap(tl.get("title") or "The Artist's Life", hf, W - 2 * m), hf, accent, 86) + 50
    entries = tl.get("entries", [])
    room = H - 100 - y
    each = room // max(1, len(entries))
    text_lines = 3 if each >= 230 else 2 if each >= 180 else 1 if each >= 140 else 0
    for entry in entries:
        if y + 90 > H - 80:
            break
        d.ellipse((m, y + 6, m + 20, y + 26), fill=accent)
        d.text((m + 44, y), entry.get("when", "").upper(), font=font("medium", 24), fill=SOFT_INK)
        hl = clamp_lines(wrap(entry.get("heading", "").replace("*", ""), font("semibold", 36), W - 2 * m - 44), 2)
        ny = draw_lines(d, (m + 44, y + 32), hl, font("semibold", 36), INK, 44)
        if text_lines and entry.get("text"):
            tf = font("regular", 27)
            ny = draw_lines(d, (m + 44, ny + 6), fit_sentences(entry["text"].replace("*", ""), tf, W - 2 * m - 44, text_lines, clip=False), tf, SOFT_INK, 38)
        y = max(ny + 34, y + min(each, 400))
    return c


def card_story(ex, accent, cover, size=(1080, 1920)):
    W, H = size
    c = Image.new("RGB", size, WALL)
    d = ImageDraw.Draw(c)
    m = 90
    pic = fit_inside(cover, (W - 2 * m, 980))
    paste_with_shadow(c, pic, ((W - pic.width) // 2, 200 + (980 - pic.height) // 2))
    y = 1260
    d.text((m, y), ex.get("kicker") or "Collection in Focus", font=font("medium", 40), fill=INK)
    tf = font("medium", 92)
    lines = clamp_lines(wrap(ex["title"], tf, W - 2 * m), 3)
    draw_lines(d, (m, y + 58), lines, tf, accent, 100)
    d.text((m, H - 190), tombstone_artist(ex.get("artist")), font=font("semibold", 34), fill=INK)
    d.text((m, H - 142), f"{len(ex['works'])} works. Now on view.", font=font("regular", 32), fill=SOFT_INK)
    return c


def caption(ex):
    share = ex.get("share") or {}
    text = share.get("caption") or f'Now on view: "{ex["title"]}". {len(ex["works"])} works from the collection of the artist.'
    tags = share.get("hashtags") or ["#MyGuggenheim"]
    if "#MyGuggenheim" not in tags:
        tags = tags + ["#MyGuggenheim"]
    return f"{text}\n\n{' '.join(tags)}\n"


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("exhibit", help="exhibit folder holding manifest.json and exhibition.json")
    ap.add_argument("--linked", action="store_true", help="write images next to the page instead of inside it")
    ap.add_argument("--image-size", type=int, default=1600, help="long side of gallery images in pixels")
    ap.add_argument("--carousel", type=int, default=8, help="most work cards in the carousel")
    args = ap.parse_args()

    folder = Path(args.exhibit)
    manifest = load_json(folder / "manifest.json")
    exhibition = load_json(folder / "exhibition.json")
    problems = check(exhibition, manifest)
    if problems:
        print("exhibition.json needs fixing:", *problems, sep="\n  ", file=sys.stderr)
        sys.exit(1)

    meta = {w["id"]: w for w in manifest["works"]}
    gallery = folder / "gallery"
    share = folder / "share"
    gallery.mkdir(exist_ok=True)
    share.mkdir(exist_ok=True)
    for old in share.glob("*.png"):
        old.unlink()
    if args.linked:
        (gallery / "images").mkdir(exist_ok=True)

    photos, srcs, thumbs = {}, {}, {}
    for work in exhibition["works"]:
        wid = work["id"]
        photo = open_photo(folder / meta[wid]["file"])
        photos[wid] = photo
        big = jpeg_bytes(web_copy(photo, args.image_size))
        small = jpeg_bytes(web_copy(photo, 200), quality=75)
        if args.linked:
            (gallery / "images" / f"{wid}.jpg").write_bytes(big)
            (gallery / "images" / f"{wid}-thumb.jpg").write_bytes(small)
            srcs[wid], thumbs[wid] = f"images/{wid}.jpg", f"images/{wid}-thumb.jpg"
        else:
            srcs[wid] = "data:image/jpeg;base64," + base64.b64encode(big).decode()
            thumbs[wid] = "data:image/jpeg;base64," + base64.b64encode(small).decode()

    page = build_page(exhibition, manifest, srcs, thumbs)
    (gallery / "index.html").write_text(page, encoding="utf-8")

    global WALL, INK, SOFT_INK
    WALL, INK, SOFT_INK = wall_colors(exhibition)
    accent = accent_color(exhibition)
    cards = [("01-wall-text.png", card_wall_text(exhibition, accent))]
    for n, work in enumerate(exhibition["works"][: args.carousel], 1):
        cards.append((f"{n + 1:02d}-{work['id']}.png", card_work(exhibition, work, meta[work["id"]], photos[work["id"]], n)))
    if (exhibition.get("timeline") or {}).get("entries"):
        cards.append((f"{len(cards) + 1:02d}-timeline.png", card_timeline(exhibition, accent)))
    cover_id = exhibition.get("cover") or exhibition["works"][0]["id"]
    for name, im in cards:
        im.save(share / name, optimize=True)
    card_story(exhibition, accent, photos.get(cover_id, photos[exhibition["works"][0]["id"]])).save(share / "story-cover.png", optimize=True)
    (share / "caption.txt").write_text(caption(exhibition), encoding="utf-8")

    size_mb = (gallery / "index.html").stat().st_size / 1e6
    print(f"Gallery: {gallery / 'index.html'} ({size_mb:.1f} MB)")
    print(f"Share:   {share}/ ({len(cards)} carousel cards, story-cover.png, caption.txt)")


if __name__ == "__main__":
    main()
