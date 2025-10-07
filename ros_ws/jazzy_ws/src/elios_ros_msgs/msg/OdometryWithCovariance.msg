# This is a message to hold odometry with confidence and covariance.

# Standard ROS odometry message
std_msgs/Header header
string child_frame_id
geometry_msgs/PoseWithCovariance pose
geometry_msgs/TwistWithCovariance twist

# Extra fields
bool confidence # True <=> High confidence, False <=> Low confidence
