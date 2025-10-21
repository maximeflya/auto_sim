"""
| File: acceleration_controller.py
| Derived from backend.py
| Description: File that implements the high-level control logic for the vehicle
"""

from typing import Tuple

import numpy as np
from numpy import float32
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

from auto_sim.drone.controller.vehicle_physics import (
    VehiclePhysics,
)
from auto_sim.drone.controller.state import State
from auto_sim.drone.controller.backends import Backend


class AccelerationController(Backend):
    def __init__(
        self,
    ) -> None:
        # Define the control gains matrix for the outer-loop and the dynamic parameters
        # for the vehicle
        super().__init__()


        # Validity params
        self.max_valid_delay = 0.5

        # init states
        self.r = Rotation.identity()
        self.w = np.zeros((3,))

    def update_state(self, state_mass: State) -> None:
        self.r = Rotation.from_quat(state_mass.attitude)
        self.w = state_mass.angular_velocity

    def get_moments_and_forces(
        self, vehicle_physics: VehiclePhysics, time: float
    ) -> Tuple[NDArray[float32], NDArray[float32]]:
        reference = self.ros_wrapper.get_acc_ref()
        acc_ref_semi_body = reference.a
        yaw_rate_ref = reference.yaw_rate

        # Transform to body frame
        roll, pitch = self.r.as_euler("xyz")[:2]

        r_sb_b = Rotation.from_euler("xyz", [-roll, -pitch, 0.0])

        acc_ref_body = r_sb_b.apply(acc_ref_semi_body)

        force_body = np.array(acc_ref_body * vehicle_physics.m())
        moment_body = np.array(
            [
                -roll - self.w[0],
                -pitch - self.w[1],
                yaw_rate_ref - self.w[2],
            ]
        )

        return moment_body, force_body

    def reset_params(self) -> None:
        self.r = Rotation.identity()
        self.w = np.zeros((3,))
