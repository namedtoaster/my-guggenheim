#!/usr/bin/env python3
"""Checks the repo before a push or a pull request is merged.

    python3 scripts/validate.py            all checks, including building the demo show
    python3 scripts/validate.py --quick    skip building the demo

  - every skill has a SKILL.md with a name matching its folder and a description
  - every SKILL.md stays under 500 lines
  - the plugin and marketplace JSON files parse
  - no long dashes (em or en) in Markdown, JSON or Python files git tracks
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
        if "Late Suburban Currents" not in html or html.count('class="room') != 6:
            errors.append("demo gallery is missing its title or rooms")
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
