#!/usr/bin/env python3
"""Makes a trailer for the exhibition: a dramatic montage cut like a film trailer.

    python3 make_trailer.py EXHIBIT_FOLDER [--format vertical|square|landscape] [--quotes 4]

Reads manifest.json and exhibition.json and writes EXHIBIT_FOLDER/share/trailer-<format>.mp4,
about 30 to 40 seconds on black: a quiet opening card, then photos full frame, each
followed by one line from its label set large, broken up by cards like "SIX WORKS."
and "ONE ARTIST.", a fast montage of every work, and the title.

The lines come from the "trailer" block in exhibition.json when there is one,
otherwise from each work's film_line or the shortest strong sentence in its label.

Like the film, it is silent on purpose: add a sound in the app you post from.
Needs ffmpeg for MP4. Without ffmpeg it writes a smaller animated GIF instead.
No network.
"""

import argparse
import re
from pathlib import Path

from common import (
    REPO_SHORT, credits_on, accent_color, redact,
    Image, ImageDraw, font, fit_cover, load_json, open_photo, tombstone_artist, wrap,
)
from make_film import FORMATS, FPS, Layer, compose, ease, encode
from PIL import ImageEnhance, ImageFilter

BLACK = (10, 10, 10)
WHITE = (240, 238, 232)
GREY = (150, 148, 142)

NUMBERS = ["No", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
           "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen",
           "Eighteen", "Nineteen", "Twenty"]


def number(n):
    return NUMBERS[n] if 0 <= n < len(NUMBERS) else str(n)


def plain(text):
    return (text or "").replace("*", "").strip()


# ---------------------------------------------------------------- words

def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", plain(text)) if s.strip()]


def strongest_line(work):
    """The line from a work that would hold a black screen on its own."""
    film = plain(work.get("film_line"))
    if film and len(film.split()) <= 16:
        return film
    picks = [s for s in sentences(work.get("label")) if 5 <= len(s.split()) <= 16 and "(" not in s]
    if picks:
        return min(picks, key=lambda s: abs(len(s.split()) - 9))
    return film or (sentences(work.get("label")) or [""])[0]


def spread(items, k):
    """k items evenly spread from first to last."""
    if k >= len(items):
        return list(items)
    if k <= 1:
        return items[:1]
    return [items[round(i * (len(items) - 1) / (k - 1))] for i in range(k)]


def pick_lines(ex, k):
    """[(work, line)] for the quote cards."""
    works = {w["id"]: w for w in ex["works"]}
    chosen = []
    for item in (ex.get("trailer") or {}).get("lines", []):
        if isinstance(item, str):
            chosen.append((None, plain(item)))
        elif item.get("text"):
            chosen.append((works.get(item.get("work")), plain(item["text"])))
    if chosen:
        return chosen[:k]
    return [(w, strongest_line(w)) for w in spread(ex["works"], k)]


MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]


def span(ex):
    """'Ten months.' or 'Eight years.' from the works' dates, or '' when too few are dated."""
    months, years = [], []
    for w in ex["works"]:
        date = (w.get("date") or "").lower()
        year = re.search(r"\b(19\d\d|20\d\d)\b", date)
        if not year:
            continue
        years.append(int(year.group(1)))
        month = re.search(r"\b(" + "|".join(MONTHS) + r")[a-z]*\b", date)
        if month:
            months.append(int(year.group(1)) * 12 + MONTHS.index(month.group(1)))
    if len(months) == len(years) and len(months) > 1:
        n = max(months) - min(months) + 1
        if 1 < n < 24:
            return f"{number(n)} months."
    n = max(years) - min(years) + 1 if years else 0
    return f"{number(n)} years." if n > 1 else ""


def beat_cards(ex):
    """Short trailer cards to cut between the quotes."""
    custom = (ex.get("trailer") or {}).get("cards")
    if custom:
        return [plain(c) for c in custom]
    n = len(ex["works"])
    cards = [f"{number(n)} works." if n != 1 else "One work."]
    if span(ex):
        cards.append(span(ex))
    cards.append("One artist.")
    return cards


# ---------------------------------------------------------------- drawing

def tracked(draw, center_x, y, text, fnt, fill, tracking):
    """Spaced out capitals, centered on center_x."""
    widths = [fnt.getlength(c) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = center_x - total / 2
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=fnt, fill=fill)
        x += w + tracking


def centered(draw, W, y, lines, fnt, fill, line_height):
    for line in lines:
        draw.text(((W - fnt.getlength(line)) / 2, y), line, font=fnt, fill=fill)
        y += line_height
    return y


