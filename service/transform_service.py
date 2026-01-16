from domain.model import StructuralModel

class TransformService:
    def move_node(self, model: StructuralModel, node_id, dx, dy, dz):
        node = model.nodes[node_id]
        new_xyz = (
            node.xyz[0] + dx,
            node.xyz[1] + dy,
            node.xyz[2] + dz,
        )
        model.update_node_position(node_id, new_xyz)

    def move_frame(self, model: StructuralModel, frame_id, dx, dy, dz):
        frame = model.frames[frame_id]

        n1 = model.nodes[frame.n1_id]
        n2 = model.nodes[frame.n2_id]

        # 1. Compute destination coordinates
        p1_new = (
            n1.xyz[0] + dx,
            n1.xyz[1] + dy,
            n1.xyz[2] + dz,
        )
        p2_new = (
            n2.xyz[0] + dx,
            n2.xyz[1] + dy,
            n2.xyz[2] + dz,
        )

        # 2. Resolve destination nodes (reuse or create)
        new_n1 = model.get_or_create_node(p1_new)
        new_n2 = model.get_or_create_node(p2_new)

        # 3. Remove old connectivity
        model.delete_frame(frame_id)

        # 4. Create replacement frame
        new_frame = model.create_frame(new_n1.id, new_n2.id)

        return new_frame.id