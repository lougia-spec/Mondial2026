// Rend video.html image par image puis encode en MP4 avec ffmpeg.
// Usage : node render.js [sortie.mp4]   (nécessite playwright, ffmpeg, python3 + numpy)
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
  const wav = path.join(frames, 'audio.wav');
  execFileSync('python3', [path.join(__dirname, 'audio.py'), wav], { stdio: 'inherit' });   // bande-son
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(frames, '%05d.jpg'), '-i', wav,
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest',
    '-movflags', '+faststart', out], { stdio: 'inherit' });
  fs.rmSync(frames, { recursive: true, force: true });
  console.log('OK →', out);
})();
