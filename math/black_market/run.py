from .game_config import GameConfig


def validate_phase_one() -> GameConfig:
    config = GameConfig()
    config.validate()
    return config


if __name__ == "__main__":
    config = validate_phase_one()
    print(f"{config.game_id}: Phase 1 math interface valid; TARGET_RTP={config.target_rtp:.2f} is provisional")
    print("No production books generated. Integrate approved simulations, optimize weights, then call output hooks.")
