/**
 * GSAP-powered animation controller for BLACK MARKET.
 *
 * Every public method returns a Promise<void> so GameRenderer.play() can
 * await it in the same way it previously awaited plain sleep() calls.
 * All timing is in ms for consistency with the event player; GSAP expects
 * seconds internally, so values are converted at the tween boundary.
 *
 * Vector FX (rings, rays, shards, confetti, badges) live in Effects; optional
 * sprite-sheet overlays (AnimatedSprite) play through OverlayAtlas.
 */
import gsap from 'gsap';
import type { Position } from '../events/types';
import type { OverlayAtlas } from './animationSheets';
import { Effects } from './Effects';
import { ReelRenderer, REEL_WIDTH as REEL_W } from './ReelRenderer';
import type { SymbolRenderer } from './SymbolRenderer';

const sec = (ms: number) => ms / 1000;

/** Tween helper: resolves when the GSAP tween completes. */
function tweenTo(target: object, props: gsap.TweenVars, durationMs: number): Promise<void> {
  return new Promise((resolve) => {
    gsap.to(target, { ...props, duration: sec(durationMs), onComplete: resolve, overwrite: true });
  });
}

/** Kill every active tween on the given targets (prevents overlap conflicts). */
function kill(targets: object[]) {
  gsap.killTweensOf(targets);
}

const CELL_W = 160;
const CELL_H = 140;
const cellCenter = (reel: number, row: number) => ({ x: reel * CELL_W + 80, y: row * CELL_H + 70 });

export type LockedCell = { reel: number; row: number; value: number };

export class AnimationController {
  private readonly fx: Effects;

  constructor(
    private readonly reels: ReelRenderer,
    private readonly overlays?: OverlayAtlas,
  ) {
    this.fx = new Effects(reels);
  }

  /* ------------------------------------------------------------------ */
  /*  Board lifecycle                                                     */
  /* ------------------------------------------------------------------ */

  /** Stagger-reveal a fresh board (alpha + scale pop). */
  async reveal(duration = 400) {
    const cells = this.reels.allCells();
    kill(cells);
    cells.forEach((c) => {
      c.alpha = 0;
      c.scale.set(0.7);
    });
    await Promise.all(
      cells.map((c, i) => tweenTo(c, { alpha: 1, ease: 'back.out(1.4)', delay: i * 0.018 }, duration)),
    );
    cells.forEach((c, i) => {
      gsap.to(c.scale, { x: 1, y: 1, ease: 'back.out(2)', duration: sec(duration), delay: i * 0.018 });
    });
  }

  /** Stagger-reveal after collapse+refill. */
  async refill(duration = 350) {
    return this.reveal(duration);
  }

  /* ------------------------------------------------------------------ */
  /*  Win / remove                                                        */
  /* ------------------------------------------------------------------ */

  /** Pulse winning positions (scale bounce + gold tint + rings). */
  async win(positions: Position[], duration = 500) {
    const cells = this.cellsAt(positions);
    if (!cells.length) return;
    kill(cells);
    cells.forEach((c) => {
      c.highlight(true, 0xffd36a);
      const { x, y } = cellCenter(c.reel, c.row);
      this.fx.ring(x, y, 0xffd36a, 96, 340);
    });
    await Promise.all(
      cells.map((c) => tweenTo(c.scale, { x: 1.18, y: 1.18, ease: 'power2.out', yoyo: true, repeat: 1 }, duration)),
    );
    cells.forEach((c) => c.highlight(false));
  }

  /** Flash red, fracture into shards, then fade the positions out. */
  async remove(positions: Position[], duration = 500) {
    const cells = this.cellsAt(positions);
    if (!cells.length) return;
    kill(cells);
    cells.forEach((c) => {
      c.highlight(true, 0xd85835);
      const { x, y } = cellCenter(c.reel, c.row);
      this.fx.shards(x, y, 5, 0xd85835, 440);
    });
    await tweenTo(cells, { alpha: 0, ease: 'power2.in' }, duration * 0.5);
    cells.forEach((c) => {
      c.highlight(false);
      c.alpha = 0;
    });
  }

  /* ------------------------------------------------------------------ */
  /*  Wild expansion                                                      */
  /* ------------------------------------------------------------------ */

  /** Wild card at the given reel expands (rays + rings + overlay + pop). */
  async expandWild(reel: number, duration = 600) {
    const cell = this.reels.allCells().find((c) => c.reel === reel && c.name === 'W');
    const { x, y } = cell ? cellCenter(cell.reel, cell.row) : cellCenter(reel, 1.5);
    this.fx.rays(x, y);
    this.fx.ring(x, y, 0xffd36a, 130, 520);
    this.overlays?.play(x, y, 'symbol-wild-expand', 0.82, this.reels);
    if (cell) {
      kill([cell]);
      cell.highlight(true, 0xffd36a);
      await tweenTo(cell.scale, { x: 1.35, y: 1.35, ease: 'elastic.out(1, 0.4)' }, duration * 0.5);
      await tweenTo(cell.scale, { x: 1, y: 1, ease: 'power2.out' }, duration * 0.5);
      cell.highlight(false);
    }
  }