def vignette(W, H):
    """A soft dark edge, the same for every photo."""
    small = Image.new("L", (W // 8, H // 8), 0)
    ImageDraw.Draw(small).ellipse((-W // 40, -H // 40, W // 8 + W // 40, H // 8 + H // 40), fill=255)
    return small.filter(ImageFilter.GaussianBlur(min(W, H) // 60)).resize((W, H), Image.BILINEAR)


def graded(photo, W, H, edge):
    """The photo filling the frame, a little larger than it (room for the push), cooler,
    contrastier and darker at the edges."""
    pw, ph = int(W * 1.08), int(H * 1.08)
    im = fit_cover(photo, (pw, ph))
    im = ImageEnhance.Color(im).enhance(0.82)
    im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Brightness(im).enhance(0.9)
    dark = Image.new("RGB", (pw, ph), BLACK)
    return Image.composite(im, dark, edge.resize((pw, ph), Image.BILINEAR))


# ---------------------------------------------------------------- scenes
# Each scene is (frames, draw(i) -> RGB image, or None for black).

def scene_black(seconds):
    return int(seconds * FPS), lambda i: None


def scene_text(W, H, layers, seconds, fade_in=0.5, fade_out=0.4):
    """Text on black that fades up and away. layers: [(Layer, start second)]."""
    n = int(seconds * FPS)
    base = Image.new("RGBA", (W, H), BLACK + (255,))

    def draw(i):
        sec = i / FPS
        out = 1 - ease((sec - (seconds - fade_out)) / fade_out)
        frame = base.copy()
        for layer, start in layers:
            t = ease((sec - start) / fade_in)
            compose(frame, layer, t * out, 10 * (1 - t))
        return frame.convert("RGB")

    return n, draw


def scene_photo(W, H, big, seconds, zoom_in=True, flash=0):
    """A photo with a slow push. flash: frames of white at the cut."""
    n = max(1, int(seconds * FPS))
    pw, ph = big.size
    white = Image.new("RGB", (W, H), (255, 255, 255))

    def draw(i):
        p = i / max(1, n - 1)
        z = 1.08 / (1.0 + 0.08 * (p if zoom_in else 1 - p))  # how much of the big photo shows
        cw, ch = min(pw, W * z), min(ph, H * z)
        left, top = (pw - cw) / 2, (ph - ch) / 2
        frame = big.resize((W, H), Image.BILINEAR, box=(left, top, left + cw, top + ch))
        if i < flash:
            frame = Image.blend(frame, white, 0.7 * (1 - i / flash))
        return frame

    return n, draw


def quote_layers(W, H, fmt, line, source):
    s = 0.86 if fmt == "square" else 1.0
    m = int((120 if fmt == "vertical" else 140 if fmt == "square" else 360) * s)
    qf = font("italic", int((76 if fmt == "vertical" else 62 if fmt == "square" else 70) * s))
    lh = int(qf.size * 1.28)
    lines = wrap(f"“{line}”", qf, W - 2 * m)
    while len(lines) > 7 and qf.size > 40:
        qf = font("italic", qf.size - 6)
        lh = int(qf.size * 1.28)
        lines = wrap(f"“{line}”", qf, W - 2 * m)
    q, src = Layer((W, H)), Layer((W, H))
    y = (H - lh * len(lines)) // 2 - int(30 * s)
    y = centered(q.draw, W, y, lines, qf, WHITE, lh)
    if source:
        tracked(src.draw, W / 2, y + int(50 * s), source.upper(), font("medium", int(24 * s)), GREY, int(5 * s))
    return [(q, 0.15), (src, 1.0)]


def card_layers(W, H, fmt, text, size=64):
    s = 0.86 if fmt == "square" else 1.0
    f = font("semibold", int(size * s))
    layer = Layer((W, H))
    tracked(layer.draw, W / 2, (H - f.size) // 2, text.upper(), f, WHITE, int(size * 0.16 * s))
    return [(layer, 0.1)]


def title_layers(W, H, fmt, ex, accent):
    s = 0.86 if fmt == "square" else 1.0
    m = int(100 * s)
    tf = font("semibold", int((112 if fmt == "vertical" else 104) * s))
    lines = wrap(plain(ex["title"]).upper(), tf, W - 2 * m)
    while len(lines) > 4 and tf.size > 50:
        tf = font("semibold", tf.size - 8)
        lines = wrap(plain(ex["title"]).upper(), tf, W - 2 * m)
    lh = int(tf.size * 1.1)
    kicker, title, foot = Layer((W, H)), Layer((W, H)), Layer((W, H))
    y = (H - lh * len(lines)) // 2
    tracked(kicker.draw, W / 2, y - int(90 * s), (ex.get("kicker") or "Collection in Focus").upper(),
            font("medium", int(30 * s)), GREY, int(7 * s))
    y = centered(title.draw, W, y, lines, tf, accent, lh)
    tracked(foot.draw, W / 2, y + int(60 * s), tombstone_artist(ex.get("artist")).upper(),
            font("medium", int(30 * s)), WHITE, int(6 * s))
    return [(title, 0.0), (kicker, 0.6), (foot, 1.1)]


def end_layers(W, H, fmt, ex):
    s = 0.86 if fmt == "square" else 1.0
    tagline = plain((ex.get("trailer") or {}).get("tagline")) or "Now on view."
    head, credit = Layer((W, H)), Layer((W, H))
    tracked(head.draw, W / 2, H // 2 - int(60 * s), tagline.upper(), font("semibold", int(56 * s)), WHITE, int(9 * s))
    tracked(head.draw, W / 2, H // 2 + int(30 * s), "In the artist's camera roll".upper(), font("medium", int(26 * s)), GREY, int(6 * s))
    if credits_on(ex):
        tracked(credit.draw, W / 2, H - int(200 * s), "MAKE YOUR OWN. MADE WITH MY GUGGENHEIM", font("medium", int(26 * s)), WHITE, int(4 * s))
        tracked(credit.draw, W / 2, H - int(150 * s), REPO_SHORT.upper(), font("regular", int(24 * s)), GREY, int(3 * s))
    return [(head, 0.2), (credit, 1.2)]


# ---------------------------------------------------------------- the cut

def build(ex, photos, W, H, fmt, quotes):
    """The trailer as a list of scenes. photos maps work id to its graded frame."""
    accent = accent_color({**ex, "walls": "black"})
    by_id = {w["id"]: w for w in ex["works"]}
    lines = pick_lines(ex, quotes)
    cards = beat_cards(ex)
    artist = (ex.get("artist") or {}).get("name") or "the artist"

    scenes = [scene_black(0.6)]
    scenes.append(scene_text(W, H, card_layers(W, H, fmt, f"From the collection of {artist}", 34), 2.6, fade_in=0.8))
    for n, (work, line) in enumerate(lines):
        if work and work["id"] in photos:
            scenes.append(scene_photo(W, H, photos[work["id"]], 1.6, zoom_in=n % 2 == 0))
        source = ""
        if work:
            source = plain(work["title"]) + (f", {work['date']}" if work.get("date") else "")
        scenes.append(scene_text(W, H, quote_layers(W, H, fmt, line, source), 3.1))
        if n < len(cards) and n < len(lines) - 1:
            scenes.append(scene_text(W, H, card_layers(W, H, fmt, cards[n]), 1.3, fade_in=0.25, fade_out=0.25))
    for card in cards[max(0, len(lines) - 1):]:
        scenes.append(scene_text(W, H, card_layers(W, H, fmt, card), 1.3, fade_in=0.25, fade_out=0.25))

    # The montage: every work, faster and faster, cut on a flash.
    order = [by_id[w["id"]] for w in ex["works"] if w["id"] in photos]
    count = len(order)
    for j, work in enumerate(order * (2 if count < 6 else 1)):
        p = j / max(1, len(order) * (2 if count < 6 else 1) - 1)
        scenes.append(scene_photo(W, H, photos[work["id"]], 0.42 - 0.27 * p, zoom_in=j % 2 == 0, flash=3))
    scenes.append(scene_black(0.7))
    scenes.append(scene_text(W, H, title_layers(W, H, fmt, ex, accent), 3.5, fade_in=0.3, fade_out=0.5))
    scenes.append(scene_text(W, H, end_layers(W, H, fmt, ex), 3.8, fade_in=0.6, fade_out=0.6))
    return scenes


def render(scenes, W, H, emit):
    black = Image.new("RGB", (W, H), BLACK)
    for frames, draw in scenes:
        for i in range(frames):
            emit(draw(i) or black)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("exhibit")
    ap.add_argument("--format", choices=sorted(FORMATS), default="vertical")
    ap.add_argument("--quotes", type=int, default=4, help="how many lines from the labels to show")
    ap.add_argument("--gif", action="store_true", help="write an animated GIF even when ffmpeg is present")
    args = ap.parse_args()

    folder = Path(args.exhibit)
    manifest = load_json(folder / "manifest.json")
    ex = load_json(folder / "exhibition.json")
    meta = {w["id"]: w for w in manifest["works"]}
    W, H = FORMATS[args.format]

    edge = vignette(W, H)
    photos = {}
    for work in ex["works"]:
        if work["id"] not in meta:
            continue
        photo = redact(open_photo(folder / meta[work["id"]]["file"]), work.get("redact"))
        photo.thumbnail((2200, 2200))
        photos[work["id"]] = graded(photo, W, H, edge)

    scenes = build(ex, photos, W, H, args.format, max(1, args.quotes))
    total = sum(f for f, _ in scenes)
    out = encode(lambda emit: render(scenes, W, H, emit), total, W, H, folder / "share", f"trailer-{args.format}", args.gif)
    print(f"Trailer: {out} ({total / FPS:.0f} seconds, {W}x{H})")


if __name__ == "__main__":
    main()
