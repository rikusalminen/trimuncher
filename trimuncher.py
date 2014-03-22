from sys import stderr
import re

from interleaver import interleave
from winged_edge import winged_edge, winged_edge_fully_connected
from adjacency import build_adjacency_triangles
from polygon import quads2tris
from binaryblob import blob_vertex_save, blob_index_save
from daeloader import daeload

def parse_vertex_format(fmt_string):
    trim = ''.join(c for c in fmt_string if not c.isspace())
    regex = re.compile(r'([A-Z_]+):(\d)([uif])(\d{1,2})?')
    matches = [regex.match(s) for s in trim.split(',')]

    if any(match is None for match in matches):
        stderr.write('Invalid vertex format: %s\n' % fmt_string)
        raise RuntimeError('Invalid vertex format')

    def attr(semantic, count, typ, bits):
        c = int(count)
        t = float if typ == 'f' else int
        s = (typ == 'i')
        b = 32 if bits is None else int(bits)
        pad = tuple([0.0] * c) if semantic != 'POSITION' else \
            tuple(0.0 if i != 3 else 1.0 for i in range(c))
        return (semantic, (c, t, s, b, pad))

    return [attr(*match.groups()) for match in matches]

def vertex_shuffle_order(semantics, fmt):
    order = dict((semantic, idx) for (idx, semantic) in enumerate(semantics))
    return [order[semantic] if semantic in order else None for (semantic, attr) in fmt]

def vertex_shuffle(verts, order):
    if order == range(len(order)):
        return verts
    return [tuple(v[i] if i is not None else () for i in order) for v in verts]

if __name__ == '__main__':
    default_fmt = 'POSITION:3f32,NORMAL:3f32,TEXCOORD:2f32'

    from argparse import ArgumentParser
    parser = ArgumentParser(
        description = """
        Convert 3D Models from collada XML files to vertex buffer binary blobs.
        """
        )
    parser.add_argument('files', metavar='file', nargs='+', type=str, help='Collada XML files')
    parser.add_argument('--adjacency', action='store_true', help='build adjacency indices for geometry shaders')
    parser.add_argument('-f', '--format', metavar='fmt', help='Vertex format', default=default_fmt)
    args = parser.parse_args()

    vertex_format = parse_vertex_format(args.format)

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

            attrs = [attr for (semantic, attr) in vertex_format]

            order = vertex_shuffle_order(semantics, vertex_format)

            if any(idx is None for idx in order):
                missing = (vertex_format[i][0] for (i, idx) in enumerate(order) if idx is None)
                stderr.write('WARNING: missing vertex attributes: %s\n' % ', '.join(missing))

            v = vertex_shuffle(v, order)

            blob_vertex_save('%s.vbo' % name, attrs, v)
            blob_index_save('%s.ibo' % name, i if not adjtri else adjtri)
