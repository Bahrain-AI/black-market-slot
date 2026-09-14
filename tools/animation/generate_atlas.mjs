/**
 * BLACK MARKET — animation sprite-sheet generator.
 *
 * Authors procedural placeholder SVG frames into assets/anim-frames/<name>/,
 * rasterizes them with sharp, and packs each animation into a horizontal
 * WebP strip + TexturePacker-compatible JSON at assets/animations/<name>.
 *
 * Produces exactly the layout described in assets/specs/mechanics-assets.md:
 *   - assets/animations/<name>.webp   (RGBA WebP strip, 256x256 frames)
 *   - assets/animations/<name>.json   (meta + frames + anchor + durations +
 *                                      named animation arrays)
 *
 * These are PLACEHOLDER frames generated procedurally so the pipeline is
 * end-to-end working. Replace them by editing the rendered SVGs in
 * assets/anim-frames/<name>/ and re-running: `pnpm gen:animations`.
 *
 * Usage:  pnpm gen:animations      (or: node tools/animation/generate_atlas.mjs)
 */
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const FRAMES_DIR = path.join(root, 'assets', 'anim-frames');
const OUT_DIR = path.join(root, 'assets', 'animations');

const FW = 256;
const FH = 256;
const FRAME_MS = 140;

const svgDoc = (inner) =>
  `<svg xmlns="http://www.w3.org/2000/svg" width="${FW}" height="${FH}" viewBox="0 0 ${FW} ${FH}">${inner}</svg>`;

/* ------------------------------------------------------------------ */
/*  Frame templates                                                     */
/* ------------------------------------------------------------------ */

const tile = (color = '#160f0a', stroke = '#b89555') =>
  `<rect x="-104" y="-104" width="208" height="208" rx="28" fill="${color}"/>` +
  `<rect x="-104" y="-104" width="208" height="208" rx="28" fill="none" stroke="${stroke}" stroke-width="6"/>`;

const glowDef = (id, color) =>
  `<defs><radialGradient id="${id}" cx="50%" cy="50%">` +
  `<stop offset="0%" stop-color="${color}"/><stop offset="100%" stop-color="${color}" stop-opacity="0"/>` +
  `</radialGradient></defs>`;

/** Expanding W badge (wild expansion, 5 frames). */
function wildFrame(i) {
  const scale = [0.55, 0.82, 1.1, 1.55, 2.0][i];
  const glow = [0.35, 0.5, 0.68, 0.85, 1][i];
  return `${glowDef('g', '#ffd36a')}
  <g transform="translate(128 128) scale(${scale})">
    <circle r="120" fill="url(#g)" opacity="${glow}"/>
    ${tile('#160f0a', '#ffd36a')}
    <text x="0" y="12" font-family="Arial Black, Arial" font-size="122" font-weight="900" fill="#ffd36a" text-anchor="middle">W</text>
  </g>`;
}

/** Pulsing S badge (free-spins scatter, 5 frames). */
function scatterFrame(i) {
  const scale = [1, 1.18, 1.3, 1.18, 1][i];
  const glow = [0.55, 0.72, 0.9, 0.72, 0.55][i];
  const rays = [2, 3].includes(i)
    ? `<g stroke="#c9b037" stroke-width="5" stroke-linecap="round" opacity="0.7">
         <line x1="128" y1="14" x2="128" y2="52"/><line x1="242" y1="128" x2="204" y2="128"/>
         <line x1="128" y1="242" x2="128" y2="204"/><line x1="14" y1="128" x2="52" y2="128"/></g>`
    : '';
  return `${glowDef('g', '#ffd36a')}
  <g transform="translate(128 128) scale(${scale})">
    <circle r="118" fill="url(#g)" opacity="${glow}"/>
    ${tile('#160f0a', '#c9b037')}
    <text x="0" y="12" font-family="Arial Black, Arial" font-size="118" font-weight="900" fill="#c9b037" text-anchor="middle">S</text>
  </g>${rays}`;
}

/** Value gem popping in (hold-and-spin lock, 6 frames). */
function holdFrame(i) {
  const values = [25, 50, 75, 100, 150, 250];
  const scale = [0.5, 0.72, 1, 1.12, 1, 1][i];
  return `<g transform="translate(128 128) scale(${scale})">
    ${tile()}
    <polygon points="0,-78 72,0 0,78 -72,0" fill="#b03a1f" stroke="#ffd36a" stroke-width="6"/>
    <polygon points="0,-78 42,0 0,78" fill="#d85835" opacity="0.85"/>
    <text x="0" y="1" font-family="Arial Black, Arial" font-size="34" font-weight="900" fill="#ffe9b0" text-anchor="middle">${values[i]}</text>
  </g>`;
}

