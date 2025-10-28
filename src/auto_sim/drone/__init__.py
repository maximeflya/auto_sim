from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Tuple
import numpy.typing as npt

import isaacsim.core.utils.prims as prim_utils
import yaml
from isaacsim.core.api.robots import Robot
from isaacsim.core.api.world import World
from isaacsim.core.prims import RigidPrim
from isaacsim.core.utils import stage
from isaacsim.sensors.rtx import LidarRtx
from isaacsim.sensors.physics import IMUSensor
import omni
from pxr import Gf
import numpy as np
from scipy.spatial.transform.rotation import Rotation

from auto_sim.drone.camera import Camera
from auto_sim.drone.controllers import Controller
from auto_sim.drone.physics.vehicle_physics import Elios3Physics
from auto_sim.drone.controllers.velocity_controller import VelocityController, VelRef
from auto_sim.drone.controllers.trajectory_controller import TrajectoryController, TrajRef
from auto_sim.drone.controllers.acceleration_controller import AccelerationController, AccRef
from auto_sim.drone.state import State

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
        stage.add_reference_to_stage(str(drone_config.usd_file), self.prim_path)
        self.prim = RigidPrim(self.prim_path, reset_xform_properties=False)


        imu_cfg = yaml.safe_load(drone_config.imus_file.read_text())
        if not isinstance(imu_cfg, list):
            raise RuntimeError(
                f"When reading {str(drone_config.imus_file)}, expected the imu config to be a list got {type(imu_cfg)}"
            )
        self._add_imu(imu_cfg)

        if drone_config.has_lights:
            light_cfg = yaml.safe_load(drone_config.lights_file.read_text())
            if not isinstance(light_cfg, list):
                raise RuntimeError(
                    f"When reading {str(drone_config.lights_file)}, expected the light config to be a list got {type(light_cfg)}"
                )

            self._add_lights(light_cfg)

        if drone_config.has_vio_cameras:
            vio_cfg = yaml.safe_load(drone_config.vio_file.read_text())
            if not isinstance(vio_cfg, list):
                raise RuntimeError(
                    f"When reading {str(drone_config.vio_file)}, expected the vio config to be a list got {type(vio_cfg)}"
                )

            self._add_camera_sensor(vio_cfg)

        if drone_config.has_lidar:
            lidar_cfg = yaml.safe_load(drone_config.lidar_file.read_text())
            if not isinstance(lidar_cfg, dict):
                raise RuntimeError(
                    f"When reading {str(drone_config.lidar_file)}, expected the lidar config to be a list got {type(lidar_cfg)}"
                )

            self._add_lidar(lidar_cfg)


        # TODO: add xacti

        self.vehicle_physics = Elios3Physics()
        self.controllers : list[Controller] = [
            VelocityController(VelRef(), self.vehicle_physics),
            # TrajectoryController(TrajRef(), self.vehicle_physics),
            # AccelerationController(AccRef(), self.vehicle_physics)
        ]


        # self._cog_prim = RigidPrim(self.prim_path + "/body/mass", reset_xform_properties=False)
        self._cog_prim = self.prim
        # self._cog_prim.initialize()
        # print(self._cog_prim.get_coms())
        self._cog_state = State()

        world.scene.add(Robot(prim_path=self.prim_path, name="drone", position=[0, 0, 1]))
        world.add_physics_callback("drone_physics_cb", self.on_physics_step)

    def on_physics_step(self, dt: float) -> None:
        self._update_state()
        mass = self.prim.get_masses()

        print(mass)

        for c in self.controllers:
            c.update_state(self._cog_state)

        moments, forces = self._get_moments_and_forces_from_controllers()

        # print(forces, moments)

        self.prim.apply_forces_and_torques_at_pos(forces, moments)

    def _update_state(self) -> None:
        """
        Method to get the kinematic state of a part of the vehicle.  Note: Linear
        acceleration cannot be retrieved from the physics engine, but can be computed by
        the user with
              knowledge of the previous state.

        Args:
            body_part (str): The name of the body part of the vehicle that we want to get
            the state from.
        """
        # Get the current position and orientation in the inertial frame
        position, orientation = self._cog_prim.get_world_poses()

        # Get the angular velocity of the vehicle expressed in the body frame of reference
        ang_vel = self._cog_prim.get_angular_velocities()[0]

        # The linear velocity [x_dot, y_dot, z_dot] of the vehicle's body frame expressed
        # in the inertial frame of reference
        linear_vel = self._cog_prim.get_linear_velocities()[0]

        # Update the state variable X = [x,y,z]
        self._cog_state.position = np.array(position[0])

        # Get the quaternion according in the [qx,qy,qz,qw] standard
        self._cog_state.attitude = np.array(orientation[0])

        # Express the velocity of the vehicle in the inertial frame X_dot = [x_dot, y_dot,
        # z_dot]
        self._cog_state.linear_velocity = np.array(linear_vel)
        self._cog_state.angular_inertial_velocity = np.array(ang_vel)

        # The linear velocity V =[u,v,w] of the vehicle's body frame expressed in the body
        # frame of reference Note that: x_dot = Rot * V
        self._cog_state.linear_body_velocity = (
            Rotation.from_quat(self._cog_state.attitude).inv().apply(self._cog_state.linear_velocity)
        )

        # omega = [p,q,r]
        self._cog_state.angular_velocity = (
            Rotation.from_quat(self._cog_state.attitude).inv().apply(np.array(ang_vel))
        )

    def _get_moments_and_forces_from_controllers(
        self,
    ) -> Tuple[npt.NDArray[np.float32], npt.NDArray[np.float32]]:

        for controller in self.controllers:
            if controller.is_valid():
                return controller.get_moments_and_forces()

        return np.zeros((3,), dtype=np.float32), np.zeros((3,), dtype=np.float32)

    def _add_lights(self, cfg: Sequence[Mapping[str, Any]]) -> None:
        for light in cfg:
            for parent in light["Parents"]:
                prim_utils.create_prim(
                    self.prim_path + parent + light["Name"],
                    "RectLight",
                    translation=light["Translation"],
                    orientation=light["Rotation"],
                    attributes={
                        "inputs:intensity": light["Intensity"],
                        "inputs:height": light["Height"],
                        "inputs:width": light["Width"],
                    },
                )

    def _add_imu(self, imu_cfg: Sequence[Mapping[str, Any]]) -> None:
        for imu in imu_cfg:
            IMUSensor(
                prim_path= f"{self.prim_path}{imu['Parent']}/{imu['Topic']}",
                name=imu['Topic'],
                frequency=imu["UpdateRate"],
                translation=np.array([0, 0, 0]),
                orientation=np.array([1, 0, 0, 0]),
            )

    def _add_camera_sensor(self, cam_cfg: Sequence[Mapping[str, Any]]) -> None:
        """
        Converts the camera configuration into a Camera object and returns the RGB annotator.

        Based on example given in
        /isaac_sim-2023.1.1/standalone-examples/api/omni.isaac.sensor/camera_opencv_fisheye.py
        """
        for cam in cam_cfg:
            print(f"Loading {cam['Topic']}")
            camera_path = f"{self.prim_path}{cam['Parent']}/{cam['Topic']}"
            downsampling_ratio = cam["DownsamplingRatio"]
            width = int(cam["Width"] // downsampling_ratio)  # px
            height = int(cam["Height"] // downsampling_ratio)  # px

            camera = Camera(
                prim_path=camera_path,
                name=cam["Topic"],
                resolution=(width, height),  # px
                translation=cam["Translation"],  # m
                orientation=cam["Rotation"],  # m
            )

            camera.initialize()

            config = cam["Calibration"]
            pixel_size = config["PixelSize"] * downsampling_ratio  # μm
            distortion_coefficients = [
                config["K1"],
                config["K2"],
                config["K3"],
                config["K4"],
            ]
            focal_length = (
                pixel_size
                * 1e-6
                * (config["Fx"] + config["Fy"])
                / (2 * downsampling_ratio)
            )

            # Set the camera properties
            camera.set_focal_length(focal_length)
            camera.set_focus_distance(config["FocusDistance"])

            camera.set_horizontal_aperture(
                pixel_size * 1e-6 * width
            )  # setting vertical aperture is redundant
            camera.set_clipping_range(
                config["ClippingRangeMin"], config["ClippingRangeMax"]
            )

            # Set the distortion coefficients
            camera.set_lens_distortion_model("OmniLensDistortionKannalaBrandtK3API")
            camera.set_kannala_brandt_properties(
                nominal_width=width,
                nominal_height=height,
                optical_centre_x=config["Cx"] / downsampling_ratio,
                optical_centre_y=config["Cy"] / downsampling_ratio,
                max_fov=config["DiagonalFOV"],
                distortion_model=distortion_coefficients,
            )

    def _add_lidar(self, lidar_cfg: Mapping[str, Any]) -> None:
        omni.kit.commands.execute(
            "IsaacSensorCreateRtxLidar",
            translation=Gf.Vec3d(*lidar_cfg["Translation"]),
            orientation=Gf.Quatd(*lidar_cfg["Rotation"]),
            path="/lidar",
            parent=self.prim_path,
            config="OS0",
        )