  /* ------------------------------------------------------------------ */
  /*  Free spins                                                          */
  /* ------------------------------------------------------------------ */

  /** Scatter symbols glow (pulse scale + rings + overlay). */
  async freeSpinsStart(duration = 600) {
    const scatters = this.reels.allCells().filter((c) => c.name === 'S');
    if (scatters.length) {
      kill(scatters);
      scatters.forEach((c) => {
        c.highlight(true, 0xc9b037);
        const { x, y } = cellCenter(c.reel, c.row);
        this.fx.ring(x, y, 0xc9b037, 104, 380);
        this.overlays?.play(x, y, 'symbol-scatter-freespins', 0.8, this.reels);
      });
      await Promise.all(
        scatters.map((c) => tweenTo(c.scale, { x: 1.2, y: 1.2, ease: 'power2.inOut', yoyo: true, repeat: 2 }, duration)),
      );
      scatters.forEach((c) => c.highlight(false));
    }
  }

  /** Multiplier increase: badge pop + brief board flash. */
  async multiplierIncrease(to: number, duration = 620) {
    const cells = this.reels.allCells();
    kill(cells);
    cells.forEach((c) => c.highlight(true, 0x90ee90));
    const badge = this.fx.badge(REEL_W / 2, 74, `${to}×`);
    await Promise.all([
      badge,
      tweenTo(cells, { alpha: 0.55, yoyo: true, repeat: 1, ease: 'power2.inOut' }, duration * 0.4),
    ]);
    cells.forEach((c) => c.highlight(false));
  }

  /* ------------------------------------------------------------------ */
  /*  Hold & Spin                                                         */
  /* ------------------------------------------------------------------ */

  /** Locked cells pop in (elastic scale + gold ring). */
  async holdSpinStart(locked: Record<string, LockedCell>, duration = 500) {
    const cells = this.lockedCells(locked);
    if (!cells.length) return;
    kill(cells);
    cells.forEach((c) => {
      c.scale.set(0);
      c.highlight(true, 0xd85835);
      const { x, y } = cellCenter(c.reel, c.row);
      this.fx.ring(x, y, 0xffd36a, 100, 400);
    });
    await Promise.all(
      cells.map((c, i) => tweenTo(c.scale, { x: 1, y: 1, ease: 'elastic.out(1, 0.5)', delay: i * 0.08 }, duration)),
    );
    cells.forEach((c) => c.highlight(false));
  }

  /** New lock lands during respins (single pop + ring). */
  async holdLock(positions: Position[], duration = 350) {
    const cells = this.cellsAt(positions);
    if (!cells.length) return;
    kill(cells);
    cells.forEach((c) => {
      c.scale.set(0);
      c.highlight(true, 0xd85835);
      const { x, y } = cellCenter(c.reel, c.row);
      this.fx.ring(x, y, 0xffd36a, 96, 340);
    });
    await Promise.all(cells.map((c) => tweenTo(c.scale, { x: 1, y: 1, ease: 'elastic.out(1, 0.5)' }, duration)));
    cells.forEach((c) => c.highlight(false));
  }

  /** Falling gold confetti — hold-and-spin / payout celebration. */
  confetti(duration = 1500) {
    this.fx.confetti(duration);
  }

  /* ------------------------------------------------------------------ */
  /*  Banner                                                              */
  /* ------------------------------------------------------------------ */

  /** Animated banner: scale-in → hold → fade-out. */
  async showBanner(banner: import('pixi.js').Text, text: string, durationMs: number) {
    banner.text = text;
    banner.alpha = 0;
    banner.scale.set(0.5);
    banner.visible = true;
    kill([banner]);
    await tweenTo(banner.scale, { x: 1, y: 1, ease: 'back.out(2)' }, 180);
    await tweenTo(banner, { alpha: 1, ease: 'power2.out' }, 120);
    await new Promise((r) => setTimeout(r, Math.max(durationMs, 200)));
    await tweenTo(banner, { alpha: 0, ease: 'power2.in' }, 180);
    banner.visible = false;
  }

  /* ------------------------------------------------------------------ */
  /*  Helpers                                                             */
  /* ------------------------------------------------------------------ */

  private cellsAt(positions: Position[]): SymbolRenderer[] {
    return positions
      .map((p) => this.reels.getCell(p.reel, p.row))
      .filter((c): c is SymbolRenderer => Boolean(c));
  }

  private lockedCells(locked: Record<string, LockedCell>): SymbolRenderer[] {
    return Object.values(locked)
      .map((item) => this.reels.getCell(item.reel, item.row))
      .filter((c): c is SymbolRenderer => Boolean(c));
  }
}