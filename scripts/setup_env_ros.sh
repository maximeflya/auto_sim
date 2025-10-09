export KIMONO_PATH="${HOME}/kimono"
export ROS_DISTRO=jazzy
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_DOMAIN_ID=123 # Change this number to avoid conflicts

# . $KIMONO_PATH/build/latest_conanrun.sh
source /opt/ros/$ROS_DISTRO/setup.sh