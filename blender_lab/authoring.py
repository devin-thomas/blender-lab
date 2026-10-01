"""Editable modular construction, vertex shading and original alpha-card studies.

The caller owns scene setup, datablock tracking, save and reset. Controls mutate
transforms or shader inputs without rebuilding geometry or accumulating assets.
"""
import math

import bpy
from mathutils import Vector


def _check(condition, message):
    if not condition:
        raise AssertionError(message)


def _connection(tree, source, destination):
    return any(link.from_socket == source and link.to_socket == destination for link in tree.links)


def _object(scene, name, mesh, location=(0, 0, 0)):
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    obj.location = location
    return obj


def _role(scene, role):
    matches = [obj for obj in scene.objects if obj.get("authoring_role") == role]
    if len(matches) != 1:
        raise AssertionError(f"Expected exactly one authoring object: {role}")
    return matches[0]


def _tag(obj, role):
    obj["authoring_role"] = role
    return obj


def _prism(scene, name, outline, depth, mat, axes=(0, 1, 2)):
    """Extrude an authored two-dimensional outline along the third axis."""
    vertices = []
    for layer in (-depth / 2, depth / 2):
        for u, v in outline:
            point = [0, 0, 0]
            point[axes[0]], point[axes[1]], point[axes[2]] = u, v, layer
            vertices.append(point)
    count = len(outline)
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    faces.extend((i, (i + 1) % count, (i + 1) % count + count, i + count)
                 for i in range(count))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    return _object(scene, name, mesh)


def _share_atlas(mesh, source):
    """Map arbitrary polygon sizes without assuming all faces are quads."""
    uv = mesh.uv_layers.new(name="Atlas UV")
    for polygon in mesh.polygons:
        for corner, index in enumerate(polygon.loop_indices):
            angle = corner * 2 * math.pi / len(polygon.loop_indices)
            uv.data[index].uv = (.5 + .45 * math.cos(angle), .5 + .45 * math.sin(angle))
    # The shared shader reads this attribute on every mesh using the atlas.
    shades = mesh.color_attributes.new(name="AuthoredShade", type='FLOAT_COLOR', domain='CORNER')
    low, high = min(vertex.co.z for vertex in mesh.vertices), max(vertex.co.z for vertex in mesh.vertices)
    height = high - low
    for loop in mesh.loops:
        z = mesh.vertices[loop.vertex_index].co.z
        shade = .55 + .45 * (z - low) / height if height > 1e-6 else 1.0
        shades.data[loop.index].color = (shade, shade * .96, shade * .88, 1)
    mesh.materials.clear()
    mesh.materials.append(source)


def _label(scene, title, position):
    from .labs import material, PALETTE
    curve = bpy.data.curves.new(title, 'FONT')
    curve.body = title
    curve.size = .16
    curve.materials.append(material(title + " ink", PALETTE["cream"]))
    obj = _object(scene, title, curve, position)
    return obj


def _kit(scene):
    from .labs import cube, material, pixel_surface, PALETTE
    mat = material("Kit / shared original masonry", PALETTE["amber"])
    wall = _tag(cube(scene, "Kit / Wall left", (0, 1.6, 1.2), (1, .125, 1.2), mat), "wall_left")
    pixel_surface(wall)
    wall.data.name = "Kit / linked two-meter wall"
    right = _tag(_object(scene, "Kit / Wall right", wall.data), "wall_right")
    # This L-shaped footprint supplies a real return at both ends of the wall.
    corner = _prism(scene, "Kit / Corner left", [(0, 0), (.25, 0), (.25, -.65),
                   (0, -.65), (0, -.25), (-.45, -.25), (-.45, 0)], 2.4, mat)
    corner.location.z = 1.2
    _tag(corner, "corner_left")
    _share_atlas(corner.data, mat)
    _tag(_object(scene, "Kit / Corner right", corner.data), "corner_right")
    post = _tag(cube(scene, "Kit / Door post left", (0, 1.6, .9), (.12, .2, .9), mat), "post_left")
    _share_atlas(post.data, mat)
    _tag(_object(scene, "Kit / Door post right", post.data), "post_right")
    lintel = _tag(cube(scene, "Kit / Door lintel", (0, 1.6, 2.1), (.75, .2, .3), mat), "lintel")
    _share_atlas(lintel.data, mat)
    stair = _prism(scene, "Kit / Four-step entrance", [(-1.4, 0), (.2, 0), (.2, .72),
                   (-.2, .72), (-.2, .54), (-.6, .54), (-.6, .36),
                   (-1, .36), (-1, .18), (-1.4, .18)], 1.2, mat, (1, 2, 0))
    stair.location.y = 1.0
    _tag(stair, "stair")
    _share_atlas(stair.data, mat)
    _label(scene, "LINKED WALL / CORNER / DOOR / STAIR", (-3.2, -1.6, .02))
    wall["blender_lab_subject"] = True
    return wall


