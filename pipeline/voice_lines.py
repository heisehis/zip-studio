# Shared helpers for the voice tools. A project's voiceover script lives in <project>/plan/lines.json:
#   [{"id": "hook", "text": "Your business deserves more..."}, {"id": "title", "hold": 2.4}, ...]
# Entries with "text" are spoken; entries with only "hold" are silent on-screen beats (seconds).
# Optional "say" overrides the text sent to the voice engine (for example extra commas for phrasing).
import os, json

def project(argv, i=1):
    if len(argv) <= i: raise SystemExit('first argument: the project folder')
    return os.path.abspath(argv[i])

def lines(proj):
    p = os.path.join(proj, 'plan', 'lines.json')
    if not os.path.exists(p): raise SystemExit('missing ' + p)
    return json.load(open(p, encoding='utf-8'))

def spoken(proj):
    """{id: text sent to the voice engine} for the spoken lines, in order."""
    return {l['id']: l.get('say', l['text']) for l in lines(proj) if l.get('text')}

def vo_dir(proj):
    d = os.path.join(proj, 'src', 'audio', 'vo'); os.makedirs(d, exist_ok=True); return d

def keep_previous(proj):
    """Copy the current voice folder to vo-<engine>-<voice>/ before it is replaced."""
    import shutil
    d = vo_dir(proj); vj = os.path.join(d, 'voice.json')
    if not os.path.exists(vj): return
    v = json.load(open(vj)); name = 'vo-%s-%s' % (v.get('engine', 'old'), str(v.get('voice', 'x')).replace('/', '_').replace(' ', '_')[:40])
    dst = os.path.join(os.path.dirname(d), name)
    if not os.path.exists(dst): shutil.copytree(d, dst); print('kept previous voice in', dst)
