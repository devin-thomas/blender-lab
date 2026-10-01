"""Owned, editable material, bake and world-lighting experiments."""
from array import array
import hashlib
import math
from pathlib import Path
import tempfile
import time
from uuid import uuid4

import bpy


DEFAULTS = {
    'BL-016': {'Bake size': 128, 'Margin': 4},
    'BL-036': {'Schema version': 2, 'Tint strength': 0.25},
    'BL-058': {'World strength': 0.5, 'Rotation': 0.0},
    'BL-059': {'Pattern scale': 4.0, 'Roughness': 0.8},
}

_ROLE_KEY = 'surface_role'
_INSTANCE_KEY = 'surface_instance_id'
_PENDING_GATES = [
    'full-card workload and execution-profile qualification pending',
    'native editor interaction and reset acceptance pending',
    'artist visual review pending',
    'renderer and color-space parity pending',
]


def _check(condition, message):
    if not condition:
        raise AssertionError(message)


def _instance(scene):
    return str(scene.get('blender_lab_instance_id', scene.name))


def _tag(id_block, scene, role):
    id_block[_ROLE_KEY] = role
    id_block[_INSTANCE_KEY] = _instance(scene)
    return id_block


def _role(scene, role):
    found = [obj for obj in scene.objects
             if obj.get(_ROLE_KEY) == role and obj.get(_INSTANCE_KEY) == _instance(scene)]
    _check(len(found) == 1, f"Expected one owned surface object {role!r}; found {len(found)}")
    return found[0]


def _owned_image(scene, role):
    found = [image for image in bpy.data.images
             if image.get(_ROLE_KEY) == role and image.get(_INSTANCE_KEY) == _instance(scene)]
    _check(len(found) == 1, f"Expected one owned surface image {role!r}; found {len(found)}")
    return found[0]


def _owned_material(scene, role):
    found = [material for material in bpy.data.materials
             if material.get(_ROLE_KEY) == role and material.get(_INSTANCE_KEY) == _instance(scene)]
    _check(len(found) == 1, f"Expected one owned surface material {role!r}; found {len(found)}")
    return found[0]


def _validate_base(scene, obj):
    _check(obj is not None and obj.name in bpy.data.objects and scene.objects.get(obj.name) == obj,
           'Disposable base subject is missing from its lab scene')
    _check(len(obj.users_scene) == 1 and obj.users_scene[0] == scene,
           'Disposable base subject is shared outside its lab scene')
    return obj


def _new_image(scene, name, width, height, role):
    image = bpy.data.images.new(name, width=width, height=height, alpha=True, float_buffer=False)
    return _tag(image, scene, role)


def _pixels(image):
    # Pixel access lazily decodes packed buffers after a save/reopen.
    count = len(image.pixels)
    _check(image.has_data and count == image.size[0] * image.size[1] * 4,
           f"Image {image.name!r} has no decoded RGBA pixel buffer")
    result = array('f', [0.0]) * count
    image.pixels.foreach_get(result)
    return result


def _fill_sky(image):
    width, height = image.size
    values = array('f')
    for y in range(height):
        v = y / max(1, height - 1)
        for x in range(width):
            u = x / max(1, width - 1)
            horizon = math.exp(-((v - .54) / .15) ** 2)
            warm_band = math.exp(-((u - .68) / .12) ** 2) * horizon
            cool_band = math.exp(-((u - .18) / .17) ** 2) * horizon
            color = (.025 + .48 * warm_band + .08 * cool_band,
                     .055 + .19 * warm_band + .22 * cool_band,
                     .13 + .035 * warm_band + .24 * cool_band)
            values.extend((*color, 1.0))
    image.pixels.foreach_set(values)
    image.update()
    image.pack()


def _new_principled(name, color=(.76, .31, .09), roughness=.8):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    tree = material.node_tree
    tree.nodes.clear()
    output = tree.nodes.new('ShaderNodeOutputMaterial')
    output.location = (420, 80)
    shader = tree.nodes.new('ShaderNodeBsdfPrincipled')
    shader.location = (160, 80)
    shader.inputs['Base Color'].default_value = (*color, 1.0)
    shader.inputs['Roughness'].default_value = roughness
    tree.links.new(shader.outputs['BSDF'], output.inputs['Surface'])
    return material, shader


def _uv_box(obj):
    """Create separate planar UV islands for each side of the original mesh."""
    mesh = obj.data
    _check(obj.type == 'MESH' and len(mesh.polygons) > 0,
           'UV box projection requires a nonempty mesh subject')
    mesh.update()
    uv = mesh.uv_layers.get('BL UV') or mesh.uv_layers.new(name='BL UV')
    face_count = len(mesh.polygons)
    columns = max(1, math.ceil(math.sqrt(face_count)))
    rows = max(1, math.ceil(face_count / columns))
    inset = .07
    for face_index, polygon in enumerate(mesh.polygons):
        drop_axis = max(range(3), key=lambda axis: abs(polygon.normal[axis]))
        axes = [axis for axis in range(3) if axis != drop_axis]
        points = [mesh.vertices[mesh.loops[index].vertex_index].co for index in polygon.loop_indices]
        limits = [(min(point[axis] for point in points), max(point[axis] for point in points)) for axis in axes]
        _check(all(high - low > 1e-8 for low, high in limits),
               'UV box projection found a degenerate face')
        column, row = face_index % columns, face_index // columns
        for loop_index, point in zip(polygon.loop_indices, points):
            values = [min(1.0, max(0.0, (point[axis] - low) / (high - low)))
                      for axis, (low, high) in zip(axes, limits)]
            u = (column + inset + values[0] * (1 - 2 * inset)) / columns
            v = (row + inset + values[1] * (1 - 2 * inset)) / rows
            uv.data[loop_index].uv = (u, v)
    mesh.uv_layers.active = uv
    return uv


