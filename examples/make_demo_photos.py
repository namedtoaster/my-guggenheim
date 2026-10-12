#!/usr/bin/env python3
"""Draws a handful of ordinary looking "photos" with made up camera data, for trying
My Guggenheim without your own pictures and for the automated checks.

    python3 examples/make_demo_photos.py examples/demo/photos

The dates, cameras and places are invented. No network.
"""

import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

random.seed(7)

PHOTOS = [
    # name, date, camera, (lat, lon) or None, painter
    ("IMG_parking_lot_sunset.jpg", "2019:06:21 20:41:09", ("Apple", "iPhone 8"), (40.73, -73.99), "sunset"),
    ("IMG_cold_coffee.jpg", "2019:11:02 08:12:44", ("Apple", "iPhone 8"), (40.73, -73.99), "coffee"),
    ("PXL_20220314_172233.jpg", None, ("Google", "Pixel 6"), (41.88, -87.63), "window"),
    ("IMG_receipt.jpg", "2022:08:09 13:05:51", ("Google", "Pixel 6"), None, "receipt"),
    ("Screenshot 2024-01-03 at 23.58.10.png", None, None, None, "screenshot"),
    ("IMG_pigeon_maybe.jpg", "2026:10:11 15:22:03", ("Apple", "iPhone 15"), (40.78, -73.96), "pigeon"),
]


def gradient(size, top, bottom):
    w, h = size
    im = Image.new("RGB", size)
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / (h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return im


def noise(im, amount=10):
    grain = Image.effect_noise(im.size, amount).convert("RGB")
    return Image.blend(im, grain, 0.06)


def sunset():
    im = gradient((1600, 1200), (255, 150, 90), (70, 40, 110))
    d = ImageDraw.Draw(im)
    d.ellipse((980, 520, 1180, 720), fill=(255, 214, 140))
    d.rectangle((0, 820, 1600, 1200), fill=(52, 52, 58))
    for x in range(60, 1600, 220):
        d.line([(x, 1200), (x + 140, 860)], fill=(235, 220, 120), width=8)
    d.rectangle((1240, 300, 1256, 840), fill=(30, 30, 34))
    d.ellipse((1196, 270, 1300, 330), fill=(255, 245, 210))
    return noise(im.filter(ImageFilter.GaussianBlur(1.2)))


def coffee():
    im = gradient((1200, 1500), (196, 170, 140), (150, 120, 96))
    d = ImageDraw.Draw(im)
    d.ellipse((260, 420, 940, 1100), fill=(245, 243, 238))
    d.ellipse((330, 490, 870, 1030), fill=(96, 62, 38))
    d.ellipse((420, 600, 600, 700), fill=(150, 110, 80))
    d.arc((880, 640, 1060, 880), -70, 70, fill=(245, 243, 238), width=40)
    return noise(im.filter(ImageFilter.GaussianBlur(2)))


def window():
    im = gradient((1500, 1500), (120, 160, 210), (200, 215, 230))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1500, 1500), outline=(40, 40, 46), width=120)
    d.rectangle((720, 0, 780, 1500), fill=(40, 40, 46))
    d.rectangle((0, 720, 1500, 780), fill=(40, 40, 46))
    for _ in range(14):
        x, y = random.randint(150, 1300), random.randint(150, 700)
        d.ellipse((x, y, x + 180, y + 70), fill=(240, 244, 248))
    return noise(im.filter(ImageFilter.GaussianBlur(3)))


def receipt():
    im = gradient((1100, 1600), (60, 60, 64), (40, 40, 44))
    d = ImageDraw.Draw(im)
    d.polygon([(300, 120), (820, 150), (790, 1500), (270, 1470)], fill=(246, 244, 236))
    for i in range(22):
        y = 220 + i * 52
        d.line([(340, y), (340 + random.randint(180, 400), y + 2)], fill=(120, 120, 120), width=10)
    return noise(im.filter(ImageFilter.GaussianBlur(1)))


def screenshot():
    im = Image.new("RGB", (1179, 2556), (250, 250, 250))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1179, 260), fill=(242, 242, 247))
    for i in range(9):
        y = 320 + i * 230
        d.rounded_rectangle((60, y, 1119, y + 190), 30, fill=(229, 229, 234) if i % 2 else (0, 122, 255))
    return im


def pigeon():
    im = gradient((1400, 1050), (170, 172, 176), (120, 118, 116))
    d = ImageDraw.Draw(im)
    d.ellipse((520, 420, 900, 760), fill=(110, 116, 132))
    d.ellipse((820, 330, 980, 480), fill=(100, 108, 126))
    d.polygon([(975, 400), (1040, 420), (975, 440)], fill=(60, 60, 60))
    d.ellipse((900, 380, 922, 402), fill=(230, 110, 40))
    return noise(im.filter(ImageFilter.GaussianBlur(9)), 30)


def rational_dms(value):
    value = abs(value)
    d = int(value)
    m = int((value - d) * 60)
    s = round(((value - d) * 60 - m) * 60, 2)
    return (float(d), float(m), float(s))


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "examples/demo/photos")
    out.mkdir(parents=True, exist_ok=True)
    painters = {f.__name__: f for f in (sunset, coffee, window, receipt, screenshot, pigeon)}
    for name, date, cam, place, painter in PHOTOS:
        im = painters[painter]()
        exif = Image.Exif()
        if cam:
            exif[0x010F], exif[0x0110] = cam
        if date:
            exif.get_ifd(0x8769)[0x9003] = date
        if place:
            gps = exif.get_ifd(0x8825)
            gps[1] = "N" if place[0] >= 0 else "S"
            gps[2] = rational_dms(place[0])
            gps[3] = "E" if place[1] >= 0 else "W"
            gps[4] = rational_dms(place[1])
        path = out / name
        if path.suffix == ".png":
            im.save(path)
        else:
            im.save(path, "JPEG", quality=88, exif=exif)
    print(f"Wrote {len(PHOTOS)} demo photos to {out}")


if __name__ == "__main__":
    main()
