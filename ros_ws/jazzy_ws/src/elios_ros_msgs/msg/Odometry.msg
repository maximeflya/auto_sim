# This is a message to hold odometry with confidence, but without the covariance.

# ROS odometry message without covariance
std_msgs/Header header
string child_frame_id
geometry_msgs/Pose pose
geometry_msgs/Twist twist

# Extra fields
bool confidence # True <=> High confidence, False <=> Low confidence