def _uv_box_metrics(obj):
    uv = obj.data.uv_layers.active
    _check(uv is not None and uv.name == 'BL UV', 'Fixture is missing its active BL UV map')
    areas, bounds = [], []
    for polygon in obj.data.polygons:
        points = [uv.data[index].uv for index in polygon.loop_indices]
        area = abs(sum(points[index].x * points[(index + 1) % len(points)].y
                       - points[(index + 1) % len(points)].x * points[index].y
                       for index in range(len(points))) * .5)
        _check(area > 1e-8, 'Fixture contains a zero-area UV face')
        areas.append(float(area))
        bounds.append([float(min(point[0] for point in points)), float(max(point[0] for point in points)),
                       float(min(point[1] for point in points)), float(max(point[1] for point in points))])
    for index, left in enumerate(bounds):
        for right in bounds[index + 1:]:
            overlap_u = min(left[1], right[1]) - max(left[0], right[0])
            overlap_v = min(left[3], right[3]) - max(left[2], right[2])
            _check(overlap_u <= 1e-7 or overlap_v <= 1e-7,
                   'Generated face UV islands overlap')
    return {'active_uv_layer': uv.name, 'face_count': len(areas),
            'uv_face_areas': areas, 'uv_face_bounds': bounds}


def _uv_subject(obj):
    return _uv_box(obj)


def _copy_subject(scene, source, role, name, x):
    copy = source.copy()
    copy.data = source.data.copy()
    copy.name = name
    scene.collection.objects.link(copy)
    copy.location.x = x
    _tag(copy, scene, role)
    _tag(copy.data, scene, role + '_mesh')
    return copy


def _private_mesh(scene, obj, role):
    _check(obj.type == 'MESH' and obj.data is not None, 'Surface fixture requires a mesh base subject')
    old_mesh = obj.data
    new_mesh = old_mesh.copy()
    _tag(new_mesh, scene, role + '_mesh')
    obj.data = new_mesh
    return new_mesh


def _sample_pixels(image, points):
    pixels = _pixels(image)
    width, height = image.size
    samples = []
    for u, v in points:
        x = min(width - 1, max(0, round(u * (width - 1))))
        y = min(height - 1, max(0, round(v * (height - 1))))
        start = (y * width + x) * 4
        samples.append([float(pixels[start + channel]) for channel in range(3)])
    return samples


def _scene_render_state(scene):
    return {
        'engine': scene.render.engine,
        'resolution_x': scene.render.resolution_x,
        'resolution_y': scene.render.resolution_y,
        'resolution_percentage': scene.render.resolution_percentage,
        'filepath': scene.render.filepath,
        'file_format': scene.render.image_settings.file_format,
        'color_mode': scene.render.image_settings.color_mode,
        'color_depth': scene.render.image_settings.color_depth,
        'samples': scene.cycles.samples,
    }


def _render_probe(scene, deadline=None):
    """Render a tiny temporary PNG, read its real pixels, and restore render state."""
    _check(scene.camera is not None, 'A preview camera is required for the bounded surface probe')
    render = scene.render
    previous = _scene_render_state(scene)
    started = time.monotonic()
    if deadline is not None and started >= deadline:
        raise TimeoutError('Surface verification reached its 180-second lab cap')
    try:
        render.engine = 'CYCLES'
        render.resolution_x = 96
        render.resolution_y = 72
        render.resolution_percentage = 100
        render.image_settings.file_format = 'PNG'
        render.image_settings.color_mode = 'RGBA'
        render.image_settings.color_depth = '8'
        scene.cycles.samples = 2
        with tempfile.TemporaryDirectory(prefix='bl-surface-probe-') as directory:
            path = Path(directory) / f'preview-{uuid4().hex}.png'
            render.filepath = str(path)
            result = bpy.ops.render.render(write_still=True, scene=scene.name)
            _check(result == {'FINISHED'}, 'Bounded Cycles preview did not finish')
            _check(time.monotonic() - started < 180 and (deadline is None or time.monotonic() < deadline),
                   'Bounded preview exceeded its 180-second lab cap')
            _check(path.is_file(), 'Bounded preview did not write its temporary PNG')
            image = bpy.data.images.load(str(path), check_existing=False)
            try:
                width, height = image.size
                _check((width, height) == (96, 72), 'Bounded preview returned unexpected dimensions')
                count = len(image.pixels)
                _check(count == width * height * 4, 'Bounded preview has an invalid pixel buffer')
                pixels = array('f', [0.0]) * count
                image.pixels.foreach_get(pixels)
                _check(image.has_data, 'Bounded preview PNG could not be decoded')
                return width, height, pixels
            finally:
                bpy.data.images.remove(image)
    finally:
        render.engine = previous['engine']
        render.resolution_x = previous['resolution_x']
        render.resolution_y = previous['resolution_y']
        render.resolution_percentage = previous['resolution_percentage']
        render.filepath = previous['filepath']
        render.image_settings.file_format = previous['file_format']
        render.image_settings.color_mode = previous['color_mode']
        render.image_settings.color_depth = previous['color_depth']
        scene.cycles.samples = previous['samples']


def _pixel_metrics(width, height, pixels):
    luminance = []
    for index in range(0, len(pixels), 4):
        luminance.append(.2126 * pixels[index] + .7152 * pixels[index + 1] + .0722 * pixels[index + 2])
    mean = sum(luminance) / len(luminance)
    variance = sum((value - mean) ** 2 for value in luminance) / len(luminance)
    row = height // 2
    samples = [luminance[row * width + x] for x in range(width)]
    transitions = sum(abs(right - left) > .035 for left, right in zip(samples, samples[1:]))
    return {'preview_dimensions': [width, height],
            'preview_sha256': hashlib.sha256(pixels.tobytes()).hexdigest(),
            'preview_luminance_mean': mean,
            'preview_luminance_variance': variance, 'center_row_transitions': transitions}


def _pixel_difference(left, right):
    _check(len(left) == len(right) and len(left) > 0, 'Rendered control probes have mismatched pixel buffers')
    values = [abs(a - b) for a, b in zip(left, right)]
    return {'mean_absolute_channel_difference': sum(values) / len(values),
            'maximum_channel_difference': max(values)}


