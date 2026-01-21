from collections.abc import Iterator
from structural_om.core.spatial_index import SpatialIndex
from structural_om.core.id_pool import IdPool
from structural_om.core.object import Node

class NodeObj:
    def __init__(self, tolerance=1e-4):
        self._nodes: dict[str, Node] = {}
        self.spatial = SpatialIndex(tolerance)
        self.ids = IdPool()

    @property
    def nodes(self) -> dict[str, Node]:
        return self._nodes

    # ---------- clear ----------

    def clear(self):
        self._nodes.clear()
        self.spatial.clear()
        self.ids = IdPool()

    # ---------- access ----------

    def __len__(self) -> int:
        return len(self._nodes)

    def __contains__(self, node_id: str) -> bool:
        return node_id in self._nodes

    def __getitem__(self, node_id: str) -> Node:
        return self._nodes[node_id]

    def __iter__(self) -> Iterator[Node]:
        return iter(self._nodes.values())

    def get(self, node_id: str, default: Node | None = None) -> Node | None:
        return self._nodes.get(node_id, default)

    def items(self):
        return self._nodes.items()

    def values(self):
        return self._nodes.values()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({len(self)} nodes)"

    # ---------- creation ----------

    def create(
        self,
        xyz,
        *,
        node_id: str | None = None,
    ) -> Node:
        """
        Create a node.
        
        - node_id=None → normal creation (allocates ID, enforces uniqueness)
        - node_id=...  → rebuild creation (injects ID)
        """
        # return existing node within tolerance, or create a new one
        existing_id = self.spatial.find_near(xyz, self._nodes)
        if existing_id:
            return self._nodes[existing_id]
        
        if node_id is None:
            node_id = self.ids.allocate()

        else:
            # rebuild path
            if node_id in self._nodes:
                raise RuntimeError(f"Duplicate node_id '{node_id}'")
            self.ids._in_use.add(int(node_id))

        node = Node(node_id, xyz)
        self._nodes[node_id] = node
        self.spatial.insert(node_id, xyz)

        return node
    
    # ---------- mutation ----------

    def move(self, *, node_id: str, direction):
        node = self._nodes[node_id]
        new_xyz = tuple(node.xyz[i] + direction[i] for i in range(3))

        self._validate_move(node_id, new_xyz)

        self.spatial.move(node_id, node.xyz, new_xyz)
        node.xyz = new_xyz
        
    def set_location(self, *, node_id: str, location):
        node = self._nodes[node_id]

        self._validate_move(node_id, location)

        self.spatial.move(node_id, node.xyz, location)
        node.xyz = location

    def _validate_move(self, node_id: str, new_xyz):
        other_id = self.spatial.find_near(new_xyz, self._nodes)
        if other_id and other_id != node_id:
            raise RuntimeError("Node collision detected")
        
    # ---------- deletion ----------

    def delete(self, node_id: str):
        node = self._nodes[node_id]

        if node.connected_frames:
            raise RuntimeError("Cannot delete node with connected frames")

        self.spatial.remove(node_id, node.xyz)
        self.ids.release(node_id)
        del self._nodes[node_id]

    # ---------- replicate ----------

    def replicate(
        self,
        *,
        src_node_ids: list[str],
        delta: tuple[float, float, float],
        count: int,
    ) -> list[list[Node]]:
        """
        Replicate nodes along a vector.

        Returns:
            A list of batches.
            Each batch corresponds to one step.
            Each batch contains nodes in src_node_ids order.
        """

        dx, dy, dz = delta
        src_nodes = [self.get(nid) for nid in src_node_ids]

        batches: list[list[Node]] = []

        for step in range(1, count + 1):
            step_dx = dx * step
            step_dy = dy * step
            step_dz = dz * step

            batch: list[Node] = []

            for src in src_nodes:
                x, y, z = src.xyz
                new_xyz = (
                    x + step_dx,
                    y + step_dy,
                    z + step_dz,
                )

                node = self.create(xyz=new_xyz)
                batch.append(node)

            batches.append(batch)

        return batches