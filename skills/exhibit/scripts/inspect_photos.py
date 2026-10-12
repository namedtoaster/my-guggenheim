#!/usr/bin/env python3
"""Reads a set of photos and writes what a curator needs to know about them.

    python3 inspect_photos.py PHOTO_OR_FOLDER [...] --out EXHIBIT_FOLDER

For each photo it records the size, when it was taken (from the camera data, the
file name, or not at all), the camera, a rough place, and the colors. It writes:

    EXHIBIT_FOLDER/manifest.json      everything above, in date order
    EXHIBIT_FOLDER/previews/*.jpg     small copies for looking at each photo

Paths in manifest.json are relative to EXHIBIT_FOLDER.

Privacy: the exact GPS position is never written. Only a rough position (about
11 km) is kept, so the curator can name the city or region and nothing closer.
Read only on the originals. No network.
"""

import argparse
import colorsys
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

from common import IMAGE_SUFFIXES, enable_heif, open_photo, write_json

from PIL import ExifTags, Image

EXIF_IFD = 0x8769
GPS_IFD = 0x8825

FILENAME_DATES = [
    # IMG_20230514_181122, PXL_20230514_181122123, 20230514_181122
    (re.compile(r"(20\d{2}|19\d{2})(\d{2})(\d{2})[_-](\d{2})(\d{2})(\d{2})"), "%Y%m%d%H%M%S"),
    # Screenshot 2023-05-14 at 18.11.22, WhatsApp Image 2023-05-14 at 18.11.22
    (re.compile(r"(20\d{2}|19\d{2})-(\d{2})-(\d{2})[ _T]?(?:at )?(\d{2})[.:\-](\d{2})[.:\-](\d{2})"), "%Y%m%d%H%M%S"),
    (re.compile(r"(20\d{2}|19\d{2})-(\d{2})-(\d{2})"), "%Y%m%d"),
    (re.compile(r"(20\d{2}|19\d{2})(\d{2})(\d{2})"), "%Y%m%d"),
]


def slug(text):
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "work"


def collect(paths):
    files = []
    for raw in paths:
        p = Path(raw).expanduser()
        if p.is_dir():
            files += sorted(f for f in p.rglob("*") if f.suffix.lower() in IMAGE_SUFFIXES and not f.name.startswith("."))
        elif p.is_file():
            files.append(p)
        else:
            print(f"Skipping {raw}: not found", file=sys.stderr)
    seen, out = set(), []
    for f in files:
        key = f.resolve()
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out


def exif_data(path):
    try:
        im = Image.open(path)
        ex = im.getexif()
    except Exception:
        return {}, {}
    base = {ExifTags.TAGS.get(k, k): v for k, v in ex.items()}
    try:
        base.update({ExifTags.TAGS.get(k, k): v for k, v in ex.get_ifd(EXIF_IFD).items()})
    except Exception:
        pass
    try:
        gps = {ExifTags.GPSTAGS.get(k, k): v for k, v in ex.get_ifd(GPS_IFD).items()}
    except Exception:
        gps = {}
    return base, gps


def parse_exif_date(base):
    for key in ("DateTimeOriginal", "DateTimeDigitized", "DateTime"):
        value = base.get(key)
        if isinstance(value, bytes):
            value = value.decode(errors="ignore")
        if isinstance(value, str) and value.strip() and not value.startswith("0000"):
            try:
                return datetime.strptime(value.strip()[:19], "%Y:%m:%d %H:%M:%S")
            except ValueError:
                continue
    return None


def parse_filename_date(name):
    for pattern, fmt in FILENAME_DATES:
        m = pattern.search(name)
        if m:
            try:
                when = datetime.strptime("".join(m.groups()), fmt)
            except ValueError:
                continue
            if 1990 <= when.year <= datetime.now().year + 1:
                return when
    return None


def to_degrees(value, ref):
    try:
        d, m, s = (float(x) for x in value)
    except Exception:
        return None
    deg = d + m / 60 + s / 3600
    if ref in ("S", "W", b"S", b"W"):
        deg = -deg
    return deg


