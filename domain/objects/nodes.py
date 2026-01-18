from structural_om.domain.spatial_index import SpatialIndex
from structural_om.domain.id_pool import IdPool
from structural_om.domain.objects.object import Node

class Nodes:
    def __init__(self, tolerance=1e-4):
        self._nodes: dict[str, Node] = {}
        self.spatial = SpatialIndex(tolerance)
        self.ids = IdPool()

    # ---------- access ----------

    def get(self, node_id: str) -> Node:
        return self._nodes[node_id]

    def all(self) -> dict[str, Node]:
        return self._nodes

    # ---------- creation ----------

    def create(
        self,
        xyz,
        *,
        node_id: str | None = None,
        allow_overlap: bool = False,
    ) -> Node:
        """
        Create a node.

        - node_id=None → normal creation (allocates ID, enforces uniqueness)
        - node_id=...  → rebuild creation (injects ID)
        """

        if not allow_overlap:
            existing_id = self.spatial.find_near(xyz, self._nodes)
            if existing_id:
                raise RuntimeError("Node already exists within tolerance")

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

    def get_or_create(
        self,
        xyz,
    ) -> Node:
        """
        Return existing node within tolerance, or create a new one.
        """

        existing_id = self.spatial.find_near(xyz, self._nodes)
        if existing_id:
            return self._nodes[existing_id]

        return self.create(xyz=xyz)
    
    # ---------- mutation ----------

    def update_position(self, node_id: str, new_xyz):
        node = self._nodes[node_id]

        other_id = self.spatial.find_near(new_xyz, self._nodes)
        if other_id and other_id != node_id:
            raise RuntimeError("Node collision detected")

        self.spatial.move(node_id, node.xyz, new_xyz)
        node.xyz = new_xyz

    # ---------- deletion ----------

    def delete(self, node_id: str):
        node = self._nodes[node_id]

        if node.connected_frames:
            raise RuntimeError("Cannot delete node with connected frames")

        self.spatial.remove(node_id, node.xyz)
        self.ids.release(node_id)
        del self._nodes[node_id]

    # ---------- replicate ----------

    def replicate_by_vector(
        self,
        *,
        src_node_ids: list[str],
        delta: tuple[float, float, float],
        count: int,
    ) -> list[Node]:

        dx, dy, dz = delta
        created: list[Node] = []

        src_nodes = [self.get(nid) for nid in src_node_ids]

        for step in range(1, count + 1):
            step_dx = dx * step
            step_dy = dy * step
            step_dz = dz * step

            for src in src_nodes:
                x, y, z = src.xyz

                new_xyz = (
                    x + step_dx,
                    y + step_dy,
                    z + step_dz,
                )

                node = self.create(xyz=new_xyz)
                created.append(node)

        return created

    # ---------- clear ----------

    def clear(self):
        self._nodes.clear()
        self.spatial.clear()
        self.ids = IdPool()