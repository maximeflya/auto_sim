import argparse
import shutil
from pathlib import Path

from isaacsim.simulation_app import SimulationApp

from auto_sim import config
from auto_sim.environment import get_environment_list

import logging
logger=logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Spawn an isaac sim instance with a basic scene and basic sensor set"
    )
    parser.add_argument("--headless", action="store_true")
    parser.add_argument(
        "--env",
        default="Warehouse",
        help=f"Environment name, possible names are: {get_environment_list()}",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Create a temporary file structure for isaac sim config
    tmp_isaac_sim_path = Path("/tmp/auto_sim")
    if not tmp_isaac_sim_path.exists():
        shutil.copytree(config.path / "apps", tmp_isaac_sim_path / "apps")

    simulation_app = SimulationApp(
        {"headless": getattr(args, "headless")},
        str(tmp_isaac_sim_path / "apps/isaacsim.exp.no_deprecated.python.kit"),
    )

    # All imports that are related to isaac sim should happen after loading the app
    from auto_sim.environment.load import setup_world, load_environment
    from auto_sim.drone import Drone

    world = setup_world()
    load_environment(getattr(args, "env"))
    Drone(world)

    while simulation_app.is_running():
        simulation_app.update()

    simulation_app.close()


if __name__ == "__main__":
    main()
