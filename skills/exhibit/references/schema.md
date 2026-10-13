# exhibition.json

The curator writes this file in the exhibit folder, next to `manifest.json`. The build
script checks it and says exactly what to fix.

```json
{
  "mood": "Museum",
  "walls": "white",
  "kicker": "Collection in Focus",
  "title": "Late Suburban Currents",
  "accent": "#1868c4",
  "artist": { "name": "A. Demo", "born": "1994" },
  "statement": [
    "First paragraph: the movement.",
    "Second paragraph: the concerns, with one sentence of gentle self-critique.",
    "Drawn from the artist's camera roll, *Late Suburban Currents* explores..."
  ],
  "cover": "img-parking-lot-sunset",
  "works": [
    {
      "id": "img-parking-lot-sunset",
      "title": "Study for a Parking Lot",
      "date": "June 2019",
      "medium": "Digital photograph (iPhone 8)",
      "credit": "Collection of the artist",
      "label": "150 to 250 words in two or three paragraphs, separated by blank lines.",
      "film_line": "One sentence for the video. Write one for every work.",
      "accession": "Optional. Defaults to the year and the work's number, like 2026.3",
      "alt": "Optional. A plain description for screen readers."
    }
  ],
  "timeline": {
    "title": "The Artist's Life",
    "entries": [
      { "when": "2019", "heading": "Early Period", "text": "One to three sentences.", "room_text": "60 to 150 words opening this room in the gallery.", "works": ["img-parking-lot-sunset"] }
    ]
  },
  "trailer": {
    "lines": [
      { "work": "img-cold-coffee", "text": "The coffee was meant to be drunk. The picture was taken instead." }
    ],
    "cards": ["Six works.", "Eight years.", "One artist."],
    "tagline": "Now on view."
  },
  "visitor_note": "You do not have to read everything. Look at what you like. Get what you get.",
  "share": {
    "caption": "Now on view: Late Suburban Currents. Six works from the collection of the artist.",
    "hashtags": ["#MyGuggenheim", "#CollectionInFocus"]
  }
}
```

| Field | Needed | Notes |
| --- | --- | --- |
| `title` | yes | The show's name. Six words at most |
| `statement` | yes | A list of paragraphs (or one string with blank lines) |
| `works` | yes | In the order they hang. Each `id` must match one in `manifest.json` |
| `works[].title`, `works[].label` | yes | `*asterisks*` make italics |
| `mood` | no | The mood the person asked for, in their own words. A record; the words do the work |
| `walls` | no | `white` (follows the viewer's light or dark setting), `grey`, `black`, or a hex color. Sets the gallery, cards and film |
| `kicker` | no | Defaults to "Collection in Focus" |
| `accent` | no | Hex color for titles. Defaults to a wall title blue. Pick from a photo's palette for a show with a strong color |
| `artist.name`, `artist.born` | no | `born` adds "(b. 1994)" to the tombstone. Only if the person offers it |
| `cover` | no | Work id for the story cover. Defaults to the first work |
| `works[].date`, `medium`, `credit` | no | Credit defaults to "Collection of the artist". Dimensions come from the photo |
| `timeline` | no | Leave it out for a show without dates. `works` in an entry shows thumbnails |
| `timeline.entries[].room_text` | no | Opens a room in the gallery before that period's first work. Use it whenever the works hang in timeline order |
| `works[].redact` | no | Black boxes over faces and personal details, as `[[left, top, right, bottom], ...]` in the photo's own upright pixels. Applied to the page, cards and film |
| `works[].accession` | no | The small number under the credit line. Defaults to the year and position |
| `trailer.lines` | no | For `make_trailer.py`: three to five lines, each 6 to 16 words, shown alone on black after its work's photo. Pick the ones that land hardest out of context, the tender or absurd ones, in hanging order. Without them the script picks from `film_line` and the labels |
| `trailer.cards` | no | The short beats cut between the lines, like "Six works." Defaults to the number of works, the years they span and "One artist." |
| `trailer.tagline` | no | The last card. Defaults to "Now on view." |
| `visitor_note` | no | The closing line |
| `share.caption`, `share.hashtags` | no | Written to `share/caption.txt`. `#MyGuggenheim` is always added |
| `share.credit` | no | `false` removes the project line from the cards, film and caption. Leave it on unless asked |

No long dashes (em or en) anywhere. The build fails on them.
