#!/usr/bin/env python3
"""Makes a short exhibition film to post: a walk through the gallery, one wall at a time.

    python3 make_film.py EXHIBIT_FOLDER [--format vertical|square|landscape] [--seconds 4.2]

Reads manifest.json and exhibition.json and writes EXHIBIT_FOLDER/share/film-<format>.mp4:
the wall title, each work with a slow camera push and its label, the timeline, and
a closing note. Vertical (1080x1920) suits Reels, TikTok and Shorts; square suits
a feed post; landscape suits YouTube.

There is no music on purpose. Add a sound in the app you post from, where the
music is licensed for that platform.

Needs ffmpeg for MP4. Without ffmpeg it writes a smaller animated GIF instead.
No network.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from common import (
    INK, SOFT_INK, WALL, Image, ImageDraw, clamp_lines, draw_lines, first_sentences, fit_inside,
    fit_sentences, font, hex_to_rgb, load_json, open_photo, tombstone_artist, wrap,
)
from PIL import ImageFilter

FORMATS = {"vertical": (1080, 1920), "square": (1080, 1080), "landscape": (1920, 1080)}
FPS = 30
FADE = 9  # frames to fade in from the wall, and out to it


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def find_ffmpeg():
    path = shutil.which("ffmpeg")
    if path:
        return path
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


class Layer:
    """Text drawn once onto a transparent sheet, shown later at any opacity and offset."""

    def __init__(self, size):
        self.im = Image.new("RGBA", size, (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.im)

    def faded(self, opacity):
        if opacity >= 0.999:
            return self.im
        alpha = self.im.getchannel("A").point(lambda a: int(a * opacity))
        out = self.im.copy()
        out.putalpha(alpha)
        return out


def compose(frame, layer, opacity, rise=0):
    if opacity <= 0.001:
        return
    frame.alpha_composite(layer.faded(opacity), (0, int(rise)))


def shadowed(canvas, im, xy):
    x, y = xy
    pad = 40
    shadow = Image.new("L", (im.width + pad * 2, im.height + pad * 2), 0)
    ImageDraw.Draw(shadow).rectangle((pad, pad + 14, pad + im.width, pad + im.height + 14), fill=100)
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    canvas.paste((0, 0, 0), (x - pad, y - pad), shadow)
    canvas.paste(im, (x, y))


def layout(fmt, W, H):
    """Where the photo hangs and where its label goes, per format."""
    if fmt == "landscape":
        return {"photo": (110, 100, 1180, 980), "text": (1260, 300, W - 110), "body_lines": 9, "scale": 1.0}
    if fmt == "square":
        return {"photo": (90, 70, W - 90, 700), "text": (90, 760, W - 90), "body_lines": 3, "scale": 0.86}
    return {"photo": (80, 170, W - 80, 1230), "text": (90, 1320, W - 90), "body_lines": 6, "scale": 1.0}


# ---------------------------------------------------------------- scenes
# Each scene returns (base, layers, frames, animate). base is the wall with any
# photo already hung. animate(i) gives the camera zoom and each layer's opacity.

def scene_title(ex, accent, W, H, fmt):
    s = 1.0 if fmt != "square" else 0.85
    base = Image.new("RGB", (W, H), WALL)
    m = int(110 * s)
    k, t, a = Layer((W, H)), Layer((W, H)), Layer((W, H))
    tf = font("medium", int((118 if fmt == "vertical" else 104) * s))
    lines = wrap(ex["title"], tf, W - 2 * m)
    lh = int(tf.size * 1.08)
    block = 70 + lh * len(lines) + 90
    y = (H - block) // 2
    k.draw.text((m, y), ex.get("kicker") or "Collection in Focus", font=font("medium", int(46 * s)), fill=INK)
    draw_lines(t.draw, (m, y + 70), lines, tf, accent, lh)
    a.draw.text((m, y + 70 + lh * len(lines) + 40), tombstone_artist(ex.get("artist")), font=font("regular", int(38 * s)), fill=SOFT_INK)
    frames = int(3.6 * FPS)

    def animate(i):
        sec = i / FPS
        return 1.0 + 0.02 * i / frames, [(k, ease((sec - 0.2) / 0.6), 0), (t, ease((sec - 0.5) / 0.8), 24 * (1 - ease((sec - 0.5) / 0.8))),
                                          (a, ease((sec - 1.3) / 0.6), 0)]

    return base, animate, frames


def scene_work(ex, work, photo, n, total, W, H, fmt, seconds):
    L = layout(fmt, W, H)
    s = L["scale"]
    base = Image.new("RGB", (W, H), WALL)
    x0, y0, x1, y1 = L["photo"]
    pic = fit_inside(photo, (x1 - x0, y1 - y0))
    shadowed(base, pic, (x0 + (x1 - x0 - pic.width) // 2, y0 + (y1 - y0 - pic.height) // 2))

    tx, ty, tr = L["text"]
    width = tr - tx
    head, body = Layer((W, H)), Layer((W, H))
    head.draw.text((tx, ty), f"{n}/{total}", font=font("regular", int(28 * s)), fill=SOFT_INK)
    y = ty + int(50 * s)
    tf = font("italic", int(44 * s))
    title = work["title"].replace("*", "") + (f", {work['date']}" if work.get("date") else "")
    y = draw_lines(head.draw, (tx, y), clamp_lines(wrap(title, tf, width), 2), tf, INK, int(56 * s))
    if work.get("medium"):
        y = draw_lines(head.draw, (tx, y + 4), clamp_lines(wrap(work["medium"], font("regular", int(30 * s)), width), 1),
                       font("regular", int(30 * s)), SOFT_INK, int(42 * s))
    bf = font("regular", int(36 * s))
    text = work.get("film_line") or first_sentences(work["label"].replace("*", ""), 210)
    draw_lines(body.draw, (tx, y + int(30 * s)), fit_sentences(text, bf, width, L["body_lines"]), bf, INK, int(52 * s))

    frames = int(seconds * FPS)
    zoom_in = n % 2 == 1

    def animate(i):
        sec = i / FPS
        p = i / frames
        z = 1.0 + 0.055 * (p if zoom_in else 1 - p)
        return z, [(head, ease((sec - 0.35) / 0.5), 16 * (1 - ease((sec - 0.35) / 0.5))),
                   (body, ease((sec - 0.8) / 0.6), 16 * (1 - ease((sec - 0.8) / 0.6)))]

    return base, animate, frames


def scene_timeline(ex, accent, W, H, fmt):
    tl = ex.get("timeline") or {}
    entries = tl.get("entries", [])[:7]
    s = 0.82 if fmt == "square" else 1.0
    base = Image.new("RGB", (W, H), WALL)
    m = int(110 * s)
    head = Layer((W, H))
    head.draw.text((m, int(170 * s)), "Chronology", font=font("medium", int(40 * s)), fill=INK)
    hf = font("medium", int(84 * s))
    y = draw_lines(head.draw, (m, int(225 * s)), wrap(tl.get("title") or "The Artist's Life", hf, W - 2 * m), hf, accent, int(92 * s)) + int(60 * s)
    rows = []
    avail = H - y - int(120 * s)
    step = min(int(330 * s), avail // max(1, len(entries)))
    text_lines = 0 if fmt == "square" else 2 if step >= 230 * s else 1 if step >= 180 * s else 0
    for entry in entries:
        r = Layer((W, H))
        r.draw.ellipse((m, y + 12, m + 22, y + 34), fill=accent)
        r.draw.text((m + 50, y), entry.get("when", "").upper(), font=font("medium", int(28 * s)), fill=SOFT_INK)
        hl = clamp_lines(wrap(entry.get("heading", "").replace("*", ""), font("semibold", int(42 * s)), W - 2 * m - 50), 2)
        ny = draw_lines(r.draw, (m + 50, y + int(40 * s)), hl, font("semibold", int(42 * s)), INK, int(50 * s))
        if text_lines and entry.get("text"):
            tf = font("regular", int(32 * s))
            draw_lines(r.draw, (m + 50, ny + 6), fit_sentences(entry["text"].replace("*", ""), tf, W - 2 * m - 50, text_lines, clip=False), tf, SOFT_INK, int(44 * s))
        rows.append(r)
        y += step
    frames = int((1.6 + 0.6 * len(rows) + 1.8) * FPS)

    def animate(i):
        sec = i / FPS
        layers = [(head, ease((sec - 0.2) / 0.6), 0)]
        for j, r in enumerate(rows):
            t = ease((sec - 1.0 - 0.6 * j) / 0.5)
            layers.append((r, t, 20 * (1 - t)))
        return 1.0, layers

    return base, animate, frames


def scene_end(ex, W, H, fmt):
    s = 0.85 if fmt == "square" else 1.0
    base = Image.new("RGB", (W, H), WALL)
    m = int(110 * s)
    note, credit = Layer((W, H)), Layer((W, H))
    nf = font("regular", int(52 * s))
    text = (ex.get("visitor_note") or "You do not have to read everything. Get what you get.").replace("*", "")
    lines = clamp_lines(wrap(text, nf, W - 2 * m), 6)
    y = H // 2 - len(lines) * int(68 * s) // 2 - int(40 * s)
    y = draw_lines(note.draw, (m, y), lines, nf, INK, int(68 * s))
    credit.draw.text((m, y + int(70 * s)), f"{tombstone_artist(ex.get('artist'))}. Collection of the artist.",
                     font=font("regular", int(32 * s)), fill=SOFT_INK)
    credit.draw.text((m, H - int(140 * s)), "Made with My Guggenheim", font=font("medium", int(30 * s)), fill=SOFT_INK)
    frames = int(3.6 * FPS)

    def animate(i):
        sec = i / FPS
        return 1.0, [(note, ease((sec - 0.2) / 0.7), 0), (credit, ease((sec - 1.2) / 0.6), 0)]

    return base, animate, frames


# ---------------------------------------------------------------- render

def render(scenes, W, H, emit):
    wall = Image.new("RGB", (W, H), WALL)
    for base, animate, frames in scenes:
        for i in range(frames):
            z, layers = animate(i)
            if z > 1.0001:
                cw, ch = W / z, H / z
                left, top = (W - cw) / 2, (H - ch) * 0.42
                frame = base.resize((W, H), Image.BILINEAR, box=(left, top, left + cw, top + ch))
            else:
                frame = base.copy()
            frame = frame.convert("RGBA")
            for layer, opacity, rise in layers:
                compose(frame, layer, opacity, rise)
            frame = frame.convert("RGB")
            edge = min(i, frames - 1 - i)
            if edge < FADE:
                frame = Image.blend(wall, frame, ease(edge / FADE))
            emit(frame)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("exhibit")
    ap.add_argument("--format", choices=sorted(FORMATS), default="vertical")
    ap.add_argument("--seconds", type=float, default=4.2, help="seconds on each work")
    ap.add_argument("--max-works", type=int, default=12, help="most works in the film")
    ap.add_argument("--gif", action="store_true", help="write an animated GIF even when ffmpeg is present")
    args = ap.parse_args()

    folder = Path(args.exhibit)
    manifest = load_json(folder / "manifest.json")
    ex = load_json(folder / "exhibition.json")
    meta = {w["id"]: w for w in manifest["works"]}
    W, H = FORMATS[args.format]
    accent = hex_to_rgb(ex.get("accent"))
    works = ex["works"][: args.max_works]

    scenes = [scene_title(ex, accent, W, H, args.format)]
    for n, work in enumerate(works, 1):
        photo = open_photo(folder / meta[work["id"]]["file"])
        photo.thumbnail((1800, 1800))
        scenes.append(scene_work(ex, work, photo, n, len(works), W, H, args.format, args.seconds))
    if (ex.get("timeline") or {}).get("entries"):
        scenes.append(scene_timeline(ex, accent, W, H, args.format))
    scenes.append(scene_end(ex, W, H, args.format))
    total = sum(f for _, _, f in scenes)

    share = folder / "share"
    share.mkdir(exist_ok=True)
    ffmpeg = None if args.gif else find_ffmpeg()

    if ffmpeg:
        out = share / f"film-{args.format}.mp4"
        cmd = [ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
               "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        count = [0]

        def emit(frame):
            proc.stdin.write(frame.tobytes())
            count[0] += 1
            if count[0] % (FPS * 5) == 0:
                print(f"  {count[0] // FPS}s of {total // FPS}s", flush=True)

        render(scenes, W, H, emit)
        proc.stdin.close()
        if proc.wait() != 0:
            sys.exit("ffmpeg could not write the film.")
    else:
        if not args.gif:
            print("ffmpeg not found, so writing an animated GIF instead of an MP4.")
        out = share / f"film-{args.format}.gif"
        frames = []
        step = [0]

        def emit(frame):
            if step[0] % 3 == 0:  # 10 frames a second
                frames.append(frame.resize((W // 2, H // 2), Image.BILINEAR).quantize(colors=128))
            step[0] += 1

        render(scenes, W, H, emit)
        frames[0].save(out, save_all=True, append_images=frames[1:], duration=100, loop=0, optimize=True)

    print(f"Film: {out} ({total / FPS:.0f} seconds, {W}x{H})")


if __name__ == "__main__":
    main()
