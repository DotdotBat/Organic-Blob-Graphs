from point import Point

 



def get_faces_of_planar_graph(edges:list[tuple[Point, Point]])->list[list[Point]]:
    if len(edges) == 2:
        A, B = edges[0]
        b, a = edges[1]
        assert A==a
        assert B == b
        face = [A, B]
        faces = [face]
        return faces    
    
    points = dict()
    adjacency = dict()
    for A, B in edges:
        assert type(A) == Point
        points[id(A)] = A
        points[id(B)] = B
    for i in points:
        adjacency[i] = []

    for A, B in edges:
        a,b = id(A), id(B)
        adjacency[a].append(b)
        adjacency[b].append(a)
    
    faces = face_traversal(points, adjacency)
    return faces

import math

def face_traversal(points, adj):
    """
    Finds all the inner faces of a connected planar graph.

    Parameters:
    - points: dict mapping id(Point) to Point instance.
    - adj: dict mapping id(Point) to list of ids of adjacent Points.

    Returns:
    - faces: list of faces, each face is a list of Point instances.
    """
    epsilon = 1e-9  # Tolerance for floating-point comparisons

    # Initialize the used dictionary to keep track of traversed edges
    used = initialize_used(adj)

    # Sort adjacency lists counter-clockwise for each vertex
    sort_all_adjacency_lists(points, adj)

    faces = []  # List to store the inner faces

    # Main traversal algorithm
    for u in adj.keys():
        for i in range(len(adj[u])):
            if used[u][i]:
                continue  # Edge already used in this direction

            # Trace out a face starting from edge (u, adj[u][i])
            face_vertices = trace_face(u, i, adj, used)

            # Convert vertex ids to Point instances
            face_points = [points[vid] for vid in face_vertices]

            # Determine if the face is an inner face based on its orientation
            if is_inner_face(face_points, epsilon):
                faces.append(face_points)

    return faces


def initialize_used(adj):
    """
    Initializes the 'used' dictionary to keep track of traversed edges.

    Parameters:
    - adj: dict mapping vertex ids to lists of adjacent vertex ids.

    Returns:
    - used: dict mapping vertex ids to lists of booleans indicating edge usage.
    """
    used = {}
    for u in adj.keys():
        used[u] = [False] * len(adj[u])
    return used


def sort_all_adjacency_lists(points, adj):
    """
    Sorts the adjacency lists of all vertices in counter-clockwise order.

    Parameters:
    - points: dict mapping vertex ids to Point instances.
    - adj: dict mapping vertex ids to lists of adjacent vertex ids.
    """
    for u in adj.keys():
        adj[u] = sort_adjacency_list(u, points, adj)


def sort_adjacency_list(u, points, adj):
    """
    Sorts the adjacency list of a single vertex in counter-clockwise order.

    Parameters:
    - u: id of the vertex whose adjacency list is to be sorted.
    - points: dict mapping vertex ids to Point instances.
    - adj: dict mapping vertex ids to lists of adjacent vertex ids.

    Returns:
    - sorted_adj_list: list of adjacent vertex ids sorted counter-clockwise.
    """
    p_u = points[u].co  # Coordinates of vertex u
    adj_list = adj[u]   # List of adjacent vertex ids

    # Compute the angle for each adjacent vertex
    adj_angle_list = []
    for v in adj_list:
        angle = compute_angle(p_u, points[v].co)
        adj_angle_list.append((angle, v))

    # Sort the adjacency list by angle
    adj_angle_list.sort()
    sorted_adj_list = [v for (angle, v) in adj_angle_list]

    return sorted_adj_list


def compute_angle(p_u, p_v):
    """
    Computes the angle between vertex u and vertex v relative to the positive x-axis.

    Parameters:
    - p_u: Vector2 coordinates of vertex u.
    - p_v: Vector2 coordinates of vertex v.

    Returns:
    - angle: Angle in radians in the range [0, 2π).
    """
    vec = p_v - p_u
    angle = math.atan2(vec.y, vec.x)
    if angle < 0:
        angle += 2 * math.pi  # Normalize angle to [0, 2π)
    return angle


def trace_face(u_start, i_start, adj, used):
    """
    Traces out a face starting from a given edge.

    Parameters:
    - u_start: Starting vertex id.
    - i_start: Index of the starting edge in adj[u_start].
    - points: dict mapping vertex ids to Point instances.
    - adj: dict mapping vertex ids to lists of adjacent vertex ids.
    - used: dict tracking which edges have been traversed.

    Returns:
    - face_vertices: List of vertex ids forming the face.
    """
    face = []
    u = u_start
    i = i_start

    while True:
        used[u][i] = True
        assert u not in face
        face.append(u)

        v = adj[u][i]
        idx_v_u = find_adjacent_index(v, u, adj)

        # Move to the next edge counter-clockwise around v
        i = (idx_v_u + 1) % len(adj[v])

        if v == u_start and i == i_start:
            break  # Completed a face

        u = v

    return face


def find_adjacent_index(u, v, adj):
    """
    Finds the index of vertex v in u's adjacency list.

    Parameters:
    - u: Vertex id whose adjacency list is searched.
    - v: Vertex id to find in u's adjacency list.
    - adj: dict mapping vertex ids to lists of adjacent vertex ids.

    Returns:
    - idx: Index of v in adj[u].

    Raises:
    - Exception: If v is not found in adj[u].
    """
    try:
        idx = adj[u].index(v)
    except ValueError:
        raise ValueError(f"Graph is not properly connected: vertex {v} not found in adj[{u}].")
    return idx


def is_inner_face(face_points, epsilon):
    """
    Determines if a face is an inner face based on its orientation.

    Parameters:
    - face_points: List of Point instances forming the face.
    - epsilon: Small number for floating-point tolerance.

    Returns:
    - inner: True if the face is an inner face (clockwise orientation), False otherwise.
    """
    area = compute_signed_area(face_points)
    return area < -epsilon


def compute_signed_area(face_points):
    """
    Computes the signed area of a polygon defined by face_points.

    Parameters:
    - face_points: List of Point instances forming the polygon.

    Returns:
    - area: Signed area of the polygon.
    """
    area = 0.0
    n = len(face_points)
    for j in range(n):
        xi, yi = face_points[j].co.x, face_points[j].co.y
        xj, yj = face_points[(j + 1) % n].co.x, face_points[(j + 1) % n].co.y
        area += xi * yj - xj * yi
    area /= 2.0
    return area