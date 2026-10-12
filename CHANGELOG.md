# Changelog

## 0.8.1 (2026-10-12)

- COMMUNITY.md, "On view elsewhere": other people's exhibitions are listed as links
  to their own posts. No one else's photos are ever stored in the repo, and a link
  comes down on request. A "Share your exhibition" form adds one.
- Validation allows real photos only in the author's own showcase folder.

## 0.8.0 (2026-10-12)

A real exhibition.

- `showcase/nothing-holds-still/`: the author's own show, fifteen photos in the
  Existential mood, published with every face, name, number plate and personal
  detail blacked out. Photos with faces were left out. The README features it.
- Showcase images may carry no camera data at all, and showcase gallery pages may
  load nothing from the internet. Validation checks both.

## 0.7.1 (2026-10-12)

- PRIVACY.md: My Guggenheim collects, stores, uploads and sells nothing, and says
  plainly what it cannot promise (how Claude handles what you send it, and anything
  you post).
- New checks that keep the promise true: no networking code in the scripts, and no
  gallery page that loads anything from the internet.

## 0.7.0 (2026-10-12)

- `share/wall-texts.md`: every word of a show in hanging order (intro wall, room
  panels, labels, timeline, closing note) to read anywhere without the photos.

## 0.6.1 (2026-10-12)

- Names that lead back to a person (their businesses, projects, apps, accounts,
  handles, websites) are now treated like faces: blacked out in the image and kept out
  of every text. The skill checks screenshots for them first.
- The examples no longer use the author's name.

## 0.6.0 (2026-10-12)

Nothing personal, ever, in the repo.

- `redact` in `exhibition.json`: black boxes over faces and personal details, drawn into
  the gallery, every card and the film. The skill checks every photo for them before a
  show is shared.
- Privacy checks in `scripts/validate.py`: no photos, videos or zips outside the drawn
  demo folders, no location data in images, no places in JSON, no email addresses.
  They run before every commit (`scripts/hooks/pre-commit`, switched on for Claude
  sessions by `.claude/settings.json`) and in CI.
- `.gitignore` keeps HEIC, video, zips and photo folders out wherever they land.

## 0.5.1 (2026-10-12)

The whole label, on the card.

- Work cards now carry the full label. The photo gives way first, then the type
  steps down, until every paragraph fits.
- The intro wall is no longer cut to its first paragraph: it runs whole across two
  cards, with "continued" between them.
- A note when a carousel goes over Instagram's 20 cards.

## 0.5.0 (2026-10-12)

Every share points back here.

- Cards, the story cover, the film's closing frame and the caption carry a small
  "Made with My Guggenheim" line with the project link.
- The gallery page gains a "Make your own" box and share buttons for X, Bluesky,
  Threads, Facebook, LinkedIn, Reddit and email, filled in with the show and the link.
- `"share": {"credit": false}` turns the project line off.

## 0.4.0 (2026-10-12)

Any mood.

- Moods replace the four tones: Museum, Existential, Retrospective, Deadpan, Tender,
  Romantic, Noir, Manifesto, Natural history, Far future and For kids, plus any mood
  asked for in the person's own words. Each sets the curator's sensibility, the
  touchstones and the walls.
- `walls` in `exhibition.json`: white, grey, black or any color, carried through the
  gallery, the cards and the film. Title colors lift themselves on dark walls.
- A philosophy page, a stories page, and a "My story" form for sharing yours.

## 0.3.0 (2026-10-12)

Send a zip.

- `inspect_photos.py` reads zip files (originals keep their date and place, unlike
  photos attached one by one) and videos (one frame becomes a still, dated from the
  recording). HEIC is supported with `pillow-heif`.
- The README and the skill now recommend sending a zip.
- Timeline cards and the film no longer cut a period's text off mid sentence.

## 0.2.0 (2026-10-12)

Labels that read like a modern museum.

- Labels are now 150 to 250 words in two or three paragraphs: close looking, a real
  art historical lineage, then context and a quiet turn. The intro wall is 350 to 500
  words.
- The voice guide has a table of touchstones (Paik, Hopper, Abbott, Duchamp, the Dutch
  still life and more), each with the reason it fits, so comparisons stay accurate.
- Room panels: each period of the timeline opens its own room in the gallery.
- Accession numbers under each credit line, and labels that stay beside a photo that
  holds still while you read.
- The demo show is rewritten at the new length.

## 0.1.0 (2026-10-12)

The first exhibition.

- `exhibit` skill: reads photos and their metadata, asks one short question when the
  dates or places are missing, and curates a show in one of four tones.
- `inspect_photos.py`: dates from camera data or file names, camera, rough place (city
  level), colors and previews. Never writes an exact location.
- `build_gallery.py`: a single file gallery page (light and dark), a 1080x1350
  carousel, a 1080x1920 story cover and a caption. Strips camera data from every image.
- `make_film.py`: a silent exhibition film in vertical, square or landscape, with a GIF
  fallback when ffmpeg is missing.
- A demo show, a validation script, CI, and a release job that publishes the skill as a
  zip for claude.ai.
