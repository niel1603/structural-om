from domain.model import StructuralModel

class ReplicationService:
    def replicate_node(self, model: StructuralModel, node_id, dx, dy, dz):
        node = model.nodes.get(node_id)
        new_xyz = (
            node.xyz[0] + dx,
            node.xyz[1] + dy,
            node.xyz[2] + dz,
        )
        return model.nodes.create(xyz=new_xyz)

    def replicate_frame(self, model: StructuralModel, frame_id, dx, dy, dz):
        frame = model.frames.get(frame_id)

        n1 = model.nodes.get(frame.n1_id)
        n2 = model.nodes.get(frame.n2_id)

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

        new_n1 = model.nodes.create(xyz=p1_new)
        new_n2 = model.nodes.create(xyz=p2_new)

        return model.frames.create(n1_id=new_n1.id, n2_id=new_n2.id)