def _bake_material(name, image=None, procedural=False):
    material, shader = _new_principled(name)
    tree = material.node_tree
    color_socket = shader.inputs['Base Color']
    if procedural:
        texcoord = tree.nodes.new('ShaderNodeTexCoord')
        texcoord.location = (-760, 80)
        noise = tree.nodes.new('ShaderNodeTexNoise')
        noise.location = (-530, 80)
        noise.inputs['Scale'].default_value = 4
        ramp = tree.nodes.new('ShaderNodeValToRGB')
        ramp.location = (-270, 80)
        ramp.color_ramp.elements[0].position = .2
        ramp.color_ramp.elements[0].color = (.08, .12, .16, 1)
        ramp.color_ramp.elements[1].position = .78
        ramp.color_ramp.elements[1].color = (.88, .4, .12, 1)
        tree.links.new(texcoord.outputs['Generated'], noise.inputs['Vector'])
        tree.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
        tree.links.new(ramp.outputs['Color'], color_socket)
        material['source_graph'] = 'Original generated-coordinate Noise to copper ramp'
    if image is not None:
        target = tree.nodes.new('ShaderNodeTexImage')
        target.name = 'BL Bake Target'
        target.label = 'Active Cycles bake image'
        target.image = image
        target.location = (-500, -200)
        tree.nodes.active = target
        material['bake_target_node'] = target.name
    return material


def _bake_inputs(scene):
    subject, portable = _role(scene, 'bake_source'), _role(scene, 'bake_portable')
    image = _owned_image(scene, 'bake_image')
    _check(subject.type == 'MESH' and subject.data.uv_layers.active is not None,
           'Bake source is missing its UV map')
    source_mat = subject.data.materials[0] if subject.data.materials else None
    _check(source_mat is not None and source_mat.use_nodes, 'Bake source has no editable node material')
    target = source_mat.node_tree.nodes.get('BL Bake Target')
    _check(target is not None and target.type == 'TEX_IMAGE' and target.image == image
           and source_mat.node_tree.nodes.active == target,
           'Bake source target image is missing or is not the active image node')
    _check(portable.data.materials and portable.data.materials[0] is not None,
           'Portable comparison subject has no image material')
    return subject, portable, source_mat, target, image


def _apply_bake(scene, params):
    size, margin = params['Bake size'], params['Margin']
    _check(isinstance(size, int) and not isinstance(size, bool), 'Bake size must be integer pixels')
    _check(isinstance(margin, int) and not isinstance(margin, bool), 'Margin must be integer pixels')
    _check(32 <= size <= 512 and 0 <= margin <= 16, 'Bake controls are outside their declared bounds')
    subject, portable, source_mat, target, previous_image = _bake_inputs(scene)
    image = _new_image(scene, f"BL-016 bake staging {size}", size, size, 'bake_image_staging')
    previous_target = target.image
    old_engine = scene.render.engine
    bake_settings = scene.render.bake
    old_bake = (bake_settings.margin, bake_settings.use_pass_color,
                bake_settings.use_pass_direct, bake_settings.use_pass_indirect)
    view_layer = bpy.context.view_layer
    old_active = view_layer.objects.active
    old_selection = [(obj, obj.select_get()) for obj in view_layer.objects]
    baked = False
    try:
        target.image = image
        scene.render.engine = 'CYCLES'
        bake_settings.margin = margin
        bake_settings.use_pass_color = True
        bake_settings.use_pass_direct = False
        bake_settings.use_pass_indirect = False
        for obj, _ in old_selection:
            obj.select_set(False)
        subject.select_set(True)
        view_layer.objects.active = subject
        result = bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, use_clear=True, margin=margin)
        _check(result == {'FINISHED'}, 'Cycles diffuse-color bake did not finish')
        values = _pixels(image)
        _check(any(value > 1e-5 for value in values), 'Cycles bake produced an empty image')
        image.pack()
        target.image = image
        portable_tex = portable.data.materials[0].node_tree.nodes.get('Baked copper color')
        _check(portable_tex is not None and portable_tex.type == 'TEX_IMAGE',
               'Portable material is missing its declared image node')
        portable_tex.image = image
        baked = True
    finally:
        if not baked:
            target.image = previous_target
            portable_tex = portable.data.materials[0].node_tree.nodes.get('Baked copper color')
            if portable_tex is not None:
                portable_tex.image = previous_image
            if image.users == 0:
                bpy.data.images.remove(image)
        scene.render.engine = old_engine
        bake_settings.margin, bake_settings.use_pass_color, bake_settings.use_pass_direct, bake_settings.use_pass_indirect = old_bake
        for obj, selected in old_selection:
            if obj.name in bpy.data.objects:
                obj.select_set(selected)
        if old_active is not None and old_active.name in bpy.data.objects:
            view_layer.objects.active = old_active
    if previous_image != image and previous_image.get(_ROLE_KEY) == 'bake_image' and previous_image.users == 0:
        bpy.data.images.remove(previous_image)
    elif previous_image != image and previous_image.get(_ROLE_KEY) == 'bake_image':
        previous_image[_ROLE_KEY] = 'bake_image_retained'
    image[_ROLE_KEY] = 'bake_image'
    _tag(image, scene, 'bake_image')
    scene['surface_bake_image'] = image.name
    scene['surface_bake_margin'] = margin


def _build_bake(scene, base_subject):
    subject = _validate_base(scene, base_subject)
    subject.name = 'Bake bridge / editable procedural source'
    _private_mesh(scene, subject, 'bake_source')
    subject.location.x = -.85
    _tag(subject, scene, 'bake_source')
    _uv_subject(subject)
    image = _new_image(scene, 'BL-016 initial bake image', 128, 128, 'bake_image')
    source_mat = _bake_material('BL-016 procedural copper source', image=image, procedural=True)
    _tag(source_mat, scene, 'bake_source_material')
    subject.data.materials.clear()
    subject.data.materials.append(source_mat)
    portable = _copy_subject(scene, subject, 'bake_portable', 'Bake bridge / portable image material', .85)
    portable_mat = _bake_material('BL-016 portable baked material')
    target_node = portable_mat.node_tree.nodes.new('ShaderNodeTexImage')
    target_node.name = 'Baked copper color'
    target_node.label = 'Portable baked color / packed image'
    target_node.image = image
    target_node.location = (-500, 80)
    shader = portable_mat.node_tree.nodes.get('Principled BSDF')
    portable_mat.node_tree.links.new(target_node.outputs['Color'], shader.inputs['Base Color'])
    _tag(portable_mat, scene, 'bake_portable_material')
    portable.data.materials.clear()
    portable.data.materials.append(portable_mat)
    scene['surface_bake_image'] = image.name
    _apply_bake(scene, DEFAULTS['BL-016'])
    return subject


