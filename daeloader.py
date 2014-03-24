import xml.etree.ElementTree as ET

from polygon import *

dae_uri = 'http://www.collada.org/2005/11/COLLADASchema'
def dae(tag): return ET.QName(dae_uri, tag)

def attribtype(typ):
    if typ == 'float': return float
    if typ == 'int': return int
    assert not 'supported attribute type'

def process_source(source):
    identifier = source.attrib['id']

    # NOTE: this does not do proper linking of accessors and source arrays based on "id" xml attributes
    accessor = source.find('%s/%s' % (dae('technique_common'), dae('accessor')))
    count = int(accessor.attrib['count'])
    stride = int(accessor.attrib['stride']) if 'stride' in accessor.attrib else 1
    offset = int(accessor.attrib['offset']) if 'offset' in accessor.attrib else 0
    params = [(param.attrib['name'], param.attrib['type']) for param in accessor.findall('%s' % dae('param'))]

    arrays = [(element.attrib['count'], element.text.split()) for element in source if element.tag[-6:] == '_array']
    assert len(arrays) == 1
    strings = arrays[0][1]

    data = [
        tuple(attribtype(typ)(strings[i + index * stride + offset]) for (i, (name, typ)) in enumerate(params))
            for index in range(count)]

    return (identifier, (params, data))

primitive_names = ['triangles', 'trifans', 'tristrips', 'polygons', 'polylist', 'lines', 'linestrips']

def to_primitives(primname, groups):
    if primname == 'triangles' or primname == 'lines': return groups
    if primname == 'polylist': return polys2tris(groups)
    assert not 'supported primitive type'

def process_primitives(element):
    # TODO: this only works for a few primitive types at the moment
    primname = element.tag[element.tag.index('}')+1:]
    assert primname in primitive_names

    count = int(element.attrib['count'])
    material = element.attrib['material'] if 'material' in element.attrib else ''

    def semantic_name(e):
        if 'set' in e.attrib:
            return e.attrib['semantic'] + e.attrib['set']
        return e.attrib['semantic'] + ('0' if e.attrib['semantic'][0:3] == 'TEX' else '')

    inputs = [(semantic_name(e), (int(e.attrib['offset']), e.attrib['source'][1:]))
                    for e in element.findall('%s' % dae('input'))]
    stride = 1 + max(offset for (semantic, (offset, source)) in inputs)

    vcounts = element.find('%s' % dae('vcount'))
    vcounts = map(int, vcounts.text.split()) if vcounts is not None else None
    # TODO: handle primitive types better

    p = map(int, element.find('%s' % dae('p')).text.split())
    assert len(p) % stride == 0

    def index_tuple(tup):
        return tuple(tup[offset] for (semantic, (offset, source)) in inputs)

    tuples = [index_tuple(p[i*stride:(i+1)*stride]) for i in range(len(p)/stride)]

    def group_by_vcount():
        idx = 0
        for num in vcounts:
            yield tuple(tuples[idx:idx+num])
            idx += num

    def group_by_primitive():
        n = 3 if primtype == 'triangles' else 2 if 'lines' else None # TODO: better grouping
        return (tuple(tuples[i*n:(i+1)*n]) for i in range(len(tuples)/n))

    groups = list(group_by_vcount()) if vcounts else list(group_by_primitive())

    tris_or_lines = list(to_primitives(primname, groups))

    return material, inputs, tris_or_lines

def process_geom(geom):
    name = geom.attrib['name'] if 'name' in geom.attrib else 'mesh'
    mesh = geom.find('%s' % dae('mesh'))
    sources = dict(map(process_source, mesh.findall('%s' % dae('source'))))
    prims = [process_primitives(element) for element in mesh if (element.tag[element.tag.index('}')+1:] in primitive_names)]
    assert len(prims) == 1 # TODO: handle many geometry batches

    vert_id = mesh.find('%s' % dae('vertices')).attrib['id']
    vert_inputs = mesh.findall('%s/%s' % (dae('vertices'), dae('input')))
    assert(len(vert_inputs) == 1) # NOTE: spec allows 1 or more inputs but what to do with the others?
    vert_pos = mesh.find('%s/%s[@semantic=\'POSITION\']' % (dae('vertices'), dae('input')))
    vert_pos_source = vert_pos.attrib['source'][1:]

    inputs = prims[0][1]

    semantics = tuple(semantic if semantic != 'VERTEX' else 'POSITION' for (semantic, (index, source)) in inputs)
    verts = tuple(sources[source if semantic != 'VERTEX' else vert_pos_source][1] for (semantic, (index, source)) in inputs)
    position_idx = [index for (semantic, (index, source)) in inputs if semantic == 'VERTEX'][0]
    indices = prims[0][2]

    return (name, (semantics, position_idx, verts, indices))

def process_geoms(collada):
    return (process_geom(geom) for geom in collada.findall('./%s/%s[%s]' % (dae('library_geometries'), dae('geometry'), dae('mesh'))))

def daeload(filename):
    return process_geoms(ET.parse(filename).getroot())
