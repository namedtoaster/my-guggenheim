# The exhibition film

## The built in film

`scripts/make_film.py` renders the film frame by frame with Pillow and encodes it with
ffmpeg. It needs nothing else, so it works in Claude Code, in claude.ai and in CI.

The sequence: the wall title, then each work hung on the wall with a slow camera
push and its label rising in, then the timeline entry by entry, then the visitor note.
Every scene fades through the wall color.

| Option | Default | |
| --- | --- | --- |
| `--format` | `vertical` | `vertical` 1080x1920, `square` 1080x1080, `landscape` 1920x1080 |
| `--seconds` | `4.2` | Time on each work. 3 feels brisk, 6 feels like a gallery |
| `--max-works` | `12` | Keeps the film under a minute |
| `--gif` | off | Writes a half size GIF instead of an MP4 |

Each work shows its `film_line` when there is one, otherwise the opening of its
label. Write `film_line` for the works where the label's best line comes last.

## The trailer

`scripts/make_trailer.py` cuts the same show like a film trailer, on black, 30 to 40
seconds:

1. A quiet card: FROM THE COLLECTION OF the artist.
2. A photo, full frame and graded a little cooler, then one line from its label set
   large on black. Three to five times, with beat cards between (SIX WORKS. EIGHT
   YEARS. ONE ARTIST.).
3. A montage of every work, faster and faster, cut on white flashes.
4. Black, then the title, then the tagline and the credit.

| Option | Default | |
| --- | --- | --- |
| `--format` | `vertical` | Same shapes as the film |
| `--quotes` | `4` | How many lines from the labels |
| `--gif` | off | Writes a half size GIF instead of an MP4 |

The lines are the whole trailer. Write `trailer.lines` (see the schema) rather than
leaving the script to guess: choose lines that make sense with no context and get
funnier or sadder said slowly. Also silent: a low swelling sound with a hit near the
end, picked in the app, suits it.

## More motion: Remotion

For a film with more movement (type animation, photos sliding between walls, a
moving timeline), [Remotion](https://www.remotion.dev) makes videos from React code
and publishes [agent skills](https://github.com/remotion-dev/skills) that teach Claude
Code to write it. As of October 2026:

- It suits Claude Code on a computer, with Node installed. It is heavy for claude.ai.
- Remotion is free for individuals and companies of up to three people. Larger
  companies need a company license. Check [remotion.dev/license](https://www.remotion.dev/license)
  before using it for work.

To use it with an exhibition:

1. In a new folder, start a blank Remotion project (`npx create-video@latest`) and add
   the skills (`npx skills add remotion-dev/skills`).
2. Copy the exhibit's `exhibition.json`, and the photos from `gallery/images/` (build
   with `--linked` to get them as files), into the project's `public/` folder.
3. Ask Claude Code for a composition that reads `exhibition.json`: the title wall,
   one scene per work with its title, date and `film_line`, the timeline, and the
   visitor note. Give it the length (30 to 60 seconds), 1080x1920, and the wall
   color `#efeeea` with the accent from the JSON.
4. Render with Remotion's render command and post the MP4 the same way.

The photos used this way are the stripped copies from `gallery/images/`, so no camera
data travels with them.
