from collections.abc import Mapping, Sequence
from typing import Any
import isaacsim.core.utils.prims as prim_utils
from isaacsim.sensors.rtx import LidarRtx
from isaacsim.sensors.physics import IMUSensor
from pxr import Gf
from auto_sim.drone.camera import Camera
import numpy as np
import omni


def add_lights(prim_path: str, cfg: Sequence[Mapping[str, Any]]) -> None:
    for light in cfg:
        for parent in light["Parents"]:
            prim_utils.create_prim(
                prim_path + parent + light["Name"],
                "RectLight",
                translation=light["Translation"],
                orientation=light["Rotation"],
                attributes={
                    "inputs:intensity": light["Intensity"],
                    "inputs:height": light["Height"],
                    "inputs:width": light["Width"],
                },
            )

def add_imu(prim_path: str, imu_cfg: Sequence[Mapping[str, Any]]) -> None:
    for imu in imu_cfg:
        IMUSensor(
            prim_path= f"{prim_path}{imu['Parent']}/{imu['Topic']}",
            name=imu['Topic'],
            frequency=imu["UpdateRate"],
            translation=np.array([0, 0, 0]),
            orientation=np.array([1, 0, 0, 0]),
        )

def add_camera_sensor(prim_path: str, cam_cfg: Sequence[Mapping[str, Any]]) -> None:
    """
    Converts the camera configuration into a Camera object and returns the RGB annotator.

    Based on example given in
    /isaac_sim-2023.1.1/standalone-examples/api/omni.isaac.sensor/camera_opencv_fisheye.py
    """
    for cam in cam_cfg:
        print(f"Loading {cam['Topic']}")
        camera_path = f"{prim_path}{cam['Parent']}/{cam['Topic']}"
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

def add_lidar(prim_path: str, lidar_cfg: Mapping[str, Any]) -> None:
    omni.kit.commands.execute(
        "IsaacSensorCreateRtxLidar",
        translation=Gf.Vec3d(*lidar_cfg["Translation"]),
        orientation=Gf.Quatd(*lidar_cfg["Rotation"]),
        path="/lidar",
        parent=prim_path,
        config="OS0",
    )