def _beacon_mesh():
    # Tiered, chamfered silhouette is identical in all three shader comparisons.
    profile = [(.58, 0), (.75, .18), (.75, .45), (.55, .65), (.55, 1.35),
               (.32, 1.55), (.32, 1.85), (.58, 1.95), (.58, 2.1)]
    vertices = [(radius * math.cos(i * math.pi / 3), radius * math.sin(i * math.pi / 3), z)
                for radius, z in profile for i in range(6)]
    faces = []
    for ring in range(len(profile) - 1):
        for i in range(6):
            a, b = ring * 6 + i, ring * 6 + (i + 1) % 6
            faces.append((a, b, b + 6, a + 6))
    for ring, reverse in ((0, True), (len(profile) - 1, False)):
        center = len(vertices)
        vertices.append((0, 0, profile[ring][1]))
        for i in range(6):
            face = (center, ring * 6 + i, ring * 6 + (i + 1) % 6)
            faces.append(tuple(reversed(face)) if reverse else face)
    mesh = bpy.data.meshes.new("Composition / hexagonal signal beacon")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    return mesh


def _emission_output(mat, color_socket):
    tree = mat.node_tree
    emission = tree.nodes.new('ShaderNodeEmission')
    emission.name = "Authored unlit surface"
    emission.inputs['Strength'].default_value = .8
    tree.links.new(color_socket, emission.inputs['Color'])
    tree.links.new(emission.outputs[0], tree.nodes['Material Output'].inputs['Surface'])


def _composition(scene):
    from .labs import material, pixel_surface, PALETTE
    mesh = _beacon_mesh()
    mat = material("Composition / texture reference", PALETTE['amber'])
    mesh.materials.append(mat)
    first = _tag(_object(scene, "Comparison / Texture only", mesh, (-2.2, 0, .1)), "texture_only")
    pixel_surface(first)
    # Authored shadow follows both height and facet direction, independent of lights.
    shades = mesh.color_attributes['AuthoredShade'].data
    for loop in mesh.loops:
        point = mesh.vertices[loop.vertex_index].co
        shade = min(1, .25 + .5 * point.z / 2.1 + .25 * (point.y + .75) / 1.5)
        shades[loop.index].color = (shade, shade * .92, shade * .82, 1)
    tex = next(node for node in mat.node_tree.nodes if node.type == 'TEX_IMAGE')
    _emission_output(mat, tex.outputs['Color'])
    for role, name, x, lit in [('vertex_unlit', "Vertex shade / unlit", 0, False),
                              ('vertex_lit', "Vertex shade / restrained light", 2.2, True)]:
        copy_mesh = mesh.copy()
        copy_mesh.name = "Composition / identical " + role
        copy_mat = mat.copy()
        copy_mat.name = "Composition / " + role
        copy_mesh.materials.clear()
        copy_mesh.materials.append(copy_mat)
        obj = _tag(_object(scene, "Comparison / " + name, copy_mesh, (x, 0, .1)), role)
        tree = copy_mat.node_tree
        mix = tree.nodes['Vertex shade strength']
        if lit:
            tree.links.new(tree.nodes['Principled BSDF'].outputs[0], tree.nodes['Material Output'].inputs['Surface'])
        else:
            tree.links.new(mix.outputs[0], tree.nodes['Authored unlit surface'].inputs['Color'])
        _label(scene, name.upper().replace(' / ', ' + '), (x - .95, -1.3, .02))
    _label(scene, "TEXTURE ONLY", (-3.15, -1.3, .02))
    first['blender_lab_subject'] = True
    return first


