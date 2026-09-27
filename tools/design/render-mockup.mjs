// Render the imported design mockup (docs/design/mockup/*.dc.html) to static PNGs.
//
// The .dc.html artboards are templates for the Design canvas runtime
// (holes, <sc-for>, <sc-if>, a renderVals() class). This script expands them
// to plain HTML with the board's default props (and one extra render per
// boolean prop flipped), then screenshots each page with headless Chrome (or
// Edge) at 2x. Output: docs/design/mockup/renders/<Board>[--<prop>-<value>].png
//
// Usage: node tools/design/render-mockup.mjs            (render every board)
//        node tools/design/render-mockup.mjs Main       (one board)
// Needs: Google Chrome or Microsoft Edge, or BROWSER_PATH pointing at a Chromium
// binary. Chrome is tried first: Edge headless is disabled by policy on some
// managed machines, where it exits 0 and writes nothing.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import crypto from 'node:crypto';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const MOCKUP = path.join(ROOT, 'docs', 'design', 'mockup');
const OUT = path.join(MOCKUP, 'renders');
const BROWSER = process.env.BROWSER_PATH ||
  ['C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
    path.join(process.env.LOCALAPPDATA || '', 'Google/Chrome/Application/chrome.exe'),
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', 'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    .find((p) => p && fs.existsSync(p));

const esc = (v) => String(v).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const lookup = (expr, scope) => {
  const e = expr.trim();
  if (e === 'true') return true;
  if (e === 'false') return false;
  if (/^-?\d+(\.\d+)?$/.test(e)) return Number(e);
  return e.split('.').reduce((o, k) => (o == null ? undefined : o[k]), scope);
};

// Replace holes: a whole-value boolean attribute is set or dropped, the rest is escaped text.
function fillHoles(html, scope) {
  html = html.replace(/\s([a-zA-Z-]+)="\{\{\s*([^}]+?)\s*\}\}"/g, (m, attr, expr) => {
    const v = lookup(expr, scope);
    if (v === true) return ` ${attr}`;
    if (v === false || v == null) return '';
    return ` ${attr}="${esc(v)}"`;
  });
  return html.replace(/\{\{\s*([^}]+?)\s*\}\}/g, (m, expr) => {
    const v = lookup(expr, scope);
    if (v === undefined) throw new Error(`hole {{ ${expr} }} is undefined`);
    return esc(v);
  });
}

// Expand the first top-level <sc-for>/<sc-if>, recursively; plain text gets its holes filled.
function expand(html, scope) {
  const open = /<(sc-for|sc-if)\b([^>]*)>/g;
  const m = open.exec(html);
  if (!m) return fillHoles(html, scope);
  const tag = m[1];
  let depth = 1, i = open.lastIndex;
  const re = new RegExp(`<(/?)${tag}\\b[^>]*>`, 'g');
  re.lastIndex = i;
  let t;
  while ((t = re.exec(html))) {
    depth += t[1] ? -1 : 1;
    if (depth === 0) break;
  }
  if (!t) throw new Error(`unclosed <${tag}>`);
  const body = html.slice(i, t.index);
  const attrs = m[2];
  let middle = '';
  if (tag === 'sc-for') {
    const list = lookup(attrs.match(/list="\{\{\s*([^}]+?)\s*\}\}"/)[1], scope) || [];
    const as = attrs.match(/as="(\w+)"/)[1];
    middle = list.map((item, k) => expand(body, { ...scope, [as]: item, $index: k })).join('');
  } else if (lookup(attrs.match(/value="\{\{\s*([^}]+?)\s*\}\}"/)[1], scope)) {
    middle = expand(body, scope);
  }
  return fillHoles(html.slice(0, m.index), scope) + middle + expand(html.slice(re.lastIndex), scope);
}

