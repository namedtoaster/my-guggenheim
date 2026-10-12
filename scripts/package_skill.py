#!/usr/bin/env python3
"""Packs the exhibit skill into a zip you can upload to claude.ai.

    python3 scripts/package_skill.py        writes dist/my-guggenheim-exhibit.zip

The zip holds one folder, exhibit/, with SKILL.md at its top, which is the shape
claude.ai expects for an uploaded skill. No network.
"""

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "exhibit"
OUT = ROOT / "dist" / "my-guggenheim-exhibit.zip"


def main():
    OUT.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(SKILL.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts and path.name != ".DS_Store":
                zf.write(path, Path("exhibit") / path.relative_to(SKILL))
    print(f"Wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
