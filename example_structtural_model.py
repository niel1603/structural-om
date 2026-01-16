from domain.model import StructuralModel

from service.transform_service import TransformService
from service.replication_service import ReplicationService

model = StructuralModel()

# Add frame by coord

# f1 = model.add_frame_by_coord((0, 0, 0), (0, 0, 3))
# f2 = model.add_frame_by_coord((0, 0, 3), (3, 0, 3))

# n = model.nodes["N2"]
# print(n.connected_frames)
# # {'F1', 'F2'}

# Move and replicate

model = StructuralModel()

# create a simple vertical frame
f1 = model.add_frame_by_coord(
    (0, 0, 0),
    (0, 0, 3),
)

print(f1.id)      # F1
print(model.nodes)
print(model.frames)

TransformService().move_node(
    model,
    node_id="N2",
    dx=0,
    dy=0,
    dz=1,
)

new_node_id = ReplicationService().replicate_node(
    model,
    node_id="N1",
    dx=3,
    dy=0,
    dz=0,
)

print(new_node_id)  # N3

new_frame_id = TransformService().move_frame(
    model,
    frame_id="F1",
    dx=3,
    dy=0,
    dz=0,
)

print(new_frame_id)  # F2

copied_frame_id = ReplicationService().replicate_frame(
    model,
    frame_id="F2",
    dx=0,
    dy=3,
    dz=0,
)

print(copied_frame_id)  # F3
