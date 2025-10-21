"""
| Author: Marcelo Jacinto (marcelo.jacinto@tecnico.ulisboa.pt)
| License: BSD-3-Clause. Copyright (c) 2023, Marcelo Jacinto. All rights reserved.
"""

from abc import ABC, abstractmethod
from typing import Any, Tuple

import numpy as np
from numpy.typing import NDArray

from auto_sim.drone.controller.vehicle_physics import (
    VehiclePhysics,
)

from ..state import State


class Backend(ABC):
    """
    Properties
    """
    @property
    def vehicle(self) -> Any:
        """A reference to the vehicle associated with this backend.

        Returns:
            Vehicle: A reference to the vehicle associated with this backend.
        """
        return self._vehicle

    def initialize(self, vehicle: Any) -> None:
        """A method that can be invoked when the simulation is starting to give
        access to the control backend to the entire vehicle object.

        Args:
            vehicle (Vehicle): A reference to the vehicle that this sensor is
            associated with
        """
        self._vehicle = vehicle

    @abstractmethod
    def update_state(self, state_mass: State) -> None:
        """Method that when implemented, should handle the receival of the state
        of the vehicle using this callback. This method will is called on every
        physics step.

        Args:
            state_mass (State): The current state of the CoG of the vehicle.
        """

    @abstractmethod
    def get_moments_and_forces(
        self, vehicle_physics: VehiclePhysics, time: float
    ) -> Tuple[NDArray[np.float32], NDArray[np.float32]]:
        """Method that when implemented, should be used to compute the moments and forces
        to be applied to the vehicle in simulation based on the motor speed. This method
        must be implemented by a class that inherits this type. This callback is called on
        every physics step where this backend is selected to provide the moments and
        forces for the vehicle.

        Args:
            time (float): The current simulation time.
        """

    @staticmethod
    def vee(s: NDArray[np.float32]) -> NDArray[np.float32]:
        """Auxiliary function that computes the 'v' map which takes elements from so(3)
        to R^3.

        Args:
            S (np.array): A matrix in so(3)
        """
        return np.array([-s[1, 2], s[0, 2], -s[0, 1]])

    def start(self) -> None:
        """
        Handle the begining of the simulation of the vehicle
        """
        self.reset_params()

    def stop(self) -> None:
        """
        Handle the stopping of the simulation of the vehicle
        """
        self.reset_params()

    def reset(self) -> None:
        """
        Handle the reset of the vehicle simulation to its original state
        """
        self.reset_params()

    @abstractmethod
    def reset_params(self) -> None:
        """
        Reset the controller to its initial state
        """
