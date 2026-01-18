from structural_om.domain.objects.nodes import Nodes
from structural_om.domain.objects.frames import Frames

import json

class StructuralModel:
    def __init__(self):
        self.nodes = Nodes()
        self.frames = Frames()

    # ---------- convenience API ----------

    def add_frame_by_coord(self, p1, p2):
        n1 = self.nodes.create(xyz=p1)
        n2 = self.nodes.create(xyz=p2)
        return self.frames.create(n1=n1, n2=n2)

    # ----------------------------
    # clear 
    # ----------------------------

    def clear(self):
        self.nodes.clear()
        self.frames.clear()

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
                for node_id, node in self.nodes.all().items()
            },
            "frames": {
                frame_id: {
                    "n1": frame.n1_id,
                    "n2": frame.n2_id,
                }
                for frame_id, frame in self.frames.all().items()
            },
        }

    def save_json(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