def _alpha_material(name, kind):
    image = bpy.data.images.new(name + " / original gradient", width=64, height=64, alpha=True)
    pixels = []
    for y in range(64):
        for x in range(64):
            u, v = (x + .5) / 64, (y + .5) / 64
            if kind == 'contact':
                alpha = max(0, 1 - math.hypot((u - .5) * 2, (v - .5) * 2)) ** 2
                color = (.012, .025, .035)
            else:
                edge = max(0, 1 - abs(u - .5) * 2)
                alpha = edge ** 2 * math.sin(v * math.pi) ** .65
                color = (.95, .69, .28)
            pixels.extend((*color, alpha))
    image.pixels = pixels
    image.pack()
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.surface_render_method = 'DITHERED'
    tree = mat.node_tree
    tree.nodes.clear()
    tex = tree.nodes.new('ShaderNodeTexImage')
    tex.image = image
    tex.interpolation = 'Linear'
    tex.extension = 'CLIP'
    alpha = tree.nodes.new('ShaderNodeMath')
    alpha.name = 'Atmosphere intensity'
    alpha.operation = 'MULTIPLY'
    alpha.inputs[1].default_value = .45
    transparent = tree.nodes.new('ShaderNodeBsdfTransparent')
    surface = tree.nodes.new('ShaderNodeEmission')
    surface.inputs['Strength'].default_value = .7
    mix = tree.nodes.new('ShaderNodeMixShader')
    output = tree.nodes.new('ShaderNodeOutputMaterial')
    for src, out, dst, inp in [(tex, 'Alpha', alpha, 0), (tex, 'Color', surface, 'Color'),
                               (alpha, 0, mix, 0), (transparent, 0, mix, 1),
                               (surface, 0, mix, 2), (mix, 0, output, 'Surface')]:
        tree.links.new(src.outputs[out], dst.inputs[inp])
    for index, node in enumerate((tex, alpha, transparent, surface, mix, output)):
        node.location = (index * 190 - 800, (index % 2) * -180)
    return mat


def _card(scene, name, vertices, mat, role):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
    mesh.materials.append(mat)
    mesh.update()
    uv = mesh.uv_layers.new(name="Gradient UV")
    for index, point in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[index].uv = point
    return _tag(_object(scene, name, mesh), role)


def _atmosphere(scene):
    from .labs import cube, material, PALETTE
    stone = material("Atmosphere / original weathered portal", PALETTE['teal'])
    for x in (-2, 0, 2):
        pier = _prism(scene, "Portal / chamfered pier", [(-.33, -.2), (.24, -.2),
                      (.33, -.08), (.33, .2), (-.33, .2)], 2.5, stone)
        pier.location = (x, 1.3, 1.25)
    cube(scene, "Portal / overhead stone", (0, 1.3, 2.55), (2.4, .25, .17), stone)
    contact = _alpha_material("Cards / authored contact darkening", 'contact')
    shafts = _alpha_material("Cards / authored amber shaft", 'shaft')
    for index, x in enumerate((-2, 0, 2)):
        _card(scene, "Contact gradient / " + str(index), [(x - .85, .4, .012),
              (x + .85, .4, .012), (x + .85, 2.15, .012), (x - .85, 2.15, .012)],
              contact, "contact_" + str(index))
    first = None
    for index, x in enumerate((-1, 1)):
        card = _card(scene, "Shaft gradient / " + str(index),
                     [(x - 1, -1.4, .12), (x + .5, -1.4, .12),
                      (x + .37, 1.2, 2.4), (x - .37, 1.2, 2.4)], shafts, "shaft_" + str(index))
        if first is None:
            first = card
    _label(scene, "AUTHORED CONTACT + SHAFT CARDS", (-3.1, -1.95, .02))
    first['blender_lab_subject'] = True
    return first


