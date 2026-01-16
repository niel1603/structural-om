from collections import defaultdict
from math import sqrt


def distance(a, b):
    return sqrt(
        (a[0] - b[0]) ** 2 +
        (a[1] - b[1]) ** 2 +
        (a[2] - b[2]) ** 2
    )


class SpatialIndex:
    """
    Grid-based spatial hash for tolerant point lookup.
    NOT authoritative. Rebuildable at any time.
    """

    def __init__(self, tolerance=1e-4):
        self.tol = tolerance
        self._cells: dict[tuple[int, int, int], set[str]] = defaultdict(set)

    # ----------------------------
    # Quantization
    # ----------------------------

    def _cell_key(self, xyz):
        return (
            int(xyz[0] / self.tol),
            int(xyz[1] / self.tol),
            int(xyz[2] / self.tol),
        )

    # ----------------------------
    # Public API
    # ----------------------------

    def insert(self, node_id: str, xyz):
        self._cells[self._cell_key(xyz)].add(node_id)

    def remove(self, node_id: str, xyz):
        key = self._cell_key(xyz)
        cell = self._cells.get(key)
        if not cell:
            return

        cell.remove(node_id)
        if not cell:
            del self._cells[key]

    def move(self, node_id: str, old_xyz, new_xyz):
        self.remove(node_id, old_xyz)
        self.insert(node_id, new_xyz)

    def find_near(self, xyz, nodes: dict):
        """
        Returns node_id if a node is within tolerance.
        """
        key = self._cell_key(xyz)

        for node_id in self._cells.get(key, []):
            node = nodes[node_id]
            if distance(node.xyz, xyz) <= self.tol:
                return node_id

        return None

    def clear(self):
        self._cells.clear()
