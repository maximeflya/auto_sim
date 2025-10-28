from pathlib import Path

import yaml
from isaacsim.core.api.world import World
from isaacsim.core.utils import stage
from isaacsim.core.utils.prims import define_prim
from isaacsim.storage import native

from auto_sim import config
from auto_sim.environment import (
    LOCAL_ENVIRONMENTS,
    NVIDIA_ENVIRONMENTS,
    OMNIVERSE_ENVIRONMENTS,
)

DEFAULT_WORLD_CONFIG_PATH = config.path / "world.yaml"


def get_environment_path(environment_name: str) -> str | Path:
    if environment_name in NVIDIA_ENVIRONMENTS:
        assets_root_path = native.get_assets_root_path()
        if assets_root_path is None:
            raise OSError("Could not find Isaac Sim assets folder")

        environment_path = (
            assets_root_path
            + "/Isaac/Environments/"
            + NVIDIA_ENVIRONMENTS[environment_name]
        )

    elif environment_name in OMNIVERSE_ENVIRONMENTS:
        environment_path = OMNIVERSE_ENVIRONMENTS[environment_name]

    elif environment_name in LOCAL_ENVIRONMENTS:
        dir_path = Path(__file__).parents[1]

        environment_path = (
            dir_path / "assets" / "environments" / LOCAL_ENVIRONMENTS[environment_name]
        )

        if not environment_path.exists():
            raise OSError(
                f"The environment path does not exist. Make sure you have downloaded "
                f"the environment file and placed it in the correct location: "
                f"{environment_path}"
            )

    else:
        raise ValueError("The environment name is not valid: " + environment_name)

    return environment_path


def setup_world(config_path: Path = DEFAULT_WORLD_CONFIG_PATH) -> World:
    cfg = yaml.safe_load(config_path.read_text())

    if not isinstance(cfg, dict):
        raise RuntimeError("Unexpected format when parsing config file")

    return World(
        physics_dt=1 / cfg["physics_fps"],
        rendering_dt=1 / cfg["rendering_fps"],
        stage_units_in_meters=cfg["stage_units_in_meters"],
    )


def load_environment(env_name: str) -> None:
    environment_path = get_environment_path(env_name)
    define_prim("/World")
    env_prim = define_prim("/World/Environment")
    stage.add_reference_to_stage(str(environment_path), prim_path=env_prim.GetPath())