function renderBoard(file, props) {
  const src = fs.readFileSync(path.join(MOCKUP, file), 'utf8');
  const script = src.match(/<script type="text\/x-dc" data-dc-script data-props='([^']*)'>([\s\S]*?)<\/script>/);
  const Component = new Function('DCLogic', script[2] + '\nreturn Component;')(class { constructor() { this.props = {}; } });
  const c = new Component();
  c.props = props;
  const vals = c.renderVals();
  const xdc = src.match(/<x-dc>([\s\S]*?)<\/x-dc>/)[1];
  const style = (xdc.match(/<helmet>([\s\S]*?)<\/helmet>/) || ['', ''])[1];
  const body = expand(xdc.replace(/<helmet>[\s\S]*?<\/helmet>/, ''), vals);
  const title = (src.match(/<title>([^<]*)<\/title>/) || ['', file])[1];
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>${title}</title>${style}</head><body>${body}</body></html>`;
}

// Lay the page out in the browser and return the root element's content height,
// so a board whose content overflows its declared size fails instead of clipping.
function contentHeight(html, w, h) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'gemail-measure-'));
  const page = path.join(dir, 'board.html');
  const probe = '<script>addEventListener("load",()=>{const r=document.body.firstElementChild;' +
    'r.style.height="auto";document.body.setAttribute("data-content-h",String(Math.ceil(r.scrollHeight)))})</script>';
  fs.writeFileSync(page, html.replace('</body>', probe + '</body>'));
  const dom = execFileSync(BROWSER, ['--headless=new', '--disable-gpu', '--no-first-run',
    `--user-data-dir=${path.join(dir, 'profile')}`, `--window-size=${w},${h}`, '--virtual-time-budget=2000',
    '--dump-dom', 'file:///' + page.replace(/\\/g, '/')], { encoding: 'utf8', timeout: 120000, stdio: ['ignore', 'pipe', 'ignore'] });
  fs.rmSync(dir, { recursive: true, force: true });
  const m = dom.match(/data-content-h="(\d+)"/);
  if (!m) throw new Error('could not measure the board content height');
  return Number(m[1]);
}

function screenshot(html, w, h, out) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'gemail-mockup-'));
  const page = path.join(dir, 'board.html');
  fs.writeFileSync(page, html);
  fs.rmSync(out, { force: true });
  execFileSync(BROWSER, ['--headless=new', '--disable-gpu', '--no-first-run', '--hide-scrollbars',
    `--user-data-dir=${path.join(dir, 'profile')}`, '--force-device-scale-factor=2',
    `--window-size=${w},${h}`, `--screenshot=${out}`, 'file:///' + page.replace(/\\/g, '/')], { stdio: 'ignore', timeout: 120000 });
  fs.rmSync(dir, { recursive: true, force: true });
  if (!fs.existsSync(out)) throw new Error(`${BROWSER} wrote no screenshot for ${path.basename(out)} (headless disabled by policy?)`);
}

if (!BROWSER) { console.error('render-mockup: no Chrome or Edge found; set BROWSER_PATH'); process.exit(2); }
const canvas = JSON.parse(fs.readFileSync(path.join(MOCKUP, 'canvas.json'), 'utf8'));
const only = process.argv[2];
fs.mkdirSync(OUT, { recursive: true });
// renders/manifest.json: which board source (sha256) each render was made from,
// so scripts/design-lint.py can refuse a render older than its board.
const MANIFEST = path.join(OUT, 'manifest.json');
const manifest = fs.existsSync(MANIFEST) ? JSON.parse(fs.readFileSync(MANIFEST, 'utf8')) : {};
// Line-ending-neutral for text (boards); PNGs are hashed raw. Matches scripts/design-lint.py.
const sha = (buf, file = '') => crypto.createHash('sha256')
  .update(file.toLowerCase().endsWith('.png') ? buf : Buffer.from(buf.toString('latin1').replace(/\r\n/g, '\n'), 'latin1'))
  .digest('hex');
for (const file of canvas.order) {
  const name = file.replace('.dc.html', '');
  if (only && only !== name) continue;
  const { w, h } = canvas.boards[file];
  const src = fs.readFileSync(path.join(MOCKUP, file), 'utf8');
  const props = JSON.parse(src.match(/data-props='([^']*)'/)[1].replace(/&#39;/g, "'").replace(/&amp;/g, '&'));
  const defaults = Object.fromEntries(Object.entries(props).filter(([k]) => k !== '$preview').map(([k, v]) => [k, v.default]));
  const variants = [['', defaults]];
  for (const [k, v] of Object.entries(defaults)) if (typeof v === 'boolean') variants.push([`--${k}-${!v}`, { ...defaults, [k]: !v }]);
  for (const [suffix, p] of variants) {
    const out = path.join(OUT, `${name}${suffix}.png`);
    const html = renderBoard(file, p);
    const need = contentHeight(html, w, h);
    if (need > h) {
      console.error(`render-mockup: ${file}${suffix} content is ${need}px tall but the board is ${h}px: raise the board height (canvas.json, root div, $preview) to at least ${need}`);
      process.exitCode = 1;
      continue;
    }
    screenshot(html, w, h, out);
    manifest[`${name}${suffix}.png`] = { board: file, props: p, boardSha256: sha(fs.readFileSync(path.join(MOCKUP, file)), file), pngSha256: sha(fs.readFileSync(out), out) };
    console.log(`rendered ${path.relative(ROOT, out)} (${w}x${h} @2x)`);
  }
}
fs.writeFileSync(MANIFEST, JSON.stringify(Object.fromEntries(Object.entries(manifest).sort()), null, 2) + '\n');
