import argparse
import logging
import shutil
from pathlib import Path

from isaacsim.simulation_app import SimulationApp

from auto_sim import config
from auto_sim.environment import get_environment_list

logger = logging.getLogger(__name__)


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
    parser.add_argument("--no-ros", dest="ros", action="store_false")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Create a temporary file structure for isaac sim config
    tmp_isaac_sim_path = Path("/tmp/auto_sim")
    # if not tmp_isaac_sim_path.exists()
    shutil.copytree(config.path / "apps", tmp_isaac_sim_path / "apps", dirs_exist_ok=True)

    simulation_app = SimulationApp(
        {"headless": getattr(args, "headless")},
        str(tmp_isaac_sim_path / "apps/isaacsim.exp.no_deprecated.python.ros.kit"),
        # str(tmp_isaac_sim_path / "apps/isaacsim.exp.full.kit"),
        # "/home/autoserver/isaacsim/_build/linux-x86_64/release/apps/isaacsim.exp.full.kit"
    )

    # All imports that are related to isaac sim should happen after loading the app
    from auto_sim.drone import Drone
    from auto_sim.environment.load import load_environment, setup_world
    from isaacsim.core.utils.extensions import enable_extension
    from auto_sim.ros2.clock import load_clock_graph


    enable_extension("isaacsim.ros2.bridge")
    enable_extension("omni.graph.bundle.action")
    enable_extension("omni.graph.visualization.nodes")
    enable_extension("omni.graph.window.action")
    enable_extension("omni.graph.window.generic")
    enable_extension("isaacsim.code_editor.vscode")

    world = setup_world()
    load_environment(getattr(args, "env"))

    if args.ros:
        load_clock_graph()

    Drone(world)

    while simulation_app.is_running():
        world.step() # simulation_app.update() crashes
        # simulation_app.update()


    simulation_app.close()


if __name__ == "__main__":
    main()