def rough_place(gps):
    lat = to_degrees(gps.get("GPSLatitude"), gps.get("GPSLatitudeRef"))
    lon = to_degrees(gps.get("GPSLongitude"), gps.get("GPSLongitudeRef"))
    if lat is None or lon is None or (lat == 0 and lon == 0):
        return None
    return {"lat": round(lat, 1), "lon": round(lon, 1)}


def text_value(value):
    if isinstance(value, bytes):
        value = value.decode(errors="ignore")
    if value is None:
        return None
    value = str(value).replace("\x00", "").strip()
    return value or None


def camera(base):
    make = text_value(base.get("Make"))
    model = text_value(base.get("Model"))
    if make and model and model.lower().startswith(make.lower().split()[0]):
        make = None
    name = " ".join(x for x in (make, model) if x) or None
    details = {}
    if base.get("FocalLength"):
        try:
            details["focal_mm"] = round(float(base["FocalLength"]), 1)
        except (TypeError, ValueError):
            pass
    if base.get("ExposureTime"):
        try:
            t = float(base["ExposureTime"])
            details["shutter"] = f"1/{round(1 / t)}" if 0 < t < 1 else f"{t:g}s"
        except (TypeError, ValueError, ZeroDivisionError):
            pass
    if base.get("FNumber"):
        try:
            details["aperture"] = f"f/{float(base['FNumber']):g}"
        except (TypeError, ValueError):
            pass
    if base.get("ISOSpeedRatings"):
        details["iso"] = base["ISOSpeedRatings"]
    flash = base.get("Flash")
    if isinstance(flash, int):
        details["flash_fired"] = bool(flash & 1)
    lens = text_value(base.get("LensModel"))
    if lens:
        details["lens"] = lens
    software = text_value(base.get("Software"))
    if software:
        details["software"] = software
    return name, details


HUES = [
    (15, "red"), (45, "orange"), (70, "yellow"), (160, "green"),
    (200, "cyan"), (255, "blue"), (290, "violet"), (335, "pink"), (360, "red"),
]


def hue_name(h):
    deg = h * 360
    for limit, name in HUES:
        if deg <= limit:
            return name
    return "red"


def colors(im):
    small = im.copy()
    small.thumbnail((160, 160))
    q = small.quantize(colors=5, method=Image.Quantize.MEDIANCUT)
    palette = q.getpalette()[:15]
    counts = sorted(q.getcolors(), reverse=True)
    swatches = []
    for count, idx in counts:
        r, g, b = palette[idx * 3 : idx * 3 + 3]
        swatches.append(f"#{r:02x}{g:02x}{b:02x}")
    pixels = list(small.get_flattened_data() if hasattr(small, "get_flattened_data") else small.getdata())
    n = len(pixels)
    light = sat = 0.0
    hue_weight = {}
    for r, g, b in pixels:
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        light += l
        sat += s
        if s > 0.2 and 0.1 < l < 0.9:
            name = hue_name(h)
            hue_weight[name] = hue_weight.get(name, 0) + s
    light, sat = light / n, sat / n
    words = []
    words.append("bright" if light > 0.62 else "dim" if light < 0.35 else "mid-toned")
    words.append("vivid" if sat > 0.45 else "muted" if sat < 0.18 else "moderately saturated")
    leaning = max(hue_weight, key=hue_weight.get) if hue_weight else None
    if leaning and hue_weight[leaning] / n > 0.08:
        words.append(f"{leaning}-leaning")
    return {
        "palette": swatches,
        "brightness": round(light, 2),
        "saturation": round(sat, 2),
        "mood": words,
    }


def guess_kind(path, base, size):
    name = path.name.lower()
    if "screenshot" in name or "screen shot" in name or "simulator" in name:
        return "screenshot"
    if base.get("Make") or base.get("Model"):
        return "photograph"
    w, h = size
    ratio = max(w, h) / min(w, h)
    if ratio > 1.9 and path.suffix.lower() == ".png":
        return "screenshot (probably)"
    if path.suffix.lower() == ".gif":
        return "animated or web image"
    return "image (no camera data)"