def build(scene, lab, base_subject):
    builders = {'BL-007': _kit, 'BL-008': _composition, 'BL-009': _atmosphere}
    if lab not in builders:
        raise ValueError(f"No authoring builder for {lab}")
    bpy.data.objects.remove(base_subject, do_unlink=True)
    obj = builders[lab](scene)
    apply(scene, lab, 1.0)
    return obj


def apply(scene, lab, value):
    if not .1 <= value <= 2:
        raise ValueError("Authoring control must be between 0.1 and 2.0")
    if lab == 'BL-007':
        span, opening = 1.8 + .35 * value, .7 + .6 * value
        for side, sign in [('left', -1), ('right', 1)]:
            wall = _role(scene, 'wall_' + side)
            wall.scale.x = span / 2
            wall.location = (sign * (opening / 2 + .24 + span / 2), 1.6, 1.2)
            corner = _role(scene, 'corner_' + side)
            corner.location = (sign * (opening / 2 + .24 + span), 1.725, 1.2)
            corner.scale.x = -sign
            post = _role(scene, 'post_' + side)
            post.location = (sign * (opening / 2 + .12), 1.6, .9)
        _role(scene, 'lintel').scale.x = (opening + .48) / 1.5
        _role(scene, 'stair').scale.x = opening / 1.2
    elif lab == 'BL-008':
        for role in ('vertex_unlit', 'vertex_lit'):
            _role(scene, role).data.materials[0].node_tree.nodes['Vertex shade strength'].inputs[0].default_value = value / 2
    elif lab == 'BL-009':
        for role in ('contact_0', 'shaft_0'):
            _role(scene, role).data.materials[0].node_tree.nodes['Atmosphere intensity'].inputs[1].default_value = value * .45
    else:
        raise ValueError(f"No authoring control for {lab}")
    bpy.context.view_layer.update()


def _bounds(obj):
    points = [obj.matrix_world @ Vector(point) for point in obj.bound_box]
    return [(min(point[i] for point in points), max(point[i] for point in points)) for i in range(3)]


