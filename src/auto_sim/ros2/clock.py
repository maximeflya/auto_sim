import omni.graph.core as og


def load_clock_graph() -> og._omni_graph_core.Graph:
    keys = og.Controller.Keys
    (clock, _, _, _) = og.Controller.edit(
        {
            "graph_path": "/ROS_Clock",
            "evaluator_name": "push",
        },
        {
            keys.CREATE_NODES: [
                ("OnTick", "omni.graph.action.OnTick"),
                ("readSimTime", "isaacsim.core.nodes.IsaacReadSimulationTime"),
                ("ros2Context", "isaacsim.ros2.bridge.ROS2Context"),
                ("publishClock", "isaacsim.ros2.bridge.ROS2PublishClock"),
            ],
            keys.CONNECT: [
                ("OnTick.outputs:tick", "publishClock.inputs:execIn"),
                ("ros2Context.outputs:context", "publishClock.inputs:context"),
                ("readSimTime.outputs:simulationTime", "publishClock.inputs:timeStamp"),
            ],
            keys.SET_VALUES: [("readSimTime.inputs:resetOnStop", True)],
        },
    )
    return clock
