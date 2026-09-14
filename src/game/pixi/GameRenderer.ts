import { Application, Assets, Container, Text, Texture } from 'pixi.js';
import type { GameEvent } from '../events/types';
import type { GameState } from '../state/gameState';
import { ReelRenderer, REEL_HEIGHT, REEL_WIDTH } from './ReelRenderer';

const SYMBOLS = ['watch', 'diamond', 'ace', 'gold', 'cash', 'passport', 'bag', 'bust', 'wild', 'vip'];
const sleep = (milliseconds: number) => new Promise((resolve) => setTimeout(resolve, milliseconds));

export class GameRenderer {
  private readonly app = new Application();
  private reels!: ReelRenderer;
  private readonly root = new Container();
  private readonly banner = new Text({ text: '', style: { fill: 0xffdf93, fontSize: 30, fontWeight: '700', align: 'center', stroke: { color: 0x120c06, width: 6 } } });

  async mount(host: HTMLElement) {
    await this.app.init({ resizeTo: host, backgroundAlpha: 0, antialias: true, autoDensity: true, resolution: Math.min(devicePixelRatio, 2) });
    host.appendChild(this.app.canvas);
    const textures: Record<string, Texture> = {};
    await Promise.all(SYMBOLS.map(async (name) => {
      const url = new URL(`./symbols/${name}.svg`, document.baseURI).href;
      textures[name] = await Assets.load<Texture>(url);
    }));
    this.reels = new ReelRenderer(textures);
    this.banner.anchor.set(0.5);
    this.banner.position.set(REEL_WIDTH / 2, REEL_HEIGHT / 2);
    this.banner.visible = false;
    this.root.addChild(this.reels, this.banner);
    this.app.stage.addChild(this.root);
    this.app.ticker.add(() => this.layout());
    this.layout();
  }

  async play(event: GameEvent, state: GameState, duration: number) {
    if (event.type === 'reveal' || event.type === 'collapse' || event.type === 'refill') this.reels.setBoard(state.board);
    if (event.type === 'win') this.reels.mark(event.positions, true);
    if (event.type === 'removeSymbols') { this.reels.mark(event.positions, true, 0xd85835); await sleep(duration); this.reels.setBoard(state.board); }
    if (event.type === 'expandingWild') { this.reels.setBoard(state.board); await this.flash(`WILD EXPANDS · REEL ${event.reel + 1}`, duration); }
    if (event.type === 'multiplierIncrease') await this.flash(`MULTIPLIER ${event.to}×`, duration);
    if (event.type === 'freeSpinsStart') await this.flash(`${event.total} FREE SPINS`, duration);
    if (event.type === 'holdSpinStart' || event.type === 'holdSpinLock' || event.type === 'holdSpinRespins') this.reels.showLocks(state.holdSpin.locked);
    if (event.type === 'holdSpinStart') await this.flash('HOLD & SPIN', duration);
    if (event.type === 'holdSpinEnd') await this.flash(`HOLD WIN ${event.total}×`, duration);
    if (!['removeSymbols', 'expandingWild', 'multiplierIncrease', 'freeSpinsStart', 'holdSpinStart', 'holdSpinEnd'].includes(event.type)) await sleep(duration);
  }

  destroy() { this.app.destroy(true, { children: true, texture: false, textureSource: false }); }

  private async flash(text: string, duration: number) {
    this.banner.text = text;
    this.banner.visible = true;
    await sleep(Math.max(duration, 120));
    this.banner.visible = false;
  }

  private layout() {
    if (!this.app.renderer) return;
    const scale = Math.min(this.app.renderer.width / REEL_WIDTH, this.app.renderer.height / REEL_HEIGHT);
    this.root.scale.set(scale);
    this.root.position.set((this.app.renderer.width - REEL_WIDTH * scale) / 2, (this.app.renderer.height - REEL_HEIGHT * scale) / 2);
  }
}
