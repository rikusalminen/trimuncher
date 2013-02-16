def quads2tris(quads):
    for a, b, c, d in quads:
        yield (a, b, d)
        yield (d, b, c)
