from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np
from numpy import float32
from numpy.typing import NDArray

from .linear_drag import LinearDrag
from auto_sim.drone.state import State
from .thrusters import Elios3Thrusters


class VehiclePhysics(ABC):
    def __init__(self) -> None:
        self.mass = 0.0
        self.state = State()

    def set_state(self, state: State) -> None:
        self.state = state

    def get_state(self) -> State:
        return self.state

    def m(self) -> float:
        return self.mass

    @abstractmethod
    def update(self, dt: float) -> Tuple[NDArray[float32], NDArray[float32]]:
        pass

    @abstractmethod
    def set_target_rotor_speeds(self, rotor_speeds: NDArray[float32]) -> None:
        pass

    @staticmethod
    def g() -> float:
        """
        Returns the gravitational acceleration.
        """
        return 9.81

    @abstractmethod
    def rotor_speeds_from_forces_and_moments(
        self, forces: NDArray[float32], moments: NDArray[float32]
    ) -> NDArray[float32]:
        pass


class Elios3Physics(VehiclePhysics):
    def __init__(self) -> None:
        super().__init__()
        self.mass = 1.86 + 0.45
        self.num_rotors = 4
        self.drag = LinearDrag([0.50, 0.30, 0.0])
        self.thrusters = Elios3Thrusters(self.num_rotors)

        # fmt: off
        self.moment_matrix = np.array([[0.094360, -0.094360, -0.121280, 0.121280],
                                       [0.060630, 0.060630, -0.100630, -0.100630],
                                       [0.033333, -0.033333, 0.033333, -0.033333]])

        self.body_torque_thrust_to_motor_thrust = np.array(
            [[2.318679, 3.100583, 8.436283, 0.312012],
             [-2.318679, 3.100583, -8.436283, 0.312012],
             [-2.318679, -3.100583, 6.563717, 0.187988],
             [2.318679, -3.100583, -6.563717, 0.187988]])
        # fmt: on

    def update(self, dt: float) -> Tuple[NDArray[float32], NDArray[float32]]:
        thrusts = self.thrusters.update(dt)
        body_moments, body_forces = self.forces_and_moments_from_thrusts(thrusts)
        drag_forces = self.drag.update(self.state, dt)
        return body_moments, body_forces + drag_forces

    def set_target_rotor_speeds(self, rotor_speeds: NDArray[float32]) -> None:
        self.thrusters.set_target_rotor_speeds(rotor_speeds)

    def forces_and_moments_from_thrusts(
        self, thrusts: NDArray[float32]
    ) -> Tuple[NDArray[float32], NDArray[float32]]:
        moments = self.moment_matrix @ thrusts
        forces = np.array([0.0, 0.0, np.sum(thrusts)])
        return moments, forces

    def rotor_speeds_from_forces_and_moments(
        self, forces: NDArray[float32], moments: NDArray[float32]
    ) -> NDArray[float32]:
        torque_thrust = np.array([moments[0], moments[1], moments[2], forces[2]])
        thrusts = self.body_torque_thrust_to_motor_thrust @ torque_thrust
        return self.thrusters.rotor_speeds_from_thrusts(thrusts)
