# Working in My Guggenheim

- The skill lives in `skills/exhibit/`. `.claude/skills/exhibit` is a link to it, so a
  cloud session opened on this repo (or a fork) can use `/exhibit` straight away. Edit
  the real folder, never the link.
- Scripts use only Python 3.9+, Pillow and (for the film) ffmpeg. No network, no other
  packages. They must keep working in claude.ai's code execution sandbox.
- Run `python3 scripts/validate.py` before every push. It also builds the demo show.
- **No personal information is ever committed.** No personal photos, videos or zips, no
  places or coordinates, no email addresses, no faces. Exhibitions live in `exhibits/`,
  which git ignores. `scripts/validate.py` enforces this and runs before every commit
  (`scripts/hooks/pre-commit`, turned on by the session start hook in
  `.claude/settings.json`) and in CI. Never bypass it with `--no-verify`.
- Showcase material in the repo (README images, examples) is drawn by
  `examples/make_demo_photos.py`, never photographed.
- No long dashes (em or en) anywhere. Plain words.
