#!/usr/bin/env bash
# Export checks for a finished video: streams, loudness, black and frozen spans, and a contact sheet to look at.
#   bash pipeline/qc.sh <video.mp4> [frames-per-second-for-sheet]      -> <video>.qc.txt and <video>.sheet.jpg
# These checks do not replace watching and listening: nothing here hears the audio or judges the edit.
set -euo pipefail
V="$1"; FPS="${2:-3}"; OUT="${V%.*}"
{
  echo "# QC: $V"
  ffprobe -v error -show_entries stream=codec_name,profile,width,height,r_frame_rate,pix_fmt,color_range,sample_rate,channels,nb_frames:format=duration,size -of compact "$V"
  echo "## loudness (target about -14 LUFS, true peak below -1 dBFS)"
  ffmpeg -hide_banner -nostats -i "$V" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|LRA:|Peak:)" || true
  echo "## black spans (0.2 s or longer) and frozen spans (2 s or longer)"
  ffmpeg -hide_banner -nostats -i "$V" -vf "blackdetect=d=0.2:pix_th=0.10,freezedetect=n=-60dB:d=2" -an -f null - 2>&1 | grep -E "black_start|freeze_start|freeze_end" || echo "none"
  echo "## decode errors"
  ffmpeg -v error -i "$V" -f null - 2>&1 | head -5 || true
} | tee "$OUT.qc.txt"
ffmpeg -hide_banner -loglevel error -y -i "$V" -vf "fps=$FPS,scale=170:-1,tile=11x6:padding=4:color=0x333333" -frames:v 1 -q:v 3 "$OUT.sheet.jpg"
echo "contact sheet: $OUT.sheet.jpg ($FPS frames per second, read left to right)"
