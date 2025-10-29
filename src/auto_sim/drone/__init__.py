from dataclasses import dataclass
from pathlib import Path

import yaml
from isaacsim.core.api.robots import Robot
from isaacsim.core.api.world import World
from isaacsim.core.utils import stage
from isaacsim.replicator.behavior.utils.behavior_utils import add_behavior_script


from auto_sim.drone.components import add_camera_sensor, add_imu, add_lidar, add_lights
from auto_sim.drone import behavior

@dataclass
class DroneConfig:
    has_lights: bool = True
    has_vio_cameras: bool = True
    has_xacti: bool = True
    has_lidar: bool = True

    prim_path: str = "/World/Drone"
    usd_file: Path = Path(__file__).parent / "config/drone.usda"
    lights_file: Path = Path(__file__).parent / "config/lights.yaml"
    vio_file: Path = Path(__file__).parent / "config/vio_cams.yaml"
    xacti_file: Path = Path(__file__).parent / "config/xacti.yaml"
    imus_file: Path = Path(__file__).parent / "config/imus.yaml"
    lidar_file: Path = Path(__file__).parent / "config/lidar.yaml"


# class or function?
class Drone:
    def __init__(self, world: World, drone_config: DroneConfig = DroneConfig()) -> None:
        self.prim_path = drone_config.prim_path
        prim = stage.add_reference_to_stage(str(drone_config.usd_file), self.prim_path)


        imu_cfg = yaml.safe_load(drone_config.imus_file.read_text())
        if not isinstance(imu_cfg, list):
            raise RuntimeError(
                f"When reading {str(drone_config.imus_file)}, expected the imu config to be a list got {type(imu_cfg)}"
            )
        add_imu(self.prim_path, imu_cfg)

        if drone_config.has_lights:
            light_cfg = yaml.safe_load(drone_config.lights_file.read_text())
            if not isinstance(light_cfg, list):
                raise RuntimeError(
                    f"When reading {str(drone_config.lights_file)}, expected the light config to be a list got {type(light_cfg)}"
                )

            add_lights(self.prim_path, light_cfg)

        if drone_config.has_vio_cameras:
            vio_cfg = yaml.safe_load(drone_config.vio_file.read_text())
            if not isinstance(vio_cfg, list):
                raise RuntimeError(
                    f"When reading {str(drone_config.vio_file)}, expected the vio config to be a list got {type(vio_cfg)}"
                )

            add_camera_sensor(self.prim_path, vio_cfg)

        if drone_config.has_lidar:
            lidar_cfg = yaml.safe_load(drone_config.lidar_file.read_text())
            if not isinstance(lidar_cfg, dict):
                raise RuntimeError(
                    f"When reading {str(drone_config.lidar_file)}, expected the lidar config to be a list got {type(lidar_cfg)}"
                )

            add_lidar(self.prim_path, lidar_cfg)

        add_behavior_script(prim, behavior.__file__)

        # Still don't know if this is required
        world.scene.add(Robot(prim_path=self.prim_path, name="drone", position=[0, 0, 1]))
        # TODO: add xacti