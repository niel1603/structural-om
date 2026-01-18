from structural_om.domain.id_pool import IdPool
from structural_om.domain.objects.nodes import Nodes
from structural_om.domain.objects.object import Frame

class Frames:
    def __init__(self):
        self._frames: dict[str, Frame] = {}
        self.ids = IdPool()

    # ---------- access ----------

    def get(self, frame_id: str) -> Frame:
        return self._frames[frame_id]

    def all(self) -> dict[str, Frame]:
        return self._frames

    # ---------- creation ----------

    # def create_by_nodes(self, n1: Node, n2: Node) -> Frame:
    #     if n1.id == n2.id:
    #         raise ValueError("Frame cannot connect a node to itself")

    #     frame_id = self.ids.allocate()
    #     frame = Frame(frame_id, n1.id, n2.id)

    #     self._frames[frame_id] = frame
    #     n1.connected_frames.add(frame_id)
    #     n2.connected_frames.add(frame_id)

    #     return frame

    # def create_by_ids(self, nodes: Nodes, n1_id: str, n2_id: str) -> Frame:
    #     return self.create_by_nodes(
    #         nodes.get(n1_id),
    #         nodes.get(n2_id),
    #     )

    def create(
        self,
        nodes: Nodes,
        *,
        n1_id: str,
        n2_id: str,
        frame_id: str | None = None,
    ) -> Frame:
        """
        Create a frame.

        - frame_id=None → normal creation
        - frame_id=...  → rebuild creation
        """

        if n1_id == n2_id:
            raise ValueError("Frame cannot connect a node to itself")

        if frame_id is None:
            frame_id = self.ids.allocate()
        else:
            # rebuild path
            if frame_id in self._frames:
                raise RuntimeError(f"Duplicate frame_id '{frame_id}'")
            self.ids._in_use.add(int(frame_id))

        frame = Frame(frame_id, n1_id, n2_id)
        self._frames[frame_id] = frame

        nodes.get(n1_id).connected_frames.add(frame_id)
        nodes.get(n2_id).connected_frames.add(frame_id)

        return frame

    # ---------- deletion ----------

    def delete(self, nodes: Nodes, frame_id: str):
        frame = self._frames[frame_id]

        nodes.get(frame.n1_id).connected_frames.remove(frame_id)
        nodes.get(frame.n2_id).connected_frames.remove(frame_id)

        self.ids.release(frame_id)
        del self._frames[frame_id]

    # ---------- clear ----------

    def clear(self):
        self._frames.clear()
        self.ids = IdPool()

