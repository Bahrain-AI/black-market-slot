import { Container, Graphics, Sprite, Text, Texture } from 'pixi.js';
import type { SymbolData } from '../events/types';

export class SymbolRenderer extends Container {
  private readonly frame = new Graphics();
  private readonly sprite: Sprite;
  private readonly caption: Text;
  private currentName = '';
  readonly reel: number;
  readonly row: number;

  constructor(symbol: SymbolData, texture: Texture, reel: number, row: number) {
    super();
    this.reel = reel;
    this.row = row;
    this.frame.roundRect(3, 3, 154, 134, 8).fill({ color: 0x100d0a, alpha: 0.92 }).stroke({ color: 0xb89555, width: 2 });
    this.sprite = new Sprite(texture);
    this.sprite.anchor.set(0.5);
    this.sprite.position.set(80, 68);
    this.sprite.width = 142;
    this.sprite.height = 122;
    this.caption = new Text({ text: '', style: { fill: 0xf4d58d, fontSize: 16, fontWeight: '700', stroke: { color: 0x120c06, width: 4 } } });
    this.caption.anchor.set(0.5);
    this.caption.position.set(80, 112);
    this.addChild(this.frame, this.sprite, this.caption);
    this.update(symbol, texture);
  }

  get name(): string {
    return this.currentName;
  }

  update(symbol: SymbolData, texture: Texture) {
    this.currentName = symbol.name;
    this.sprite.texture = texture;
    this.caption.text = symbol.value ? `${symbol.value}×${symbol.multiplier ?? 1}` : (symbol.name === 'empty' ? '' : symbol.name.toUpperCase());
    this.alpha = symbol.name === 'empty' ? 0 : 1;
  }

  highlight(active: boolean, color = 0xffd36a) {
    this.frame.tint = active ? color : 0xffffff;
  }
}
