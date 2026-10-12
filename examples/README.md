# The demo show

*Late Suburban Currents*, six invented photos by "A. Demo", with made up dates,
cameras and places. Use it to see what the skill makes without using your own photos.

```
python3 -m pip install pillow
python3 examples/make_demo_photos.py examples/demo/photos
python3 skills/exhibit/scripts/inspect_photos.py examples/demo/photos --out examples/demo
python3 skills/exhibit/scripts/build_gallery.py examples/demo
python3 skills/exhibit/scripts/make_film.py examples/demo
```

Then open `examples/demo/gallery/index.html` and look in `examples/demo/share/`.

`examples/demo/exhibition.json` is what the curator writes. It is a good reference for
the voice, and for the format in
[skills/exhibit/references/schema.md](../skills/exhibit/references/schema.md).
