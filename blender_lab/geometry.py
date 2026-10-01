"""Bounded, editable Geometry Nodes and mesh-authoring experiments."""
import math
from array import array
import bmesh
import bpy
from mathutils import Vector


def _check(condition, message):
    if not condition:
        raise AssertionError(message)


def _tag(obj, role):
    obj["geometry_role"] = role
    return obj


def _role(scene, role):
    matches = [obj for obj in scene.objects if obj.get("geometry_role") == role]
    if len(matches) != 1:
        raise AssertionError(f"Expected one geometry role {role!r}; found {len(matches)}")
    return matches[0]


def _object(scene, name, vertices, faces, role, location=(0, 0, 0)):
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    obj.location = location
    return _tag(obj, role)


def _material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.82
    return mat


def _scene_token(scene):
    return str(scene.get("blender_lab_instance_id", scene.name))


def _cube_mesh(half):
    x, y, z = half
    vertices = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
                (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return vertices, faces


def _new_node(tree, kind, name, location):
    node = tree.nodes.new(kind)
    node.label = name
    node.location = location
    return node


def _gn_modifier(obj, name, graph):
    mod = obj.modifiers.new(name, 'NODES')
    mod.node_group = graph
    return mod


def _new_graph(name):
    graph = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    graph.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    graph.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    return graph


def _scatter_graph(obj, source, density, seed):
    graph = _new_graph("Scatter / surface distribution")
    nodes, links = graph.nodes, graph.links
    inp = _new_node(graph, 'NodeGroupInput', "Terrain", (-700, 100))
    out = _new_node(graph, 'NodeGroupOutput', "Realized export geometry", (600, 100))
    distribute = _new_node(graph, 'GeometryNodeDistributePointsOnFaces', "Seeded surface points", (-450, 150))
    distribute.inputs['Density'].default_value = density
    distribute.inputs['Seed'].default_value = seed
    info = _new_node(graph, 'GeometryNodeObjectInfo', "Original hex reed", (-450, -140))
    info.inputs['Object'].default_value = source
    info.transform_space = 'ORIGINAL'
    instance = _new_node(graph, 'GeometryNodeInstanceOnPoints', "Instance on surface points", (-130, 160))
    instance.inputs['Pick Instance'].default_value = False
    realize = _new_node(graph, 'GeometryNodeRealizeInstances', "Explicit evaluated/export boundary", (120, 160))
    join = _new_node(graph, 'GeometryNodeJoinGeometry', "Terrain plus realized reeds", (360, 100))
    links.new(inp.outputs['Geometry'], distribute.inputs['Mesh'])
    links.new(distribute.outputs['Points'], instance.inputs['Points'])
    links.new(info.outputs['Geometry'], instance.inputs['Instance'])
    links.new(instance.outputs['Instances'], realize.inputs['Geometry'])
    links.new(inp.outputs['Geometry'], join.inputs['Geometry'])
    links.new(realize.outputs['Geometry'], join.inputs['Geometry'])
    links.new(join.outputs['Geometry'], out.inputs['Geometry'])
    _gn_modifier(obj, "Seeded surface scatter", graph)


def _build_scatter(scene):
    # A small, triangulated 4 x 4 terrain; the source remains a separate mesh object.
    verts = []
    for j in range(5):
        for i in range(5):
            x, y = -1.5 + i * .75, -1.5 + j * .75
            verts.append((x, y, .07 * math.sin(i * .9) * math.cos(j * .7)))
    faces = []
    for j in range(4):
        for i in range(4):
            a = j * 5 + i
            faces.extend(((a, a + 1, a + 6), (a, a + 6, a + 5)))
    terrain = _object(scene, "Scatter / original terrain", verts, faces, 'scatter_surface')
    terrain.data.materials.append(_material("Scatter / deep teal", (.045, .26, .24)))
    outline = [(-.15, -.11), (.0, -.19), (.15, -.11), (.15, .11), (.0, .19), (-.15, .11)]
    source_verts = [(x, y, z) for z in (0, .42) for x, y in outline]
    n = len(outline)
    source_faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    source_faces.extend((i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n))
    source = _object(scene, "Scatter / hex reed source", source_verts, source_faces, 'scatter_source')
    source.data.materials.append(_material("Scatter / copper reed", (.76, .31, .09)))
    source.hide_render = True
    source.display_type = 'WIRE'
    _scatter_graph(terrain, source, 4, 17)
    return terrain


def _field_graph(obj, domain, threshold):
    graph = _new_graph("Field inspector / domain transfer")
    nodes, links = graph.nodes, graph.links
    inp = _new_node(graph, 'NodeGroupInput', "Asymmetric wedge grid", (-760, 100))
    out = _new_node(graph, 'NodeGroupOutput', "Inspectable mesh attributes", (780, 100))
    named = _new_node(graph, 'GeometryNodeInputNamedAttribute', "Known point samples", (-550, -100))
    named.data_type = 'FLOAT'
    named.inputs['Name'].default_value = "ProbeValue"
    transfer = _new_node(graph, 'GeometryNodeFieldOnDomain', "Evaluate on selected domain", (-300, -80))
    transfer.data_type = 'FLOAT'
    transfer.domain = domain
    links.new(named.outputs['Attribute'], transfer.inputs['Value'])
    store = _new_node(graph, 'GeometryNodeStoreNamedAttribute', "Store transferred scalar", (0, 150))
    store.data_type = 'FLOAT'
    store.domain = domain
    store.inputs['Name'].default_value = "DomainSample"
    links.new(inp.outputs['Geometry'], store.inputs['Geometry'])
    links.new(transfer.outputs['Value'], store.inputs['Value'])
    compare = _new_node(graph, 'ShaderNodeMath', "Threshold selection", (-80, -170))
    compare.operation = 'GREATER_THAN'
    compare.inputs[1].default_value = threshold
    links.new(transfer.outputs['Value'], compare.inputs[0])
    selection = _new_node(graph, 'GeometryNodeStoreNamedAttribute', "Store threshold mask", (410, 150))
    selection.data_type = 'BOOLEAN'
    selection.domain = domain
    selection.inputs['Name'].default_value = "AboveThreshold"
    links.new(store.outputs['Geometry'], selection.inputs['Geometry'])
    links.new(compare.outputs[0], selection.inputs['Value'])
    links.new(selection.outputs['Geometry'], out.inputs['Geometry'])
    _gn_modifier(obj, "Field domain probe", graph)


def _build_field(scene):
    # An asymmetric, closed prism with deliberately nonuniform point samples.
    outline = [(-1.4, -.8), (.9, -.8), (1.25, -.15), (.55, .75), (-.9, .55)]
    vertices = [(x, y, z) for z in (.08, .58) for x, y in outline]
    n = len(outline)
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    faces.extend((i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n))
    obj = _object(scene, "Field inspector / asymmetric prism", vertices, faces, 'field_mesh')
    attr = obj.data.attributes.new("ProbeValue", 'FLOAT', 'POINT')
    low, high = min(v[0] for v in outline), max(v[0] for v in outline)
    for i, point in enumerate(vertices):
        attr.data[i].value = (point[0] - low) / (high - low)
    obj.data.materials.append(_material("Field inspector / slate", (.12, .3, .4)))
    _field_graph(obj, 'POINT', .5)
    return obj


def _uv_area(coords):
    return abs(sum(coords[i][0] * coords[(i + 1) % len(coords)][1]
                   - coords[(i + 1) % len(coords)][0] * coords[i][1]
                   for i in range(len(coords))) / 2)


def _set_uvs(scene, target_density, margin_pixels):
    width = 512
    token = _scene_token(scene)
    image = next((item for item in bpy.data.images
                  if item.get("geometry_role") == "uv_checker"
                  and item.get("geometry_scene_instance") == token), None)
    if image is None:
        image = bpy.data.images.new("UV audit / original packed checker", width=width, height=width)
        image.generated_type = 'BLANK'
        image["geometry_role"] = "uv_checker"
        image["geometry_scene_instance"] = token
    if image.size[0] != width or image.size[1] != width:
        raise ValueError("Owned UV checker image has unexpected dimensions")
    pixels = array('f')
    for y in range(width):
        for x in range(width):
            color = (.09, .2, .24, 1) if ((x // 32) + (y // 32)) % 2 == 0 else (.82, .39, .12, 1)
            pixels.extend(color)
    image.pixels.foreach_set(pixels)
    image.update()
    image.pack()
    if image.packed_file is None:
        raise AssertionError("Could not pack the current UV checker pixels")
    side = target_density / width
    gap = margin_pixels / width
    start = .12
    panels = [_role(scene, 'uv_panel_a'), _role(scene, 'uv_panel_b')]
    # The second island has a visibly elongated shape with preserved area; it is
    # an anisotropy warning even when its area-based texel density agrees.
    shapes = [((0, 0), (side, 0), (side, side), (0, side)),
              ((0, 0), (side * 1.8, 0), (side * 1.8, side / 1.8), (0, side / 1.8))]
    offsets = [(start, .18), (start + side + gap, .18)]
    for panel, shape, (u, v), panel_key in zip(panels, shapes, offsets, ('a', 'b')):
        layer = panel.data.uv_layers.active or panel.data.uv_layers.new(name="Audit UV")
        for index, coord in enumerate(shape):
            layer.data[index].uv = (u + coord[0], v + coord[1])
        role = "uv_checker_material_" + panel_key
        mat = next((item for item in bpy.data.materials
                    if item.get("geometry_role") == role
                    and item.get("geometry_scene_instance") == token), None)
        if mat is None:
            mat = bpy.data.materials.new("UV audit / checker material " + panel_key)
            mat["geometry_role"] = role
            mat["geometry_scene_instance"] = token
        if mat not in panel.data.materials[:]:
            panel.data.materials.clear()
            panel.data.materials.append(mat)
        elif len(panel.data.materials) != 1:
            panel.data.materials.clear()
            panel.data.materials.append(mat)
        mat.use_nodes = True
        tree = mat.node_tree
        texture = next((node for node in tree.nodes if node.get("geometry_role") == "uv_checker_texture"), None)
        if texture is None:
            texture = tree.nodes.new('ShaderNodeTexImage')
            texture["geometry_role"] = "uv_checker_texture"
        texture.image = image
        shader = tree.nodes.get('Principled BSDF')
        if shader is None:
            raise ValueError("Owned UV checker material lost its Principled shader")
        if not any(link.from_node == texture and link.to_node == shader
                   and link.to_socket == shader.inputs['Base Color'] for link in tree.links):
            tree.links.new(texture.outputs['Color'], shader.inputs['Base Color'])


def _build_uv(scene):
    panels = []
    for i, x in enumerate((-1.0, 1.0)):
        obj = _object(scene, f"UV audit / reference panel {i + 1}",
                      [(-.5, -.5, 0), (.5, -.5, 0), (.5, .5, 0), (-.5, .5, 0)],
                      [(0, 1, 2, 3)], f"uv_panel_{'a' if i == 0 else 'b'}", (x, .4, .08))
        panels.append(obj)
    _set_uvs(scene, 32, 2)
    return panels[0]


def _uv_metrics(scene):
    panels = [_role(scene, 'uv_panel_a'), _role(scene, 'uv_panel_b')]
    densities, bounds, axis_ratios = [], [], []
    for obj in panels:
        uv = obj.data.uv_layers.active
        coords = [tuple(uv.data[i].uv) for i in obj.data.polygons[0].loop_indices]
        uv_area = _uv_area(coords)
        face_area = obj.data.polygons[0].area
        image = next(node.image for node in obj.data.materials[0].node_tree.nodes if node.type == 'TEX_IMAGE')
        if min(image.size) <= 0 or face_area <= 1e-12 or uv_area <= 1e-12:
            raise ValueError("UV audit has missing image dimensions or degenerate UV/face area")
        densities.append(math.sqrt(uv_area * image.size[0] * image.size[1] / face_area))
        us, vs = [p[0] for p in coords], [p[1] for p in coords]
        bounds.append((min(us), min(vs), max(us), max(vs)))
        axis_ratios.append((max(us) - min(us)) / (max(vs) - min(vs)))
    image = next(node.image for node in panels[0].data.materials[0].node_tree.nodes if node.type == 'TEX_IMAGE')
    margin = (bounds[1][0] - bounds[0][2]) * image.size[0]
    return densities, margin, axis_ratios


def _wedge_mesh(cut, dissolve_angle):
    # Extruded pentagonal wedge; BMesh inserts a true cross-section cut.
    # The middle point on the flat bottom creates a real coplanar band for
    # the limited-dissolve step, separate from the adjustable cross-section cut.
    profile = [(-.72, 0), (0, 0), (.72, 0), (.72, .8), (0, 1.28), (-.72, .8)]
    verts = [(x, y, z) for x in (-1.4, 1.4) for y, z in profile]
    n = len(profile)
    faces = [tuple(reversed(range(n))), tuple(range(n, n * 2))]
    faces.extend((i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n))
    bm = bmesh.new()
    temporary = _mesh_from_data("Topology surgery / temporary", verts, faces)
    bm.from_mesh(temporary)
    bpy.data.meshes.remove(temporary)
    geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(cut, 0, 0), plane_no=(1, 0, 0),
                           dist=1e-6, clear_inner=False, clear_outer=False)
    cut_edges = [edge for edge in bm.edges if edge.is_boundary
                 and all(abs(vertex.co.x - cut) < 1e-5 for vertex in edge.verts)]
    if cut_edges:
        bmesh.ops.holes_fill(bm, edges=cut_edges, sides=0)
    # Limit the real dissolve to coplanar surface edges away from the new cut.
    planar = [edge for edge in bm.edges if len(edge.link_faces) == 2
              and all(abs(face.normal.x) < .999 for face in edge.link_faces)
              and not all(abs(vertex.co.x - cut) < 1e-5 for vertex in edge.verts)]
    if planar:
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(dissolve_angle), use_dissolve_boundaries=False,
                                  verts=list({v for e in planar for v in e.verts}), edges=planar,
                                  delimit={'NORMAL'})
    bm.normal_update()
    mesh = bpy.data.meshes.new("Topology surgery / wedge")
    bm.to_mesh(mesh)
    mesh.update()
    bm.free()
    return mesh


def _mesh_from_data(name, vertices, faces):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    return mesh


def _build_topology(scene):
    obj = bpy.data.objects.new("Topology surgery / edited wedge", _wedge_mesh(0, 5))
    scene.collection.objects.link(obj)
    _tag(obj, 'topology_wedge')
    obj.data.materials.append(_material("Topology surgery / terracotta", (.57, .19, .09)))
    return obj


def _apply_topology(obj, cut, angle):
    old = obj.data
    materials = list(old.materials)
    mesh = _wedge_mesh(-1.4 + 2.8 * cut, angle)
    # The cut plane's computed x coordinate is also the measured control.
    obj.data = mesh
    for material in materials:
        mesh.materials.append(material)
    if old.users == 0:
        bpy.data.meshes.remove(old)
    obj["dissolve_angle_degrees"] = angle


def _make_wall(scene):
    vertices, faces = _cube_mesh((1.45, .28, 1.2))
    wall = _object(scene, "Boolean / editable wall", vertices, faces, 'boolean_wall', (0, .65, 1.2))
    wall.data.materials.append(_material("Boolean / deep stone", (.17, .29, .34)))
    cutter_vertices, cutter_faces = _cube_mesh((.5, .42, .66))
    cutter = _object(scene, "Boolean / editable opening cutter", cutter_vertices, cutter_faces,
                     'boolean_cutter', (0, .65, .78))
    cutter.display_type = 'WIRE'
    cutter.hide_render = True
    boolean = wall.modifiers.new("Exact opening operation", 'BOOLEAN')
    boolean.object = cutter
    boolean.solver = 'EXACT'
    boolean.operation = 'DIFFERENCE'
    return wall


def _apply_boolean(scene, width, operation):
    wall, cutter = _role(scene, 'boolean_wall'), _role(scene, 'boolean_cutter')
    cutter.dimensions.x = width
    bpy.context.view_layer.update()
    mod = next((m for m in wall.modifiers if m.type == 'BOOLEAN'), None)
    if mod is None or mod.object is None:
        raise ValueError("Boolean operand or modifier is missing")
    mod.operation = operation


def _shell_height(x, y):
    return .36 + .2 * math.sin(x * 1.25) + .12 * math.cos(y * 1.4)


def _build_projection(scene, density=8):
    n = density + 1
    verts, faces = [], []
    for j in range(n):
        y = -1.3 + 2.6 * j / density
        for i in range(n):
            x = -1.3 + 2.6 * i / density
            verts.append((x, y, _shell_height(x, y)))
    for j in range(density):
        for i in range(density):
            a = j * n + i
            faces.append((a, a + 1, a + n + 1, a + n))
    target = _object(scene, "Projection / bent shell target", verts, faces, 'projection_target')
    target.data.materials.append(_material("Projection / shell teal", (.04, .35, .31)))
    return _build_cage(scene, density, .02)


def _build_cage(scene, density=8, offset=.02):
    n = density + 1
    verts, faces = [], []
    for j in range(n):
        y = -1.3 + 2.6 * j / density
        for i in range(n):
            x = -1.3 + 2.6 * i / density
            verts.append((x, y, _shell_height(x, y) + .22))
    for j in range(density):
        for i in range(density):
            a = j * n + i
            faces.append((a, a + 1, a + n + 1, a + n))
    cage = _object(scene, "Projection / independent quad cage", verts, faces, 'projection_cage')
    cage.data.materials.append(_material("Projection / copper cage", (.83, .38, .1)))
    cage.display_type = 'WIRE'
    cage.show_in_front = True
    mod = cage.modifiers.new("Negative Z surface projection", 'SHRINKWRAP')
    mod.target = _role(scene, 'projection_target')
    mod.wrap_method = 'PROJECT'
    mod.wrap_mode = 'ON_SURFACE'
    mod.use_project_z = True
    mod.use_positive_direction = False
    mod.use_negative_direction = True
    mod.project_limit = 1.0
    mod.offset = offset
    return cage


def _grid_topology(scene, lab):
    """Create an original closed asymmetric prism for attribute contracts."""
    outline = [(-1.1, -.7), (.85, -.7), (1.2, -.25), (.55, .72), (-.75, .5)]
    vertices = [(x, y, z) for z in (.06, .62) for x, y in outline]
    n = len(outline)
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    faces.extend((i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n))
    return _object(scene, "Attribute contract / asymmetric prism", vertices, faces, 'attribute_mesh')


def _attribute_spec(domain, data_type):
    domains = {'POINT': 'POINT', 'FACE': 'FACE', 'CORNER': 'CORNER'}
    types = {'FLOAT': 'FLOAT', 'FLOAT_VECTOR': 'FLOAT_VECTOR', 'FLOAT_COLOR': 'FLOAT_COLOR'}
    if domain not in domains or data_type not in types:
        raise ValueError("Unsupported attribute domain/type contract")
    return domains[domain], types[data_type]


def _write_contract_attribute(mesh, domain, data_type):
    domain, data_type = _attribute_spec(domain, data_type)
    name = "LabContractValue"
    existing = mesh.attributes.get(name)
    if existing is not None:
        owned = set(str(mesh.get("geometry_owned_attribute_names", "")).split(","))
        if name not in owned:
            raise ValueError("Attribute name collides with existing user data")
        mesh.attributes.remove(existing)
    attr = mesh.attributes.new(name, data_type, domain)
    owned = set(str(mesh.get("geometry_owned_attribute_names", "")).split(","))
    owned.add(name)
    mesh["geometry_owned_attribute_names"] = ",".join(sorted(owned))
    for index, item in enumerate(attr.data):
        value = (index + 1) / max(1, len(attr.data))
        if data_type == 'FLOAT':
            item.value = value
        elif data_type == 'FLOAT_VECTOR':
            item.vector = (value, value * .5, 1.0 - value)
        else:
            item.color = (value, value * .5, 1.0 - value, 1.0)
    return attr


def _build_attribute(scene):
    obj = _grid_topology(scene, 'BL-028')
    _write_contract_attribute(obj.data, 'POINT', 'FLOAT')
    return obj


def build(scene, lab, base_subject):
    builders = {
        'BL-013': _build_scatter,
        'BL-014': _build_field,
        'BL-015': _build_uv,
        'BL-025': _build_topology,
        'BL-026': _make_wall,
        'BL-027': _build_projection,
        'BL-028': _build_attribute,
    }
    if lab not in builders:
        raise ValueError(f"No geometry builder for {lab}")
    if base_subject is not None and base_subject.name in bpy.data.objects:
        bpy.data.objects.remove(base_subject, do_unlink=True)
    obj = builders[lab](scene)
    defaults = {
        'BL-013': {'Density': 4, 'Seed': 17},
        'BL-014': {'Domain': 'POINT', 'Threshold': .5},
        'BL-015': {'Target density': 32, 'Margin pixels': 2},
        'BL-025': {'Cut position': .5, 'Dissolve angle': 5},
        'BL-026': {'Opening width': 1, 'Operation': 'DIFFERENCE'},
        'BL-027': {'Surface offset': .02, 'Cage density': 8},
        'BL-028': {'Attribute domain': 'POINT', 'Data type': 'FLOAT'},
    }[lab]
    apply_controls(scene, lab, defaults)
    return obj


def apply_controls(scene, lab, params):
    if lab == 'BL-013':
        density, seed = params['Density'], params['Seed']
        if not 0 <= density <= 16 or not 0 <= seed <= 65535:
            raise ValueError("Scatter controls are outside their declared bounds")
        obj = _role(scene, 'scatter_surface')
        graph = obj.modifiers[-1].node_group
        distribute = next(n for n in graph.nodes if n.bl_idname == 'GeometryNodeDistributePointsOnFaces')
        distribute.inputs['Density'].default_value = density
        distribute.inputs['Seed'].default_value = seed
    elif lab == 'BL-014':
        domain, threshold = params['Domain'], params['Threshold']
        if domain not in ('POINT', 'EDGE', 'FACE', 'CORNER') or not 0 <= threshold <= 1:
            raise ValueError("Field inspector controls are outside their declared choices/bounds")
        graph = _role(scene, 'field_mesh').modifiers[-1].node_group
        for node in graph.nodes:
            if node.bl_idname in ('GeometryNodeFieldOnDomain', 'GeometryNodeStoreNamedAttribute'):
                node.domain = domain
            if node.bl_idname == 'ShaderNodeMath' and node.label == 'Threshold selection':
                node.inputs[1].default_value = threshold
    elif lab == 'BL-015':
        density, margin = params['Target density'], params['Margin pixels']
        if not 8 <= density <= 128 or not 0 <= margin <= 8:
            raise ValueError("UV audit controls are outside their declared bounds")
        _set_uvs(scene, density, margin)
    elif lab == 'BL-025':
        cut, angle = params['Cut position'], params['Dissolve angle']
        if not .1 <= cut <= .9 or not 0 <= angle <= 30:
            raise ValueError("Topology surgery controls are outside their declared bounds")
        _apply_topology(_role(scene, 'topology_wedge'), cut, angle)
    elif lab == 'BL-026':
        width, operation = params['Opening width'], params['Operation']
        if not .2 <= width <= 2 or operation not in ('DIFFERENCE', 'UNION', 'INTERSECT'):
            raise ValueError("Boolean controls are outside their declared choices/bounds")
        _apply_boolean(scene, width, operation)
    elif lab == 'BL-027':
        offset, density = params['Surface offset'], params['Cage density']
        if not 0 <= offset <= .1 or not 4 <= density <= 24:
            raise ValueError("Projection controls are outside their declared bounds")
        target, cage = _role(scene, 'projection_target'), _role(scene, 'projection_cage')
        target_signature = tuple(tuple(v.co) for v in target.data.vertices)
        old = cage.data
        materials = list(old.materials)
        rebuilt = _build_cage_mesh(density)
        for material in materials:
            rebuilt.materials.append(material)
        cage.data = rebuilt
        if old.users == 0:
            bpy.data.meshes.remove(old)
        mod = next(m for m in cage.modifiers if m.type == 'SHRINKWRAP')
        mod.offset = offset
        cage['target_signature'] = str(target_signature)
    elif lab == 'BL-028':
        _write_contract_attribute(_role(scene, 'attribute_mesh').data,
                                  params['Attribute domain'], params['Data type'])
    else:
        raise ValueError(f"No geometry controls for {lab}")
    bpy.context.view_layer.update()


def _build_cage_mesh(density):
    n = density + 1
    vertices, faces = [], []
    for j in range(n):
        y = -1.3 + 2.6 * j / density
        for i in range(n):
            x = -1.3 + 2.6 * i / density
            vertices.append((x, y, _shell_height(x, y) + .22))
    for j in range(density):
        for i in range(density):
            a = j * n + i
            faces.append((a, a + 1, a + n + 1, a + n))
    return _mesh_from_data("Projection / editable quad cage", vertices, faces)


def _evaluated_mesh(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    if mesh is None:
        raise AssertionError(f"{obj.name} did not produce evaluated mesh geometry")
    return evaluated, mesh


def _manifold_counts(mesh):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    boundary = sum(1 for edge in bm.edges if not edge.is_manifold)
    wire = sum(1 for edge in bm.edges if not edge.link_faces)
    bm.free()
    return boundary, wire


def verify(scene, lab, params, output):
    bpy.context.view_layer.update()
    if lab == 'BL-013':
        density, seed = params['Density'], params['Seed']
        obj = _role(scene, 'scatter_surface')
        evaluated, mesh = _evaluated_mesh(obj)
        try:
            _check(len(mesh.polygons) >= len(obj.data.polygons), "Scatter evaluation lost the original terrain")
            source_faces = len(_role(scene, 'scatter_source').data.polygons)
            _check(source_faces > 0, "Scatter instance source is empty")
            instance_faces = len(mesh.polygons) - len(obj.data.polygons)
            _check(instance_faces % source_faces == 0, "Evaluated scatter is not a whole number of source instances")
            count = instance_faces // source_faces
            _check(count <= 256, "Scatter exceeded the fixture point cap")
            _check(count > 0 or density == 0, "Positive scatter density produced no instances")
            coords = tuple(sorted((round(v.co.x, 5), round(v.co.y, 5), round(v.co.z, 5)) for v in mesh.vertices))
            _check(coords, "Scatter output has no evaluated vertices")
            expected_area = sum(poly.area for poly in obj.data.polygons)
            _check(count <= min(256, math.ceil(density * expected_area * 2 + 12)),
                   "Scatter exceeded the bounded density estimate")
            evaluated_vertices = len(mesh.vertices)
        finally:
            evaluated.to_mesh_clear()
        repeated, repeated_mesh = _evaluated_mesh(obj)
        try:
            repeated_coords = tuple(sorted((round(v.co.x, 5), round(v.co.y, 5), round(v.co.z, 5))
                                           for v in repeated_mesh.vertices))
        finally:
            repeated.to_mesh_clear()
        _check(coords == repeated_coords, "Same density and seed did not reproduce scatter positions")
        return {'seed': seed, 'density': density, 'evaluated_instance_count': count,
                'evaluated_vertices': evaluated_vertices, 'terrain_area': expected_area,
                'position_signature': hash(coords), 'same_seed_reproduced': True}
    if lab == 'BL-014':
        obj = _role(scene, 'field_mesh')
        source_values = obj.data.attributes.get('ProbeValue')
        _check(source_values is not None and source_values.domain == 'POINT'
               and len(source_values.data) == len(obj.data.vertices),
               "Required ProbeValue named attribute is missing or has invalid point cardinality")
        evaluated, mesh = _evaluated_mesh(obj)
        try:
            domain = params['Domain']
            expected = {'POINT': len(mesh.vertices), 'EDGE': len(mesh.edges), 'FACE': len(mesh.polygons),
                        'CORNER': len(mesh.loops)}[domain]
            values = mesh.attributes.get('DomainSample')
            masks = mesh.attributes.get('AboveThreshold')
            _check(values is not None and values.domain == domain and len(values.data) == expected,
                   "Transferred field attribute has incorrect domain cardinality")
            _check(masks is not None and masks.domain == domain and masks.data_type == 'BOOLEAN'
                   and len(masks.data) == expected, "Threshold field mask violates domain contract")
            samples = [item.value for item in values.data]
            _check(samples and all(math.isfinite(v) and 0 <= v <= 1 for v in samples),
                   "Named point field produced missing, degenerate or invalid samples")
            selected = sum(item.value for item in masks.data)
            _check(selected == sum(value > params['Threshold'] for value in samples),
                   "Threshold mask does not match the transferred field samples")
            return {'domain': domain, 'attribute_count': len(values.data), 'expected_count': expected,
                    'sample_range': [min(samples), max(samples)], 'selected_count': selected,
                    'threshold': params['Threshold']}
        finally:
            evaluated.to_mesh_clear()
    if lab == 'BL-015':
        densities, margin, ratios = _uv_metrics(scene)
        target, margin_px = params['Target density'], params['Margin pixels']
        _check(all(abs(value - target) < .02 for value in densities), "UV panels do not meet the requested texel density")
        _check(abs(margin - margin_px) < .02, "Measured UV island gap differs from margin control")
        _check(abs(ratios[0] - 1) < .01 and ratios[1] > 1.5,
               "UV audit fixture lost its square reference or deliberately stretched island")
        _check(all(next(node.image for node in panel.data.materials[0].node_tree.nodes
                        if node.type == 'TEX_IMAGE').packed_file for panel in
                   (_role(scene, 'uv_panel_a'), _role(scene, 'uv_panel_b'))),
               "UV audit checker dependency is not packed")
        return {'target_density': target, 'measured_densities': densities, 'margin_pixels': margin,
                'uv_axis_ratios': ratios,
                'image_size': list(next(node.image for node in _role(scene, 'uv_panel_a').data.materials[0].node_tree.nodes
                                        if node.type == 'TEX_IMAGE').size)}
    if lab == 'BL-025':
        obj = _role(scene, 'topology_wedge')
        mesh = obj.data
        boundary, wire = _manifold_counts(mesh)
        _check(boundary == 0 and wire == 0, "Topology edit produced a boundary or wire edge on a closed wedge")
        xs = [v.co.x for v in mesh.vertices]
        cut_x = -1.4 + 2.8 * params['Cut position']
        _check(any(abs(x - cut_x) < 1e-5 for x in xs), "BMesh cut position is absent from edited topology")
        _check(len(mesh.polygons) >= 7, "BMesh surgery returned an empty or degenerate wedge")
        return {'vertices': len(mesh.vertices), 'edges': len(mesh.edges), 'faces': len(mesh.polygons),
                'cut_x': cut_x, 'boundary_edges': boundary, 'wire_edges': wire,
                'dissolve_angle_degrees': params['Dissolve angle']}
    if lab == 'BL-026':
        wall = _role(scene, 'boolean_wall')
        mod = next((m for m in wall.modifiers if m.type == 'BOOLEAN'), None)
        _check(mod is not None and mod.object == _role(scene, 'boolean_cutter') and mod.solver == 'EXACT',
               "Boolean modifier has no exact owned operand")
        _check(mod.operation == params['Operation'], "Boolean operation control did not reach the modifier")
        cutter = _role(scene, 'boolean_cutter')
        _check(abs(cutter.dimensions.x - params['Opening width']) < 1e-5,
               "Boolean cutter width differs from the opening control")
        evaluated, mesh = _evaluated_mesh(wall)
        try:
            volume_mesh = bmesh.new()
            try:
                volume_mesh.from_mesh(mesh)
                volume = abs(volume_mesh.calc_volume(signed=True))
            finally:
                volume_mesh.free()
            boundary, wire = _manifold_counts(mesh)
            _check(volume > 1e-5 and len(mesh.polygons) >= 4, "Boolean evaluated to empty or zero-volume geometry")
            if params['Operation'] == 'DIFFERENCE':
                _check(volume < 8 * 1.45 * .28 * 1.2, "Difference did not remove volume from the wall")
                _check(boundary == 0 and wire == 0, "Boolean opening has open or wire edges")
            return {'operation': mod.operation, 'opening_width': params['Opening width'],
                    'evaluated_volume': volume, 'evaluated_vertices': len(mesh.vertices),
                    'boundary_edges': boundary, 'wire_edges': wire,
                    'cutter_dimensions': list(_role(scene, 'boolean_cutter').dimensions)}
        finally:
            evaluated.to_mesh_clear()
    if lab == 'BL-027':
        target, cage = _role(scene, 'projection_target'), _role(scene, 'projection_cage')
        before = cage.get('target_signature')
        current = str(tuple(tuple(v.co) for v in target.data.vertices))
        _check(before == current, "Projection modified the protected target mesh")
        mod = next((m for m in cage.modifiers if m.type == 'SHRINKWRAP'), None)
        _check(mod is not None and mod.target == target and mod.wrap_method == 'PROJECT'
               and mod.use_project_z and mod.use_negative_direction and not mod.use_positive_direction,
               "Projection modifier lost the explicit negative-Z target setup")
        evaluated, mesh = _evaluated_mesh(cage)
        try:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            target_eval = target.evaluated_get(depsgraph)
            distances = []
            for vertex in mesh.vertices:
                world = evaluated.matrix_world @ vertex.co
                ok, closest, _normal, _index = target_eval.closest_point_on_mesh(target_eval.matrix_world.inverted() @ world)
                _check(ok, "Projection sample could not find a target surface point")
                distances.append((world - target_eval.matrix_world @ closest).length)
            expected = params['Surface offset']
            _check(max(abs(distance - expected) for distance in distances) < .015,
                   "Evaluated cage-to-target distances exceed the requested offset tolerance")
            _check(len(cage.data.vertices) == (params['Cage density'] + 1) ** 2,
                   "Cage density did not update editable source topology")
            return {'cage_vertices': len(cage.data.vertices), 'cage_faces': len(cage.data.polygons),
                    'target_vertices_unchanged': len(target.data.vertices), 'distance_range': [min(distances), max(distances)],
                    'surface_offset': expected, 'projection_direction': '-Z'}
        finally:
            evaluated.to_mesh_clear()
    if lab == 'BL-028':
        mesh = _role(scene, 'attribute_mesh').data
        domain, data_type = _attribute_spec(params['Attribute domain'], params['Data type'])
        attr = mesh.attributes.get('LabContractValue')
        expected = {'POINT': len(mesh.vertices), 'FACE': len(mesh.polygons), 'CORNER': len(mesh.loops)}[domain]
        _check(attr is not None and attr.domain == domain and attr.data_type == data_type
               and len(attr.data) == expected, "Mesh attribute violates selected type/domain/cardinality contract")
        _check(len(attr.data) > 0, "Mesh attribute contract has no data samples")
        values = ([entry.value for entry in attr.data] if data_type == 'FLOAT' else
                  [tuple(entry.vector) for entry in attr.data] if data_type == 'FLOAT_VECTOR' else
                  [tuple(entry.color) for entry in attr.data])
        _check(all(all(math.isfinite(component) for component in ((value,) if isinstance(value, float) else value))
                   for value in values), "Mesh attribute contains nonfinite values")
        return {'attribute': attr.name, 'domain': attr.domain, 'data_type': attr.data_type,
                'element_count': len(attr.data), 'expected_count': expected, 'sample': values[0]}
    raise ValueError(f"No geometry verifier for {lab}")
