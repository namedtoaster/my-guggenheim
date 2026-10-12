# Changelog

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
