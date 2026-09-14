import type { GameEvent } from '../events/types';
import { initialGameState, reduceGameEvent, type GameState } from '../state/gameState';
import type { GameRenderer } from '../pixi/GameRenderer';

export class EventPlayer {
  private state = initialGameState();

  constructor(
    private readonly renderer: GameRenderer,
    private readonly onState: (state: GameState, event: GameEvent) => void,
    private readonly delay: () => number
  ) {}

  get snapshot() { return this.state; }

  async play(events: GameEvent[]) {
    this.state = initialGameState(this.state.board);
    for (const event of events) {
      this.state = reduceGameEvent(this.state, event);
      this.onState(this.state, event);
      await this.renderer.play(event, this.state, this.delay());
    }
    return this.state;
  }
}
