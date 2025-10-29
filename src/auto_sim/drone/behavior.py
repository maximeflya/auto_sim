import carb
from omni.kit.scripting import BehaviorScript

from isaacsim.core.api.world import World
from isaacsim.core.prims import RigidPrim
import numpy as np
from scipy.spatial.transform.rotation import Rotation
from typing import Tuple
import numpy.typing as npt

from auto_sim.drone.controllers import Controller
from auto_sim.drone.state import State

from auto_sim.drone.physics.vehicle_physics import Elios3Physics
from auto_sim.drone.controllers.velocity_controller import VelocityController, VelRef
from auto_sim.drone.controllers.trajectory_controller import TrajectoryController, TrajRef
from auto_sim.drone.controllers.acceleration_controller import AccelerationController, AccRef

class DroneBehavior(BehaviorScript):
    def on_init(self):
        carb.log_warn(f"{type(self).__name__}.on_init()->{self.prim_path}")
        self.world = World.instance()

        self._cog_prim = RigidPrim(self.prim_path.pathString + "/mass", reset_xform_properties=False)
        self.world.add_physics_callback("drone_physics_cb", self.on_physics_step)

    def on_physics_step(self, dt: float) -> None:
        self._update_state()
        for c in self.controllers:
            c.update_state(self._cog_state)

        moments, forces = self._get_moments_and_forces_from_controllers()
        self._cog_prim.apply_forces_and_torques_at_pos(forces, moments)


    def on_destroy(self):
        carb.log_warn(f"{type(self).__name__}.on_destroy()->{self.prim_path}")

    def on_play(self):
        self.vehicle_physics = Elios3Physics()
        self.controllers : list[Controller] = [
            VelocityController(VelRef(), self.vehicle_physics),
            TrajectoryController(TrajRef(), self.vehicle_physics),
            AccelerationController(AccRef(), self.vehicle_physics)
        ]
        self._cog_state = State()


        self.world = World.instance()

        carb.log_info(f"{type(self).__name__}.on_play()->{self.prim_path}")
        for c in self.controllers:
            c.start()


    def on_pause(self):
        carb.log_info(f"{type(self).__name__}.on_pause()->{self.prim_path}")
        for c in self.controllers:
            c.stop()

    def on_stop(self):
        carb.log_warn(f"{type(self).__name__}.on_stop()->{self.prim_path}")
        for c in self.controllers:
            c.stop()

    def on_update(self, current_time: float, delta_time: float):
        pass

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
        position, orientation = self._cog_prim.get_world_poses() # [x,y,z], [qw, qx, qy, qz]

        # Get the angular velocity of the vehicle expressed in the body frame of reference
        ang_vel = self._cog_prim.get_angular_velocities()[0]

        # The linear velocity [x_dot, y_dot, z_dot] of the vehicle's body frame expressed
        # in the inertial frame of reference
        linear_vel = self._cog_prim.get_linear_velocities()[0]

        # Update the state variable X = [x,y,z]
        self._cog_state.position = np.array(position[0])

        # Get the quaternion according in the [qx,qy,qz,qw] standard
        self._cog_state.attitude = np.array(np.roll(orientation[0], -1))

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