# Local voiceover with Kokoro (offline once the model files exist).
#   python tts_kokoro.py <project> [voice] [speed]      default voice am_michael, speed 1.0
# Model folder: KOKORO_DIR (default: tools/kokoro next to this repo) holding kokoro-v1.0.onnx and voices-v1.0.bin.
# Writes <project>/src/audio/vo/<id>.wav, durations.json, voice.json. Then: node make_timeline.js <project> ; python place_vo.py <project>
import sys, os, json
import numpy as np, soundfile as sf
from voice_lines import project, spoken, vo_dir, keep_previous

def trim(x, sr, thr=0.01, pad=0.04):
    idx = np.where(np.abs(x) > thr)[0]
    if not len(idx): return x
    return x[max(0, idx[0] - int(pad * sr)):min(len(x), idx[-1] + int(pad * sr))]

proj = project(sys.argv); voice = sys.argv[2] if len(sys.argv) > 2 else 'am_michael'; speed = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
KOK = os.environ.get('KOKORO_DIR', os.path.join(os.path.dirname(__file__), '..', 'tools', 'kokoro'))
from kokoro_onnx import Kokoro
keep_previous(proj); VO = vo_dir(proj)
k = Kokoro(os.path.join(KOK, 'kokoro-v1.0.onnx'), os.path.join(KOK, 'voices-v1.0.bin')); durs = {}
for name, text in spoken(proj).items():
    x, sr = k.create(text, voice=voice, speed=speed, lang='en-us'); x = trim(np.asarray(x, dtype=np.float32), sr)
    sf.write(os.path.join(VO, name + '.wav'), x, sr); durs[name] = round(len(x) / sr, 3); print(name, durs[name], flush=True)
json.dump(durs, open(os.path.join(VO, 'durations.json'), 'w'), indent=1)
json.dump({'engine': 'kokoro-onnx', 'model': 'kokoro-v1.0', 'voice': voice, 'speed': speed}, open(os.path.join(VO, 'voice.json'), 'w'), indent=1)
print('total speech', round(sum(durs.values()), 2))
