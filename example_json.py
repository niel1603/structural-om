from domain.model import StructuralModel

model = StructuralModel()

# Save model to JSON

# f1 = model.add_frame_by_coord((0, 0, 0), (5, 0, 0))
# f2 = model.add_frame_by_coord((5, 0, 0), (5, 3, 0))
# f3 = model.add_frame_by_coord((0, 0, 0), (0, 3, 0))
# f4 = model.add_frame_by_coord((0, 3, 0), (5, 3, 0))

# model.save_json("portal_frame.json")

#Load model from JSON

loaded_model = StructuralModel.load_json("portal_frame.json")

loaded_model.update_node_position(
    node_id="N4",
    new_xyz=(6, 3, 0)
)

loaded_model.save_json("portal_frame_after_move.json")