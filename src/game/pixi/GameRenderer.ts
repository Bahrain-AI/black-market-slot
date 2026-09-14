import { Application, Assets, Container, Text, Texture } from 'pixi.js';
import gsap from 'gsap';
import type { GameEvent } from '../events/types';
import type { GameState } from '../state/gameState';
import { AnimationController } from './AnimationController';
import { ReelRenderer, REEL_HEIGHT, REEL_WIDTH } from './ReelRenderer';

const SYMBOLS = ['watch', 'diamond', 'ace', 'gold', 'cash', 'passport', 'bag', 'bust', 'wild', 'vip'];
const wait = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

export class GameRenderer {
  private readonly app = new Application();
  private reels!: ReelRenderer;
  private anim!: AnimationController;
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
    this.anim = new AnimationController(this.reels);
    this.banner.anchor.set(0.5);
    this.banner.position.set(REEL_WIDTH / 2, REEL_HEIGHT / 2);
    this.banner.visible = false;
    this.root.addChild(this.reels, this.banner);
    this.app.stage.addChild(this.root);
    this.app.ticker.add(() => this.layout());
    this.layout();
  }

  async play(event: GameEvent, state: GameState, duration: number) {
    const anim = this.anim;

    switch (event.type) {
      case 'reveal':
        this.reels.setBoard(state.board);
        await anim.reveal(duration);
        break;
      case 'collapse':
        this.reels.setBoard(state.board);
        break;
      case 'refill':
        this.reels.setBoard(state.board);
        await anim.refill(duration);
        break;
      case 'win':
        this.reels.mark(event.positions, true);
        await anim.win(event.positions, duration);
        break;
      case 'removeSymbols':
        this.reels.mark(event.positions, true, 0xd85835);
        await anim.remove(event.positions, duration);
        this.reels.setBoard(state.board);
        break;
      case 'expandingWild':
        this.reels.setBoard(state.board);
        await anim.expandWild(event.reel, duration);
        await anim.showBanner(this.banner, `WILD EXPANDS · REEL ${event.reel + 1}`, duration);
        break;
      case 'multiplierIncrease':
        await anim.multiplierIncrease(duration);
        await anim.showBanner(this.banner, `MULTIPLIER ${event.to}×`, duration);
        break;
      case 'freeSpinsStart':
        await anim.freeSpinsStart(duration);
        await anim.showBanner(this.banner, `${event.total} FREE SPINS`, duration);
        break;
      case 'holdSpinStart':
        this.reels.showLocks(state.holdSpin.locked);
        await anim.holdSpinStart(state.holdSpin.locked, duration);
        await anim.showBanner(this.banner, 'HOLD & SPIN', duration);
        break;
      case 'holdSpinLock':
        this.reels.showLocks(state.holdSpin.locked);
        await anim.holdLock(event.locks.map((l) => ({ reel: l.reel, row: l.row })), duration);
        break;
      case 'holdSpinRespins':
        this.reels.showLocks(state.holdSpin.locked);
        break;
      case 'holdSpinEnd':
        await anim.showBanner(this.banner, `HOLD WIN ${event.total}×`, duration);
        break;
      case 'payout':
        await anim.showBanner(this.banner, `WIN ${event.total}×`, duration);
        break;
      case 'roundEnd':
        break;
      default:
        await wait(duration);
    }
  }

  destroy() {
    gsap.killTweensOf('*');
    this.app.destroy(true, { children: true, texture: false, textureSource: false });
  }

  private layout() {
    if (!this.app.renderer) return;
    const scale = Math.min(this.app.renderer.width / REEL_WIDTH, this.app.renderer.height / REEL_HEIGHT);
    this.root.scale.set(scale);
    this.root.position.set((this.app.renderer.width - REEL_WIDTH * scale) / 2, (this.app.renderer.height - REEL_HEIGHT * scale) / 2);
  }
}
