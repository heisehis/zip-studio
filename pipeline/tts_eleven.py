# Voiceover with ElevenLabs (official API; sends the script text to ElevenLabs; uses account credits).
# The API key is read from the environment variable ELEVENLABS_API_KEY. It is never written to disk.
# Commercial use needs a paid plan at the time the audio is generated; library voices can carry their own terms.
#   python tts_eleven.py voices                                list the voices saved in the account
#   python tts_eleven.py <project> <voice_id> [speed] [model]  default model eleven_multilingual_v2
# Writes <project>/src/audio/vo/<id>.wav (24 kHz mono), durations.json, words.json, voice.json.
import sys, os, json, base64, subprocess, time, urllib.request, urllib.error
import numpy as np, soundfile as sf
from voice_lines import spoken, vo_dir, keep_previous

API = 'https://api.elevenlabs.io/v1'; SR = 24000

def key():
    k = os.environ.get('ELEVENLABS_API_KEY', '').strip()
    if not k: raise SystemExit('ELEVENLABS_API_KEY is not set. Set it in this terminal, then run again.')
    return k

def call(method, path, body=None):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={'xi-api-key': key(), 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=120) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError('HTTP %s: %s' % (e.code, e.read().decode('utf-8', 'replace')[:400]))

def word_times(al):
    """Group per-character times into words split at whitespace."""
    out, cur = [], None
    for ch, a, b in zip(al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']):
        if ch.isspace():
            if cur: out.append(cur); cur = None
        elif cur: cur['text'] += ch; cur['t1'] = b
        else: cur = {'text': ch, 't0': a, 't1': b}
    if cur: out.append(cur)
    return out

def synth(proj, voice, speed, model):
    L = spoken(proj); key(); keep_previous(proj); VO = vo_dir(proj); durs, allw = {}, {}; ids = list(L)
    for i, name in enumerate(ids):
        body = {'text': L[name], 'model_id': model, 'voice_settings': {'speed': speed}}
        if i: body['previous_text'] = L[ids[i - 1]]
        if i + 1 < len(ids): body['next_text'] = L[ids[i + 1]]
        res = None
        for attempt in range(4):
            try: res = call('POST', '/text-to-speech/%s/with-timestamps' % voice, body); break
            except Exception as e:
                print('retry', name, str(e)[:300], flush=True)
                if 'HTTP 4' in str(e) and 'HTTP 429' not in str(e): raise SystemExit('stopped: request refused, see message above')
                time.sleep(4)
        if res is None: raise SystemExit('failed: ' + name)
        mp3 = os.path.join(VO, name + '.mp3'); wav = os.path.join(VO, name + '.wav')
        open(mp3, 'wb').write(base64.b64decode(res['audio_base64']))
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', mp3, '-ac', '1', '-ar', str(SR), wav + '.raw.wav'], check=True)
        x, _ = sf.read(wav + '.raw.wav', dtype='float32'); os.remove(wav + '.raw.wav'); os.remove(mp3)
        idx = np.where(np.abs(x) > 0.01)[0]; a = max(0, idx[0] - int(.04 * SR)); b = min(len(x), idx[-1] + int(.04 * SR))
        sf.write(wav, x[a:b], SR); off = a / SR; durs[name] = round((b - a) / SR, 3)
        ws = word_times(res.get('alignment') or res.get('normalized_alignment') or {'characters': [], 'character_start_times_seconds': [], 'character_end_times_seconds': []})
        allw[name] = [{'text': w['text'], 't0': round(max(0, w['t0'] - off), 3), 't1': round(max(0, w['t1'] - off), 3)} for w in ws]
        print(name, durs[name], len(ws), 'words', flush=True)
    json.dump(durs, open(os.path.join(VO, 'durations.json'), 'w'), indent=1)
    json.dump(allw, open(os.path.join(VO, 'words.json'), 'w'), indent=1)
    json.dump({'engine': 'elevenlabs', 'voice': voice, 'model': model, 'speed': speed}, open(os.path.join(VO, 'voice.json'), 'w'), indent=1)
    print('total speech', round(sum(durs.values()), 2), 's; characters sent', sum(len(t) for t in L.values()))

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['voices']:
        for v in call('GET', '/voices').get('voices', []):
            print(v.get('voice_id'), '|', v.get('name'), '|', v.get('category'), '|', json.dumps(v.get('labels') or {}))
    elif len(a) >= 2:
        synth(os.path.abspath(a[0]), a[1], float(a[2]) if len(a) > 2 else 1.0, a[3] if len(a) > 3 else 'eleven_multilingual_v2')
    else: print('usage: tts_eleven.py voices | <project> <voice_id> [speed] [model_id]')
