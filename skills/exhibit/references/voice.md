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

Four paragraphs, 350 to 500 words in all. This is the big intro panel by the
entrance, and it should read like one at a serious modern museum:

1. **The movement.** Situate the artist as part of something larger, with mock
   gravity: "The vernacular photographers of the early twenty-first century..."
2. **The influences.** Name the real artists and movements these pictures are in
   conversation with (see the touchstones below), and what the artist took from them.
3. **The concerns.** What actually runs through these pictures: recurring subjects,
   colors (use `mood` and `palette`), times of day, places, the arc of the timeline.
   Include one or two sentences of gentle self-critique, the kind real museums now
   add, aimed at the museum or the genre, never at the person. ("This exhibition,
   like many before it, may assign more intention to a lunch than the lunch can bear.")
4. **The frame.** Start with "Drawn from the artist's camera roll, *Title* explores..."
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

**150 to 250 words, in two or three paragraphs.** Modern museum labels are not
captions. They teach you how to look, place the work in a history, and then let
it go. A shape that works:

1. **Close looking.** What we see, elevated, and how it is made: composition, light,
   color, focus, the crop, the angle, the medium. Be specific. Name what the eye
   does first and where it goes next.
2. **The lineage.** One or two real artists, movements or ideas the work is in
   dialogue with, and *why* (a shared device, subject or problem). See the
   touchstones below. One sentence of real art history makes the joke land harder.
3. **Context and the turn.** What the data adds: the hour, the season, the camera,
   where it sits in the artist's life and in this show. Then a contemporary reading
   (attention, tourism, screens, memory, the self as performance) and a quiet last
   line. Funny, or tender, or both. Often the most honest sentence.

`film_line` is one sentence, under 150 characters, for the video. Write one for
every work: a long label never fits the film, and the best line often comes last.

### Room panels (`room_text`)

Modern museums open each room with a panel. Give each timeline entry a `room_text`
of 60 to 150 words: what this period of the artist's life was, what changed in the
work, and what to look for in the room. The gallery page shows it before the first
work of that period.

### The timeline

"The Artist's Life" (or a better title). Build periods from the dates and places
in `suggested_periods`, merged into 3 to 6 entries. Name them the way biographies
name an artist's periods: "Early Period", "The Chicago Years", "The Blue Period"
(only if the colors say blue), "The Screenshot Period", "Late Style" (for this
year, said with a straight face). Each entry is one to three sentences, built only
from the photos, the data and what the person told you. Playful uncertainty is
allowed and very museum: "Scholars disagree on what happened in 2021." The short
`text` goes on the timeline; the longer `room_text` opens the room.

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

## Touchstones

Real comparisons, safe to make, with the reason they fit. Use them when the
picture earns it, and only for the stated reason. Do not invent quotes or facts.

| When the photo has | Reach for |
| --- | --- |
| Old televisions, screens, video | Nam June Paik, who made art from TV sets (and set them among live plants in *TV Garden*, 1974) |
| Cities seen from below, odd angles | Alexander Rodchenko's tilted Constructivist views of the 1920s; Berenice Abbott's *Changing New York* (1930s), old and new side by side |
| Empty rooms, seats, waiting | Edward Hopper's solitary interiors and empty theaters; Marc Augé's "non-places" (airports, motorways) |
| Airports, signs, words | Ed Ruscha's paintings of words and signs; Auge again |
| Dappled light, promenades, parks | Renoir's *Bal du moulin de la Galette* (1876); Seurat's *A Sunday on La Grande Jatte* (1884 to 1886) |
| Blur, soft focus, night lights | Pictorialism, which chose softness on purpose around 1900; Gerhard Richter's blurred photo paintings |
| Staged poses, costumes, role play | Cindy Sherman's *Untitled Film Stills* (1977 to 1980); Yves Klein's staged *Leap into the Void* (1960) |
| A lone figure facing a scene | Caspar David Friedrich's *Wanderer above the Sea of Fog* (about 1818) |
| Street scenes, markets, passersby | Helen Levitt's New York streets; Henri Cartier-Bresson's "decisive moment" |
| A person in their surroundings | The environmental portrait, as Arnold Newman practised it |
| Food, tables, leftovers | Dutch still life of the 1600s, especially the vanitas and the lavish *pronkstilleven* |
| Colored light, neon | Dan Flavin's fluorescent light works |
| Screenshots, found images, objects | Marcel Duchamp's readymades (*Fountain*, 1917); post-internet art |
| Repetition, grids, rows | Bernd and Hilla Becher's typologies; Andreas Gursky's vast ordered scenes |
| Selfies, mirrors | Self portraiture from Rembrandt to Vivian Maier's reflections |

## A worked example

Photo: a paper cup of coffee on a counter, morning light, iPhone 8, 8:12 a.m.,
November 2019.

> **Self Portrait as a Cold Coffee**, 2019
> Digital photograph (iPhone 8), taken at 8:12 a.m.
>
> A cup, still full, sits at the exact center of the frame, photographed from
> directly above at 8:12 in the morning. The artist allows nothing else in: no hand,
> no table edge, no window. The warm browns of the counter rise around the cup like
> a mount around a print, and a single pale reflection floats on the surface of the
> coffee, the only highlight in the picture.
>
> The overhead view belongs to the long tradition of the still life, which since the
> Dutch painters of the 1600s has asked ordinary objects on tables to stand in for
> larger ideas about time and appetite. Those painters favored the half eaten pie
> and the overturned glass. The artist goes further, and photographs the meal
> before it has begun.
>
> Made in the first autumn of what the chronology calls the Early Period, the work
> is one of several in which the artist documents a plan rather than an event. It
> anticipates a whole genre of the decade, the picture taken instead of the thing
> itself. The coffee was meant to be drunk. The picture was taken instead.