def _bake_verify(scene, params):
    subject, portable, source_mat, target, image = _bake_inputs(scene)
    expected = (params['Bake size'], params['Bake size'])
    _check(tuple(image.size) == expected and image.packed_file is not None,
           'Bake image dimensions or packed persistence do not match the request')
    values = _pixels(image)
    alpha = values[3::4]
    _check(max(values[0::4]) - min(values[0::4]) > .02,
           'Baked copper source contains no measurable color variation')
    _check(all(0 <= value <= 1 for value in alpha), 'Baked alpha values are outside the image range')
    portable_tree = portable.data.materials[0].node_tree
    portable_tex = portable_tree.nodes.get('Baked copper color')
    shader = portable_tree.nodes.get('Principled BSDF')
    _check(portable_tex is not None and portable_tex.image == image and shader is not None
           and any(link.from_node == portable_tex and link.to_socket == shader.inputs['Base Color']
                   for link in portable_tree.links), 'Portable material does not use the baked image for Base Color')
    samples = _sample_pixels(image, ((.2, .5), (.5, .5), (.8, .5)))
    covered_pixels = sum(1 for index in range(0, len(values), 4)
                         if any(values[index + channel] > 1e-5 for channel in range(3)))
    alpha_covered_pixels = sum(value > 1e-5 for value in alpha)
    pixel_digest = hashlib.sha256(values.tobytes()).hexdigest()
    _check(scene.get('surface_bake_margin') == params['Margin'],
           'Applied bake margin does not match the owned bake receipt')
    return {'image_dimensions': list(image.size), 'packed': image.packed_file is not None,
            'pixel_count': len(image.pixels) // 4, 'margin_pixels': params['Margin'],
            'margin_coverage_pixels': covered_pixels,
            'margin_alpha_coverage_pixels': alpha_covered_pixels,
            'baked_rgba_sha256': pixel_digest,
            'baked_pixel_sha256': pixel_digest,
            'margin_pixel_selector': 'covered RGB/alpha pixels and packed RGBA digest',
            'sample_uv': [[.2, .5], [.5, .5], [.8, .5]], 'baked_rgb_samples': samples,
            'red_channel_range': [float(min(values[0::4])), float(max(values[0::4]))],
            'active_target_node': target.name, 'portable_base_color_linked': True,
            'matched_preview_difference': None,
            'matched_preview_gate': 'rendered source/portable tolerance remains pending'}


