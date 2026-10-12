#!/usr/bin/env python3
"""Checks the repo before a push or a pull request is merged.

    python3 scripts/validate.py            all checks, including building the demo show
    python3 scripts/validate.py --quick    skip building the demo

  - every skill has a SKILL.md with a name matching its folder and a description
  - every SKILL.md stays under 500 lines
  - the plugin and marketplace JSON files parse
  - no long dashes (em or en) in Markdown, JSON or Python files git tracks
  - privacy: no personal photos, videos or zips outside the known folders, no
    location data in any image, no places in any manifest, no email addresses
  - the demo photos build into a gallery, share cards and a film

Only the demo build writes files, all of them under examples/demo/ (ignored by git).
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []


def repo_files():
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout
        return [ROOT / f for f in out.split("\0") if f and (ROOT / f).is_file()]
    except Exception:
        return [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]


# Skills
for skill in sorted((ROOT / "skills").iterdir()):
    if not skill.is_dir():
        continue
    file = skill / "SKILL.md"
    if not file.exists():
        errors.append(f"skills/{skill.name}: missing SKILL.md")
        continue
    text = file.read_text(encoding="utf-8")
    front = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not front:
        errors.append(f"skills/{skill.name}/SKILL.md: missing frontmatter")
        continue
    name = re.search(r"^name:\s*(.+)$", front.group(1), re.M)
    desc = re.search(r"^description:\s*(.+)$", front.group(1), re.M)
    if not name or name.group(1).strip() != skill.name:
        errors.append(f"skills/{skill.name}/SKILL.md: name should be {skill.name}")
    if not desc:
        errors.append(f"skills/{skill.name}/SKILL.md: missing description")
    elif len(desc.group(1)) > 1024:
        errors.append(f"skills/{skill.name}/SKILL.md: description over 1024 characters")
    lines = text.count("\n") + 1
    if lines > 500:
        errors.append(f"skills/{skill.name}/SKILL.md: {lines} lines, keep it under 500")

# JSON
for rel in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", "examples/demo/exhibition.json"):
    try:
        json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as err:
        errors.append(f"{rel}: {err}")

# Style
DASHES = re.compile("[\u2013\u2014]")
for path in repo_files():
    if path.suffix not in {".md", ".json", ".py", ".yml", ".html"} or "fonts" in path.parts:
        continue
    for n, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        if DASHES.search(line):
            errors.append(f"{path.relative_to(ROOT)}:{n}: long dash, use a comma, period or parentheses")

# Privacy. Nothing about a real person may ever be committed: no personal photos,
# no location data, no places, no email addresses. Runs on every commit (see
# scripts/hooks/pre-commit) and in CI.
MEDIA = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".gif", ".tif", ".tiff", ".bmp",
         ".mov", ".mp4", ".m4v", ".avi", ".zip"}
# Only these folders may hold images. docs/ and assets/ are drawn, not photographed.
# showcase/ holds exhibitions their owner chose to publish, checked one by one with
# personal details blacked out; its images must carry no camera data at all.
MEDIA_ALLOWED = ("docs/images/", "skills/exhibit/assets/", "showcase/")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
EMAIL_OK = ("noreply@anthropic.com", "@users.noreply.github.com", "@example.com")
for path in repo_files():
    rel = path.relative_to(ROOT).as_posix()
    if path.suffix.lower() in MEDIA:
        if not rel.startswith(MEDIA_ALLOWED):
            errors.append(f"{rel}: photos, videos and zips can't be committed outside {', '.join(MEDIA_ALLOWED)} (personal photos stay in exhibits/, which git ignores)")
            continue
        try:
            from PIL import Image
            with Image.open(path) as im:
                exif = im.getexif()
                if exif.get_ifd(0x8825):
                    errors.append(f"{rel}: carries GPS location data; re-save it without camera data")
                elif rel.startswith("showcase/") and len(exif):
                    errors.append(f"{rel}: showcase images must carry no camera data at all")
        except Exception:
            pass
    if path.suffix == ".json":
        text = path.read_text(encoding="utf-8", errors="ignore")
        if re.search(r'"rough_place"\s*:\s*\{', text) or re.search(r'"lat"\s*:', text):
            errors.append(f"{rel}: holds a place (rough_place or lat/lon); manifests with places stay in exhibits/")
    if path.suffix in {".md", ".json", ".py", ".yml", ".html", ".txt"}:
        for n, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            for addr in EMAIL.findall(line):
                if not any(ok in addr for ok in EMAIL_OK):
                    errors.append(f"{rel}:{n}: an email address ({addr}); leave personal contact details out")

# Published galleries must load nothing from the internet either.
for page in (ROOT / "showcase").rglob("index.html") if (ROOT / "showcase").exists() else []:
    text = page.read_text(encoding="utf-8")
    if re.findall(r'(?:src|srcset)="https?:|<link[^>]+href="https?:|url\(\s*["\']?https?:|@import|fetch\(|XMLHttpRequest|sendBeacon|new Image\(', text):
        errors.append(f"{page.relative_to(ROOT)}: loads something from the internet")

# No network, ever: the scripts must not be able to send anything anywhere.
NETWORK = re.compile(r"^\s*(import|from)\s+(urllib|requests|http\.client|httpx|aiohttp|socket|ftplib|smtplib)\b", re.M)
for path in (ROOT / "skills").rglob("*.py"):
    if NETWORK.search(path.read_text(encoding="utf-8")):
        errors.append(f"{path.relative_to(ROOT)}: imports a networking module; the scripts must work offline and send nothing")

# Demo build
if "--quick" not in sys.argv:
    scripts = ROOT / "skills" / "exhibit" / "scripts"
    demo = ROOT / "examples" / "demo"
    steps = [
        [sys.executable, str(ROOT / "examples" / "make_demo_photos.py"), str(demo / "photos")],
        [sys.executable, str(scripts / "inspect_photos.py"), str(demo / "photos"), "--out", str(demo)],
        [sys.executable, str(scripts / "build_gallery.py"), str(demo)],
        [sys.executable, str(scripts / "make_film.py"), str(demo), "--format", "square", "--seconds", "1.5", "--max-works", "3"],
    ]
    for step in steps:
        result = subprocess.run(step, capture_output=True, text=True)
        if result.returncode != 0:
            errors.append(f"demo build failed at {Path(step[1]).name}:\n{result.stdout}{result.stderr}")
            break
    else:
        html = (demo / "gallery" / "index.html").read_text(encoding="utf-8")
        if "github.com/namedtoaster/my-guggenheim" not in html or 'data-net="bluesky"' not in html:
            errors.append("demo gallery is missing its share buttons or project link")
        if "github.com/namedtoaster/my-guggenheim" not in (demo / "share" / "caption.txt").read_text():
            errors.append("demo caption is missing the project link")
        if "Late Suburban Currents" not in html or html.count('class="room') != 6:
            errors.append("demo gallery is missing its title or rooms")
        # The gallery page must load nothing from anywhere: no fonts, scripts, images or trackers.
        loads = re.findall(r'(?:src|srcset)="https?:|<link[^>]+href="https?:|url\(\s*["\']?https?:|@import|fetch\(|XMLHttpRequest|sendBeacon|new Image\(', html)
        if loads:
            errors.append(f"demo gallery loads something from the internet: {loads}")
        if "Late Suburban Currents" not in (demo / "share" / "wall-texts.md").read_text():
            errors.append("demo wall-texts.md is missing")
        if not list((demo / "share").glob("film-square.*")):
            errors.append("demo film was not written")
        if len(list((demo / "share").glob("*.png"))) < 8:
            errors.append("demo share cards are missing")
        # The same photos sent as a zip must come through with their dates.
        import tempfile
        import zipfile
        with tempfile.TemporaryDirectory() as tmp:
            zpath = Path(tmp) / "photos.zip"
            with zipfile.ZipFile(zpath, "w") as zf:
                for f in (demo / "photos").iterdir():
                    zf.write(f, f"My Photos/{f.name}")
                zf.writestr("__MACOSX/My Photos/._junk.jpg", b"not a photo")
            result = subprocess.run([sys.executable, str(scripts / "inspect_photos.py"), str(zpath), "--out", str(Path(tmp) / "out")],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                errors.append(f"reading a zip failed:\n{result.stdout}{result.stderr}")
            else:
                m = json.loads((Path(tmp) / "out" / "manifest.json").read_text())
                if m["count"] != 6 or m["dated"] != 6 or m["problems"]:
                    errors.append(f"reading a zip gave {m['count']} photos, {m['dated']} dated, problems {m['problems']}")

if errors:
    print(f"{len(errors)} problem(s):")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
print("All checks passed.")
