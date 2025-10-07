from pathlib import Path

import yaml
from isaacsim.core.api.world import World

from auto_sim import config

DEFAULT_WORLD_CONFIG_PATH = config.path / "world.yaml"


def setup_world(config_path: Path = DEFAULT_WORLD_CONFIG_PATH) -> World:
    cfg = yaml.safe_load(config_path.read_text())

    if not isinstance(cfg, dict):
        raise RuntimeError("Unexpected format when parsing config file")

    return World(
        1 / cfg["physics_fps"], 1 / cfg["rendering_fps"], cfg["stage_units_in_meters"]
    )
