# Example: chat promo

A 21.9-second vertical promo told as a story in chat bubbles: a supermarket owner scrolls another store's website at night,
asks their manager about it, then messages a studio with screenshots and gets the answer "No wahala, we've got you covered."
It ends on a tagline card and the studio's logo with one call to action. `script.md` has the full script and timings.

Everything is drawn in `src/comp/comp.html` from the cue times in `src/comp/timeline.js`. The supermarket, its website and
the people in the chats are invented.

## Files you need to add (not in this repository)

| Path | What |
|---|---|
| `src/comp/assets/Montserrat-Variable.ttf` | Montserrat, from Google Fonts (SIL Open Font License) |
| `src/comp/assets/Poppins-Regular.ttf`, `-Medium.ttf`, `-Bold.ttf` | Poppins, from Google Fonts (SIL Open Font License) |
| `src/comp/assets/bliz-logo-primary.svg`, `bliz-icon-black.svg` | The studio's logo files; swap in your own logo and change the names in `comp.html` |
| `inputs/sfx/whoosh.mp3`, `pop-sent.mp3`, `pop-received.mp3` | Any whoosh and two short pops you are licensed to use; see `src/audio/sfx-map.json` |

## Make it yours

- Words: edit the chat bubbles and cards in `comp.html`, then the times in `timeline.js` so each bubble stays readable
  (about 0.6 s plus 0.15 s per word).
- Brand: colours are CSS variables at the top of `comp.html` (`--y`, `--k`, `--c`); fonts are the `Disp` and `Body` faces.
- Sound: cue times are in `TL.sfx`; the files and their gains are in `src/audio/sfx-map.json`.
