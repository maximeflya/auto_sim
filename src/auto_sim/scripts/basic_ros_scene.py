import argparse

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
    simulation_app = SimulationApp(
        {"headless": getattr(args, "headless")},
        str(config.path / "apps/isaacsim.exp.no_deprecated.python.kit"),
    )

    while simulation_app.is_running():
        simulation_app.update()

    simulation_app.close()

if __name__ == "__main__":
    main()
