# QC and sources

## Before a version leaves the studio

1. `bash pipeline/qc.sh <file>`: size, frame rate, codec, loudness (about -14 LUFS integrated, true peak below -1 dBFS),
   no unintended black or frozen spans, no decode errors.
2. Look at the contact sheet, and at full-size stills of every scene start, middle and end, every cut, and anything that moves fast.
3. Check text against the safe area for vertical platforms: keep essentials roughly between x 100-980 and y 250-1500 at 1080x1920,
   clear of the caption and button overlays at the bottom and right.
4. Watch it in real time and listen to it on a phone speaker and on headphones.
5. Write `qc/REVIEW.md`: what changed, what was measured, what was **not** checked, known issues.

Steps 1-3 can be automated or delegated. Steps 4-5 need a person.

## sources.csv

One row per input, with these columns:

```
asset,project_path,origin,supplied_by,licence,restrictions,sha256
```

- Record where it came from and under what terms, even for your own files.
- Commercial music, voices and stock effects: record the plan or licence in force when the file was made or downloaded.
- AI voices: note the engine, the voice and whether the plan allowed commercial use at that time.
- Client material: note that permission to show it was given, by whom and when.
- Anything uncleared is marked "test only" and stays out of a final export.
