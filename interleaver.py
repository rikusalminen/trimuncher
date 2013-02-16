def interleave(vertices, indices):
    unique = set(sum(indices, ()))
    mapping = dict((x, i) for (i, x) in enumerate(unique))
    reverse_mapping = dict((i, idx_tuple) for (idx_tuple, i) in mapping.iteritems())

    return (
        mapping,
        reverse_mapping,
        [tuple(vertices[i][idx] for (i, idx) in enumerate(idx_tuple)) for idx_tuple in unique],
        [tuple(mapping[idx_tuple] for idx_tuple in primitive) for primitive in indices])
