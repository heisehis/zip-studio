# Voiceover with a Microsoft Edge online voice through the edge-tts package. Sends the script text to Microsoft.
# The route is unofficial and the right to use the audio commercially is unclear: use it for drafts only.
#   python tts_edge.py <project> [voice] [rate]      default en-NG-EzinneNeural, +0%
# Writes <project>/src/audio/vo/<id>.wav (24 kHz mono), durations.json, words.json (word times per line), voice.json.
import sys, os, json, asyncio, subprocess
import numpy as np, soundfile as sf, edge_tts
from voice_lines import project, spoken, vo_dir, keep_previous

proj = project(sys.argv)
VOICE = sys.argv[2] if len(sys.argv) > 2 else 'en-NG-EzinneNeural'
RATE = sys.argv[3] if len(sys.argv) > 3 else '+0%'
SR = 24000

async def synth(text, mp3):
    try: com = edge_tts.Communicate(text, VOICE, rate=RATE, boundary='WordBoundary')
    except TypeError: com = edge_tts.Communicate(text, VOICE, rate=RATE)
    words = []
    with open(mp3, 'wb') as f:
        async for ch in com.stream():
            if ch['type'] == 'audio': f.write(ch['data'])
            elif ch['type'] == 'WordBoundary': words.append({'text': ch['text'], 't0': ch['offset'] / 1e7, 't1': (ch['offset'] + ch['duration']) / 1e7})
    return words

async def main():
    keep_previous(proj); VO = vo_dir(proj); durs, allw = {}, {}
    for name, text in spoken(proj).items():
        mp3 = os.path.join(VO, name + '.mp3'); wav = os.path.join(VO, name + '.wav'); words = None
        for attempt in range(4):
            try: words = await synth(text, mp3); break
            except Exception as e: print('retry', name, repr(e)[:120], flush=True); await asyncio.sleep(3)
        if words is None: raise SystemExit('failed: ' + name)
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', mp3, '-ac', '1', '-ar', str(SR), wav + '.raw.wav'], check=True)
        x, _ = sf.read(wav + '.raw.wav', dtype='float32'); os.remove(wav + '.raw.wav'); os.remove(mp3)
        idx = np.where(np.abs(x) > 0.01)[0]; a = max(0, idx[0] - int(.04 * SR)); b = min(len(x), idx[-1] + int(.04 * SR))
        sf.write(wav, x[a:b], SR); off = a / SR; durs[name] = round((b - a) / SR, 3)
        allw[name] = [{'text': w['text'], 't0': round(max(0, w['t0'] - off), 3), 't1': round(w['t1'] - off, 3)} for w in words]
        print(name, durs[name], len(words), 'words', flush=True)
    json.dump(durs, open(os.path.join(VO, 'durations.json'), 'w'), indent=1)
    json.dump(allw, open(os.path.join(VO, 'words.json'), 'w'), indent=1)
    json.dump({'engine': 'edge-tts', 'voice': VOICE, 'rate': RATE}, open(os.path.join(VO, 'voice.json'), 'w'), indent=1)
    print('total speech', round(sum(durs.values()), 2))
asyncio.run(main())
