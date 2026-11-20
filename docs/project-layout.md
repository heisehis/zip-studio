# Project layout

One folder per video, named `YYYY-MM-DD-short-name`. The pipeline tools take that folder as their first argument.

```
<project>/
  brief.md               what the video is for, who it is for, where it will be posted, deadlines
  sources.csv            every input: path, origin, who supplied it, licence, limits, sha256
  inputs/                original files, never edited (footage, recordings, music, effects, client material)
  plan/
    lines.json           the voiceover script, one entry per spoken line or silent beat
    script.md            the human-readable script with timings and on-screen text
  src/
    comp/comp.html       the compositor: draws any frame from window.renderAt(t)
    comp/timeline.js     window.TL, written by make_timeline.js or by hand
    comp/assets/         fonts, logos and images the compositor uses (copies)
    audio/vo/            one WAV per voice line, durations.json, words.json, voice.json
    audio/vo.wav         the placed voice track
    audio/sfx-map.json   cue kind -> effect file, gain and alignment
    audio/sfx.wav        the effects track
    render/              silent renders
  previews/              finished files to review, one subfolder per version (v1, v2, ...)
  qc/                    contact sheets, measurements and REVIEW.md
```

## `plan/lines.json`

```json
[
  {"id": "hook", "text": "Your business deserves more than \"DM for price\"."},
  {"id": "title", "hold": 2.4},
  {"id": "cta", "text": "Follow us and apply through the link in bio.", "say": "Follow us, and apply through the link in bio."}
]
```

- `text` is spoken and becomes the captions. `hold` is a silent beat in seconds.
- `say` (optional) is what the voice engine reads, for example with extra commas for phrasing. Captions still use `text`.

## The compositor contract

`comp.html` must set:

- `window.TL` with at least `dur` (seconds);
- `window.ready`, a Promise that resolves when fonts and images are loaded;
- `window.renderAt(t)`, which puts the page in the state for time `t` without timers or CSS animations.

Hide whole scenes with `display: none`, not `visibility: hidden`: a child set to `visibility: visible` shows through a hidden parent.
Avoid animating blur and large scale changes on many elements in a row; played back, it reads as the camera hunting for focus.
