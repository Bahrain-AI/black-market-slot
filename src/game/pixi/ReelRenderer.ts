import { Container, Texture } from 'pixi.js';
import type { Board, Position } from '../events/types';
import type { LockedSymbol } from '../state/gameState';
import { SymbolRenderer } from './SymbolRenderer';

export const REEL_WIDTH = 800;
export const REEL_HEIGHT = 560;

export class ReelRenderer extends Container {
  private symbols: SymbolRenderer[][] = [];

  constructor(private readonly textures: Record<string, Texture>) { super(); }

  setBoard(board: Board) {
    this.removeChildren();
    this.symbols = board.map((reel, reelIndex) => reel.map((symbol, rowIndex) => {
      const view = new SymbolRenderer(symbol, this.texture(symbol.name), reelIndex, rowIndex);
      view.position.set(reelIndex * 160, rowIndex * 140);
      this.addChild(view);
      return view;
    }));
  }

  mark(positions: Position[], active = true, color?: number) {
    positions.forEach(({ reel, row }) => this.symbols[reel]?.[row]?.highlight(active, color));
  }

  showLocks(locked: Record<string, LockedSymbol>) {
    Object.values(locked).forEach((item) => {
      const view = this.symbols[item.reel]?.[item.row];
      if (view) { view.update({ name: 'cash', value: item.value, multiplier: item.multiplier, locked: true }, this.texture('cash')); view.highlight(true, 0xd85835); }
    });
  }

  private texture(name: string) { return this.textures[name] ?? this.textures.cash ?? Texture.WHITE; }
}