/** Tile dissolving into shards (cascade removal, 4 frames). */
function cascadeFrame(i) {
  const alpha = [1, 0.72, 0.42, 0.12][i];
  const dist = [30, 52, 74, 96][i];
  const shards = [
    `<path d="M-7 -24 L22 -18 L-2 4 Z" transform="translate(128 128) rotate(20) translate(${dist} 0)"/>`,
    `<path d="M-7 -24 L22 -18 L-2 4 Z" transform="translate(128 128) rotate(110) translate(${dist} 0)"/>`,
    `<path d="M-7 -24 L22 -18 L-2 4 Z" transform="translate(128 128) rotate(200) translate(${dist} 0)"/>`,
    `<path d="M-7 -24 L22 -18 L-2 4 Z" transform="translate(128 128) rotate(290) translate(${dist} 0)"/>`,
    `<path d="M-7 -24 L22 -18 L-2 4 Z" transform="translate(128 128) rotate(65) translate(${dist + 14} 0)"/>`,
    `<path d="M-7 -24 L22 -18 L-2 4 Z" transform="translate(128 128) rotate(155) translate(${dist + 14} 0)"/>`,
  ].join('');
  return `<rect x="16" y="16" width="224" height="224" rx="24" fill="#160f0a" opacity="${alpha}"/>
  <rect x="16" y="16" width="224" height="224" rx="24" fill="none" stroke="#b89555" stroke-width="5" opacity="${alpha}"/>
  <g transform="translate(58 58) rotate(15)" opacity="${alpha}"><path d="M0 0 L72 30 L0 62 L-20 30 Z" fill="#d85835"/></g>
  <g transform="translate(172 70) rotate(-25)" opacity="${alpha}"><path d="M0 0 L82 26 L0 54 L-19 26 Z" fill="#d85835"/></g>
  <g fill="#d85835" fill-opacity="${Math.max(alpha, 0.4)}">${shards}</g>`;
}

/** Gold drop falling into a cell (reel refill, 4 frames). */
function refillFrame(i) {
  const yOff = [-110, -52, 0, 8][i];
  const alpha = [0.8, 0.95, 1, 0.95][i];
  return `<defs><linearGradient id="d" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#ffe9b0"/><stop offset="100%" stop-color="#d8a737"/></linearGradient></defs>
  <g transform="translate(128 ${128 + yOff})" opacity="${alpha}">
    <path d="M0 -36 C 20 -8, 26 8, 0 32 C -26 8, -20 -8, 0 -36 Z" fill="url(#d)"/>
    <ellipse cx="0" cy="40" rx="15" ry="4" fill="#ffd36a" opacity="0.7"/>
  </g>`;
}

/* ------------------------------------------------------------------ */
/*  Animation definitions                                               */
/* ------------------------------------------------------------------ */

const ANIMATIONS = {
  'symbol-wild-expand': { frames: 5, render: wildFrame },
  'symbol-scatter-freespins': { frames: 5, render: scatterFrame },
  'symbol-hold-lock': { frames: 6, render: holdFrame },
  'fx-cascade-remove': { frames: 4, render: cascadeFrame },
  'fx-reel-refill': { frames: 4, render: refillFrame },
};

/* ------------------------------------------------------------------ */
/*  Build                                                               */
/* ------------------------------------------------------------------ */

let summary = [];

for (const [name, def] of Object.entries(ANIMATIONS)) {
  const animDir = path.join(FRAMES_DIR, name);
  await mkdir(animDir, { recursive: true });

  const buffers = [];
  const frameNames = [];
  const durations = [];

  for (let i = 0; i < def.frames; i++) {
    const inner = def.render(i);
    const svgText = svgDoc(inner);
    const svgPath = path.join(animDir, `frame-${String(i).padStart(2, '0')}.svg`);
    await writeFile(svgPath, svgText, 'utf8');
    // Ensure a leading BOM-free buffer with explicit width/height density.
    const png = await sharp(Buffer.from(svgText), { density: 72 }).png().toBuffer();
    buffers.push(png);
    frameNames.push(`frame_${i}`);
    durations.push(FRAME_MS);
  }

  const sheetWidth = FW * def.frames;
  const sheetName = `${name}.webp`;
  const sheetPath = path.join(OUT_DIR, sheetName);
  await mkdir(OUT_DIR, { recursive: true });
  await sharp({
    create: { width: sheetWidth, height: FH, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } },
  })
    .composite(buffers.map((b, i) => ({ input: b, left: i * FW, top: 0 })))
    .webp({ quality: 88, alphaQuality: 100 })
    .toFile(sheetPath);

  const frames = {};
  for (let i = 0; i < def.frames; i++) {
    frames[frameNames[i]] = {
      frame: { x: i * FW, y: 0, w: FW, h: FH },
      anchor: { x: 0.5, y: 0.5 },
      duration: FRAME_MS,
    };
  }

  const json = {
    meta: { image: sheetName, size: { w: sheetWidth, h: FH }, scale: '1' },
    frames,
    animations: { default: frameNames },
    durations: { default: durations },
  };
  await writeFile(path.join(OUT_DIR, `${name}.json`), JSON.stringify(json, null, 2), 'utf8');

  const size = (await import('node:fs/promises')).stat(sheetPath);
  summary.push(`${name}: ${def.frames} frames, ${sheetWidth}x${FH}, ${Math.round((await size).size / 1024)} KB`);
}

console.log('Generated animation sheets:');
summary.forEach((line) => console.log(`  ${line}`));