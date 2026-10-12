# Sharing an exhibition

What to offer once the show is built. Pick what fits the person's setup; don't list
everything.

## Posting it

| Where | What to post | Notes |
| --- | --- | --- |
| Instagram feed | The carousel in `share/`, in file order | Cards are 1080x1350 (4:5), the tallest a feed post shows. Paste `caption.txt` |
| Instagram Stories | `share/story-cover.png`, then the film | Add a link sticker if the gallery is hosted |
| Reels, TikTok, YouTube Shorts | `share/film-vertical.mp4` | 1080x1920. Pick a sound in the app; the film is silent so any licensed track fits |
| X, Threads, Bluesky | The wall text card plus 3 work cards, or the film | Shorten the caption |
| LinkedIn | `--format square` film or the carousel | For the brave |
| A group chat | `gallery/index.html` itself | It is one file with the photos inside. It opens in any browser |

`#MyGuggenheim` is always in the caption, so people can find each other's shows.

## Giving it a link

The page is a single file, so anything that serves a file works.

- **As a Claude artifact.** When your tools let you publish an HTML page (Claude Code
  on the web, claude.ai), offer to publish `gallery/index.html`. It starts private and
  the person chooses whether to share the link.
- **GitHub Pages.** Build with `--linked` so the images are separate files, put the
  `gallery/` folder in a public repo, and turn on Pages for it (Settings, Pages,
  deploy from branch). The link is `https://<user>.github.io/<repo>/`. Only do this
  with photos the person is happy to make public.
- **Any static host** with drag and drop upload works the same way.

## Before anything goes public

- The scripts strip camera data (including GPS) from every image they save, and the
  texts never name a place closer than a city. The original photos are untouched.
- Remind the person that a public link is public: the photos themselves can show a
  house number, a street sign, a school uniform. Offer to drop a work if they hesitate.
