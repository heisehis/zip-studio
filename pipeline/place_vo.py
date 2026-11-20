# Assembles <project>/src/audio/vo.wav: each voice line placed at its start time from src/comp/timeline.js.
#   python place_vo.py <project>
import sys, os, json, numpy as np, soundfile as sf
from voice_lines import project, vo_dir
proj = project(sys.argv)
js = open(os.path.join(proj, 'src', 'comp', 'timeline.js'), encoding='utf-8').read().split('\nTL.word')[0]
tl = json.loads(js[js.index('{'):js.rindex('}') + 1])
VO = vo_dir(proj); sr = 24000; out = np.zeros(int(tl['dur'] * sr) + 1, dtype=np.float32)
for v in tl['vo']:
    x, r = sf.read(os.path.join(VO, v['id'] + '.wav'), dtype='float32'); assert r == sr, 'voice files must be 24 kHz'
    a = int(v['t0'] * sr); out[a:a + len(x)] += x[:len(out) - a]
sf.write(os.path.join(proj, 'src', 'audio', 'vo.wav'), out, sr)
print('vo.wav', round(len(out) / sr, 2), 's peak', float(np.abs(out).max()))
