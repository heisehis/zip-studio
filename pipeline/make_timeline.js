// Builds <project>/src/comp/timeline.js (window.TL) from <project>/plan/lines.json and the measured voice files.
//   node pipeline/make_timeline.js <project> [gap] [lead] [tail]
// With src/audio/vo/durations.json the scene times are measured from the voice; without it they are estimated from word counts.
// With src/audio/vo/words.json the captions are timed per word; otherwise by character share inside each line.
// TL = { measured, dur, scenes:[{id,t0,t1,v0,v1}], captions:[{text,t0,t1}], vo:[{id,t0,t1}], words:{id:[...]} }
const fs = require('fs'), path = require('path');
const proj = path.resolve(process.argv[2] || '.');
const GAP = +(process.argv[3] || .32), LEAD = +(process.argv[4] || .25), TAIL = +(process.argv[5] || 2.2), WPS = 2.6;
const LINES = JSON.parse(fs.readFileSync(path.join(proj, 'plan', 'lines.json'), 'utf8'));
const vo = path.join(proj, 'src', 'audio', 'vo');
const read = f => fs.existsSync(path.join(vo, f)) ? JSON.parse(fs.readFileSync(path.join(vo, f), 'utf8')) : null;
const measured = read('durations.json'), WORDS = read('words.json') || {};
let exact = 0, approx = 0, t = LEAD; const scenes = [], captions = [], voL = [];
LINES.forEach(({ id, text, hold }) => {
  const d = text ? (measured && measured[id] != null ? measured[id] : text.split(/\s+/).length / WPS) : (hold || 2);
  const s0 = scenes.length ? scenes[scenes.length - 1].t1 : 0, v0 = t, v1 = t + d;
  if (text) {
    voL.push({ id, t0: +v0.toFixed(3), t1: +v1.toFixed(3) });
    const words = text.split(/\s+/), chunks = []; let cur = [];                     // caption chunks: up to 4 words, split at punctuation
    words.forEach(w => { cur.push(w); if (cur.length >= 4 || /[.?!,]"?$/.test(w)) { chunks.push(cur.join(' ')); cur = []; } });
    if (cur.length) chunks.push(cur.join(' '));
    for (let k = chunks.length - 1; k > 0; k--) if (chunks[k].split(' ').length === 1 && chunks[k - 1].split(' ').length < 4) { chunks[k - 1] += ' ' + chunks[k]; chunks.splice(k, 1); }
    const wt = WORDS[id];
    if (wt && wt.length === words.length) {
      exact++; let k = 0; const starts = chunks.map(c => { const st = wt[k].t0; k += c.split(' ').length; return st; });
      chunks.forEach((c, j) => captions.push({ text: c, t0: +(v0 + (j ? starts[j] : 0)).toFixed(3), t1: +(v0 + (j + 1 < chunks.length ? starts[j + 1] : d)).toFixed(3) }));
    } else {
      approx++; const total = chunks.reduce((a, c) => a + c.length, 0); let c0 = v0;
      chunks.forEach(c => { const cd = d * c.length / total; captions.push({ text: c, t0: +c0.toFixed(3), t1: +(c0 + cd).toFixed(3) }); c0 += cd; });
    }
  }
  t = v1 + GAP;
  scenes.push({ id, t0: +s0.toFixed(3), t1: +(v1 + GAP / 2).toFixed(3), v0: +v0.toFixed(3), v1: +v1.toFixed(3) });
});
scenes[scenes.length - 1].t1 = +(scenes[scenes.length - 1].t1 + TAIL).toFixed(3);
// absolute word times the picture can react to: TL.word('line-id', 'word')
const TL = { measured: !!measured, dur: scenes[scenes.length - 1].t1, scenes, captions, vo: voL, words: WORDS };
fs.writeFileSync(path.join(proj, 'src', 'comp', 'timeline.js'),
  'window.TL=' + JSON.stringify(TL, null, 1) + ';\nTL.word=(l,w)=>{const v=TL.vo.find(x=>x.id===l),x=(TL.words[l]||[]).find(x=>x.text.toLowerCase().replace(/[^a-z0-9\']/g,"")===w);return v&&x?v.t0+x.t0:null};\n');
console.log('captions with measured word times:', exact, 'approximate:', approx);
console.log(measured ? 'measured' : 'ESTIMATED', 'dur', TL.dur, scenes.map(s => `${s.id}@${s.t0}`).join(' '));
