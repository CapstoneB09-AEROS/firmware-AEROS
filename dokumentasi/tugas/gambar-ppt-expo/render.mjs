// Membuat PNG rumus dari rumus.json (KaTeX + Chrome tanpa kepala).
// Pakai : cd <folder sementara berisi node_modules katex dan puppeteer-core> && node render.mjs <folder gambar-ppt-expo>
// Diagram : npx mmdc -i diagram/NAMA.mmd -o diagram/NAMA.png -s 3 -b white -c mermaid-config.json -p puppeteer.json
//           (puppeteer.json: {"executablePath": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"})
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(path.join(process.cwd(), 'x.js'));
const katex = require('katex');
const puppeteer = require('puppeteer-core');

const dir = path.resolve(process.argv[2]);
const rumus = (await import(path.join(dir, 'rumus.mjs'))).default;
const css = fs.readFileSync(path.join(process.cwd(), 'node_modules/katex/dist/katex.min.css'), 'utf8')
  .replace(/url\(fonts\//g, 'url(file://' + path.join(process.cwd(), 'node_modules/katex/dist/fonts/') );
fs.mkdirSync(path.join(dir, 'rumus'), { recursive: true });

const browser = await puppeteer.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  args: ['--allow-file-access-from-files'],
});
const page = await browser.newPage();
await page.setViewport({ width: 1400, height: 400, deviceScaleFactor: 3 });
for (const [nama, tex] of Object.entries(rumus)) {
  const html = katex.renderToString(tex, { displayMode: true, throwOnError: true });
  await page.setContent(`<!doctype html><meta charset="utf-8"><style>${css}
    body{margin:0;background:#fff;display:inline-block}
    #w{display:inline-block;padding:18px 28px;font-size:30px;background:#fff}
    .katex-display{margin:0}</style><div id="w">${html}</div>`);
  await page.evaluate(() => document.fonts.ready);
  const el = await page.$('#w');
  await el.screenshot({ path: path.join(dir, 'rumus', nama + '.png') });
  console.log('ok', nama);
}
await browser.close();
