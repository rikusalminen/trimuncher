from sys import stderr

from interleaver import interleave
from winged_edge import winged_edge, winged_edge_fully_connected
from adjacency import build_adjacency_triangles
from polygon import quads2tris
from binaryblob import blob_vertex_save, blob_index_save
from daeloader import daeload

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('files', metavar='file', nargs='+', type=str, help='Collada XML files')
    parser.add_argument('--adjacency', action='store_true', help='build adjacency indices for geometry shaders')
    args = parser.parse_args()

    for filename in args.files:
        geoms = daeload(filename)
        for (name, (semantics, position_idx, vertices, indices)) in geoms:
            prim_verts = len(indices[0]) # 1 for points, 2 for lines, 3 for triangles
            assert prim_verts == 3 # TODO: handle points and lines

            mapping, reverse_mapping, v, i = interleave(vertices, indices)

            adjtri = None
            if args.adjacency:
                edges = winged_edge(indices, position_idx)
                if not winged_edge_fully_connected(edges):
                    stderr.write('Mesh not fully connected, not building adjacency')
                else:
                    adjtri = list(build_adjacency_triangles(i, mapping, reverse_mapping, edges))

            attrs = [ # TODO: do not hard code vertex attributes
                (4, float, False, 32, (0.0, 0.0, 0.0, 1.0)),
                (4, float, False, 32, tuple([0.0] * 4))
                ]

            blob_vertex_save('%s.vbo' % name, attrs, v)
            blob_index_save('%s.ibo' % name, i if not adjtri else adjtri)
