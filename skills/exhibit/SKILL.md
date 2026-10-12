---
name: exhibit
description: Turns any set of photos into a museum exhibition of the person's own life. Writes earnest, slightly ridiculous wall texts for each picture in any mood the person asks for (museum, existential, noir, tender or their own words), builds an "Artist's Life" timeline from the photos' dates and places, and makes a gallery page, social media cards and a short vertical video to post. Use when someone uploads or points to photos and wants an exhibit, a gallery, wall labels, a museum description, an art critique of their pictures, or says "My Guggenheim".
---

# Exhibit

Turn a camera roll into a museum show. The person brings photos, the more random the
better. You are the curator: you look closely, read the metadata, and write the wall
texts with total sincerity. The scripts do the building.

The spirit, from the person who started this: they used to try to "win" at museums,
reading every label and understanding everything. Now they read what they can and get
what they get. The texts should be fun to read and fine to skip.

## What you make

In an exhibit folder:

- `gallery/index.html`: the exhibition as one page. Intro wall, a room per work with
  its label, the timeline, a closing note. Opens anywhere, no internet needed.
- `share/`: a carousel (`01-wall-text.png`, one card per work, `timeline.png`), a story
  cover (1080x1920) and `caption.txt`.
- `share/film-vertical.mp4`: a 30 to 60 second walk through the show for Reels,
  TikTok or Shorts.

## Before you start

- The scripts are in `scripts/` next to this file. Call this skill's folder
  `SKILL_DIR` below and use its real path.
- They need Python 3.9+ and Pillow. If `python3 -c "import PIL"` fails, run
  `python3 -m pip install pillow`. iPhone HEIC photos also need `pillow-heif`.
  The film needs `ffmpeg`. Without it you get a GIF instead.
- Where to work: in a project, `exhibits/<short-name>/` (git ignores it, so private
  photos are never committed). In claude.ai, work in `/home/claude/exhibits/<short-name>/`
  and copy the finished `gallery/` and `share/` folders to `/mnt/user-data/outputs/`
  so the person can download them.

## Step 1: Gather the photos

Use the photos the person uploaded or pointed to. Uploads in claude.ai are in
`/mnt/user-data/uploads/`. In Claude Code, use the paths they give or the upload paths
in the conversation. 3 is the minimum, 6 to 15 is the sweet spot, more than 24 makes a
long film (the film uses the first 12 unless told otherwise).

- **A zip is the best way to send photos.** Photos attached one by one in a chat app
  usually lose their date and place; a zip keeps the originals. Pass the zip itself
  to the script below. If someone attaches loose photos and they come back undated,
  suggest a zip next time.
- **Videos work too.** The script saves one frame as a still and dates it from the
  video's own recording date. Call the medium "Video still, from an N second moving
  image". If the moment you want is not the frame it picked, take another with ffmpeg.
- **iPhone photos are HEIC.** If the script reports HEIC problems, run
  `python3 -m pip install pillow-heif` and run it again.

## Step 2: Read them

```
python3 SKILL_DIR/scripts/inspect_photos.py PHOTOS_FOLDERS_ZIPS_OR_VIDEOS... --out EXHIBIT
```

This writes `EXHIBIT/manifest.json` (date, where the date came from, camera, rough
place, colors, size, a guess at the kind of image) and small previews in
`EXHIBIT/previews/`. It never writes an exact location.

Then **look at every preview** with your image reading tool. Note what is actually in
each one: subject, light, composition, anything odd. The labels depend on it.

## Step 3: Fill the gaps, in one message

Photos sent through a chat app or the Claude app often lose their date and place on
the way. Check `dated` and `with_place` in the manifest. Ask everything you need in a
single short message, with defaults, so the person can just say "go":

- How should the artist be credited? (a name, initials, or "The Artist")
- If more than a third have no date: "Roughly when were these taken? A year, or
  'college', is plenty." Same for places if the timeline would be thin.
- Mood: anything they like, in their own words. Offer a few examples (Museum,
  Existential, Noir, Tender, Far future) and say custom is welcome. See the voice guide.
- Optional: a birth year for the tombstone, anything a picture means to them.

If they already said to just do it, skip the questions, credit "The Artist", and use
"Undated" or "c." dates. Never invent personal facts to fill a gap.

## Step 4: Curate

Read [references/voice.md](references/voice.md) now, every time. Then decide:

- **The order.** Date order by default, which makes the timeline the spine. A
  thematic order (all skies, then all food) is fine when the dates are thin.
- **The periods.** Merge `suggested_periods` into 3 to 6 timeline entries. Each one
  becomes a room in the gallery, opened by its `room_text` panel.
- **The title and the accent color.** The accent defaults to wall title blue. Pick a
  color from a work's `palette` only if the show has a strong one.

Write `EXHIBIT/exhibition.json` following [references/schema.md](references/schema.md).
Each work `id` must match the manifest.

## Step 5: Build

```
python3 SKILL_DIR/scripts/build_gallery.py EXHIBIT
python3 SKILL_DIR/scripts/make_film.py EXHIBIT
```

If `build_gallery.py` lists problems, fix `exhibition.json` and run it again. The film
takes about a minute. Add `--format square` or `--format landscape` for other shapes,
or `--seconds 3` for a quicker cut. Use `--linked` on the gallery for GitHub Pages
hosting (see [references/sharing.md](references/sharing.md)).

## Step 6: Check your work

Open `share/01-wall-text.png` and two of the work cards with your image reading tool.
The cards carry each label in full, so a very long label makes its photo small; trim
labels over 250 words.
Text should end on whole sentences and nothing should overlap. Then count: every
label 150 to 250 words, the wall text 350 to 500. Short labels are the most common
way a show falls flat. If a title runs long,
shorten it and rebuild. Make sure no label names an address, guesses who someone is,
or comments on anyone's looks.

## Step 7: Hand it over

Tell the person, briefly:

1. The show's title and one favourite line from it.
2. Where the files are, and what each is for: the page to open or send, the carousel
   to post in order, the story cover, the film, the caption.
3. How to share. Read [references/sharing.md](references/sharing.md) and offer what
   fits their setup. If you can publish an HTML page as an artifact or a link, offer
   to publish `gallery/index.html`. It is a private page until they share it.
4. That the film has no music on purpose: add a sound in the app they post from.
5. That every card, the film, the caption and the page carry a small "Made with My
   Guggenheim" line and link, so friends can make their own. It can be turned off.

Then offer one round of changes: a different mood, a renamed work, a photo dropped or
added, a longer timeline. Edit `exhibition.json` (or run `inspect_photos.py` again for
new photos) and rebuild.

## Fancier video

The built in film is clean and reliable everywhere. For motion design with more
movement, see [references/film.md](references/film.md), which explains handing the same
`exhibition.json` to Remotion.

## Never

- Write an exact location, a street or "the artist's home", even if you can tell.
- Name or identify people in the photos unless the person names them.
- Comment on anyone's body or looks, or make the person the butt of a joke.
- Present the show as the real Guggenheim or any real museum. The page says it is a
  personal exhibition.
- Use long dashes (em or en). The build rejects them.
