from sys import stdin, stdout
from struct import pack, unpack

def float2half(float_val):
    f = unpack('I', pack('f', float_val))
    if f == 0: return 0
    if f == 0x80000000: return 0x8000
    return ((f>>16)&0x8000)|((((f&0x7f800000)-0x38000000)>>13)&0x7c00)|((f>>13)&0x03ff)

def half2float(h):
    if h == 0: return 0
    if h == 0x8000: return 0x80000000
    f = ((h&0x8000)<<16) | (((h&0x7c00)+0x1C000)<<13) | ((h&0x03FF)<<13)
    return unpack('f', pack('I', f))

def blob_pack_vertex_attr((count, typ, signed, bits, padding), v, little_endian = True):
    assert typ is int or typ is float
    assert len(padding) == count
    assert len(v) <= count

    pad = v + padding[len(v):]
    fmt = None

    if typ is float:
        float_fmts = {16: 'H', 32: 'f', 64: 'd'}
        if bits == 16:
            pad = map(float2half, pad)
        fmt = float_fmts[bits]
    else:
        int_fmts = {8: 'b', 16: 'h', 32: 'i', 64: 'q'}
        uint_fmts = {8: 'B', 16: 'H', 32: 'I', 64: 'Q'}
        fmt = int_fmts[bits] if signed else uint_fmts[bits]

    return pack(('<' if little_endian else '>') + fmt * count, *pad)

def blob_vertices(attrs, verts):
    for v in verts:
        for (attr, data) in zip(attrs, v):
            yield blob_pack_vertex_attr(attr, data)

def blob_indices(indices, restart = None):
    for primitive in indices:
        for index in primitive:
            yield pack('H', index)
        if restart is not None:
            yield pack('H', restart)

def blob_vertex_write(attrs, verts, out=stdout):
    for blob in blob_vertices(attrs, verts):
        out.write(blob)

def blob_vertex_save(filename, attrs, verts):
    with open(filename, 'w') as f:
        blob_vertex_write(attrs, verts, f)

def blob_index_write(indices, out=stdout):
    for blob in blob_indices(indices):
        out.write(blob)

def blob_index_save(filename, indices):
    with open(filename, 'w') as f:
        blob_index_write(indices, f)
