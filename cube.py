cube_vertices = [
    (  1.0,  1.0,  1.0),
    ( -1.0,  1.0,  1.0),
    (  1.0, -1.0,  1.0),
    ( -1.0, -1.0,  1.0),
    (  1.0,  1.0, -1.0),
    ( -1.0,  1.0, -1.0),
    (  1.0, -1.0, -1.0),
    ( -1.0, -1.0, -1.0),
    ]

cube_normals = [
    ( 1.0,  0.0,  0.0),
    ( 0.0,  1.0,  0.0),
    ( 0.0,  0.0,  1.0),
    (-1.0,  0.0,  0.0),
    ( 0.0, -1.0,  0.0),
    ( 0.0,  0.0, -1.0),
    ]

cube_tangents = [
    (  0.0,   0.0,  -1.0),
    ( -1.0,   0.0,   0.0),
    (  0.0,  -1.0,   0.0),
    (  0.0,   0.0,  -1.0),
    ( -1.0,   0.0,   0.0),
    (  0.0,  -1.0,   0.0),

    ]

cube_texcoords = [
    (0.0, 0.0),
    (0.0, 1.0),
    (1.0, 0.0),
    (1.0, 1.0),
    ]

cube_faces = [
    (
        (0, 0, 0, 0),
        (2, 0, 0, 1),
        (6, 0, 0, 3),
        (4, 0, 0, 2),
    ),
    (
        (0, 1, 1, 0),
        (4, 1, 1, 1),
        (5, 1, 1, 3),
        (1, 1, 1, 2),
    ),
    (
        (0, 2, 2, 0),
        (1, 2, 2, 1),
        (3, 2, 2, 3),
        (2, 2, 2, 2),
    ),
    (
        (3, 3, 3, 0),
        (1, 3, 3, 1),
        (5, 3, 3, 3),
        (7, 3, 3, 2),
    ),
    (
        (6, 4, 4, 0),
        (2, 4, 4, 1),
        (3, 4, 4, 3),
        (7, 4, 4, 2),
    ),
    (
        (5, 5, 5, 0),
        (4, 5, 5, 1),
        (6, 5, 5, 3),
        (7, 5, 5, 2)
    )]

if __name__ == '__main__':
    from interleaver import *
    from winged_edge import *
    from adjacency import *
    from polygon import *
    from binaryblob import *

    tris = list(quads2tris(cube_faces))
    mapping, reverse_mapping, v, i = interleave((cube_vertices, cube_normals, cube_tangents, cube_texcoords), tris)

    edges = winged_edge(tris)
    adjtri = list(build_adjacency_triangles(i, mapping, reverse_mapping, edges))

    attrs = [
        (4, float, False, 32, (0.0, 0.0, 0.0, 1.0)),
        (4, float, False, 32, tuple([0.0] * 4)),
        (4, float, False, 32, tuple([0.0] * 4)),
        (4, float, False, 32, tuple([0.0] * 4))
        ]

    blob_vertex_save('cube.vbo', attrs, v)
    blob_index_save('cube.ibo', adjtri)
