class Node:
    def __init__(self, id: str, xyz: tuple[float, float, float]):
        self.id = id
        self.xyz = xyz
        self.connected_frames: set[str] = set()

class Frame:
    def __init__(self, id: str, n1_id: str, n2_id: str):
        self.id = id
        self.n1_id = n1_id
        self.n2_id = n2_id