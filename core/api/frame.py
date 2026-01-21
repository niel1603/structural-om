from collections.abc import Iterator
from structural_om.core.id_pool import IdPool
from structural_om.core.api.node import NodeObj
from structural_om.core.object import Node, Frame

class FrameObj:
    def __init__(self):
        self._frames: dict[str, Frame] = {}
        self.ids = IdPool()

    @property
    def frames(self) -> dict[str, Frame]:
        return self._frames

    # ---------- clear ----------

    def clear(self, nodes: NodeObj | None = None):
        """
        Clear all frames.
        Optionally detaches frames from nodes.
        """
        if nodes is not None:
            for frame in self._frames.values():
                nodes.get(frame.n1_id).connected_frames.discard(frame.id)
                nodes.get(frame.n2_id).connected_frames.discard(frame.id)

        self._frames.clear()
        self.ids = IdPool()

    # ---------- access ----------

    def __len__(self) -> int:
        return len(self._frames)

    def __contains__(self, frame_id: str) -> bool:
        return frame_id in self._frames

    def __getitem__(self, frame_id: str) -> Frame:
        return self._frames[frame_id]

    def __iter__(self) -> Iterator[Frame]:
        return iter(self._frames.values())

    def get(self, frame_id: str, default: Frame | None = None) -> Frame | None:
        return self._frames.get(frame_id, default)

    def items(self):
        return self._frames.items()

    def values(self):
        return self._frames.values()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({len(self)} frames)"
    
    # ---------- creation ----------

    def create(
        self,
        nodes: NodeObj,
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
    
    # ---------- mutation ----------

    def move(
        self,
        *,
        node_obj: NodeObj,
        frame_id: str,
        direction: tuple[float, float, float],
    ) -> Frame:
        """
        Move a frame by a vector.

        - If a destination node already exists (within tolerance), reuse it
        - Otherwise, create a new node
        - Does NOT move nodes that are shared with other frames
        """

        frame = self._frames[frame_id]
        dx, dy, dz = direction

        # original nodes
        n1 = node_obj[frame.n1_id]
        n2 = node_obj[frame.n2_id]

        # destination coordinates
        n1_new_xyz = (n1.xyz[0] + dx, n1.xyz[1] + dy, n1.xyz[2] + dz)
        n2_new_xyz = (n2.xyz[0] + dx, n2.xyz[1] + dy, n2.xyz[2] + dz)

        # find or create destination nodes
        new_n1 = node_obj.create(xyz=n1_new_xyz)
        new_n2 = node_obj.create(xyz=n2_new_xyz)

        # reconnect frame
        old_n1_id = frame.n1_id
        old_n2_id = frame.n2_id

        frame.n1_id = new_n1.id
        frame.n2_id = new_n2.id

        # update connectivity
        node_obj[old_n1_id].connected_frames.remove(frame_id)
        node_obj[old_n2_id].connected_frames.remove(frame_id)

        new_n1.connected_frames.add(frame_id)
        new_n2.connected_frames.add(frame_id)

        # clean up orphaned nodes
        for old_id in (old_n1_id, old_n2_id):
            old_node = node_obj[old_id]
            if not old_node.connected_frames:
                node_obj.delete(old_id)

        return frame
        
    def set_location(
        self,
        *,
        nodes: NodeObj,
        frame_id: str,
        location: tuple[float, float, float],
    ) -> Frame:
        """
        Set frame location by moving its midpoint to `location`.

        - Reuses existing destination nodes if found
        - Creates new nodes otherwise
        - Does NOT move shared nodes
        """

        frame = self._frames[frame_id]

        # original nodes
        n1 = nodes[frame.n1_id]
        n2 = nodes[frame.n2_id]

        # current midpoint
        mid = tuple((a + b) / 2 for a, b in zip(n1.xyz, n2.xyz))

        # translation vector
        dx = location[0] - mid[0]
        dy = location[1] - mid[1]
        dz = location[2] - mid[2]

        # destination coordinates
        n1_new_xyz = (n1.xyz[0] + dx, n1.xyz[1] + dy, n1.xyz[2] + dz)
        n2_new_xyz = (n2.xyz[0] + dx, n2.xyz[1] + dy, n2.xyz[2] + dz)

        # find or create destination nodes
        new_n1 = nodes.create(xyz=n1_new_xyz)
        new_n2 = nodes.create(xyz=n2_new_xyz)

        # reconnect frame
        old_n1_id = frame.n1_id
        old_n2_id = frame.n2_id

        frame.n1_id = new_n1.id
        frame.n2_id = new_n2.id

        # update connectivity
        nodes[old_n1_id].connected_frames.remove(frame_id)
        nodes[old_n2_id].connected_frames.remove(frame_id)

        new_n1.connected_frames.add(frame_id)
        new_n2.connected_frames.add(frame_id)

        # clean up orphaned nodes
        for old_id in (old_n1_id, old_n2_id):
            old_node = nodes[old_id]
            if not old_node.connected_frames:
                nodes.delete(old_id)

        return frame

    # ---------- deletion ----------

    def delete(self, nodes: NodeObj, frame_id: str):
        frame = self._frames[frame_id]

        nodes.get(frame.n1_id).connected_frames.remove(frame_id)
        nodes.get(frame.n2_id).connected_frames.remove(frame_id)

        self.ids.release(frame_id)
        del self._frames[frame_id]

    # ---------- replicate ----------

    def replicate(
        self,
        *,
        nodes: NodeObj,
        frames: 'FrameObj',
        src_frame_ids: list[str],
        delta: tuple[float, float, float],
        count: int,
    ) -> tuple[list[list[Frame]], list[list[Node]]]:
        """
        Replicate frames along a vector.

        Returns:
            A list of batches.
            Each batch corresponds to one step.
            Each batch contains frames in src_frame_ids order.
        """

        # collect unique source node ids (preserve order)
        src_node_ids: list[str] = []
        seen = set()

        for fid in src_frame_ids:
            frame = frames[fid]
            for nid in (frame.n1_id, frame.n2_id):
                if nid not in seen:
                    seen.add(nid)
                    src_node_ids.append(nid)

        # replicate nodes first
        node_batches = nodes.replicate(
            src_node_ids=src_node_ids,
            delta=delta,
            count=count,
        )

        # map src node id -> index
        node_index = {nid: i for i, nid in enumerate(src_node_ids)}

        frame_batches: list[list[Frame]] = []

        # replicate frames per batch
        for batch in node_batches:
            frames_in_step: list[Frame] = []

            for fid in src_frame_ids:
                src_frame = frames[fid]

                new_n1 = batch[node_index[src_frame.n1_id]].id
                new_n2 = batch[node_index[src_frame.n2_id]].id

                frame = frames.create(
                    nodes,
                    n1_id=new_n1,
                    n2_id=new_n2,
                )

                frames_in_step.append(frame)

            frame_batches.append(frames_in_step)

        return [frame_batches, node_batches]
