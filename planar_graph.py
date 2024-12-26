from point import Point

def get_faces_of_planar_graph(edges:list[tuple[Point, Point]], graph_connections:dict[str:list[Point]]):
    if len(edges) == 1:
        a, b = edges[0]
        assert a == b
        face = [edges[0]]
        faces = [face]
        return faces
    

    
    raise NotImplementedError()


