/**
 * Schema acceptance test for generated animation sprite sheets.
 *
 * Validates the TexturePacker-compatible JSON produced by
 * tools/animation/generate_atlas.mjs (see assets/specs/mechanics-assets.md):
 * frames with rect+anchor+duration, named animation arrays, matching image
 * file, and compact sheet size.
 */
import { readFileSync, readdirSync, statSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const dir = path.join(root, 'assets', 'animations');

describe('animation sprite sheets', () => {
  const jsons = readdirSync(dir).filter((f) => f.endsWith('.json'));

  it('has the required sheets for the production spec', () => {
    expect(jsons).toContain('symbol-wild-expand.json');
    expect(jsons).toContain('symbol-scatter-freespins.json');
    expect(jsons).toContain('symbol-hold-lock.json');
    expect(jsons).toContain('fx-cascade-remove.json');
    expect(jsons).toContain('fx-reel-refill.json');
  });

  for (const file of jsons) {
    describe(file, () => {
      const data = JSON.parse(readFileSync(path.join(dir, file), 'utf8'));
      const frames = Object.keys(data.frames ?? {});
      const anim = data.animations?.default ?? [];
      const imagePath = path.join(dir, data.meta?.image ?? '');

      it('references a real image file', () => {
        expect(statSync(imagePath).isFile()).toBe(true);
      });

      it('has well-formed frames with anchors and durations', () => {
        expect(frames.length).toBeGreaterThan(0);
        for (const name of frames) {
          const frame = data.frames[name];
          expect(frame).toBeDefined();
          expect(frame.frame.x + frame.frame.w).toBeLessThanOrEqual(data.meta.size.w);
          expect(frame.frame.y + frame.frame.h).toBeLessThanOrEqual(data.meta.size.h);
          expect(frame.anchor).toEqual({ x: 0.5, y: 0.5 });
          expect(frame.duration).toBeGreaterThan(0);
        }
      });

      it('has a default animation referencing every frame once', () => {
        expect(anim.length).toBe(frames.length);
        expect(new Set(anim).size).toBe(frames.length);
        for (const name of anim) expect(frames).toContain(name);
      });

      it('has matching duration metadata', () => {
        expect(data.durations?.default?.length ?? 0).toBe(frames.length);
      });

      it('sheet is compact (< 1 MB)', () => {
        expect(statSync(imagePath).size).toBeLessThan(1_000_000);
      });
    });
  }
});