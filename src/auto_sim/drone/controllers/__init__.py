from abc import ABC, abstractmethod
from typing import Tuple, Generic, TypeVar

import numpy as np
from numpy.typing import NDArray

from isaacsim.core.api import SimulationContext

from auto_sim.drone.physics.vehicle_physics import VehiclePhysics
from auto_sim.drone.state import State


Reference = TypeVar("Reference")

class Controller(ABC, Generic[Reference]):
    def __init__(self, reference: Reference,  vehicle_physics: VehiclePhysics,) -> None:
        self._ref = reference
        self._sim_context = SimulationContext.instance()
        self._vehicle_physics = vehicle_physics

    @abstractmethod
    def update_state(self, state_mass: State) -> None:
        """Method that when implemented, should handle the receival of the state
        of the vehicle using this callback. This method will is called on every
        physics step.

        Args:
            state_mass (State): The current state of the CoG of the vehicle.
        """

    @abstractmethod
    def is_valid(self) -> bool:
        """If the controller is in a state to control the drone or not."""


    @abstractmethod
    def get_moments_and_forces(
        self
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

    def update_reference(self, ref: Reference) -> None:
        """Update the reference of the controller"""
        self._ref = ref

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
