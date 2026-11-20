# Zip Studio

A small, scriptable video and motion-graphics pipeline for short vertical videos (1080x1920 Reels, TikTok and Shorts),
built to be driven from a coding agent such as Claude Code or by hand from a terminal.

Every frame is drawn by an HTML page that exposes a pure function of time, `window.renderAt(t)`. Headless Chromium renders
each frame and ffmpeg encodes them, so a render is repeatable frame for frame and every part of the design stays editable
as code. Voice, captions, sound effects and music are added by separate small tools, and every finished file goes through
the same export checks.

## What is in here

| Path | What it does |
|---|---|
| `pipeline/render.js` | Renders `<project>/src/comp/comp.html` to stills or to a silent H.264 video. |
| `pipeline/make_timeline.js` | Turns `<project>/plan/lines.json` plus measured voice files into `src/comp/timeline.js`: scene times, captions, word times. |
| `pipeline/tts_kokoro.py` | Voiceover from the local Kokoro model (offline, free). |
| `pipeline/tts_edge.py` | Draft voiceover from Microsoft Edge online voices, with word times. Drafts only: the route is unofficial. |
| `pipeline/tts_eleven.py` | Voiceover from ElevenLabs (official API, key in `ELEVENLABS_API_KEY`), with word times. |
| `pipeline/split_vo.py` | Splits one continuous recording (a voice actor's take) into the script's lines, using local speech recognition. |
| `pipeline/place_vo.py` | Lays the voice lines on the timeline as one `vo.wav`. |
| `pipeline/sfx.py` | Builds a sound-effects track from cue times in the timeline and a map of effect files. |
| `pipeline/mix.ps1` | Mixes voice, music (ducked under the voice) and effects; normalises loudness; muxes with the render. |
| `pipeline/qc.sh` | Export checks: streams, loudness, black and frozen spans, decode errors, and a contact sheet. |
| `examples/chat-promo/` | A complete 22-second example: a story told in chat bubbles, with a website mock-up, cards and an end card. |
| `docs/` | How a project is laid out, the QC routine, and the rules for sources and licences. |

## Requirements

- Node.js 18 or later, and Playwright with a Chromium build (`npm i playwright && npx playwright install chromium`).
  Set `PLAYWRIGHT_MODULE` and `CHROMIUM_PATH` if they live somewhere unusual.
- ffmpeg and ffprobe on `PATH`.
- Python 3.10 or later with `numpy` and `soundfile`; plus, only for the tools you use: `kokoro-onnx`, `edge-tts`, `faster-whisper`.
- PowerShell 7 for `mix.ps1`; Bash for `qc.sh` (Git Bash works on Windows).

## Quick start with the example

```bash
node pipeline/render.js examples/chat-promo stills 4.3 13.0 21.5
python pipeline/sfx.py examples/chat-promo
node pipeline/render.js examples/chat-promo video 1 demo
pwsh pipeline/mix.ps1 -Project examples/chat-promo -Video examples/chat-promo/src/render/demo_noaudio.mp4 -Out examples/chat-promo/previews/demo.mp4 -Sfx examples/chat-promo/src/audio/sfx.wav -Lufs -16
bash pipeline/qc.sh examples/chat-promo/previews/demo.mp4
```

The example needs its fonts, logo files and sound effects in place first: see `examples/chat-promo/README.md`.
They are not included in this repository.

## A voiced project, start to finish

1. Write the script as `<project>/plan/lines.json` (see `docs/project-layout.md`).
2. Make the voice: `python pipeline/tts_eleven.py <project> <voice_id>`, or record a person and run
   `python pipeline/split_vo.py <project> <recording>`.
3. `node pipeline/make_timeline.js <project>` and `python pipeline/place_vo.py <project>`.
4. Build `<project>/src/comp/comp.html` against `window.TL`; check stills with `render.js ... stills`.
5. Render, mix with `mix.ps1`, then run `qc.sh` and look at the contact sheet before anyone else sees the file.

## Ground rules

- Use only footage, music, voices and other assets you made or are licensed to use, and record each one in the project's
  `sources.csv` with its licence and any limits.
- Keep the original files untouched; work on copies.
- Nothing is published automatically. Posting stays a manual step.
- An export that passes `qc.sh` has still not been watched or heard. Say so until a person has done both.

## Licence

The code and documentation are under the MIT License (see `LICENSE`). Brand names, logos and any assets you add to the
example are not covered by it and belong to their owners.