def periods(works, gap_days=45):
    """Group dated works into runs separated by long gaps. A hint for the timeline."""
    dated = [w for w in works if w["taken"]]
    groups = []
    for w in dated:
        when = datetime.fromisoformat(w["taken"])
        if groups and when - groups[-1]["_last"] <= timedelta(days=gap_days):
            groups[-1]["works"].append(w["id"])
            groups[-1]["_last"] = when
        else:
            groups.append({"start": w["taken"][:10], "works": [w["id"]], "_last": when})
    for g in groups:
        g["end"] = g.pop("_last").isoformat()[:10]
    return groups


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("photos", nargs="+", help="photo files or folders of photos")
    ap.add_argument("--out", required=True, help="exhibit folder to write into")
    ap.add_argument("--preview-size", type=int, default=768)
    args = ap.parse_args()

    out = Path(args.out)
    (out / "previews").mkdir(parents=True, exist_ok=True)
    files = collect(args.photos)
    if not files:
        sys.exit("No photos found.")
    if any(f.suffix.lower() in {".heic", ".heif"} for f in files):
        enable_heif()

    works, problems, used_ids = [], [], set()
    today = datetime.now()
    for path in files:
        try:
            im = open_photo(path)
        except Exception as err:  # unreadable or HEIC without support
            problems.append({"file": str(path), "problem": str(err)})
            continue
        base, gps = exif_data(path)

        when, source = parse_exif_date(base), "camera"
        if when is None:
            when, source = parse_filename_date(path.name), "file name"
        if when is None:
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            # A file modified in the last two days was almost always just
            # uploaded or copied, so its date says nothing about the photo.
            if today - mtime > timedelta(days=2):
                when, source = mtime, "file modified (weak)"
            else:
                source = "unknown"

        wid = slug(path.stem)
        n = 2
        while wid in used_ids:
            wid = f"{slug(path.stem)}-{n}"
            n += 1
        used_ids.add(wid)

        preview = im.copy()
        preview.thumbnail((args.preview_size, args.preview_size), Image.LANCZOS)
        preview_path = out / "previews" / f"{wid}.jpg"
        preview.save(preview_path, "JPEG", quality=80)

        cam, cam_details = camera(base)
        works.append({
            "id": wid,
            "file": os.path.relpath(path.resolve(), out.resolve()),
            "preview": os.path.relpath(preview_path.resolve(), out.resolve()),
            "width": im.width,
            "height": im.height,
            "orientation": "portrait" if im.height > im.width * 1.05 else "landscape" if im.width > im.height * 1.05 else "square",
            "kind": guess_kind(path, base, im.size),
            "taken": when.isoformat(timespec="minutes") if when else None,
            "date_source": source,
            "camera": cam,
            "camera_details": cam_details,
            "rough_place": rough_place(gps),
            "colors": colors(im),
        })

    works.sort(key=lambda w: (w["taken"] is None, w["taken"] or "", w["id"]))
    manifest = {
        "made_by": "My Guggenheim inspect_photos.py",
        "count": len(works),
        "dated": sum(1 for w in works if w["taken"]),
        "with_place": sum(1 for w in works if w["rough_place"]),
        "suggested_periods": periods(works),
        "works": works,
        "problems": problems,
    }
    write_json(out / "manifest.json", manifest)

    print(f"Read {len(works)} photos into {out / 'manifest.json'}")
    print(f"  dated: {manifest['dated']}   with a rough place: {manifest['with_place']}")
    undated = [w["id"] for w in works if not w["taken"]]
    if undated:
        print(f"  no date for: {', '.join(undated)}")
    for p in problems:
        print(f"  could not read {p['file']}: {p['problem']}")


if __name__ == "__main__":
    main()
