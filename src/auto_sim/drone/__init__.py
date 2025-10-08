from pathlib import Path
from collections.abc import Sequence, Mapping
from typing import Any
from dataclasses import dataclass

import yaml

from isaacsim.core.api.robots import Robot
from isaacsim.core.api.world import World
from isaacsim.core.utils import stage

@dataclass
class DroneConfig:
    prim_path: str = "/World/Drone"
    usd_file: Path = Path(__file__).parent / "drone.usda"
    prims_file: Path =  Path(__file__).parent / "prims.yaml"
    lights_file: Path =  Path(__file__).parent / "lights.yaml"
    vio_file: Path =  Path(__file__).parent / "vio_cams.yaml"
    xacti_file: Path =  Path(__file__).parent / "xacti.yaml"
    imus_file: Path =  Path(__file__).parent / "imus.yaml"
    lidar_file: Path =  Path(__file__).parent / "lidar.yaml"

# class or function?
class Drone:
    def _add_prims(self, prim_configs: Sequence[Mapping[str, Any]]) -> None:
        return [
                XFormPrim(
                    prim_paths_expr=self.prim_path + prim["Parent"] + prim["Name"],
                    name=prim["Name"],
                    translations=prim["Translation"],
                    orientations=prim["Rotation"],
                )
            for prim in prim_configs]

    def __init__(self, world: World, drone_config:DroneConfig = DroneConfig()) -> None:
        self.prim_path = drone_config.prim_path
        stage.add_reference_to_stage(str(drone_config.usd_file), self.prim_path)

        prims_cfg = yaml.safe_load(drone_config.prims_file.read_text())
        if not isinstance(prims_cfg, list):
            raise RuntimeError(f"When reading {str(drone_config.prims_file)}, expected the prims config to be a list got {type(prims_cfg)}")
        self.prims = self._add_prims(prims_cfg)

        # Is this really required?
        world.scene.add(Robot(prim_path=self.prim_path, name="drone", position=[0,0,1]))

