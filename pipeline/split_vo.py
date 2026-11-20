# Splits one continuous voiceover recording (a voice actor's take, or an AI voice exported as one file) into the script's lines.
#   python split_vo.py <project> <recording> [model]      default model base.en (faster-whisper, downloaded once)
# Method: transcribe locally with word times, match the known script words to the heard words in order, and cut each line
# at the middle of the gap before the next. Nothing leaves the machine except the one-time model download.
# Writes <project>/src/audio/vo/<id>.wav (24 kHz mono), durations.json, words.json, voice.json, align-report.txt.
import sys, os, re, json, difflib, subprocess
import numpy as np, soundfile as sf
from voice_lines import project, spoken, vo_dir, keep_previous

SR = 24000
def norm(w): return re.sub(r"[^a-z0-9']", '', w.lower().replace('’', "'"))

def main():
    proj = project(sys.argv); rec = sys.argv[2]; model = sys.argv[3] if len(sys.argv) > 3 else 'base.en'
    tmp = os.path.join(proj, 'src', 'audio', '_full.wav')
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', rec, '-ac', '1', '-ar', str(SR), tmp], check=True)
    x, _ = sf.read(tmp, dtype='float32'); total = len(x) / SR; os.remove(tmp)
    w16 = tmp + '.16k.wav'
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', rec, '-ac', '1', '-ar', '16000', w16], check=True)
    a16, _ = sf.read(w16, dtype='float32'); os.remove(w16)        # an array avoids PyAV version mismatches in faster-whisper
    from faster_whisper import WhisperModel
    segs, _ = WhisperModel(model, device='cpu', compute_type='int8').transcribe(a16, language='en', word_timestamps=True, beam_size=5)
    heard = [{'t': w.word.strip(), 'a': float(w.start), 'b': float(w.end)} for s in segs for w in (s.words or [])]
    print('heard', len(heard), 'words:', ' '.join(h['t'] for h in heard))
    L = spoken(proj); script = [(lid, w) for lid, text in L.items() for w in text.split()]
    A = [norm(w) for _, w in script]; B = [norm(h['t']) for h in heard]
    at = [None] * len(script)
    for blk in difflib.SequenceMatcher(a=A, b=B, autojunk=False).get_matching_blocks():
        for k in range(blk.size): at[blk.a + k] = (heard[blk.b + k]['a'], heard[blk.b + k]['b'])
    matched = sum(1 for v in at if v)
    for i, v in enumerate(at):                                   # unmatched words: interpolate between matched neighbours
        if v: continue
        p = next((j for j in range(i - 1, -1, -1) if at[j]), None); n = next((j for j in range(i + 1, len(at)) if at[j]), None)
        if p is None and n is None: raise SystemExit('no words matched; the recording does not look like the script')
        if p is None: at[i] = (max(0, at[n][0] - .2 * (n - i)), at[n][0] - .2 * (n - i) + .15)
        elif n is None: at[i] = (at[p][1] + .05 + .2 * (i - p - 1), at[p][1] + .05 + .2 * (i - p))
        else: g0, g1 = at[p][1], at[n][0]; f = (i - p) / (n - p); at[i] = (g0 + (g1 - g0) * (f - .5 / (n - p)), g0 + (g1 - g0) * f)
    ids = list(L); span = {}
    for lid in ids:
        idx = [i for i, w in enumerate(script) if w[0] == lid]; span[lid] = (at[idx[0]][0], at[idx[-1]][1], idx)
    cuts = [0.0] + [(span[ids[k]][1] + span[ids[k + 1]][0]) / 2 for k in range(len(ids) - 1)] + [total]
    keep_previous(proj); VO = vo_dir(proj); durs, allw, rep = {}, {}, []
    for k, lid in enumerate(ids):
        seg = x[int(cuts[k] * SR):int(cuts[k + 1] * SR)]
        idx = np.where(np.abs(seg) > 0.01)[0]; s0 = max(0, idx[0] - int(.04 * SR)); s1 = min(len(seg), idx[-1] + int(.04 * SR)); seg = seg[s0:s1]
        off = cuts[k] + s0 / SR; sf.write(os.path.join(VO, lid + '.wav'), seg, SR); durs[lid] = round(len(seg) / SR, 3)
        allw[lid] = [{'text': norm(script[i][1]), 't0': round(max(0, at[i][0] - off), 3), 't1': round(max(0, at[i][1] - off), 3)} for i in span[lid][2]]
        rep.append('%-10s %6.2f-%6.2f s  dur %5.2f  words %d' % (lid, off, off + len(seg) / SR, durs[lid], len(allw[lid])))
    json.dump(durs, open(os.path.join(VO, 'durations.json'), 'w'), indent=1); json.dump(allw, open(os.path.join(VO, 'words.json'), 'w'), indent=1)
    json.dump({'engine': 'recording', 'voice': os.path.basename(rec), 'aligned_with': 'faster-whisper ' + model}, open(os.path.join(VO, 'voice.json'), 'w'), indent=1)
    rep += ['script words matched to heard words: %d of %d' % (matched, len(script)), 'recording %.2f s, speech %.2f s' % (total, sum(durs.values()))]
    open(os.path.join(VO, 'align-report.txt'), 'w').write('\n'.join(rep) + '\n'); print('\n'.join(rep))

main()
