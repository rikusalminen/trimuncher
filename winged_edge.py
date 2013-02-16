def winged_edge(triangles, position_idx = 0):
    edges = {}

    def edge(idx, nxt, adj):
        forward = idx < nxt
        pair = (min(idx, nxt), max(idx, nxt))
        prev = edges[pair] if pair in edges else (None, None)
        assert prev[0 if forward else 1] is None
        edges[pair] = (adj, prev[1]) if forward else (prev[0], adj)

    def pos(idx):
        return idx[position_idx] if position_idx is not None else idx

    for a, b, c in triangles:
        edge(pos(a), pos(b), (a, b, c))
        edge(pos(b), pos(c), (b, c, a))
        edge(pos(c), pos(a), (c, a, b))

    return edges

def winged_edge_lookup(edges, (a, b)):
    if a < b:
        return edges[(a, b)]
    else:
        x, y = edges[(b, a)]
        return (y, x)

def winged_edge_fully_connected(edges):
    return all(x is not None and y is not None for (x, y) in edges.itervalues())
