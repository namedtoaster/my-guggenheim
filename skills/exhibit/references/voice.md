# The curator's voice

How the wall texts should sound. Read this before writing `exhibition.json`.

## The one idea

Write like a real museum. Earnest, art historical, slightly overwritten, completely
sincere. The fun comes from that sincerity meeting a photo of a parking lot. Never
wink at the reader. No "lol", no emoji, no "okay but", no telling anyone it's a joke.
A good label could hang next to a Cezanne, and reads funny only because of the
picture beside it.

The second idea sits under the first: these are the person's own pictures, so the
texts should leave them feeling seen. Under the grand words, a good label notices
something true: the light they stopped for, the thing they kept photographing,
the year everything changed. Silly and kind at the same time.

## Ground rules

- **Anchor every claim in something real.** What is visible in the photo, or a fact
  from `manifest.json` (date, time of day, camera, flash, rough place, colors). Do
  not invent life events. If the person told you something, use it.
- **Treat every accident as a choice.** Blur is "a refusal of fixity". A thumb in the
  corner is "the artist's hand, literally present". A screenshot is "found digital
  material". A tilted horizon is a decision.
- **Never mock the person.** Not their home, body, clothes, food, money, taste or
  friends. Elevate, don't punch down. The joke is the museum, never the artist.
- **People in photos.** Do not guess who someone is, and do not comment on how anyone
  looks. Describe what they are doing, or call them "a figure". Use names only when
  the person gives them. Children stay unnamed unless the parent names them.
- **Places stay at city level at most.** Use `rough_place` only to name a city,
  region or "a coastal town". Never an address, a street or "the artist's home".
- **Real artists, lightly.** Comparisons are welcome ("recalls Hopper's empty
  diners") when they rest on well known features of that artist's work. No made
  up quotes, dates or facts about real people.
- **One or two flourishes per label.** "Liminal", "the picture plane", "chiaroscuro",
  "vernacular", "in dialogue with", "transmutes the everyday". Spend them, don't
  pour them.
- **Plain punctuation.** No long dashes (em or en). Use commas, periods, parentheses.
  The build script rejects them.

## The pieces

### Exhibition title

Echo how museums name shows: a period, a place, a current, a mood.
"Modern European Currents" becomes "Late Suburban Currents", "Kitchen Light:
2019 to Now", "The Commute Years", "Studies in Leftovers". Short. Six words at most.
The kicker above it is "Collection in Focus" unless something else fits better
("A Retrospective", "New Acquisitions", "Early Works").

### The wall text (`statement`)

Three paragraphs, 200 to 300 words in all, the way a real intro panel runs:

1. **The movement.** Situate the artist as part of something larger, with mock
   gravity: "The vernacular photographers of the early twenty-first century..."
2. **The concerns.** What actually runs through these pictures: recurring subjects,
   colors (use `mood` and `palette`), times of day, places. Include one sentence of
   gentle self-critique, the kind real museums now add, aimed at the museum or the
   genre, never at the person. ("This exhibition, like many before it, may assign
   more intention to a lunch than the lunch can bear.")
3. **The frame.** Start with "Drawn from the artist's camera roll, *Title* explores..."
   and end on an idea about looking.

### Work titles

Museum style. Mix the forms: "Untitled (Receipt)", "Study for a Parking Lot",
"Pigeon, Possibly", "Self Portrait as a Cold Coffee", "Composition with Blue
Notification". Never "IMG_4033". Titles of other works inside a text go in
`*asterisks*` to be italic.

### Tombstone fields

- `date`: "2019", "June 2019", "c. 2021", or "Undated". Use the manifest; if the
  person gave a rough time, use "c.".
- `medium`: built from the camera data, in museum language. "Digital photograph
  (iPhone 8)", "Digital photograph, flash", "Screenshot, found digital material",
  "Digital photograph, taken at 11:58 p.m.". When there is no camera data, say
  what it looks like: "Digital image".
- `credit`: "Collection of the artist" unless the person says otherwise. "Gift of
  the artist's mother" is a fine thing to use if they tell you.

### The label

60 to 110 words. A shape that works:

1. What we see, elevated. ("A paper cup, abandoned at the threshold of the
   morning.")
2. The formal move. Composition, light, color, the crop.
3. Context from the data. Time of day, the season, the camera, where it sits in the
   artist's life.
4. A quiet turn. Funny, or tender, or both. Often the most honest sentence.

Optional `film_line`: one sentence, under 150 characters, for the video. If it is
left out, the film uses the opening of the label.

### The timeline

"The Artist's Life" (or a better title). Build periods from the dates and places
in `suggested_periods`, merged into 3 to 6 entries. Name them the way biographies
name an artist's periods: "Early Period", "The Chicago Years", "The Blue Period"
(only if the colors say blue), "The Screenshot Period", "Late Style" (for this
year, said with a straight face). Each entry is one to three sentences, built only
from the photos, the data and what the person told you. Playful uncertainty is
allowed and very museum: "Scholars disagree on what happened in 2021."

### The visitor note

The last thing on the wall. A short note on how to look at the show. This project
began with someone realising they no longer had to "win" at museums by reading
every word, so the default sounds like that: "You do not have to read everything.
Look at what you like. Get what you get." Rewrite it to fit each show.

## Tones

Ask once, default to **Museum**.

| Tone | Sounds like |
| --- | --- |
| Museum | A real wall text. Sincere, measured, gently grand. The default |
| Retrospective | A blockbuster show for a giant of the art world. Maximum reverence |
| Deadpan | Dry, short, factual, devastatingly literal |
| Tender | Warm and quiet. For pictures of someone who is gone, a pet, a hard year. Funny only if the person wants it |

If the photos show grief, illness or a memorial, switch to Tender without being asked
and keep the jokes out unless the person brings them.

## A worked example

Photo: a paper cup of coffee on a counter, morning light, iPhone 8, 8:12 a.m.,
November 2019.

> **Self Portrait as a Cold Coffee**, 2019
> Digital photograph (iPhone 8)
> 
> A cup, still full, photographed at 8:12 a.m. and never finished. The artist
> centers it with the confidence of a still life painter, letting the warm browns
> of the counter rise around it like a frame. Made in the first autumn of what the
> chronology calls the Early Period, it is one of several works in which the
> artist documents a plan rather than an event. The coffee was meant to be drunk.
> The picture was taken instead.
