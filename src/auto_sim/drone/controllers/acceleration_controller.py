"""File that implements the high-level control logic for the vehicle."""

from dataclasses import dataclass, field
from typing import Any, Tuple

import numpy as np
from numpy import float32
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

from auto_sim.drone.controllers import Controller
from auto_sim.drone.physics.vehicle_physics import VehiclePhysics
from auto_sim.drone.state import State

@dataclass
class AccRef:
    time: float = 0.0
    a: NDArray[Any] = field(default_factory=lambda: np.zeros((3,)))
    yaw_rate: float = 0.0
    valid: bool = False


class AccelerationController(Controller[AccRef]):
    def __init__(
        self,
        ref: AccRef,
        vehicle_physics: VehiclePhysics
    ) -> None:
        # Define the control gains matrix for the outer-loop and the dynamic parameters
        # for the vehicle
        super().__init__(ref, vehicle_physics)

        self.max_valid_delay = 0.5

        # init states
        self.r = Rotation.identity()
        self.w = np.zeros((3,))
        self.ref = AccRef()

    def update_state(self, state_mass: State) -> None:
        self.r = Rotation.from_quat(state_mass.attitude)
        self.w = state_mass.angular_velocity

    def is_valid(self) -> bool:
        return (
            self._ref.valid
            and self._ref.time <= self._sim_context.current_time
            and self._sim_context.current_time - self._ref.time < self.max_valid_delay
        )

    def get_moments_and_forces(
        self,
    ) -> Tuple[NDArray[float32], NDArray[float32]]:
        acc_ref_semi_body = self.ref.a
        yaw_rate_ref = self.ref.yaw_rate

        # Transform to body frame
        roll, pitch = self.r.as_euler("xyz")[:2]

        r_sb_b = Rotation.from_euler("xyz", [-roll, -pitch, 0.0])

        acc_ref_body = r_sb_b.apply(acc_ref_semi_body)

        force_body = np.array(acc_ref_body * self._vehicle_physics.m())
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
        self.ref = AccRef()
