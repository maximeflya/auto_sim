from typing import Any, Tuple

import numpy as np
from numpy import float32
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

from autonomy_simulator.utils.datatypes import overrides
from autonomy_simulator.utils.logic_pegasus.vehicles.vehicle_physics import (
    VehiclePhysics,
)

from ..state import State  # noqa: E402
from .backend import Backend  # noqa: E402
from .roswrapper import DroneRosWrapper


class TrajectoryController(Backend):
    def __init__(
        self,
        ros_wrapper: DroneRosWrapper,
        num_rotors: int = 4,
        init_pos: NDArray[Any] = np.zeros((3,)),
        init_yaw: float = 0.0,
    ) -> None:
        super().__init__()

        self.ros_wrapper = ros_wrapper

        self.kp = np.diag([10.0, 10.0, 10.0])
        self.kd = np.diag([8.5, 8.5, 8.5])
        self.ki = np.diag([5.0, 5.0, 5.0])
        self.kr = np.diag([3.5, 3.5, 3.5])
        self.kw = np.diag([0.5, 0.5, 0.5])

        self.last_time = 0.0
        self.controller_timeout = 0.1  # Allowed duration without setpoint message

        # Sace the configuration for this backend
        self._num_rotors = num_rotors
        self.init_pos = init_pos
        self.init_yaw = init_yaw

        # Initial state of the vehicle expressed in the inertial frame (in ENU)
        self.p = self.init_pos  # The vehicle position
        self.r = Rotation.from_euler("y", self.init_yaw)  # The vehicle attitude
        self.w = np.zeros((3,))  # The angular velocity of vehicle
        self.v = np.zeros((3,))  # The linear velocity of vehicle in inertial frame
        self.integral_error = np.array([0.0, 0.0, 0.0])

    @overrides(Backend)
    def is_valid(self) -> bool:
        # Backend is only valid if the last setpoint message is withing controller timeout
        reference = self.ros_wrapper.get_traj_ref()
        return self.last_time - reference.timestamp < self.controller_timeout

    @overrides(Backend)
    def update_state(self, state_mass: State) -> None:
        self.p = state_mass.position
        self.r = Rotation.from_quat(state_mass.attitude)
        self.w = state_mass.angular_velocity
        self.v = state_mass.linear_velocity

    def get_ref(
        self,
    ) -> Tuple[NDArray[Any], NDArray[Any], NDArray[Any], NDArray[Any], float, float]:
        reference = self.ros_wrapper.get_traj_ref()
        p_ref = reference.position
        v_ref = reference.velocity
        a_ref = reference.acceleration
        j_ref = reference.jerk
        yaw_ref = reference.yaw
        yaw_rate_ref = reference.yaw_rate

        return p_ref, v_ref, a_ref, j_ref, yaw_ref, yaw_rate_ref

    @overrides(Backend)
    def get_moments_and_forces(
        self, vehicle_physics: VehiclePhysics, time: float
    ) -> Tuple[NDArray[float32], NDArray[float32]]:

        # Update the time step
        dt = time - self.last_time
        self.last_time = time

        # Get references
        p_ref, v_ref, a_ref, j_ref, yaw_ref, yaw_rate_ref = self.get_ref()

        # Set controller reference to the current state if it was inactive
        if dt > self.controller_timeout:
            p_ref = self.p  # The vehicle position
            v_ref = np.zeros((3,))  # The linear velocity of vehicle in inertial frame
            a_ref = np.zeros((3,))  # The linear acceleration of vehicle in inertial frame
            j_ref = np.zeros((3,))
            yaw_ref = self.r.as_euler("xyz")[2]  # The vehicle attitude
            yaw_rate_ref = 0.0  # The angular velocity of vehicle
            self.integral_error = np.zeros((3,))

        # Compute the tracking errors
        ep = self.p - p_ref
        ev = self.v - v_ref
        self.integral_error = self.integral_error + (ep * dt)
        ei = self.integral_error

        # Compute the control inputs (u_1, tau)
        u_1, tau = self.compute_control_inputs(
            vehicle_physics,
            ep,
            ev,
            ei,
            yaw_ref,
            yaw_rate_ref,
            a_ref,
            j_ref,
        )

        # Use the allocation matrix provided by the Multirotor vehicle to convert the
        # desired force and torque to angular velocity [rad/s] references to give to each
        # rotor
        rotor_speed_ref = vehicle_physics.rotor_speeds_from_forces_and_moments(u_1, tau)

        vehicle_physics.set_target_rotor_speeds(rotor_speed_ref)

        # Forces and moments in body frame
        return vehicle_physics.update(dt)

    def compute_control_inputs(
        self,
        vehicle_physics: VehiclePhysics,
        ep: NDArray[Any],
        ev: NDArray[Any],
        ei: NDArray[Any],
        yaw_ref: float,
        yaw_rate_ref: float,
        a_ref: NDArray[Any],
        j_ref: NDArray[Any],
    ) -> Tuple[NDArray[float32], NDArray[float32]]:
        f_des = (
            -(self.kp @ ep)
            - (self.kd @ ev)
            - (self.ki @ ei)
            + np.array([0.0, 0.0, vehicle_physics.m() * vehicle_physics.g()])
            + (vehicle_physics.m() * a_ref)
        )

        # Get the current axis
        z_b = self.r.as_matrix()[:, 2]

        # Get the desired total thrust in z_b direction (u_1)
        u_1 = f_des @ z_b

        # Compute the desired body-frame axis z_b
        z_b_des = f_des / np.linalg.norm(f_des)

        # Compute x_c_des
        x_c_des = np.array([np.cos(yaw_ref), np.sin(yaw_ref), 0.0])

        # Compute y_b_des
        z_b_cross_x_c = np.cross(z_b_des, x_c_des)
        y_b_des = z_b_cross_x_c / np.linalg.norm(z_b_cross_x_c)

        # Compute x_b_des
        x_b_des = np.cross(y_b_des, z_b_des)

        # Compute the desired rotation r_des = [x_b_des | y_b_des | z_b_des]
        r_des = np.c_[x_b_des, y_b_des, z_b_des]
        r = self.r.as_matrix()

        # Compute the rotation error
        e_r = 0.5 * self.vee((r_des.T @ r) - (r.T @ r_des))

        # Compute the desired angular velocity by projecting the angular velocity in the
        # Xb-Yb plane projection of angular velocity on xB − yB plane see eqn (7) from
        # [2].
        hw = (vehicle_physics.m() / u_1) * (j_ref - np.dot(z_b_des, j_ref) * z_b_des)

        # desired angular velocity
        w_des = np.array(
            [-np.dot(hw, y_b_des), np.dot(hw, x_b_des), yaw_rate_ref * z_b_des[2]]
        )

        # Compute the angular velocity error
        e_w = self.w - w_des

        # Compute the torques to apply on the rigid body
        tau = -(self.kr @ e_r) - (self.kw @ e_w)
        return np.array([0.0, 0.0, u_1], dtype=float32), tau

    @overrides(Backend)
    def reset_params(self) -> None:
        # Reset state
        self.p = np.zeros((3,))
        self.r = Rotation.identity()
        self.w = np.zeros((3,))
        self.v = np.zeros((3,))
        self.integral_error = np.zeros((3,))
