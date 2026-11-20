// Renders a project's HTML compositor (src/comp/comp.html) frame by frame with headless Chromium and pipes the frames to ffmpeg.
// The compositor must expose window.renderAt(t) (a pure function of time), window.ready (a Promise) and window.TL.dur (seconds).
//
//   node pipeline/render.js <project-dir> stills <t1> <t2> ...   -> <project>/previews/stills/t_<t>.jpg (half size)
//   node pipeline/render.js <project-dir> video [scale] [name]   -> <project>/src/render/<name>_noaudio.mp4 (scale 1 = 1080x1920)
//
// Needs Node, ffmpeg on PATH and Playwright. Playwright is found with require('playwright'); set PLAYWRIGHT_MODULE to its folder
// if it lives elsewhere, and CHROMIUM_PATH to use a specific Chromium build.
const path = require('path'), fs = require('fs'), { spawn } = require('child_process');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const FPS = +(process.env.FPS || 30), W = +(process.env.WIDTH || 1080), H = +(process.env.HEIGHT || 1920);
(async () => {
  const [proj, mode, ...rest] = process.argv.slice(2);
  if (!proj || !['stills', 'video'].includes(mode)) { console.error('usage: render.js <project-dir> stills <t...> | video [scale] [name]'); process.exit(2); }
  const root = path.resolve(proj);
  const scale = mode === 'video' ? parseFloat(rest[0] || '1') : 0.5;
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined, args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: scale });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.goto('file:///' + path.join(root, 'src', 'comp', 'comp.html').replace(/\\/g, '/'));
  await page.evaluate(() => window.ready);
  const dur = await page.evaluate(() => window.TL.dur);
  const shot = (o) => page.screenshot({ type: 'jpeg', clip: { x: 0, y: 0, width: W, height: H }, timeout: 180000, ...o });
  if (mode === 'stills') {
    const dir = path.join(root, 'previews', 'stills'); fs.mkdirSync(dir, { recursive: true });
    for (const s of rest) { await page.evaluate(t => renderAt(t), parseFloat(s)); await shot({ quality: 82, path: path.join(dir, `t_${parseFloat(s).toFixed(2).padStart(6, '0')}.jpg`) }); }
  } else {
    const dir = path.join(root, 'src', 'render'); fs.mkdirSync(dir, { recursive: true });
    const out = path.join(dir, `${rest[1] || 'video'}_noaudio.mp4`);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-color_range', 'tv', '-vf', 'scale=in_range=full:out_range=tv', '-r', String(FPS), out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const total = Math.round(dur * FPS);
    for (let f = 0; f < total; f++) {
      await page.evaluate(t => renderAt(t), f / FPS);
      let buf; for (let k = 0; k < 3 && !buf; k++) buf = await shot({ quality: 93 }).catch(() => null);
      if (!buf) throw new Error('frame ' + f + ' failed 3 times');
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 150 === 0) console.log(`frame ${f}/${total}`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r)); console.log('wrote', out);
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
