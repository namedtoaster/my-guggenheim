"""Shared helpers for the My Guggenheim scripts: fonts, text wrapping, image loading.

Needs only Python 3.9+ and Pillow. Nothing here touches the network.
"""

import json
import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:  # pragma: no cover
    sys.exit("Pillow is missing. Install it with:  python3 -m pip install pillow")

SKILL_DIR = Path(__file__).resolve().parent.parent
FONT_DIR = SKILL_DIR / "assets" / "fonts"

# Colors of a white walled museum. The accent is the blue of a wall title.
WALL = (239, 238, 234)
INK = (28, 28, 28)
SOFT_INK = (92, 92, 92)
ACCENT = (24, 104, 196)

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".tif", ".tiff", ".bmp", ".gif"}

_HEIF_READY = None


def enable_heif():
    """Teach Pillow to open iPhone HEIC files when pillow-heif is installed."""
    global _HEIF_READY
    if _HEIF_READY is None:
        try:
            from pillow_heif import register_heif_opener

            register_heif_opener()
            _HEIF_READY = True
        except ImportError:
            _HEIF_READY = False
    return _HEIF_READY


def open_photo(path):
    """Open a photo, turned the right way up, in RGB."""
    path = Path(path)
    if path.suffix.lower() in {".heic", ".heif"} and not enable_heif():
        raise RuntimeError(
            f"{path.name} is a HEIC file. Install HEIC support with "
            "'python3 -m pip install pillow-heif', or convert it to JPEG first."
        )
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, WALL)
        bg.paste(im, mask=im.split()[-1])
        return bg
    return im.convert("RGB")


_FONT_FILES = {
    "regular": "Inter-Regular.otf",
    "medium": "Inter-Medium.otf",
    "semibold": "Inter-SemiBold.otf",
    "italic": "Inter-Italic.otf",
}
_font_cache = {}


def font(style, size):
    key = (style, size)
    if key not in _font_cache:
        path = FONT_DIR / _FONT_FILES[style]
        try:
            _font_cache[key] = ImageFont.truetype(str(path), size)
        except OSError:
            _font_cache[key] = ImageFont.load_default(size)
    return _font_cache[key]


def text_width(fnt, text):
    return fnt.getlength(text)


def wrap(text, fnt, max_width):
    """Split text into lines that fit max_width pixels."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        line = ""
        for word in words:
            trial = f"{line} {word}".strip()
            if text_width(fnt, trial) <= max_width or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def clamp_lines(lines, max_lines):
    """Keep at most max_lines, ending the last kept line with an ellipsis."""
    if len(lines) <= max_lines:
        return lines
    kept = lines[:max_lines]
    kept[-1] = kept[-1].rstrip(" ,;:.") + "..."
    return kept


def draw_lines(draw, xy, lines, fnt, fill, line_height):
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_height
    return y


def first_sentences(text, max_chars):
    """The opening sentence or two of a label, for places with little room."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    out = ""
    for part in parts:
        if len(out) + len(part) + 1 > max_chars and out:
            break
        out = f"{out} {part}".strip()
    return out


def fit_cover(im, size):
    """Scale and crop im to fill size exactly."""
    return ImageOps.fit(im, size, Image.LANCZOS, centering=(0.5, 0.5))


def fit_inside(im, size):
    im = im.copy()
    im.thumbnail(size, Image.LANCZOS)
    return im


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def tombstone_artist(artist):
    """'Dave Campbell (b. 1994)' or just the name."""
    name = (artist or {}).get("name") or "The Artist"
    born = (artist or {}).get("born")
    return f"{name} (b. {born})" if born else name


def hex_to_rgb(value, default=ACCENT):
    if not value:
        return default
    value = value.lstrip("#")
    if len(value) != 6:
        return default
    try:
        return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return default


def fit_sentences(text, fnt, max_width, max_lines, clip=True):
    """Wrapped lines holding as many whole sentences as fit in max_lines.

    When even the first sentence is too long, clips it, or returns [] if clip is False.
    """
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    best = None
    out = ""
    for part in parts:
        trial = f"{out} {part}".strip()
        lines = wrap(trial, fnt, max_width)
        if len(lines) > max_lines:
            break
        out, best = trial, lines
    if best:
        return best
    return clamp_lines(wrap(text, fnt, max_width), max_lines) if clip else []


# Wall colors for the gallery, cards and film. A show's mood can ask for darker
# walls: "black" for a black box room, "grey" for a quieter one, or any hex color.
WALLS = {
    "white": (WALL, INK, SOFT_INK),
    "grey": ((206, 205, 200), (24, 24, 24), (72, 72, 70)),
    "black": ((21, 21, 20), (236, 234, 228), (158, 156, 150)),
}


def wall_colors(ex):
    """(wall, ink, soft ink) for an exhibition, from its "walls" field."""
    walls = (ex.get("walls") or "white").strip().lower()
    if walls in WALLS:
        return WALLS[walls]
    wall = hex_to_rgb(walls, default=None)
    if wall is None:
        return WALLS["white"]
    light = (0.2126 * wall[0] + 0.7152 * wall[1] + 0.0722 * wall[2]) / 255
    return (wall, INK, SOFT_INK) if light > 0.5 else (wall, WALLS["black"][1], WALLS["black"][2])


def accent_color(ex):
    """The title color, lifted for dark walls so it stays readable."""
    wall = wall_colors(ex)[0]
    dark = (0.2126 * wall[0] + 0.7152 * wall[1] + 0.0722 * wall[2]) / 255 < 0.5
    if not ex.get("accent"):
        return (110, 166, 255) if dark else ACCENT
    color = hex_to_rgb(ex["accent"])
    light = (0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]) / 255
    if dark and light < 0.35:  # mix toward white until it reads on a dark wall
        color = tuple(int(c + (255 - c) * 0.45) for c in color)
    return color