def _image_fixture(scene, role, name, width=32, height=32):
    image = _new_image(scene, name, width, height, role)
    values = array('f')
    for y in range(height):
        for x in range(width):
            band = (x // max(1, width // 4)) % 4
            mortar = y % max(1, height // 8) == 0
            colors = ((.12, .22, .27), (.32, .18, .1), (.76, .34, .12), (.95, .66, .25))
            color = (.035, .07, .1) if mortar else colors[band]
            values.extend((*color, 1.0))
    image.pixels.foreach_set(values)
    image.update()
    image.pack()
    return image


def _migration_fixture(scene, base_subject):
    subject = _validate_base(scene, base_subject)
    subject.name = 'Graph migration / original v1 subject'
    _private_mesh(scene, subject, 'migration_subject')
    _tag(subject, scene, 'migration_subject')
    _uv_box(subject)
    image = _image_fixture(scene, 'migration_image', 'BL-036 original packed UV texture')
    material, shader = _new_principled('BL-036 material schema v1')
    tree = material.node_tree
    uv = tree.nodes.new('ShaderNodeTexCoord')
    uv.name = 'Source UV'
    uv.location = (-700, 100)
    tex = tree.nodes.new('ShaderNodeTexImage')
    tex.name = 'Source image'
    tex.image = image
    tex.location = (-450, 100)
    tree.links.new(uv.outputs['UV'], tex.inputs['Vector'])
    tree.links.new(tex.outputs['Color'], shader.inputs['Base Color'])
    sentinel = tree.nodes.new('ShaderNodeValue')
    sentinel.name = 'User sentinel / preserve'
    sentinel.label = 'Unrelated user node / preserve through migration'
    sentinel.location = (-410, -220)
    sentinel.outputs[0].default_value = .375
    material['surface_schema_version'] = 1
    material.use_fake_user = True
    _tag(material, scene, 'migration_v1_material')
    subject.data.materials.clear()
    subject.data.materials.append(material)
    subject['surface_v1_material_name'] = material.name
    scene['surface_migration_subject'] = subject.name
    return subject


def _schema(material):
    return int(material.get('surface_schema_version', 0))


def _validate_v1(material):
    tree = material.node_tree
    shader = tree.nodes.get('Principled BSDF')
    tex = tree.nodes.get('Source image')
    uv = tree.nodes.get('Source UV')
    sentinel = tree.nodes.get('User sentinel / preserve')
    _check(shader is not None and tex is not None and tex.type == 'TEX_IMAGE' and tex.image is not None,
           'Known v1 source image/Principled nodes are missing')
    _check(uv is not None and uv.bl_idname == 'ShaderNodeTexCoord'
           and any(link.from_node == uv and link.to_node == tex for link in tree.links),
           'Known v1 UV input is missing or disconnected')
    _check(sentinel is not None and sentinel.type == 'VALUE', 'Unrelated user-node sentinel is missing')
    _check(any(link.from_node == tex and link.to_socket == shader.inputs['Base Color'] for link in tree.links),
           'Known v1 material output connection is unsupported')
    return tex, shader, sentinel


def _migrate_v1(source, tint_strength):
    stage = source.copy()
    stage.use_fake_user = False
    stage.name = 'BL-036 staged schema v2 material'
    tex, shader, sentinel = _validate_v1(stage)
    tree = stage.node_tree
    old_link = next(link for link in tree.links
                    if link.from_node == tex and link.to_socket == shader.inputs['Base Color'])
    old_from = old_link.from_socket
    tree.links.remove(old_link)
    mix = tree.nodes.new('ShaderNodeMixRGB')
    mix.name = 'V2 tint contribution'
    mix.label = 'Schema v2 / bounded copper tint'
    mix.blend_type = 'MIX'
    mix.location = (-100, 100)
    mix.inputs['Fac'].default_value = tint_strength
    mix.inputs[2].default_value = (.82, .3, .09, 1)
    tree.links.new(old_from, mix.inputs[1])
    tree.links.new(mix.outputs['Color'], shader.inputs['Base Color'])
    stage['surface_schema_version'] = 2
    stage['surface_migration'] = 'v1 UV image graph -> v2 bounded copper tint'
    _check(tree.nodes.get(sentinel.name) == sentinel,
           'Staged migration failed to preserve the unrelated user-node sentinel')
    return stage


def _migration_apply(scene, params):
    version, tint = params['Schema version'], params['Tint strength']
    _check(isinstance(version, int) and not isinstance(version, bool) and version in (1, 2),
           'Only known material schema versions 1 and 2 can be selected')
    _check(0 <= tint <= 1, 'Tint strength must remain between zero and one')
    subject = _role(scene, 'migration_subject')
    original = _owned_material(scene, 'migration_v1_material')
    _check(_schema(original) == 1, 'Original v1 graph schema changed; refusing automatic migration')
    if version == 1:
        _validate_v1(original)
        previous = subject.data.materials[0] if subject.data.materials else None
        subject.data.materials[0] = original
        if previous is not None and previous != original and previous.get(_ROLE_KEY) == 'migration_v2_material' and previous.users == 0:
            bpy.data.materials.remove(previous)
        return
    current = subject.data.materials[0]
    current_version = _schema(current)
    if current_version == 2:
        existing_mix = current.node_tree.nodes.get('V2 tint contribution')
        _check(existing_mix is not None and existing_mix.bl_idname == 'ShaderNodeMixRGB',
               'Current v2 graph is unsupported; original v1 remains available')
        _validate_v2(current, float(existing_mix.inputs['Fac'].default_value))
    else:
        _check(current_version == 1, 'Unknown graph schema blocks automatic mutation')
        _validate_v1(current)

    stage = None
    committed = False
    try:
        if current_version == 2:
            stage = current.copy()
            stage.use_fake_user = False
            stage.name = 'BL-036 staged schema v2 update'
            stage.node_tree.nodes['V2 tint contribution'].inputs['Fac'].default_value = tint
        else:
            stage = _migrate_v1(current, tint)
        _tag(stage, scene, 'migration_v2_material')
        _validate_v2(stage, tint)
        subject.data.materials[0] = stage
        committed = True
    finally:
        if not committed and stage is not None and stage.users == 0:
            bpy.data.materials.remove(stage)
    if current != stage and current.get(_ROLE_KEY) == 'migration_v2_material' and current.users == 0:
        bpy.data.materials.remove(current)


def _validate_v2(material, tint):
    tree = material.node_tree
    tex = tree.nodes.get('Source image')
    uv = tree.nodes.get('Source UV')
    shader = tree.nodes.get('Principled BSDF')
    sentinel = tree.nodes.get('User sentinel / preserve')
    _check(tex is not None and tex.type == 'TEX_IMAGE' and tex.image is not None
           and uv is not None and uv.bl_idname == 'ShaderNodeTexCoord'
           and any(link.from_node == uv and link.to_node == tex for link in tree.links),
           'V2 schema lost its source image or UV input')
    _check(shader is not None and sentinel is not None and sentinel.type == 'VALUE',
           'V2 schema lost its Principled output or unrelated user sentinel')
    mix = tree.nodes.get('V2 tint contribution')
    _check(mix is not None and mix.bl_idname == 'ShaderNodeMixRGB', 'V2 tint node is missing')
    _check(abs(mix.inputs['Fac'].default_value - tint) < 1e-6,
           'V2 tint node does not match the selected contribution')
    _check(any(link.from_node == tex and link.to_socket == mix.inputs[1] for link in tree.links)
           and any(link.from_node == mix and link.to_socket == shader.inputs['Base Color'] for link in tree.links),
           'V2 contribution is not connected through to Principled Base Color')
    _check(tree.nodes.get(sentinel.name) == sentinel, 'V2 migration dropped the unrelated user-node sentinel')
    return tex, shader, mix


def _migration_verify(scene, params):
    subject = _role(scene, 'migration_subject')
    material = subject.data.materials[0]
    version = params['Schema version']
    _check(_schema(material) == version, 'Selected schema version is not the assigned graph version')
    original = _owned_material(scene, 'migration_v1_material')
    _check(_schema(original) == 1, 'Original v1 recovery graph was not retained')
    uv_metrics = _uv_box_metrics(subject)
    if version == 1:
        tex, shader, sentinel = _validate_v1(material)
        strength = 0.0
        mix = None
    else:
        tex, shader, mix = _validate_v2(material, params['Tint strength'])
        sentinel = material.node_tree.nodes.get('User sentinel / preserve')
        strength = float(mix.inputs['Fac'].default_value)
    image = tex.image
    _check(image is not None and image.packed_file is not None, 'Migration lost its packed original image dependency')
    reference_uv = ((.167, .3), (.5, .3), (.833, .3),
                    (.167, .7), (.5, .7), (.833, .7))
    samples = _sample_pixels(image, reference_uv)
    tint = [float(value) for value in material.node_tree.nodes.get('V2 tint contribution').inputs[2].default_value[:3]] if version == 2 else None
    migrated = [[(1 - strength) * channel + strength * target for channel, target in zip(pixel, tint)]
                for pixel in samples] if version == 2 else samples
    deadline = time.monotonic() + 180
    _, _, preview = _render_probe(scene, deadline)
    tree = material.node_tree
    color_input = mix.inputs[1] if mix is not None else shader.inputs['Base Color']
    texture_link = next((link for link in tree.links
                         if link.from_socket == tex.outputs['Color'] and link.to_socket == color_input), None)
    _check(texture_link is not None, 'Original packed image does not feed the rendered material patch')
    old_color = tuple(color_input.default_value)
    try:
        tree.links.remove(texture_link)
        color_input.default_value = (.45, .45, .45, 1.0)
        _, _, flat_preview = _render_probe(scene, deadline)
    finally:
        color_input.default_value = old_color
        tree.links.new(tex.outputs['Color'], color_input)
    texture_effect = _pixel_difference(preview, flat_preview)
    texture_visibility = 'masked-by-full-tint' if version == 2 and strength >= 1 - 1e-6 else 'measured'
    if texture_visibility == 'masked-by-full-tint':
        _check(texture_effect['mean_absolute_channel_difference'] <= 1e-6,
               'Full tint should mask the packed texture contribution')
    else:
        _check(texture_effect['mean_absolute_channel_difference'] > 1e-6,
               'Packed UV image did not change rendered pixels on the migration fixture')
    preview_digest = hashlib.sha256(preview.tobytes()).hexdigest()
    preview_stats = _pixel_metrics(96, 72, preview)
    tint_effect = None
    if mix is not None:
        original_strength = float(mix.inputs['Fac'].default_value)
        try:
            mix.inputs['Fac'].default_value = 0.0 if original_strength > 0 else 1.0
            _, _, alternate = _render_probe(scene, deadline)
        finally:
            mix.inputs['Fac'].default_value = original_strength
        tint_effect = _pixel_difference(preview, alternate)
        _check(tint_effect['mean_absolute_channel_difference'] > 1e-6,
               'V2 tint did not change bounded rendered reference pixels')
    return {'schema_version': version, 'source_image_dimensions': list(image.size),
            'source_image_packed': image.packed_file is not None, 'uv_input_connected': True,
            'uv_layout': uv_metrics,
            'user_sentinel_value': float(sentinel.outputs[0].default_value),
            'tint_strength': strength, 'reference_uv': [list(uv) for uv in reference_uv],
            'source_reference_rgb': samples, 'migrated_reference_rgb': migrated,
            'rendered_textured_pixel_variance': preview_stats['preview_luminance_variance'],
            'texture_render_difference': texture_effect,
            'texture_visibility': texture_visibility,
            'base_color_reaches_surface': any(link.to_node.bl_idname == 'ShaderNodeOutputMaterial'
                                              for link in material.node_tree.links
                                              if link.from_node == shader),
            'recovery_schema_available': _schema(original),
            'tint_render_difference': tint_effect,
            'rendered_preview_sha256': preview_digest,
            'rendered_reference_patch_difference': None,
            'renderer_patch_gate': 'matched rendered patch comparison remains pending'}


def _world_fixture(scene, base_subject):
    subject = _validate_base(scene, base_subject)
    _private_mesh(scene, subject, 'world_reference')
    subject.name = 'Environment forge / neutral reference'
    subject.location = (0, 0, 1.2)
    _tag(subject, scene, 'world_reference')
    material, shader = _new_principled('BL-058 neutral reference material', (.72, .72, .72), .72)
    _tag(material, scene, 'world_reference_material')
    subject.data.materials.clear()
    subject.data.materials.append(material)
    image = _new_image(scene, 'BL-058 original 256x128 equirectangular sky', 256, 128, 'world_image')
    _fill_sky(image)
    world = bpy.data.worlds.new('BL-058 original environment world')
    _tag(world, scene, 'world_data')
    world.use_nodes = True
    tree = world.node_tree
    tree.nodes.clear()
    coordinates = tree.nodes.new('ShaderNodeTexCoord')
    coordinates.name = 'Environment direction'
    coordinates.location = (-760, 100)
    mapping = tree.nodes.new('ShaderNodeMapping')
    mapping.name = 'Environment rotation'
    mapping.location = (-520, 100)
    environment = tree.nodes.new('ShaderNodeTexEnvironment')
    environment.name = 'Original packed equirectangular sky'
    environment.image = image
    environment.projection = 'EQUIRECTANGULAR'
    environment.location = (-260, 100)
    background = tree.nodes.new('ShaderNodeBackground')
    background.name = 'Independent environment energy'
    background.location = (0, 100)
    output = tree.nodes.new('ShaderNodeOutputWorld')
    output.location = (240, 100)
    tree.links.new(coordinates.outputs['Generated'], mapping.inputs['Vector'])
    tree.links.new(mapping.outputs['Vector'], environment.inputs['Vector'])
    tree.links.new(environment.outputs['Color'], background.inputs['Color'])
    tree.links.new(background.outputs['Background'], output.inputs['Surface'])
    scene.world = world
    scene['surface_world_image'] = image.name
    return subject


def _world_nodes(scene):
    world = scene.world
    _check(world is not None and world.get(_ROLE_KEY) == 'world_data'
           and world.get(_INSTANCE_KEY) == _instance(scene) and world.use_nodes,
           'Owned environment world is missing')
    tree = world.node_tree
    mapping = tree.nodes.get('Environment rotation')
    environment = tree.nodes.get('Original packed equirectangular sky')
    background = tree.nodes.get('Independent environment energy')
    _check(mapping is not None and mapping.bl_idname == 'ShaderNodeMapping'
           and environment is not None and environment.bl_idname == 'ShaderNodeTexEnvironment'
           and background is not None and background.bl_idname == 'ShaderNodeBackground',
           'Environment graph is missing a declared node')
    image = _owned_image(scene, 'world_image')
    _check(environment.image == image and environment.projection == 'EQUIRECTANGULAR'
           and image.packed_file is not None, 'Environment image is unresolved or has the wrong projection')
    _check(tuple(image.size) == (256, 128), 'Environment image aspect/dimensions are unsupported')
    _check(any(link.from_node == mapping and link.to_node == environment for link in tree.links)
           and any(link.from_node == environment and link.to_node == background for link in tree.links),
           'Environment direction or energy graph link is missing')
    return mapping, environment, background, image


def _world_apply(scene, params):
    strength, rotation = params['World strength'], params['Rotation']
    _check(0 <= strength <= 2 and 0 <= rotation <= 360,
           'World controls are outside their declared bounds')
    mapping, _, background, _ = _world_nodes(scene)
    mapping.inputs['Rotation'].default_value[2] = math.radians(rotation)
    background.inputs['Strength'].default_value = strength


def _env_sample(image, azimuth, elevation, rotation, strength):
    # Sample the packed equirectangular image in the same mapped direction.
    longitude = (azimuth + rotation) % (2 * math.pi)
    u = (longitude / (2 * math.pi)) % 1.0
    v = min(1.0, max(0.0, .5 - elevation / math.pi))
    pixel = _sample_pixels(image, ((u, v),))[0]
    return [channel * strength for channel in pixel]


def _world_verify(scene, params):
    mapping, _, background, image = _world_nodes(scene)
    rotation = math.radians(params['Rotation'])
    actual_rotation = float(mapping.inputs['Rotation'].default_value[2])
    strength = float(background.inputs['Strength'].default_value)
    _check(abs(actual_rotation - rotation) < 1e-6 and abs(strength - params['World strength']) < 1e-6,
           'World controls did not reach the mapping/energy inputs')
    azimuths = (0.0, math.pi / 2, math.pi, 3 * math.pi / 2)
    elevation = .1
    raw_samples = [_env_sample(image, azimuth, elevation, rotation, 1.0) for azimuth in azimuths]
    samples = [[channel * strength for channel in color] for color in raw_samples]
    _check(len({tuple(round(channel, 4) for channel in color) for color in raw_samples}) > 1,
           'Packed world samples do not distinguish the authored directional bands')
    deadline = time.monotonic() + 180
    actual_width, actual_height, actual = _render_probe(scene, deadline)
    try:
        mapping.inputs['Rotation'].default_value[2] = (rotation + math.pi / 2) % (2 * math.pi)
        _, _, rotated = _render_probe(scene, deadline)
        background.inputs['Strength'].default_value = 0.0
        _, _, dark = _render_probe(scene, deadline)
    finally:
        mapping.inputs['Rotation'].default_value[2] = rotation
        background.inputs['Strength'].default_value = strength
    rotation_effect = _pixel_difference(actual, rotated)
    strength_effect = _pixel_difference(actual, dark)
    if strength > 0:
        _check(rotation_effect['mean_absolute_channel_difference'] > 1e-6,
               'World rotation did not change bounded rendered reference pixels')
        _check(strength_effect['mean_absolute_channel_difference'] > 1e-6,
               'World strength did not change bounded rendered reference pixels')
    else:
        _check(rotation_effect['mean_absolute_channel_difference'] < 1e-6
               and strength_effect['mean_absolute_channel_difference'] < 1e-6,
               'Zero-strength environment should render independently of rotation')
    preview_digest = hashlib.sha256(actual.tobytes()).hexdigest()
    return {'image_dimensions': list(image.size), 'image_packed': image.packed_file is not None,
            'projection': 'EQUIRECTANGULAR', 'rotation_degrees': params['Rotation'],
            'world_strength': strength, 'sample_azimuths_radians': list(azimuths),
            'directional_reference_rgb': raw_samples, 'reference_rgb_times_strength': samples,
            'rendered_preview_dimensions': [actual_width, actual_height],
            'rendered_preview_sha256': preview_digest,
            'rendered_preview_sha256_selector': preview_digest,
            'rotation_render_difference': rotation_effect,
            'strength_render_difference': strength_effect,
            'rotation_effect_gate': 'unobservable while strength is zero' if strength == 0 else 'measured',
            'background_color_linked': True, 'reference_object_role': _role(scene, 'world_reference').get(_ROLE_KEY)}


def _procedural_material(scene, role, name, stone=False):
    material, shader = _new_principled(name)
    _tag(material, scene, role)
    tree = material.node_tree
    tree.nodes.clear()
    output = tree.nodes.new('ShaderNodeOutputMaterial')
    output.location = (620, 100)
    shader = tree.nodes.new('ShaderNodeBsdfPrincipled')
    shader.location = (370, 100)
    shader.inputs['Roughness'].default_value = .8
    if shader.inputs.get('Specular IOR Level') is not None:
        shader.inputs['Specular IOR Level'].default_value = .5
    shader.inputs['Metallic'].default_value = .08
    coord = tree.nodes.new('ShaderNodeTexCoord')
    coord.name = 'Original generated coordinates'
    coord.location = (-850, 100)
    noise = tree.nodes.new('ShaderNodeTexNoise')
    noise.name = 'Copper noise pattern'
    noise.location = (-590, 260)
    noise.inputs['Scale'].default_value = 4
    voronoi = tree.nodes.new('ShaderNodeTexVoronoi')
    voronoi.name = 'Stone cellular pattern'
    voronoi.location = (-590, -140)
    voronoi.distance = 'EUCLIDEAN'
    voronoi.inputs['Scale'].default_value = 8 if stone else 6
    noise_ramp = tree.nodes.new('ShaderNodeValToRGB')
    noise_ramp.name = 'Copper shade ramp'
    noise_ramp.location = (-310, 260)
    noise_ramp.color_ramp.elements[0].color = (.12, .055, .018, 1)
    noise_ramp.color_ramp.elements[1].color = (.88, .38, .09, 1)
    cell_ramp = tree.nodes.new('ShaderNodeValToRGB')
    cell_ramp.name = 'Stone shade ramp'
    cell_ramp.location = (-310, -140)
    cell_ramp.color_ramp.elements[0].color = (.08, .14, .17, 1)
    cell_ramp.color_ramp.elements[1].color = (.44, .53, .49, 1)
    combine = tree.nodes.new('ShaderNodeMixRGB')
    combine.name = 'Original copper and stone blend'
    combine.location = (30, 120)
    combine.inputs['Fac'].default_value = .88 if stone else .16
    tree.links.new(coord.outputs['Generated'], noise.inputs['Vector'])
    tree.links.new(coord.outputs['Generated'], voronoi.inputs['Vector'])
    tree.links.new(noise.outputs['Fac'], noise_ramp.inputs['Fac'])
    tree.links.new(voronoi.outputs['Distance'], cell_ramp.inputs['Fac'])
    tree.links.new(noise_ramp.outputs['Color'], combine.inputs[1])
    tree.links.new(cell_ramp.outputs['Color'], combine.inputs[2])
    tree.links.new(combine.outputs['Color'], shader.inputs['Base Color'])
    tree.links.new(shader.outputs['BSDF'], output.inputs['Surface'])
    material['surface_pattern_kind'] = 'stone' if stone else 'copper'
    return material


def _pattern_fixture(scene, base_subject):
    copper = _validate_base(scene, base_subject)
    _private_mesh(scene, copper, 'pattern_copper')
    copper.name = 'Procedural spectrum / copper sample'
    copper.location = (-1.0, 0, 1.2)
    _tag(copper, scene, 'pattern_copper')
    copper.data.materials.clear()
    copper.data.materials.append(_procedural_material(scene, 'pattern_copper_material',
                                                       'BL-059 original copper stipple'))
    stone = _copy_subject(scene, copper, 'pattern_stone', 'Procedural spectrum / cellular stone', 1.0)
    stone.data.materials.clear()
    stone.data.materials.append(_procedural_material(scene, 'pattern_stone_material',
                                                      'BL-059 original cellular stone', stone=True))
    return copper


def _pattern_apply(scene, params):
    scale, roughness = params['Pattern scale'], params['Roughness']
    _check(1 <= scale <= 16 and 0 <= roughness <= 1,
           'Procedural material controls are outside their declared bounds')
    for role in ('pattern_copper', 'pattern_stone'):
        subject = _role(scene, role)
        _check(subject.data.materials and subject.data.materials[0] is not None,
               f'{role} has no original procedural material')
        tree = subject.data.materials[0].node_tree
        noise, voronoi = tree.nodes.get('Copper noise pattern'), tree.nodes.get('Stone cellular pattern')
        shader = tree.nodes.get('Principled BSDF')
        _check(noise is not None and voronoi is not None and shader is not None,
               f'{role} is missing its noise/Voronoi/Principled graph')
        noise.inputs['Scale'].default_value = scale
        voronoi.inputs['Scale'].default_value = scale * (2 if role == 'pattern_stone' else 1.5)
        shader.inputs['Roughness'].default_value = roughness


def _pattern_verify(scene, params):
    controls = []
    for role in ('pattern_copper', 'pattern_stone'):
        subject = _role(scene, role)
        material = subject.data.materials[0]
        tree = material.node_tree
        noise, voronoi = tree.nodes.get('Copper noise pattern'), tree.nodes.get('Stone cellular pattern')
        noise_ramp, cell_ramp = tree.nodes.get('Copper shade ramp'), tree.nodes.get('Stone shade ramp')
        shader = tree.nodes.get('Principled BSDF')
        _check(all(node is not None for node in (noise, voronoi, noise_ramp, cell_ramp, shader)),
               f'{role} lost a declared procedural shader node')
        _check(any(link.from_node == noise and link.to_socket == noise_ramp.inputs['Fac'] for link in tree.links)
               and any(link.to_socket == noise.inputs['Vector'] for link in tree.links)
               and any(link.from_node == voronoi and link.to_socket == cell_ramp.inputs['Fac'] for link in tree.links)
               and any(link.to_socket == voronoi.inputs['Vector'] for link in tree.links)
               and any(link.to_socket == shader.inputs['Base Color'] for link in tree.links),
               f'{role} has a missing coordinate/ramp/Base Color connection')
        _check(abs(noise.inputs['Scale'].default_value - params['Pattern scale']) < 1e-6
               and abs(shader.inputs['Roughness'].default_value - params['Roughness']) < 1e-6,
               f'{role} control values do not match the material inputs')
        controls.append({'role': role, 'noise_scale': float(noise.inputs['Scale'].default_value),
                         'voronoi_scale': float(voronoi.inputs['Scale'].default_value),
                         'roughness': float(shader.inputs['Roughness'].default_value),
                         'noise_ramp_elements': len(noise_ramp.color_ramp.elements),
                         'voronoi_ramp_elements': len(cell_ramp.color_ramp.elements)})
    deadline = time.monotonic() + 180
    preview_width, preview_height, preview = _render_probe(scene, deadline)
    materials = [_role(scene, role).data.materials[0] for role in ('pattern_copper', 'pattern_stone')]
    previous = [(material.node_tree.nodes['Copper noise pattern'].inputs['Scale'].default_value,
                 material.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value)
                for material in materials]
    alternate_scale = params['Pattern scale'] * .5 if params['Pattern scale'] > 1 else 2
    try:
        for material in materials:
            material.node_tree.nodes['Copper noise pattern'].inputs['Scale'].default_value = min(16, alternate_scale)
        _, _, scale_pixels = _render_probe(scene, deadline)
        for material in materials:
            material.node_tree.nodes['Copper noise pattern'].inputs['Scale'].default_value = params['Pattern scale']
            alternate_roughness = 0.0 if params['Roughness'] >= .5 else 1.0
            material.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = alternate_roughness
        _, _, roughness_pixels = _render_probe(scene, deadline)
    finally:
        for material, (scale, roughness) in zip(materials, previous):
            material.node_tree.nodes['Copper noise pattern'].inputs['Scale'].default_value = scale
            material.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = roughness
    scale_effect = _pixel_difference(preview, scale_pixels)
    roughness_effect = _pixel_difference(preview, roughness_pixels)
    _check(scale_effect['mean_absolute_channel_difference'] > 1e-6,
           'Pattern scale did not change bounded rendered reference pixels')
    _check(roughness_effect['mean_absolute_channel_difference'] > 1e-6,
           'Roughness did not change bounded rendered reference pixels')
    preview_metrics = _pixel_metrics(preview_width, preview_height, preview)
    return {'materials': controls, 'pattern_scale': params['Pattern scale'],
            'roughness': params['Roughness'], 'preview': preview_metrics,
            'pattern_scale_render_difference': scale_effect,
            'roughness_render_difference': roughness_effect,
            'preview_kind': '96x72 Cycles pixel samples; not a visual acceptance claim'}


def build(scene, lab, base_subject):
    builders = {'BL-016': _build_bake, 'BL-036': _migration_fixture,
                'BL-058': _world_fixture, 'BL-059': _pattern_fixture}
    if lab not in builders:
        raise ValueError(f'No surface builder for {lab}')
    subject = builders[lab](scene, base_subject)
    subject['blender_lab_subject'] = True
    apply_controls(scene, lab, DEFAULTS[lab])
    return subject


def apply_controls(scene, lab, params):
    handlers = {'BL-016': _apply_bake, 'BL-036': _migration_apply,
                'BL-058': _world_apply, 'BL-059': _pattern_apply}
    if lab not in handlers:
        raise ValueError(f'No surface controls for {lab}')
    handlers[lab](scene, params)


def verify(scene, lab, params, output):
    verifiers = {'BL-016': _bake_verify, 'BL-036': _migration_verify,
                 'BL-058': _world_verify, 'BL-059': _pattern_verify}
    if lab not in verifiers:
        raise ValueError(f'No surface verifier for {lab}')
    metrics = verifiers[lab](scene, params)
    metrics['pending_gates'] = list(_PENDING_GATES)
    return metrics
