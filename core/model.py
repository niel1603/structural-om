from structural_om.core.api.node import NodeObj
from structural_om.core.api.frame import FrameObj

import json

class StructuralModel:
    def __init__(self):
        self.node = NodeObj()
        self.frame = FrameObj()

    # ---------- convenience API ----------

    def add_frame_by_coord(self, p1, p2):
        n1 = self.node.create(xyz=p1)
        n2 = self.node.create(xyz=p2)
        return self.frame.create(n1=n1, n2=n2)

    # ----------------------------
    # clear 
    # ----------------------------

    def clear(self):
        self.node.clear()
        self.frame.clear()

    # ----------------------------
    # JSON
    # ----------------------------

    def to_dict(self) -> dict:
        return {
            "schema_version": 1,
            "model_info": {
                "name": "Unnamed Model",
                "units": "m",
            },
            "nodes": {
                node_id: {
                    "xyz": list(node.xyz),
                }
                for node_id, node in self.node.all().items()
            },
            "frames": {
                frame_id: {
                    "n1": frame.n1_id,
                    "n2": frame.n2_id,
                }
                for frame_id, frame in self.frame.all().items()
            },
        }

    def save_json(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
