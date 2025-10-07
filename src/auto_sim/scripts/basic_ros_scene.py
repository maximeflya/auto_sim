import argparse
import shutil
from pathlib import Path

from isaacsim.simulation_app import SimulationApp

from auto_sim import config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Spawn an isaac sim instance with a basic scene and basic sensor set"
    )
    parser.add_argument("--headless", action="store_true")
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
    from auto_sim.environment import setup_world

    setup_world()

    while simulation_app.is_running():
        simulation_app.update()

    simulation_app.close()


if __name__ == "__main__":
    main()
