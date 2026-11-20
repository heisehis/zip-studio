// Shared timeline: read by comp.html (picture) and src/tools/sfx.py (sound effects). Times in seconds.
// v4: supermarket story (plan/script.md). Bubbles stay readable for about 0.6 s plus 0.15 s per word.
window.TL = {
  dur: 21.9,
  scenes: [
    { id: 'scroll', t0: 0.0,  t1: 3.0 },
    { id: 'chat1',  t0: 3.0,  t1: 9.0 },
    { id: 'card1',  t0: 9.0,  t1: 10.4 },
    { id: 'chat2',  t0: 10.4, t1: 17.4 },
    { id: 'card2',  t0: 17.4, t1: 19.4 },
    { id: 'end',    t0: 19.4, t1: 21.9 }
  ],
  // chat events: msg = bubble appears; typing = dots shown from t to t1
  chat1: [
    { k: 'msg', id: 'a1', t: 3.5 },
    { k: 'msg', id: 'a2', t: 3.9 },
    { k: 'typing', id: 'ty1', t: 4.9, t1: 5.4 },
    { k: 'msg', id: 'a3', t: 5.4 },
    { k: 'msg', id: 'a4', t: 6.5 },
    { k: 'typing', id: 'ty2', t: 7.1, t1: 7.5 },
    { k: 'msg', id: 'a5', t: 7.5 }
  ],
  chat2: [
    { k: 'msg', id: 'b1', t: 10.9 },
    { k: 'msg', id: 'b2', t: 11.9 },
    { k: 'msg', id: 'b3', t: 12.5 },
    { k: 'typing', id: 'ty3', t: 13.4, t1: 14.2 },
    { k: 'msg', id: 'b4', t: 14.2 },
    { k: 'msg', id: 'b5', t: 15.3 }
  ],
  scrollMove: { t0: 0.5, t1: 2.7, px: 760 },
  pushIn: { t0: 16.4, t1: 17.4, target: 'b5' },
  // sound cues (sfx.py). whoosh: the loudest moment lands on t; the others start on t.
  sfx: [
    { k: 'whoosh', t: 3.2 }, { k: 'sent', t: 3.5 }, { k: 'sent', t: 3.9 }, { k: 'recv', t: 5.4 }, { k: 'sent', t: 6.5 }, { k: 'recv', t: 7.5 },
    { k: 'whoosh', t: 10.6 }, { k: 'sent', t: 10.9 }, { k: 'sent', t: 11.9 }, { k: 'sent', t: 12.5 }, { k: 'recv', t: 14.2 }, { k: 'recv', t: 15.3 },
    { k: 'whoosh', t: 16.9 }, { k: 'whoosh', t: 19.65 }, { k: 'sent', t: 20.3 }
  ]
};
