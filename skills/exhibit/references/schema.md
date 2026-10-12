# exhibition.json

The curator writes this file in the exhibit folder, next to `manifest.json`. The build
script checks it and says exactly what to fix.

```json
{
  "kicker": "Collection in Focus",
  "title": "Late Suburban Currents",
  "accent": "#1868c4",
  "artist": { "name": "Dave Campbell", "born": "1994" },
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
      "label": "60 to 110 words. Use a blank line for a second paragraph.",
      "film_line": "Optional. One sentence for the video.",
      "alt": "Optional. A plain description for screen readers."
    }
  ],
  "timeline": {
    "title": "The Artist's Life",
    "entries": [
      { "when": "2019", "heading": "Early Period", "text": "One to three sentences.", "works": ["img-parking-lot-sunset"] }
    ]
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
| `kicker` | no | Defaults to "Collection in Focus" |
| `accent` | no | Hex color for titles. Defaults to a wall title blue. Pick from a photo's palette for a show with a strong color |
| `artist.name`, `artist.born` | no | `born` adds "(b. 1994)" to the tombstone. Only if the person offers it |
| `cover` | no | Work id for the story cover. Defaults to the first work |
| `works[].date`, `medium`, `credit` | no | Credit defaults to "Collection of the artist". Dimensions come from the photo |
| `timeline` | no | Leave it out for a show without dates. `works` in an entry shows thumbnails |
| `visitor_note` | no | The closing line |
| `share.caption`, `share.hashtags` | no | Written to `share/caption.txt`. `#MyGuggenheim` is always added |

No long dashes (em or en) anywhere. The build fails on them.
