import omni.graph.core as og

async def load_odometry_graph() -> og._omni_graph_core.Graph:
    print("action")
    keys = og.Controller.Keys
    (odom, _, _, _) = og.Controller.edit(
        {
            "graph_path": "/Odometry",
            "evaluator_name": "push",
        },
        {
            keys.CREATE_NODES: [
                ("OnTick", "omni.graph.action.OnTick"),
                ("readSimTime", "isaacsim.core.nodes.IsaacReadSimulationTime"),
                ("ros2Context", "isaacsim.ros2.bridge.ROS2Context"),
                ("computeOdometry", "isaacsim.core.nodes.IsaacComputeOdometry"),
                ("publishOdometryWorld", "isaacsim.ros2.bridge.ROS2Publisher"),
                ("publishOdometryBody", "isaacsim.ros2.bridge.ROS2Publisher"),
            ],
            keys.CONNECT: [
                ("OnTick.outputs:tick", "computeOdometry.inputs:execIn"),
                ("computeOdometry.outputs:execOut", "publishOdometryWorld.inputs:execIn"),
                ("computeOdometry.outputs:execOut", "publishOdometryBody.inputs:execIn"),
                ("ros2Context.outputs:context", "publishOdometryWorld.inputs:context"),
                ("ros2Context.outputs:context", "publishOdometryBody.inputs:context"),
                # ("readSimTime.outputs:simulationTime", "publishOdometryWorld.inputs:timeStamp"),
                # ("readSimTime.outputs:simulationTime", "publishOdometryBody.inputs:timeStamp"),
            ],
            keys.SET_VALUES: [
                ("OnTick.inputs:framePeriod", 3), # TODO: remove hardcoded 10Hz
                ("readSimTime.inputs:resetOnStop", True),
                ("publishOdometryWorld.inputs:messageName", "Odometry"),
                ("publishOdometryWorld.inputs:messagePackage", "elios_ros_msgs"),
                ("publishOdometryBody.inputs:messageName", "Odometry"),
                ("publishOdometryBody.inputs:messagePackage", "elios_ros_msgs"),
                ("publishOdometryBody.inputs:confidence", True)
            ]
        },
    )

    # await(og.Controller.evaluate("/Odometry"))

    # og.Controller.edit(odom, {keys.SET_VALUES: [(]})

    # await(og.Controller.evaluate("/Odometry"))
    # print("done")

    return odom