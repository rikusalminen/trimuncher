def quads2tris(quads):
    for a, b, c, d in quads:
        yield (a, b, d)
        yield (d, b, c)

def strips2tris(strips):
    for strip in strips:
        edge = tuple(strip[0:2])
        odd = False
        for vertex in strip[2:]:
            yield (edge[0], edge[1], vertex)
            edge = (vertex, edge[1]) if not odd else (edge[0], vertex)
            odd = not odd

def poly2strip(poly):
    assert len(poly) >= 3

    def strip(top, bottom):
        odd = False
        while top or bottom:
            yield (bottom if odd else top).pop()
            odd = not odd

    mid = len(poly)/2
    return [poly[0]] + list(strip(list(reversed(poly[1:mid+1])), list(poly[mid+1:])))


def polys2tris(polys):
    return strips2tris(map(poly2strip, polys))
