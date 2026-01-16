import heapq

class IdPool:
    """
    ETABS-style ID allocator with free-id reuse.
    Deterministic, compact, transactional-friendly.
    """

    def __init__(self, start: int = 1):
        self._next_id: int = start
        self._free_ids: list[int] = []   # min-heap
        self._in_use: set[int] = set()   # safety + debugging

    def allocate(self) -> str:
        if self._free_ids:
            i = heapq.heappop(self._free_ids)
        else:
            i = self._next_id
            self._next_id += 1

        self._in_use.add(i)
        return str(i)

    def release(self, id_: str):
        i = int(id_)
        if i not in self._in_use:
            raise ValueError(f"ID {i} not allocated")

        self._in_use.remove(i)
        heapq.heappush(self._free_ids, i)

    # ----------------------------
    # Persistence / recovery
    # ----------------------------

    def rebuild_from_existing(self, existing_ids: list[str]):
        ints = sorted(int(i) for i in existing_ids)
        self._in_use = set(ints)

        if not ints:
            self._next_id = 1
            self._free_ids.clear()
            return

        self._next_id = max(ints) + 1

        self._free_ids = [
            i for i in range(1, self._next_id)
            if i not in self._in_use
        ]
        heapq.heapify(self._free_ids)

        