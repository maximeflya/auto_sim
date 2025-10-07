# Message packing the informations needed to control the drone using acceleration 
# (semibody) and yaw rate (body) commands.

std_msgs/Header       header
geometry_msgs/Vector3 acceleration_semibody
float32               yaw_rate_body
uint8                 is_valid
