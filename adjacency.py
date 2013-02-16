from winged_edge import winged_edge_lookup

def build_adjacency_triangles(triangles, mapping, reverse_mapping, edges, position_idx = 0):
    # TODO: This function shouldn't be hard to modify to handle triangle strips and fans
    def adjacent_vertex(a, b):
        ap, bp = [reverse_mapping[x][position_idx] for x in [a, b]]
        nxt, adj = winged_edge_lookup(edges, (ap, bp))
        return mapping[adj[2]]

    for a, b, c in triangles:
        yield (a, adjacent_vertex(a, b), b, adjacent_vertex(b, c), c, adjacent_vertex(c, a))
