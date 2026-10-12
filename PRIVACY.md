# Privacy

**My Guggenheim does not collect, store, upload or sell anything about you.** There is
no server, no account, no database, no analytics and no tracking. It is a set of
instructions and a few small scripts that run where you run them, on your photos, and
nowhere else.

## What happens to your photos

1. **They stay where you put them.** The scripts read your photos and write the
   exhibition into a folder next to them. They never copy your photos anywhere else.
2. **Nothing goes over the internet.** The scripts contain no networking code at all.
   They work with Wi-Fi turned off.
3. **Your originals are never changed.** Every image the scripts save for sharing is a
   new copy with the camera data removed, including GPS location.
4. **Places are kept rough.** The notes the scripts keep about each photo round any
   location to about 11 km, enough to name a city and no closer. Labels never name a
   street, an address or anyone's home.
5. **Faces and names can be blacked out** before you share anything, and the skill
   checks every photo for them first.

## The gallery page

The gallery is a single file with your photos inside it. When someone opens it, it
loads nothing from anywhere else: no fonts, no scripts, no images, no trackers. The
share buttons are ordinary links that do nothing until someone clicks one.

## This repository

**This repository never holds your photos or personal details.** The one exception is
the author's own exhibition in `showcase/`, which they chose to publish, with photos
of faces left out and every name, number plate and personal detail blacked out.
Exhibitions are made in a folder that git ignores, and every commit and every
pull request is checked automatically. It is refused if it contains:

- a photo, video or zip outside the folders of drawn demo images and `showcase/`,
  where an owner chose to publish their own exhibition with every face, name and
  personal detail blacked out
- any camera data in a showcase image
- location data inside any image
- a place or coordinates in any data file
- an email address
- a network call in the scripts, or a gallery page that loads anything from the internet

## What we can't promise for you

My Guggenheim runs inside Claude (or another AI assistant you choose). The photos you
show to Claude are handled under your own Claude account and Anthropic's privacy
policy, the same as anything else you send in a chat. My Guggenheim adds nothing to
that, sends nothing anywhere of its own, and keeps nothing.

And once you post an exhibition, it is public like anything else you post. Look at
it before you share it.

## If something looks wrong

If you find anything in this repo that could leak a photo, a place or a personal
detail, please report it privately using GitHub's private vulnerability reporting on
this repository. See [SECURITY.md](SECURITY.md).
