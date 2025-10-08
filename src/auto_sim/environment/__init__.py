from collections.abc import Sequence


NVIDIA_ENVIRONMENTS = {
    "DefaultEnvironment": "Grid/default_environment.usd",
    "BlackGridroom": "Grid/gridroom_black.usd",
    "CurvedGridroom": "Grid/gridroom_curved.usd",
    "Hospital": "Hospital/hospital.usd",
    "Office": "Office/office.usd",
    "SimpleRoom": "Simple_Room/simple_room.usd",
    "Warehouse": "Simple_Warehouse/warehouse.usd",
    "WarehouseWithForklifts": "Simple_Warehouse/warehouse_with_forklifts.usd",
    "WarehouseWithShelves": "Simple_Warehouse/warehouse_multiple_shelves.usd",
    "FullWarehouse": "Simple_Warehouse/full_warehouse.usd",
    "FlatPlane": "Terrains/flat_plane.usd",
    "RoughPlane": "Terrains/rough_plane.usd",
    "SlopePlane": "Terrains/slope.usd",
    "StairsPlane": "Terrains/stairs.usd",
}

OMNIVERSE_ENVIRONMENTS = {
    "ExhibitionHall": (
        "omniverse://localhost/NVIDIA/Assets/Scenes/Templates/Interior/"
        "ZetCG_ExhibitionHall.usd"
    ),
}

LOCAL_ENVIRONMENTS = {
    "Tunnel": "tunnel.usda",
    "Building": "building.usd",
    "Cave": "cave.usdc",
    "Silo": "silo/silo.usd",
    "Sewer": "sewer/sewer.usd",
    "Watertower": "watertower/watertower.usd",
}


def get_environment_list() -> Sequence[str]:
    environment_list = []
    for key in NVIDIA_ENVIRONMENTS.keys():
        environment_list.append(key)

    for key in OMNIVERSE_ENVIRONMENTS.keys():
        environment_list.append(key)

    for key in LOCAL_ENVIRONMENTS.keys():
        environment_list.append(key)

    return environment_list