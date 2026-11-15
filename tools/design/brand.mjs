// Render the brand pictures from their SVG sources in assets/brand/, which embed the approved app icon.
//
//   node tools/design/brand.mjs     assets/brand/banner.svg -> assets/banner.png (1280x420, the README banner)
//                                   assets/brand/social-preview.svg -> assets/social-preview.png (1280x640, GitHub's size)
//
// The text is set in Segoe UI Variable, the design's system font, so render on Windows (resvg loads system fonts
// here; the icon renders in icons.mjs never do, which is what keeps those byte-identical on every platform).
// The app icon inside each source is a copy of assets/icons/src/app/gemail.svg: this script refuses a source
// whose copy has drifted from it, so the banner can never show a retired icon.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Resvg } from '@resvg/resvg-js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const icon = fs.readFileSync(path.join(ROOT, 'assets/icons/src/app/gemail.svg'), 'utf8').trim()
  .replace(/^<svg[^>]*>/, '').replace(/<\/svg>$/, '');
const JOBS = [['assets/brand/banner.svg', 'assets/banner.png', 1280], ['assets/brand/social-preview.svg', 'assets/social-preview.png', 1280]];
for (const [src, out, width] of JOBS) {
  const svg = fs.readFileSync(path.join(ROOT, src), 'utf8');
  if (!svg.includes(icon)) {
    console.error(`brand: ${src} does not embed the current assets/icons/src/app/gemail.svg; paste its paths into the <g id="app-icon"> group`);
    process.exit(1);
  }
  const png = new Resvg(svg, { fitTo: { mode: 'width', value: width }, font: { loadSystemFonts: true } }).render().asPng();
  fs.writeFileSync(path.join(ROOT, out), png);
  console.log(`brand: wrote ${out}`);
}
