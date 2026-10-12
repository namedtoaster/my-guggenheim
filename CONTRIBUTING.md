# Contributing

Thanks for helping. My Guggenheim is maintained by one person, so the bar is simple:
every change should make the exhibitions more fun to make, to read, or to share,
without making anyone's photos less private.

## What gets accepted

| Change | How |
| --- | --- |
| A fix to a script, a card or the gallery page | Pull request |
| A better rule or example in the voice guide | Pull request, or the "curator said" issue |
| A new tone | Pull request adding it to `skills/exhibit/references/voice.md`, with one example label |
| A new output (a card size, a film style, a print layout) | Start a post in Discussions first |

## Rules for scripts

- Python 3.9+, Pillow and (for the film) ffmpeg only. No network, no other packages.
  They have to run in claude.ai's code execution sandbox as well as on a laptop.
- Explain what a script does at the top. Expect every line to be read in review.
- Never write exact locations. Strip camera data from every image you save.

## Rules for the voice

- Sincere, never winking. The joke is the museum, never the person.
- No guessing who people are, no comments on anyone's looks, no places closer than a city.
- Read `skills/exhibit/references/voice.md` before changing it.

## Style

- Plain words. No long dashes (em or en dashes) in prose or wall texts. Use a period,
  a comma or parentheses.
- Never commit personal photos, including in issues. The demo photos are drawn by
  `examples/make_demo_photos.py`.

## Privacy

Nothing about a real person goes in this repo, and nobody's photos are stored here.
To share an exhibition, add a link to [COMMUNITY.md](COMMUNITY.md) with the
"Share your exhibition" form. Nothing else about a real person goes in either: no personal photos, videos or zips,
no places or coordinates, no faces, no email addresses. Turn on the check that runs
before every commit, once per clone:

```
git config core.hooksPath scripts/hooks
```

## Checks

Run `python3 scripts/validate.py` before opening a pull request. It checks the skill,
the JSON files and the style, then builds the demo show from scratch. Pull requests
run it too.
