# Working in My Guggenheim

- The skill lives in `skills/exhibit/`. `.claude/skills/exhibit` is a link to it, so a
  cloud session opened on this repo (or a fork) can use `/exhibit` straight away. Edit
  the real folder, never the link.
- Scripts use only Python 3.9+, Pillow and (for the film) ffmpeg. No network, no other
  packages. They must keep working in claude.ai's code execution sandbox.
- Run `python3 scripts/validate.py` before every push. It also builds the demo show.
- Never commit anyone's personal photos. `exhibits/` is ignored for that reason.
- No long dashes (em or en) anywhere. Plain words.
