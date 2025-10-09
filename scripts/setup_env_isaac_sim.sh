export ISAACSIM_PATH="${HOME}/isaacsim"
alias ISAAC_PYTHON="${ISAACSIM_PATH}/_build/linux-x86_64/release/python.sh"

export ROS_DISTRO=jazzy
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export LD_LIBRARY_PATH=${ISAACSIM_PATH}/exts/isaacsim.ros2.bridge/jazzy/lib
export ROS_DOMAIN_ID=123

source $HOME/autonomy_simulator/ros_ws/build_ws/jazzy/jazzy_ws/install/local_setup.bash
source $HOME/autonomy_simulator/ros_ws/build_ws/jazzy/isaac_sim_ros_ws/install/local_setup.bash