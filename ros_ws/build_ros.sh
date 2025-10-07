#!/bin/bash


# Part of this code comes from https://github.com/isaac-sim/IsaacSim-ros_workspaces
#
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


UBUNTU_VERSION="24.04"
ROS_DISTRO="jazzy"
DOCKERFILE="dockerfiles/ubuntu_24_jazzy_python_311_minimal.dockerfile" 

# Build the Docker image
docker build . --network=host -f $DOCKERFILE -t isaac_sim_ros:ubuntu_${UBUNTU_VERSION%.*}_${ROS_DISTRO}

# Prepare the target directory
rm -rf build_ws/${ROS_DISTRO}
mkdir -p build_ws/${ROS_DISTRO}

pushd build_ws/${ROS_DISTRO}

# Extract files from Docker container
docker cp $(docker create --rm isaac_sim_ros:ubuntu_${UBUNTU_VERSION%.*}_${ROS_DISTRO}):/workspace/${ROS_DISTRO}_ws ${ROS_DISTRO}_ws

docker cp $(docker create --rm isaac_sim_ros:ubuntu_${UBUNTU_VERSION%.*}_${ROS_DISTRO}):/workspace/build_ws isaac_sim_ros_ws

popd

echo "Build complete for $ROS_DISTRO on Ubuntu $UBUNTU_VERSION"
