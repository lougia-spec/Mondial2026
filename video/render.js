// Rend video.html image par image puis encode en MP4 avec ffmpeg.
// Usage : node render.js [sortie.mp4]   (nécessite playwright + ffmpeg)
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const FPS = 30, W = 1920, H = 1080, WORKERS = 4;
const out = path.resolve(process.argv[2] || path.join(__dirname, 'mondial2026.mp4'));

(async () => {
  const frames = fs.mkdtempSync(path.join(os.tmpdir(), 'mondial-frames-'));
  const browser = await chromium.launch();
  const url = 'file://' + path.join(__dirname, 'video.html');
  const pages = [];
  for (let i = 0; i < WORKERS; i++) {
    const p = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
    await p.goto(url);
    await p.evaluate(() => document.fonts.ready);
    pages.push(p);
  }
  const duration = await pages[0].evaluate(() => window.DURATION);
  const total = Math.round(duration * FPS);
  let next = 0;
  await Promise.all(pages.map(async (p) => {
    while (next < total) {
      const f = next++;
      await p.evaluate((t) => window.seek(t), f / FPS);
      await p.screenshot({ path: path.join(frames, String(f).padStart(5, '0') + '.jpg'), type: 'jpeg', quality: 95 });
      if (f % 150 === 0) console.log(`image ${f}/${total}`);
    }
  }));
  await browser.close();
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(frames, '%05d.jpg'),
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: 'inherit' });
  fs.rmSync(frames, { recursive: true, force: true });
  console.log('OK →', out);
})();
