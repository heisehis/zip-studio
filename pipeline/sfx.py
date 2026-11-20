# Builds a sound-effects track from cue times in the compositor's timeline (TL.sfx) and a map of effect files.
#   python sfx.py <project>      -> <project>/src/audio/sfx.wav (48 kHz stereo)
# <project>/src/audio/sfx-map.json maps cue kinds to files in <project>/inputs/sfx:
#   {"whoosh": {"file": "whoosh.mp3", "gain": 0.55, "align": "peak"}, "sent": {"file": "pop.mp3", "gain": 0.9, "align": "onset"}}
# "onset": the first audible sample lands on the cue time. "peak": the loudest moment lands on the cue time (whooshes, risers).
import sys, os, re, json, subprocess, numpy as np, soundfile as sf
proj = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.'); SR = 48000
js = open(os.path.join(proj, 'src', 'comp', 'timeline.js'), encoding='utf-8').read()
body = '\n'.join(l.split('//')[0] for l in js[js.index('{'):js.rindex('}') + 1].splitlines())
body = re.sub(r'([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:', r'\1"\2":', body).replace("'", '"')
TL = json.loads(re.sub(r',\s*([}\]])', r'\1', body))
MAP = json.load(open(os.path.join(proj, 'src', 'audio', 'sfx-map.json'), encoding='utf-8'))

def load(name):
    raw = os.path.join(proj, 'src', 'audio', '_sfx_tmp.wav')
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', os.path.join(proj, 'inputs', 'sfx', name), '-ac', '2', '-ar', str(SR), raw], check=True)
    x, _ = sf.read(raw, dtype='float32'); os.remove(raw); return x / max(1e-9, np.abs(x).max())
SND = {}
for k, m in MAP.items():
    x = load(m['file']) * m.get('gain', 1.0); env = np.abs(x).max(axis=1)
    on = int(np.argmax(env > .01)); pk = int(np.argmax(np.convolve(env, np.ones(480) / 480, 'same')))
    SND[k] = (x, pk if m.get('align') == 'peak' else on)
out = np.zeros((int(TL['dur'] * SR) + 3 * SR, 2), dtype=np.float32)
for c in TL.get('sfx', []):
    if c['k'] not in SND: raise SystemExit('no file mapped for cue kind: ' + c['k'])
    x, ref = SND[c['k']]; a = int(c['t'] * SR) - ref
    if a < 0: x, a = x[-a:], 0
    out[a:a + len(x)] += x[:len(out) - a]
out = out[: int(TL['dur'] * SR)]; out *= .89 / max(1e-9, np.abs(out).max())
sf.write(os.path.join(proj, 'src', 'audio', 'sfx.wav'), out, SR)
print('sfx.wav', round(len(out) / SR, 2), 's,', len(TL.get('sfx', [])), 'cues')
