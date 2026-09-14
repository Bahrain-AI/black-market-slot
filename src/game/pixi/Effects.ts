/**
 * Vector FX effects for BLACK MARKET (PixiJS v8 + GSAP).
 *
 * All effects are fire-and-forget: they spawn into the host container,
 * tween with GSAP, then destroy themselves. Coordinates are in
 * ReelRenderer space (800x560).
 */
import { Container, Graphics, Text } from 'pixi.js';
import gsap from 'gsap';

export const GOLD = 0xffd36a;
export const RED = 0xd85835;
export const GOLD_DIM = 0xb89555;

const sec = (ms: number) => ms / 1000;
const rad = (deg: number) => (deg * Math.PI) / 180;

export class Effects {
  constructor(private readonly host: Container) {}

  /** Expanding golden ring at a point in host space. */
  ring(x: number, y: number, color = GOLD, maxRadius = 110, durationMs = 420, width = 5) {
    const g = new Graphics();
    g.circle(0, 0, maxRadius).stroke({ color, width, alpha: 0.9 });
    g.position.set(x, y);
    g.scale.set(0.2);
    this.host.addChild(g);
    gsap.to(g.scale, { x: 1.7, y: 1.7, duration: sec(durationMs), ease: 'power2.out' });
    gsap.to(g, {
      alpha: 0,
      duration: sec(durationMs),
      ease: 'power2.in',
      onComplete: () => this.dispose(g),
    });
  }

  /** Rotating sunburst of spikes, ideal for wild expansions. */
  rays(x: number, y: number, color = GOLD, durationMs = 700, count = 16) {
    const g = new Graphics();
    const r1 = 96;
    const r2 = 172;
    const w = rad(12);
    for (let i = 0; i < count; i++) {
      const a = (i / count) * Math.PI * 2;
      g.moveTo(Math.cos(a - w) * r1, Math.sin(a - w) * r1)
        .lineTo(Math.cos(a) * r2, Math.sin(a) * r2)
        .lineTo(Math.cos(a + w) * r1, Math.sin(a + w) * r1)
        .closePath();
    }
    g.fill({ color, alpha: 0.85 });
    g.position.set(x, y);
    this.host.addChild(g);
    gsap.to(g, {
      rotation: 0.6,
      alpha: 0,
      duration: sec(durationMs),
      ease: 'power2.out',
      onComplete: () => this.dispose(g),
    });
  }

  /** Fracture shards flying outward (symbol removal / cascade). */
  shards(x: number, y: number, count = 6, color = RED, durationMs = 470) {
    for (let i = 0; i < count; i++) {
      const g = new Graphics();
      const size = 7 + Math.random() * 9;
      g.poly([0, -size, size * 0.7, size * 0.6, -size * 0.7, size * 0.6]).fill({ color, alpha: 0.9 });
      g.position.set(x, y);
      g.rotation = Math.random() * Math.PI * 2;
      this.host.addChild(g);
      const angle = Math.random() * Math.PI * 2;
      const dist = 26 + Math.random() * 52;
      gsap.to(g.position, {
        x: x + Math.cos(angle) * dist,
        y: y + Math.sin(angle) * dist,
        duration: sec(durationMs),
        ease: 'power2.out',
      });
      gsap.to(g, {
        alpha: 0,
        rotation: g.rotation + (Math.random() - 0.5) * 2.4,
        duration: sec(durationMs),
        ease: 'power2.in',
        onComplete: () => this.dispose(g),
      });
    }
  }

  /** Falling gold confetti (hold-and-spin win / payout celebration). */
  confetti(durationMs = 1500, count = 26) {
    const palette = [GOLD, 0xf4d58d, RED, GOLD_DIM, 0x90ee90];
    for (let i = 0; i < count; i++) {
      const g = new Graphics();
      g.rect(-4, -7, 8, 14).fill({ color: palette[i % palette.length], alpha: 0.95 });
      const x = Math.random() * 800;
      g.position.set(x, -20 - Math.random() * 40);
      g.rotation = Math.random() * Math.PI;
      this.host.addChild(g);
      const drift = (Math.random() - 0.5) * 90;
      gsap.to(g.position, {
        x: x + drift,
        y: 620 + Math.random() * 60,
        duration: sec(durationMs),
        ease: 'power1.in',
      });
      gsap.to(g, { rotation: g.rotation + (Math.random() * 6 - 3), duration: sec(durationMs), ease: 'none' });
      gsap.to(g, {
        alpha: 0.15,
        duration: sec(durationMs * 0.3),
        delay: sec(durationMs * 0.7),
        onComplete: () => this.dispose(g),
      });
    }
  }

  /** Value / multiplier badge that pops in, holds, then fades. */
  badge(x: number, y: number, label: string, color = GOLD, durationMs = 820): Promise<void> {
    const c = new Container();
    const g = new Graphics();
    g.roundRect(-72, -29, 144, 58, 12).fill({ color: 0x160f0a, alpha: 0.94 }).stroke({ color, width: 3 });
    const t = new Text({ text: label, style: { fill: color, fontSize: 34, fontWeight: '800', align: 'center' } });
    t.anchor.set(0.5);
    c.addChild(g, t);
    c.position.set(x, y);
    c.scale.set(0.3);
    c.alpha = 0;
    this.host.addChild(c);
    return new Promise((resolve) => {
      gsap.to(c, { alpha: 1, duration: 0.12 });
      gsap.to(c.scale, { x: 1, y: 1, duration: 0.26, ease: 'back.out(2)' });
      gsap.to(c, {
        alpha: 0,
        duration: 0.22,
        delay: sec(Math.max(durationMs - 280, 180)),
        ease: 'power2.in',
        onComplete: () => {
          this.dispose(c);
          resolve();
        },
      });
    });
  }

  /** Kill remaining tweens, detach and destroy an effect. */
  private dispose(target: Container) {
    gsap.killTweensOf(target);
    gsap.killTweensOf(target.scale);
    gsap.killTweensOf(target.position);
    if (target.parent === this.host) this.host.removeChild(target);
    target.destroy({ children: true });
  }
}