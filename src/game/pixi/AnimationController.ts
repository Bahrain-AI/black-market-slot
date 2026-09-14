/**
 * GSAP-powered animation controller for BLACK MARKET.
 *
 * Every public method returns a Promise<void> so GameRenderer.play() can
 * await it in the same way it previously awaited plain sleep() calls.
 * All timing is in ms for consistency with the event player; GSAP expects
 * seconds internally, so values are converted at the tween boundary.
 *
 * No external PixiPlugin is required — we tween container.scale.x/y,
 * alpha, and position.x/y directly (ObservablePoint properties).
 */
import gsap from 'gsap';
import { Container, Text } from 'pixi.js';
import type { Position } from '../events/types';
import { ReelRenderer } from './ReelRenderer';
import { SymbolRenderer } from './SymbolRenderer';

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

export class AnimationController {
  constructor(private readonly reels: ReelRenderer) {}

  /* ------------------------------------------------------------------ */
  /*  Board lifecycle                                                     */
  /* ------------------------------------------------------------------ */

  /** Stagger-reveal a fresh board (alpha + scale pop). */
  async reveal(duration = 400) {
    const cells = this.reels.allCells();
    kill(cells);
    cells.forEach((c) => { c.alpha = 0; c.scale.set(0.7); });
    await Promise.all(
      cells.map((c, i) =>
        tweenTo(c, { alpha: 1, ease: 'back.out(1.4)', delay: i * 0.018 }, duration)
      ),
    );
    // scale pop (parallel, does not block)
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

  /** Pulse winning positions (scale bounce + gold tint). */
  async win(positions: Position[], duration = 500) {
    const cells = positions.map((p) => this.reels.getCell(p.reel, p.row)).filter(Boolean) as SymbolRenderer[];
    if (!cells.length) return;
    kill(cells);
    cells.forEach((c) => c.highlight(true, 0xffd36a));
    await Promise.all(cells.map((c) => tweenTo(c.scale, { x: 1.18, y: 1.18, ease: 'power2.out', yoyo: true, repeat: 1 }, duration)));
    cells.forEach((c) => c.highlight(false));
  }

  /** Flash red on positions then fade them out. */
  async remove(positions: Position[], duration = 500) {
    const cells = positions.map((p) => this.reels.getCell(p.reel, p.row)).filter(Boolean) as SymbolRenderer[];
    if (!cells.length) return;
    kill(cells);
    cells.forEach((c) => c.highlight(true, 0xd85835));
    await tweenTo(cells, { alpha: 0, ease: 'power2.in' }, duration * 0.5);
    cells.forEach((c) => { c.highlight(false); c.alpha = 0; });
  }

  /* ------------------------------------------------------------------ */
  /*  Wild expansion                                                      */
  /* ------------------------------------------------------------------ */

  /** Wild card at the given reel expands (scale pop + golden tint + settle). */
  async expandWild(reel: number, duration = 600) {
    const wildCell = this.reels.allCells().find((c) => c.reel === reel && c.name === 'W');
    if (!wildCell) return;
    kill([wildCell]);
    wildCell.highlight(true, 0xffd36a);
    // scale up then settle
    await tweenTo(wildCell.scale, { x: 1.35, y: 1.35, ease: 'elastic.out(1, 0.4)' }, duration * 0.5);
    await tweenTo(wildCell.scale, { x: 1, y: 1, ease: 'power2.out' }, duration * 0.5);
    wildCell.highlight(false);
  }

  /* ------------------------------------------------------------------ */
  /*  Free spins                                                          */
  /* ------------------------------------------------------------------ */

  /** Scatter symbols glow (pulse scale on S symbols). */
  async freeSpinsStart(duration = 600) {
    const scatters = this.reels.allCells().filter((c) => c.name === 'S');
    if (scatters.length) {
      kill(scatters);
      scatters.forEach((c) => c.highlight(true, 0xc9b037));
      await Promise.all(scatters.map((c) => tweenTo(c.scale, { x: 1.2, y: 1.2, ease: 'power2.inOut', yoyo: true, repeat: 2 }, duration)));
      scatters.forEach((c) => c.highlight(false));
    }
  }

  /** Brief counter pulse on a free-spin. */
  async freeSpin(duration = 300) {
    // no board change needed — just a brief delay for banner display
    await tweenTo({}, { onComplete() {} }, duration); // effectively a wait; GSAP handles frame sync
  }

  /** Multiplier badge pulse (all cells briefly flash). */
  async multiplierIncrease(duration = 400) {
    const cells = this.reels.allCells();
    kill(cells);
    cells.forEach((c) => c.highlight(true, 0x90ee90));
    await tweenTo(cells, { alpha: 0.5, yoyo: true, repeat: 1, ease: 'power2.inOut' }, duration * 0.4);
    cells.forEach((c) => c.highlight(false));
  }

  /* ------------------------------------------------------------------ */
  /*  Hold & Spin                                                         */
  /* ------------------------------------------------------------------ */

  /** Locked cells pop in (scale bounce). */
  async holdSpinStart(locked: Record<string, { reel: number; row: number; value: number }>, duration = 500) {
    const cells = Object.values(locked)
      .map((item) => this.reels.getCell(item.reel, item.row))
      .filter(Boolean) as SymbolRenderer[];
    if (!cells.length) return;
    kill(cells);
    cells.forEach((c) => { c.scale.set(0); c.highlight(true, 0xd85835); });
    await Promise.all(
      cells.map((c, i) => tweenTo(c.scale, { x: 1, y: 1, ease: 'elastic.out(1, 0.5)', delay: i * 0.08 }, duration)),
    );
  }

  /** New lock lands during respins (single pop). */
  async holdLock(positions: Position[], duration = 350) {
    const cells = positions.map((p) => this.reels.getCell(p.reel, p.row)).filter(Boolean) as SymbolRenderer[];
    if (!cells.length) return;
    kill(cells);
    cells.forEach((c) => { c.scale.set(0); c.highlight(true, 0xd85835); });
    await Promise.all(cells.map((c) => tweenTo(c.scale, { x: 1, y: 1, ease: 'elastic.out(1, 0.5)' }, duration)));
  }

  /* ------------------------------------------------------------------ */
  /*  Banner (replaces GameRenderer.flash)                                */
  /* ------------------------------------------------------------------ */

  /** Animated banner: scale-in → hold → fade-out. */
  async showBanner(banner: Text, text: string, durationMs: number) {
    banner.text = text;
    banner.alpha = 0;
    banner.scale.set(0.5);
    banner.visible = true;
    kill([banner]);
    await tweenTo(banner.scale, { x: 1, y: 1, ease: 'back.out(2)' }, 180);
    await tweenTo(banner, { alpha: 1, ease: 'power2.out' }, 120);
    await wait(Math.max(durationMs, 200));
    await tweenTo(banner, { alpha: 0, ease: 'power2.in' }, 180);
    banner.visible = false;
  }
}

function wait(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}
