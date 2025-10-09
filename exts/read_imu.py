from isaacsim.sensors.physics import IMUSensor
from isaacsim.core.api.world import World

import time

world = World()
sensor = IMUSensor("/World/Drone/body/body_imu")

print(sensor)

end_time = time.time() + 5

b = 0
def cb(t):
    global b
    a = sensor.get_current_frame()

    b += 1
    if not (b % 33):
        print(a)

# world.add_physics_callback("test", cb)
world.remove_physics_callback("test")


# print(sensor.get_current_frame())
