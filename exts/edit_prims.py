from pathlib import Path

import yaml
from isaacsim.core.utils.stage import get_current_stage
from omni.isaac.core.prims import XFormPrim

from auto_sim import drone

stage = get_current_stage()

prim_path = "/drone"

prims_file: Path = Path(drone.__file__).parent / "prims.yaml"

prims_cfg = yaml.safe_load(prims_file.read_text())
if not isinstance(prims_cfg, list):
    raise RuntimeError(
        f"When reading {str(prims_file)}, expected the prims config to be a list got {type(prims_cfg)}"
    )


stage.DefinePrim(f"{prim_path}/body", "Xform")
for prim in prims_cfg:
    stage.DefinePrim(prim_path + prim["Parent"] + prim["Name"], "Xform")
    XFormPrim(
        prim_path=prim_path + prim["Parent"] + prim["Name"],
        name=prim["Name"],
        translation=prim["Translation"],
        orientation=prim["Rotation"],
    )
