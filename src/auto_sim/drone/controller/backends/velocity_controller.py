"""
| File: velocity_controller.py
| Derived from backend.py
| Description: File that implements the high-level control logic for the vehicle
"""

from typing import Any, Tuple

import numpy as np
from numpy import float32
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

from autonomy_simulator.utils.logic_pegasus.vehicles.vehicle_physics import (
    VehiclePhysics,
)

from ..state import State  # noqa: E402
from .backend import Backend  # noqa: E402
from .roswrapper import DroneRosWrapper


class VelocityController(Backend):
    def __init__(
        self,
        ros_wrapper: DroneRosWrapper,
        num_rotors: int = 4,
        init_yaw: float = 0.0,
    ) -> None:
        super().__init__()

        self.ros_wrapper = ros_wrapper

        self.kp = np.diag([10.0, 10.0, 10.0])
        self.kd = np.diag([0.0, 0.0, 0.0])
        self.ki = np.diag([5.0, 5.0, 5.0])
        self.kr = np.diag([3.5, 3.5, 3.5])
        self.kw = np.diag([0.5, 0.5, 0.5])

        self.last_time = 0.0
        self.controller_timeout = 0.1  # Allowed duration without setpoint message

        # Save the configurations for this backend
        self._num_rotors = num_rotors
        self.init_yaw = init_yaw

        # Initial states
        self.yaw_ref = self.init_yaw
        self.r = Rotation.identity()
        self.w = np.zeros((3,))
        self.v = np.zeros((3,))
        self.integral_error = np.zeros((3,))

    def is_valid(self) -> bool:
        return True

    def update_state(self, state_mass: State) -> None:
        self.p = state_mass.position
        self.r = Rotation.from_quat(state_mass.attitude)
        self.w = state_mass.angular_velocity
        self.v = state_mass.linear_velocity

    def get_ref(self) -> Tuple[NDArray[Any], float, NDArray[Any], NDArray[Any]]:
        reference = self.ros_wrapper.get_vel_ref()
        linear_vel_ref = reference.vel
        a_ref = np.zeros((3,))
        j_ref = np.zeros((3,))

        if reference.mode == "body":
            yaw = self.r.as_euler("xyz")[2]
            v_x = np.sin(yaw) * linear_vel_ref[0] + np.cos(yaw) * linear_vel_ref[1]
            v_y = -np.cos(yaw) * linear_vel_ref[0] + np.sin(yaw) * linear_vel_ref[1]
            linear_vel_ref = np.array([v_x, v_y, linear_vel_ref[2]])
        elif reference.mode == "local":
            linear_vel_ref[0], linear_vel_ref[1] = linear_vel_ref[1], linear_vel_ref[0]
        else:
            raise NotImplementedError

        return linear_vel_ref, reference.yaw_rate, a_ref, j_ref

    def get_moments_and_forces(
        self, vehicle_physics: VehiclePhysics, time: float
    ) -> Tuple[NDArray[float32], NDArray[float32]]:
        dt = time - self.last_time
        self.last_time = time

        linear_vel_ref, yaw_vel_ref, a_ref, j_ref = self.get_ref()

        ev = self.v - linear_vel_ref
        self.integral_error = self.integral_error + ev * dt
        self.yaw_ref = self.yaw_ref + yaw_vel_ref * dt

        if dt > self.controller_timeout:
            self.integral_error = np.zeros((3,))
            self.yaw_ref = self.r.as_euler("xyz")[2]

        # Compute the control inputs (u_1, tau)
        u_1, tau = self.compute_control_inputs(
            vehicle_physics,
            ev,
            np.zeros((3,)),
            self.integral_error,
            self.yaw_ref,
            yaw_vel_ref,
            a_ref,
            j_ref,
        )

        rotor_speed_ref = vehicle_physics.rotor_speeds_from_forces_and_moments(u_1, tau)

        vehicle_physics.set_target_rotor_speeds(rotor_speed_ref)

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

    def reset_params(self) -> None:
        self.yaw_ref = self.init_yaw
        self.r = Rotation.identity()
        self.w = np.zeros((3,))
        self.v = np.zeros((3,))
        self.integral_error = np.zeros((3,))
