from structural_om.domain.spatial_index import SpatialIndex
from structural_om.domain.id_pool import IdPool
from structural_om.domain.object import (
    Node, 
    Frame
    )

import json

class StructuralModel:
    def __init__(self, tolerance=1e-4):
        self.nodes: dict[str, Node] = {}
        self.frames: dict[str, Frame] = {}

        self.spatial = SpatialIndex(tolerance)

        self.node_ids = IdPool()
        self.frame_ids = IdPool()
    
    # ----------------------------
    # Object APIs
    # ----------------------------

    def get_or_create_node(self, xyz):
        existing_id = self.spatial.find_near(xyz, self.nodes)
        if existing_id:
            return self.nodes[existing_id]

        node_id = self.node_ids.allocate()
        node = Node(node_id, xyz)

        self.nodes[node_id] = node
        self.spatial.insert(node_id, xyz)

        return node
    
    def add_frame_by_nodes(self, n1: Node, n2: Node):
        if n1.id == n2.id:
            raise ValueError("Frame cannot connect a node to itself")

        frame_id = self.frame_ids.allocate()
        frame = Frame(frame_id, n1.id, n2.id)

        self.frames[frame_id] = frame
        n1.connected_frames.add(frame_id)
        n2.connected_frames.add(frame_id)

        return frame

    def add_frame_by_coord(self, p1, p2):
        n1 = self.get_or_create_node(p1)
        n2 = self.get_or_create_node(p2)
        return self.add_frame_by_nodes(n1, n2)

    def delete_node(self, node_id):
        node = self.nodes[node_id]

        if node.connected_frames:
            raise RuntimeError("Cannot delete node with connected frames")

        self.spatial.remove(node_id, node.xyz)
        self.node_ids.release(node_id)
        del self.nodes[node_id]

    def delete_frame(self, frame_id):
        frame = self.frames[frame_id]

        self.nodes[frame.n1_id].connected_frames.remove(frame_id)
        self.nodes[frame.n2_id].connected_frames.remove(frame_id)

        self.frame_ids.release(frame_id)
        del self.frames[frame_id]
        
    # ----------------------------
    # Model manipulation: move and replicate
    # ----------------------------

    def update_node_position(self, node_id, new_xyz):
        node = self.nodes[node_id]

        other_id = self.spatial.find_near(new_xyz, self.nodes)
        if other_id and other_id != node_id:
            raise RuntimeError("Node collision detected")

        self.spatial.move(node_id, node.xyz, new_xyz)
        node.xyz = new_xyz

    def create_node(self, xyz):
        if self.spatial.find_near(xyz, self.nodes):
            raise RuntimeError("Node already exists within tolerance")

        node_id = self.node_ids.allocate()
        node = Node(node_id, xyz)

        self.nodes[node_id] = node
        self.spatial.insert(node_id, xyz)

        return node

    def create_frame(self, n1_id: str, n2_id: str):
        frame_id = self.frame_ids.allocate()
        frame = Frame(frame_id, n1_id, n2_id)

        self.frames[frame_id] = frame
        self.nodes[n1_id].connected_frames.add(frame_id)
        self.nodes[n2_id].connected_frames.add(frame_id)

        return frame
    
    # ----------------------------
    # REBUILD
    # ----------------------------
    def clear(self):
        self.nodes.clear()
        self.frames.clear()
        self.spatial.clear()
        self.node_ids = IdPool()
        self.frame_ids = IdPool()

    def add_node_forced(self, node_id: str, xyz):
        node = Node(node_id, xyz)
        self.nodes[node_id] = node
        self.spatial.insert(node_id, xyz)
        self.node_ids._in_use.add(int(node_id))
        return node

    def add_frame_forced(self, frame_id: str, n1_id: str, n2_id: str):
        frame = Frame(frame_id, n1_id, n2_id)
        self.frames[frame_id] = frame
        self.nodes[n1_id].connected_frames.add(frame_id)
        self.nodes[n2_id].connected_frames.add(frame_id)
        self.frame_ids._in_use.add(int(frame_id))
        return frame
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
                nid: {
                    "xyz": list(node.xyz)
                }
                for nid, node in self.nodes.items()
            },
            "frames": {
                fid: {
                    "n1": frame.n1_id,
                    "n2": frame.n2_id,
                }
                for fid, frame in self.frames.items()
            },
        }


    def save_json(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
