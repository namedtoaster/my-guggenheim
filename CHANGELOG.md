# Changelog

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