def verify(scene, lab, value):
    bpy.context.view_layer.update()
    if lab == 'BL-007':
        left, right = _role(scene, 'wall_left'), _role(scene, 'wall_right')
        posts = [_role(scene, 'post_' + side) for side in ('left', 'right')]
        opening = _bounds(posts[1])[0][0] - _bounds(posts[0])[0][1]
        errors = [abs(_bounds(left)[0][1] - _bounds(posts[0])[0][0]),
                  abs(_bounds(right)[0][0] - _bounds(posts[1])[0][1])]
        corners = [_role(scene, 'corner_' + side) for side in ('left', 'right')]
        pivot_errors = [abs(corners[0].matrix_world.translation.x - _bounds(left)[0][0]),
                        abs(corners[1].matrix_world.translation.x - _bounds(right)[0][1])]
        lintel = _role(scene, 'lintel')
        errors.extend(abs(_bounds(lintel)[2][0] - _bounds(post)[2][1]) for post in posts)
        _check(left.data == right.data and posts[0].data == posts[1].data, "Kit parts lost linked mesh reuse")
        _check(_role(scene, 'corner_left').data == _role(scene, 'corner_right').data, "Corners lost linked reuse")
        _check(max(errors) < 1e-5, "Door/wall module seam opened")
        _check(max(pivot_errors) < 1e-5, "Corner socket pivot no longer aligns with wall endpoint")
        _check(abs(opening - (.7 + .6 * value)) < 1e-5, "Doorway opening differs from control")
        _check(abs((_bounds(left)[0][1] - _bounds(left)[0][0]) - (1.8 + .35 * value)) < 1e-5, "Wall span differs from control")
        mat = left.data.materials[0]
        atlas = next(node.image for node in mat.node_tree.nodes if node.type == 'TEX_IMAGE')
        parts = [obj for obj in scene.objects if obj.get('authoring_role')]
        _check(all(obj.data.materials[0] == mat and obj.data.uv_layers for obj in parts), "Kit lost shared atlas or UVs")
        _check(atlas.packed_file is not None, "Kit atlas is not packed")
        shade_ranges = {}
        for part in parts:
            shades = part.data.color_attributes.get('AuthoredShade')
            _check(shades is not None and shades.domain == 'CORNER' and len(shades.data) == len(part.data.loops),
                   f"Kit part lacks the shader's corner shade attribute: {part.name}")
            channels = [channel for entry in shades.data for channel in entry.color]
            _check(all(math.isfinite(channel) and .05 < channel <= 1 for channel in channels),
                   f"Kit part has invalid or black vertex shades: {part.name}")
            shade_ranges[part['authoring_role']] = [min(channels), max(channels)]
        tree = mat.node_tree
        texture = next(node for node in tree.nodes if node.type == 'TEX_IMAGE')
        vertex = next(node for node in tree.nodes if node.type == 'VERTEX_COLOR')
        mix = tree.nodes['Vertex shade strength']
        shader, output = tree.nodes['Principled BSDF'], tree.nodes['Material Output']
        _check(vertex.layer_name == 'AuthoredShade' and mix.blend_type == 'MULTIPLY'
               and abs(mix.inputs[0].default_value - 1) < 1e-5, "Kit shader no longer reads authored vertex shade")
        _check(_connection(tree, texture.outputs['Color'], mix.inputs[1])
               and _connection(tree, vertex.outputs['Color'], mix.inputs[2])
               and _connection(tree, mix.outputs[0], shader.inputs['Base Color'])
               and _connection(tree, shader.outputs[0], output.inputs['Surface']),
               "Kit's shared texture/vertex shader output path is disconnected")
        _check(all(abs(obj.matrix_world.determinant()) > .001 for obj in parts), "Kit has singular transform")
        _check(abs((_bounds(_role(scene, 'stair'))[0][1] - _bounds(_role(scene, 'stair'))[0][0]) - opening) < 1e-5,
               "Entrance stair width does not fit doorway")
        _check(len(left.data.vertices) == 8 and len(corners[0].data.vertices) == 14
               and len(_role(scene, 'stair').data.vertices) == 20, "Control unexpectedly rebuilt kit geometry")
        return {'wall_span': _bounds(left)[0][1] - _bounds(left)[0][0], 'door_opening': opening,
                'door_seam_error': max(errors), 'corner_pivot_error': max(pivot_errors), 'kit_parts': len(parts),
                'unique_meshes': len({obj.data.name for obj in parts}), 'atlas_size': list(atlas.size),
                'part_shade_ranges': shade_ranges,
                'stair_width': _bounds(_role(scene, 'stair'))[0][1] - _bounds(_role(scene, 'stair'))[0][0]}
    if lab == 'BL-008':
        parts = [_role(scene, role) for role in ('texture_only', 'vertex_unlit', 'vertex_lit')]
        geometry = [tuple(tuple(vertex.co) for vertex in obj.data.vertices) for obj in parts]
        _check(geometry[0] == geometry[1] == geometry[2], "Comparison geometry differs")
        images = [next(node.image for node in obj.data.materials[0].node_tree.nodes if node.type == 'TEX_IMAGE') for obj in parts]
        _check(images[0] == images[1] == images[2] and images[0].packed_file, "Comparison texture differs or is unpacked")
        signatures = []
        for obj in parts:
            tree = obj.data.materials[0].node_tree
            output = tree.nodes['Material Output'].inputs['Surface']
            _check(output.is_linked, "Comparison has no output shader")
            signatures.append(output.links[0].from_node.type)
        _check(signatures == ['EMISSION', 'EMISSION', 'BSDF_PRINCIPLED'], "Comparison shader modes differ from authored contract")
        for obj in parts[1:]:
            tree = obj.data.materials[0].node_tree
            mix = tree.nodes['Vertex shade strength']
            _check(abs(mix.inputs[0].default_value - value / 2) < 1e-5, "Vertex strength control missed target")
            _check(mix.inputs[1].is_linked and mix.inputs[2].is_linked and mix.outputs[0].is_linked, "Vertex composition graph is disconnected")
        shades = parts[0].data.color_attributes['AuthoredShade'].data
        luminance = [entry.color[0] for entry in shades]
        _check(max(luminance) - min(luminance) > .4, "Authored shades do not vary across silhouette")
        return {'identical_vertices': len(parts[0].data.vertices), 'shader_modes': signatures,
                'vertex_strength': parts[1].data.materials[0].node_tree.nodes['Vertex shade strength'].inputs[0].default_value,
                'shade_range': [min(luminance), max(luminance)],
                'packed_atlases': 1}
    if lab == 'BL-009':
        cards = [obj for obj in scene.objects if str(obj.get('authoring_role', '')).startswith(('contact_', 'shaft_'))]
        _check({obj['authoring_role'] for obj in cards} == {'contact_0', 'contact_1', 'contact_2', 'shaft_0', 'shaft_1'}
               and len(cards) == 5, "Atmosphere authored card set is incomplete or duplicated")
        _check(all(obj.type == 'MESH' and len(obj.data.polygons) == 1
                   and len(obj.data.polygons[0].vertices) == 4 and obj.data.uv_layers for obj in cards),
               "Atmosphere cards must be editable UV-mapped quads")
        for prefix, roles in (('contact', ('contact_0', 'contact_1', 'contact_2')), ('shaft', ('shaft_0', 'shaft_1'))):
            _check(len({_role(scene, role).data.materials[0].name for role in roles}) == 1,
                   f"Atmosphere {prefix} cards no longer share their authored material")
        texture_ranges = []
        for role in ('contact_0', 'shaft_0'):
            mat = _role(scene, role).data.materials[0]
            tree = mat.node_tree
            texture = next(node for node in tree.nodes if node.type == 'TEX_IMAGE')
            image = texture.image
            alpha = list(image.pixels)[3::4]
            _check(image.packed_file and max(alpha) > .8 and min(alpha) < .01, "Atmosphere texture lacks packed alpha gradient")
            intensity = tree.nodes['Atmosphere intensity']
            _check(abs(intensity.inputs[1].default_value - value * .45) < 1e-5, "Atmosphere control missed target")
            mix = next(node for node in tree.nodes if node.type == 'MIX_SHADER')
            transparent = next(node for node in tree.nodes if node.type == 'BSDF_TRANSPARENT')
            emission = next(node for node in tree.nodes if node.type == 'EMISSION')
            output = next(node for node in tree.nodes if node.type == 'OUTPUT_MATERIAL')
            _check(intensity.operation == 'MULTIPLY'
                   and _connection(tree, texture.outputs['Alpha'], intensity.inputs[0])
                   and _connection(tree, intensity.outputs[0], mix.inputs[0])
                   and _connection(tree, transparent.outputs[0], mix.inputs[1])
                   and _connection(tree, texture.outputs['Color'], emission.inputs['Color'])
                   and _connection(tree, emission.outputs[0], mix.inputs[2])
                   and _connection(tree, mix.outputs[0], output.inputs['Surface']),
                   "Atmosphere texture alpha / shader mix output path is disconnected")
            _check(mat.surface_render_method == 'DITHERED', "Atmosphere material is not configured for alpha surfaces")
            texture_ranges.append([min(alpha), max(alpha)])
        shaft = _role(scene, 'shaft_0')
        normal = shaft.data.polygons[0].normal
        _check(abs(normal.y) > .2 and abs(normal.z) > .2, "Shaft card has no depth/angle composition")
        _check(abs(_bounds(_role(scene, 'contact_0'))[2][0] - .012) < 1e-5, "Contact card lost floor separation")
        return {'card_count': len(cards), 'alpha_ranges': texture_ranges,
                'intensity_multiplier': _role(scene, 'shaft_0').data.materials[0].node_tree.nodes['Atmosphere intensity'].inputs[1].default_value,
                'shaft_normal': list(normal), 'contact_floor_offset': .012,
                'surface_render_method': 'DITHERED'}
    raise ValueError(f"No authoring verifier for {lab}")
