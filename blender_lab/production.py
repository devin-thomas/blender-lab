"""Original, bounded compositor, lighting, asset and sprite-production fixtures."""
from array import array
from contextlib import contextmanager
import hashlib
import json
import math
from pathlib import Path
import uuid

import bpy
from mathutils import Vector

from .labs import PALETTE, cube, material


DEFAULTS = {
    'BL-019': {'Treatment amount': 0, 'Output width': 800},
    'BL-020': {'Key energy': 500, 'Renderer': 'CYCLES'},
    'BL-021': {'Asset role': 'module', 'Preview size': 128},
    'BL-022': {'Frames': 8, 'Cell size': 128},
}
ASSET_NAMESPACE = uuid.UUID('ddc21e45-edb4-48ed-aef6-d8d874ca47ab')


def _check(condition, message):
    if not condition:
        raise AssertionError(message)


def _tag(obj, role):
    obj['production_role'] = role
    return obj


def _role(scene, role):
    found = [obj for obj in scene.objects if obj.get('production_role') == role]
    _check(len(found) == 1, f'Expected one production role {role!r}; found {len(found)}')
    return found[0]


def _pixels(value, minimum, maximum, name):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f'{name} must be integer pixels')
    if not minimum <= value <= maximum:
        raise ValueError(f'{name} must be between {minimum} and {maximum} pixels')
    return value


def _packed_image(image, label, expected=None):
    _check(image is not None and image.packed_file is not None,
           f'Missing packed {label}; refusing unresolved external image data')
    # Packed images reopen without an ImBuf until RNA pixel access decodes their data.
    pixel_count = len(image.pixels)
    _check(pixel_count > 0 and image.has_data, f'Packed {label} cannot decode its pixel buffer')
    size = tuple(image.size)
    _check(len(size) == 2 and all(axis > 0 for axis in size) and pixel_count == size[0] * size[1] * 4,
           f'Packed {label} has invalid RGBA dimensions')
    if expected is not None:
        _check(size == tuple(expected), f'Packed {label} has incorrect dimensions: {size}')
    return image


def _camera(scene, role, location, target, size):
    data = bpy.data.cameras.new('Copper production camera')
    obj = bpy.data.objects.new('Copper production camera', data)
    scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()
    data.type = 'ORTHO'
    data.ortho_scale = size
    return _tag(obj, role)


def _chart():
    width, height = 96, 64
    image = bpy.data.images.new('Copper / original edge-and-ramp chart', width=width, height=height, alpha=True)
    values = array('f')
    letters = {
        'C': ('111', '100', '100', '100', '111'),
        'O': ('111', '101', '101', '101', '111'),
        'P': ('110', '101', '110', '100', '100'),
        'E': ('111', '100', '110', '100', '111'),
        'R': ('110', '101', '110', '101', '101'),
    }
    for y in range(height):
        for x in range(width):
            color = PALETTE['navy']
            if 5 <= x < 91 and 7 <= y < 29:
                ramp = (x - 5) / 85
                color = (.08 + .65 * ramp, .06 + .42 * ramp, .035 + .2 * ramp, 1)
            if y in (6, 29, 57) and 5 <= x < 91 or x in (5, 90) and 6 <= y <= 57:
                color = PALETTE['teal']
            if 36 <= y < 46 and 9 <= x < 57:
                letter, column = divmod((x - 9) // 2, 4)
                row = 4 - (y - 36) // 2
                if column < 3 and letter < 6 and letters['COPPER'[letter]][row][column] == '1':
                    color = PALETTE['cream']
            values.extend(color)
    image.pixels.foreach_set(values)
    image.pack()
    image['production_source'] = 'Original authored Copper chart: bitmap lettering, one-pixel edges, shade ramp'
    return image


def _bench(scene, subject):
    _check(hasattr(scene, 'compositing_node_group'), 'Compositor bench requires Blender 5.x scene node groups')
    graph = bpy.data.node_groups.new('Copper / clean and treated compositor', 'CompositorNodeTree')
    graph.interface.new_socket(name='Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    source = graph.nodes.new('CompositorNodeImage')
    source.name, source.label, source.location = 'Original chart', 'Packed original source', (-450, 40)
    source.image = _chart()
    treatment = graph.nodes.new('CompositorNodeBrightContrast')
    treatment.name, treatment.label, treatment.location = 'Treatment', 'Bounded brightness treatment; zero = identity', (-220, 40)
    treatment.inputs['Contrast'].default_value = 0
    scale = graph.nodes.new('CompositorNodeScale')
    scale.name, scale.label, scale.location = 'Output size', 'Requested render dimensions', (20, 40)
    scale.inputs['Type'].default_value = 'Render Size'
    scale.inputs['Frame Type'].default_value = 'Stretch'
    output = graph.nodes.new('NodeGroupOutput')
    output.name, output.location = 'Final output', (230, 40)
    graph.links.new(source.outputs['Image'], treatment.inputs['Image'])
    graph.links.new(treatment.outputs['Image'], scale.inputs['Image'])
    graph.links.new(scale.outputs['Image'], output.inputs['Image'])
    scene.compositing_node_group = graph
    scene.render.use_compositing = True
    _tag(subject, 'bench_subject')
    # The source chart is also a native material dependency, visible in the station.
    mat = material('Copper / editable chart display', PALETTE['cream'])
    texture = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texture.image, texture.interpolation = source.image, 'Closest'
    mat.node_tree.links.new(texture.outputs['Color'], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    uv = subject.data.uv_layers.new(name='Chart UV')
    for polygon in subject.data.polygons:
        for index, loop in enumerate(polygon.loop_indices):
            uv.data[loop].uv = ((0, 0), (1, 0), (1, 1), (0, 1))[index]
    subject.data.materials.clear()
    subject.data.materials.append(mat)
    return subject


def _lighting(scene, subject):
    _tag(subject, 'matte_cube')
    subject.location.x = -1.25
    subject.data.materials.clear()
    subject.data.materials.append(material('Copper / neutral matte reference', (.42, .42, .42, 1)))
    vertices, faces = [], []
    for z in (0, 2):
        for i in range(17):
            angle = math.pi * i / 16
            vertices.append((1.1 + .85 * math.cos(angle), .7 + .85 * math.sin(angle), z))
    for i in range(16):
        faces.append((i, i + 1, i + 18, i + 17))
    mesh = bpy.data.meshes.new('Copper / editable curved shell')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    shell = bpy.data.objects.new('Copper / curved shell', mesh)
    scene.collection.objects.link(shell)
    shell.data.materials.append(material('Copper / shell matte', PALETTE['teal']))
    _tag(shell, 'curved_shell')
    for i, color in enumerate((PALETTE['cream'], (.18, .18, .18, 1), PALETTE['amber'])):
        _tag(cube(scene, 'Copper / reference patch', (-1.6 + i * 1.1, -1.7, .08), (.45, .35, .07),
                  material('Copper / reference patch material', color)), 'patch_' + str(i))
    data = bpy.data.lights.new('Copper / observatory key', 'AREA')
    obj = bpy.data.objects.new('Copper / observatory key', data)
    scene.collection.objects.link(obj)
    obj.location = (-2, -3, 4.5)
    obj.rotation_euler = (Vector((0, 0, 1)) - obj.location).to_track_quat('-Z', 'Y').to_euler()
    data.shape, data.size = 'DISK', 3
    _tag(obj, 'key_light')
    return subject


def _asset_targets(scene):
    module = _role(scene, 'asset_module')
    return {'module': module, 'material': module.data.materials[0], 'camera': _role(scene, 'asset_camera')}


def _assets(scene, subject):
    _tag(subject, 'asset_module')
    mat = material('Copper / original module finish', PALETTE['amber'])
    image = bpy.data.images.new('Copper / local asset motif', width=16, height=16, alpha=True)
    image.pixels.foreach_set(array('f', [channel for y in range(16) for x in range(16)
                                       for channel in PALETTE['teal' if (x // 4 + y // 4) % 2 else 'amber']]))
    image.pack()
    image['production_asset_source_id'] = 'copper-observatory/BL-021/motif'
    texture = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texture.name, texture.image, texture.interpolation = 'Original packed motif', image, 'Closest'
    mat.node_tree.links.new(texture.outputs['Color'], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    subject.data.materials.clear()
    subject.data.materials.append(mat)
    uv = subject.data.uv_layers.new(name='Original motif UV')
    for polygon in subject.data.polygons:
        for index, loop in enumerate(polygon.loop_indices):
            uv.data[loop].uv = ((0, 0), (1, 0), (1, 1), (0, 1))[index]
    camera = _camera(scene, 'asset_camera', (7, -9, 7), (0, 0, 1), 8)
    camera.hide_render = True
    instance = scene.get('blender_lab_instance', scene.get('blender_lab_instance_id', scene.name))
    for role, target in _asset_targets(scene).items():
        target['production_asset_id'] = str(uuid.uuid5(ASSET_NAMESPACE, f'{instance}:BL-021:{role}'))
        target['production_asset_source_id'] = f'copper-observatory/BL-021/{role}'
        target['production_asset_role'] = role
        target['production_provenance'] = 'Original local Blender Lab fixture; no external assets'
    return subject


def _preview(target, role, size):
    preview = target.preview_ensure()
    preview.image_size = (size, size)
    values = array('f')
    for y in range(size):
        for x in range(size):
            u, v = x / size, y / size
            icon = (.22 < u < .78 and .25 < v < .75) if role == 'module' else (
                (u - .5) ** 2 + (v - .5) ** 2 < .1 if role == 'material' else
                (.2 < u < .63 and .32 < v < .68 or .63 <= u < .82 and abs(v - .5) < (u - .63)))
            values.extend(PALETTE['amber' if icon else 'navy'])
    preview.image_pixels_float = values
    target['production_preview_kind'] = 'Original generated provenance icon; not a rendered appearance preview'


def _sprites(scene, subject):
    _tag(subject, 'sprite_subject')
    subject.scale = (.45, .45, .45)
    # Asymmetric edits make orientation samples distinguishable without external art.
    for vertex in subject.data.vertices:
        if vertex.co.z > 0 and vertex.co.x > 0:
            vertex.co.x *= .4
            vertex.co.z *= 1.25
    subject.location = (0, 0, 1.35)
    _camera(scene, 'sprite_camera', (4, -6, 4.2), (0, 0, 1.35), 3.5)
    atlas = bpy.data.images.new('Copper / bounded sprite atlas', width=1024, height=128, alpha=True)
    atlas.colorspace_settings.name = 'sRGB'
    atlas['production_role'] = 'sprite_atlas'
    atlas['production_instance_id'] = scene.get('blender_lab_instance_id', scene.name)
    scene['production_atlas_name'] = atlas.name
    # An actual native ID dependency keeps this output image through save/reopen.
    # It remains disconnected from shading so the source sprite stays copper.
    surface = material('Copper / sprite surface and owned atlas', PALETTE['amber'])
    reference = surface.node_tree.nodes.new('ShaderNodeTexImage')
    reference.name, reference.label, reference.image = 'Owned sprite atlas', 'Generated output / inspect in Image Editor', atlas
    subject.data.materials.clear()
    subject.data.materials.append(surface)
    return subject


def _atlas(scene):
    image = bpy.data.images.get(scene.get('production_atlas_name', ''))
    _check(image is not None and image.get('production_role') == 'sprite_atlas'
           and image.get('production_instance_id') == scene.get('blender_lab_instance_id', scene.name),
           'Missing owned sprite atlas; refusing to mutate an unrelated image')
    subject = _role(scene, 'sprite_subject')
    _check(len(subject.data.materials) == 1 and subject.data.materials[0] is not None,
           'Sprite atlas has no owned surface material dependency')
    reference = subject.data.materials[0].node_tree.nodes.get('Owned sprite atlas')
    _check(reference is not None and reference.bl_idname == 'ShaderNodeTexImage' and reference.image == image,
           'Sprite atlas lost its native material dependency; refusing an unrelated image')
    return image


def build(scene, lab, base_subject):
    builders = {'BL-019': _bench, 'BL-020': _lighting, 'BL-021': _assets, 'BL-022': _sprites}
    if lab not in builders:
        raise ValueError(f'No production builder for {lab}')
    primary = builders[lab](scene, base_subject)
    primary['blender_lab_subject'] = True
    apply_controls(scene, lab, DEFAULTS[lab])
    return primary


def apply_controls(scene, lab, params):
    if lab == 'BL-019':
        amount = params['Treatment amount']
        if not isinstance(amount, (int, float)) or isinstance(amount, bool) or not math.isfinite(amount) or not 0 <= amount <= 1:
            raise ValueError('Treatment amount must be finite between zero and one')
        width = _pixels(params['Output width'], 320, 1280, 'Output width')
        graph = scene.compositing_node_group
        _check(graph is not None and graph.nodes.get('Treatment') is not None, 'Missing editable compositor treatment')
        graph.nodes['Treatment'].inputs['Brightness'].default_value = amount * 20
        scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = width, round(width * 2 / 3), 100
    elif lab == 'BL-020':
        energy = params['Key energy']
        if isinstance(energy, bool) or not isinstance(energy, (int, float)) or not math.isfinite(energy) or not 0 <= energy <= 2000:
            raise ValueError('Key energy must be finite between zero and 2000')
        _check(scene.camera is not None and scene.camera.type == 'CAMERA', 'Lighting observatory requires a valid scene camera')
        engine = params['Renderer']
        if engine not in ('CYCLES', 'BLENDER_EEVEE'):
            raise ValueError(f'Unsupported observatory renderer: {engine}')
        try:
            scene.render.engine = engine
        except TypeError as error:
            raise ValueError(f'Renderer profile {engine} is unavailable in this Blender runtime') from error
        _role(scene, 'key_light').data.energy = energy
    elif lab == 'BL-021':
        role = params['Asset role']
        size = _pixels(params['Preview size'], 64, 256, 'Preview size')
        targets = _asset_targets(scene)
        if role not in targets:
            raise ValueError(f'Unknown asset role: {role}')
        for name, target in targets.items():
            if name != role and target.asset_data is not None:
                target.asset_clear()
        selected = targets[role]
        selected.asset_mark()
        selected.asset_data.author = 'Blender Lab'
        selected.asset_data.description = selected['production_provenance'] + '; ' + selected['production_asset_source_id']
        selected.asset_data.license = 'MIT'
        selected.asset_data.tags.new('Copper Observatory', skip_if_exists=True)
        selected.asset_data.tags.new(role, skip_if_exists=True)
        _preview(selected, role, size)
        scene['production_asset_role'] = role
    elif lab == 'BL-022':
        frames = params['Frames']
        if isinstance(frames, bool) or not isinstance(frames, int) or not 4 <= frames <= 24:
            raise ValueError('Frames must be an integer between 4 and 24')
        size = _pixels(params['Cell size'], 32, 256, 'Cell size')
        scene['production_sprite_frames'], scene['production_sprite_cell_size'] = frames, size
        scene.frame_start, scene.frame_end = 1, frames
        subject = _role(scene, 'sprite_subject')
        if subject.animation_data and subject.animation_data.action:
            # Reuse the owned action; repeated control changes must not orphan actions.
            for old_frame in range(1, 25):
                subject.keyframe_delete(data_path='rotation_euler', frame=old_frame)
                subject.keyframe_delete(data_path='location', frame=old_frame)
        for frame in range(1, frames + 1):
            angle = 2 * math.pi * (frame - 1) / frames
            subject.rotation_euler.z = angle
            subject.location.z = 1.35 + .15 * math.sin(angle)
            subject.keyframe_insert(data_path='rotation_euler', frame=frame)
            subject.keyframe_insert(data_path='location', frame=frame)
        scene.frame_set(1)
        atlas = _atlas(scene)
        if tuple(atlas.size) != (frames * size, size):
            atlas.scale(frames * size, size)
    else:
        raise ValueError(f'No production controls for {lab}')
    bpy.context.view_layer.update()


@contextmanager
def _render_scope(scene, directory, size, camera=None, isolated=None):
    render = scene.render
    keys = ('resolution_x', 'resolution_y', 'resolution_percentage', 'filepath', 'film_transparent', 'use_compositing')
    previous = {key: getattr(render, key) for key in keys}
    image = render.image_settings
    image_previous = {key: getattr(image, key) for key in ('file_format', 'color_mode', 'color_depth')}
    camera_previous, frame_previous = scene.camera, scene.frame_current
    hidden = [(obj, obj.hide_render) for obj in scene.objects]
    samples_previous = scene.cycles.samples if render.engine == 'CYCLES' else None
    try:
        _check(camera or scene.camera, 'Production render requires a scene camera')
        render.resolution_x, render.resolution_y, render.resolution_percentage = size[0], size[1], 100
        image.file_format, image.color_mode, image.color_depth = 'PNG', 'RGBA', '8'
        render.filepath = str(directory)
        if camera:
            scene.camera = camera
        if isolated is not None:
            render.film_transparent = True
            render.use_compositing = False
            for obj in scene.objects:
                if obj.type not in ('LIGHT', 'CAMERA'):
                    obj.hide_render = obj not in isolated
        if samples_previous is not None:
            scene.cycles.samples = 4
        yield
    finally:
        scene.camera = camera_previous
        scene.frame_set(frame_previous)
        for obj, value in hidden:
            obj.hide_render = value
        for key, value in previous.items():
            setattr(render, key, value)
        for key, value in image_previous.items():
            setattr(image, key, value)
        if samples_previous is not None:
            scene.cycles.samples = samples_previous


def _directory(output, prefix):
    root = Path(output).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    directory = root / (prefix + '-' + uuid.uuid4().hex[:12])
    directory.mkdir(exist_ok=False)
    _check(directory.resolve().parent == root, 'Production output escaped the selected directory')
    return directory


def _read_image(path, expected):
    _check(path.is_file(), f'Missing production frame: {path.name}')
    image = bpy.data.images.load(str(path), check_existing=False)
    try:
        _check(tuple(image.size) == tuple(expected), f'Unexpected frame dimensions: {path.name}')
        values = array('f', [0]) * (expected[0] * expected[1] * 4)
        image.pixels.foreach_get(values)
        _check(all(math.isfinite(value) for value in values), f'Nonfinite production pixels: {path.name}')
        return values
    finally:
        bpy.data.images.remove(image)


def _render(scene, path, size):
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True, scene=scene.name)
    return _read_image(path, size)


def _linked(graph, output, input_socket):
    return any(link.from_socket == output and link.to_socket == input_socket for link in graph.links)


def _verify_bench(scene, params, output):
    graph = scene.compositing_node_group
    _check(graph is not None, 'Missing compositor scene group')
    source, treatment, scale, final = (graph.nodes.get(name) for name in ('Original chart', 'Treatment', 'Output size', 'Final output'))
    _check(all(node is not None for node in (source, treatment, scale, final)), 'Compositor graph is incomplete')
    _check([node.bl_idname for node in (source, treatment, scale, final)] ==
           ['CompositorNodeImage', 'CompositorNodeBrightContrast', 'CompositorNodeScale', 'NodeGroupOutput'],
           'Unsupported compositor node mode; restore the original clean/treatment graph')
    _packed_image(source.image, 'compositor input image', (96, 64))
    _check(_linked(graph, source.outputs['Image'], treatment.inputs['Image'])
           and _linked(graph, treatment.outputs['Image'], scale.inputs['Image'])
           and _linked(graph, scale.outputs['Image'], final.inputs['Image']), 'Compositor output path is disconnected')
    _check(scale.inputs['Type'].default_value == 'Render Size'
           and scale.inputs['Frame Type'].default_value == 'Stretch', 'Unsupported compositor output sizing mode')
    width = _pixels(params['Output width'], 320, 1280, 'Output width')
    _check(scene.render.resolution_x == width and scene.render.resolution_y == round(width * 2 / 3), 'Output width control missed render dimensions')
    amount = params['Treatment amount']
    _check(abs(treatment.inputs['Brightness'].default_value - amount * 20) < 1e-5, 'Treatment control missed compositor input')
    directory = _directory(output, 'compositor')
    original_bright = treatment.inputs['Brightness'].default_value
    try:
        with _render_scope(scene, directory, (96, 64), isolated=set()):
            scene.render.use_compositing = True
            graph.links.new(source.outputs['Image'], scale.inputs['Image'])
            clean = _render(scene, directory / 'clean.png', (96, 64))
            graph.links.new(treatment.outputs['Image'], scale.inputs['Image'])
            requested = _render(scene, directory / 'requested.png', (96, 64))
            treatment.inputs['Brightness'].default_value = 20
            treated = _render(scene, directory / 'treated.png', (96, 64))
    finally:
        graph.links.new(treatment.outputs['Image'], scale.inputs['Image'])
        treatment.inputs['Brightness'].default_value = original_bright
    requested_error = max(abs(a - b) for a, b in zip(clean, requested))
    changed = sum(abs(a - b) for a, b in zip(clean, treated)) / len(clean)
    _check(changed > .005, 'Enabled compositor treatment did not change rendered output')
    if amount == 0:
        _check(requested_error < 1 / 255 + 1e-5, 'Zero treatment did not reproduce clean output')
    else:
        _check(requested_error > 0, 'Requested treatment did not change rendered output')
    return {'output_width': width, 'output_height': scene.render.resolution_y,
            'treatment_amount': amount, 'clean_requested_max_error': requested_error,
            'enabled_mean_pixel_difference': changed, 'pixel_probe_size': [96, 64],
            'rendered_outputs': [str(directory / name) for name in ('clean.png', 'requested.png', 'treated.png')],
            'compositor_api': 'Scene.compositing_node_group / NodeGroupOutput',
            'readability_and_requested_resolution_pixel_qualification': 'pending-human-and-full-size-render'}


def _verify_lighting(scene, params):
    key = _role(scene, 'key_light')
    _check(scene.camera is not None and scene.camera.type == 'CAMERA', 'Lighting camera is missing')
    _check(key.data.type == 'AREA' and abs(key.data.energy - params['Key energy']) < 1e-4, 'Key energy control missed area light')
    _check(scene.render.engine == params['Renderer'], 'Renderer control missed render engine')
    cube_obj, shell = _role(scene, 'matte_cube'), _role(scene, 'curved_shell')
    _check(len(cube_obj.data.vertices) == 8 and len(shell.data.polygons) == 16, 'Lighting reference geometry changed')
    patches = [_role(scene, 'patch_' + str(i)) for i in range(3)]
    _check(all(obj.data.materials for obj in [cube_obj, shell, *patches]), 'Missing matte lighting reference material')
    return {'key_energy': key.data.energy, 'renderer': scene.render.engine, 'camera': scene.camera.name,
            'resolution': [scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage],
            'view_transform': scene.view_settings.view_transform, 'look': scene.view_settings.look,
            'reference_patch_colors': [list(obj.data.materials[0].diffuse_color) for obj in patches],
            'shell_polygons': len(shell.data.polygons),
            'reference_luminance_response': 'pending-rendered-energy-comparison',
            'renderer_backend_execution': 'pending-render', 'matched_renderer_receipts': 'pending-both-renderers'}


def _verify_assets(scene, params):
    targets = _asset_targets(scene)
    role = params['Asset role']
    selected = targets[role]
    marked = [name for name, target in targets.items() if target.asset_data is not None]
    _check(marked == [role], 'Asset selection did not mark exactly the requested datablock')
    ids = [target.get('production_asset_id') for target in targets.values()]
    _check(all(ids) and len(set(ids)) == 3, 'Asset roles lost distinct stable identities')
    _check(selected.asset_data.author == 'Blender Lab' and selected.asset_data.license == 'MIT'
           and selected['production_asset_source_id'] in selected.asset_data.description, 'Asset provenance metadata is incomplete')
    size = _pixels(params['Preview size'], 64, 256, 'Preview size')
    _check(selected.preview is not None, 'Selected asset has no original custom preview')
    _check(tuple(selected.preview.image_size) == (size, size), 'Asset preview size control missed custom preview')
    module, mat = targets['module'], targets['material']
    texture = mat.node_tree.nodes.get('Original packed motif')
    _check(module.data.materials[0] == mat and texture is not None and texture.image is not None,
           'Asset module material/image dependency is unresolved')
    image = _packed_image(texture.image, 'asset motif', (16, 16))
    _check(image.get('production_asset_source_id') == 'copper-observatory/BL-021/motif',
           'Asset motif is not a self-contained packed image')
    _check(module.data.uv_layers.active is not None and targets['camera'].data.type == 'ORTHO', 'Asset role data is incomplete')
    _check(_linked(mat.node_tree, texture.outputs['Color'], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color']),
           'Asset original motif is disconnected from its material')
    pending, seen = [mat.node_tree], set()
    while pending:
        tree = pending.pop()
        if tree in seen:
            continue
        seen.add(tree)
        for node in tree.nodes:
            if node.type == 'GROUP':
                _check(node.node_tree is not None, f'Unresolved asset node-group dependency: {node.name}')
                pending.append(node.node_tree)
            elif node.type == 'TEX_IMAGE':
                _check(node.image is not None, f'Unresolved asset image dependency: {node.name}')
                _packed_image(node.image, f'asset dependency {node.image.name}')
    return {'selected_role': role, 'asset_id': selected['production_asset_id'], 'preview_size': list(selected.preview.image_size),
            'asset_role_ids': {name: target['production_asset_id'] for name, target in targets.items()},
            'dependencies': {'module_mesh': module.data.name, 'material': mat.name, 'packed_image': image.name,
                             'camera_data': targets['camera'].data.name},
            'external_files': [], 'preview_kind': selected['production_preview_kind'],
            'save_reopen_and_append_qualification': 'pending-receiving-file-roundtrip'}


def _alpha_bounds(values, size):
    covered = [index for index, alpha in enumerate(values[3::4]) if alpha > .01]
    _check(covered, 'Sprite frame has no visible subject alpha')
    xmin, xmax = min(index % size for index in covered), max(index % size for index in covered)
    ymin, ymax = min(index // size for index in covered), max(index // size for index in covered)
    _check(xmin > 0 and ymin > 0 and xmax < size - 1 and ymax < size - 1,
           'Sprite subject is clipped or touches cell boundary; increase camera margin')
    _check(max(values[3::4]) > .8 and min(values[3::4]) < .01, 'Sprite frame lost opaque subject or transparent background')
    return [xmin, ymin, xmax + 1, ymax + 1]


def _pixel_hash(values):
    return hashlib.sha256(bytes(max(0, min(255, round(channel * 255))) for channel in values)).hexdigest()


def _verify_sprites(scene, params, output):
    frames, size = params['Frames'], _pixels(params['Cell size'], 32, 256, 'Cell size')
    _check(scene['production_sprite_frames'] == frames and scene['production_sprite_cell_size'] == size,
           'Sprite controls differ from requested frame/cell contract')
    _check(isinstance(frames, int) and not isinstance(frames, bool) and 4 <= frames <= 24, 'Sprite frame budget exceeded')
    subject, camera = _role(scene, 'sprite_subject'), _role(scene, 'sprite_camera')
    atlas = _atlas(scene)
    _check(tuple(atlas.size) == (frames * size, size), 'Sprite atlas has incorrect owned dimensions')
    directory = _directory(output, 'sprites')
    records, cells = [], []
    with _render_scope(scene, directory, (size, size), camera=camera, isolated={subject}):
        for frame in range(1, frames + 1):
            scene.frame_set(frame)
            angle = 2 * math.pi * (frame - 1) / frames
            _check(abs(subject.rotation_euler.z - angle) < 1e-5
                   and abs(subject.location.z - (1.35 + .15 * math.sin(angle))) < 1e-5,
                   f'Sprite frame {frame} does not match its authored motion identity')
            path = directory / f'frame-{frame:03d}.png'
            pixels = _render(scene, path, (size, size))
            bbox = _alpha_bounds(pixels, size)
            cells.append(pixels)
            records.append({'frame': frame, 'file': path.name, 'rect_bottom_left': [(frame - 1) * size, 0, size, size],
                            'alpha_bounds_bottom_left': bbox, 'pixel_sha256': _pixel_hash(pixels),
                            'file_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'rotation_z': angle})
    _check(len({record['pixel_sha256'] for record in records}) == frames, 'Sprite frame identities are not visually distinct')
    width = frames * size
    packed = array('f', [0]) * (width * size * 4)
    for column, pixels in enumerate(cells):
        for row in range(size):
            start = (row * width + column * size) * 4
            packed[start:start + size * 4] = pixels[row * size * 4:(row + 1) * size * 4]
    atlas.pixels.foreach_set(packed)
    atlas.filepath_raw, atlas.file_format = str(directory / 'atlas.png'), 'PNG'
    atlas.save()
    reimported = _read_image(directory / 'atlas.png', (width, size))
    order_errors, alpha_errors, maximum_errors = [], [], []
    for column, original in enumerate(cells):
        crop = array('f')
        for row in range(size):
            start = (row * width + column * size) * 4
            crop.extend(reimported[start:start + size * 4])
        _alpha_bounds(crop, size)
        # RGB passes through PNG's color encoding; alpha and arrangement have stricter acceptance.
        alpha_errors.append(max(abs(a - b) for a, b in zip(original[3::4], crop[3::4])))
        errors = [abs(a - b) for a, b in zip(original, crop)]
        _check(max(errors) < .01, f'Atlas cell {column + 1} differs from its requested frame pixels/order')
        maximum_errors.append(max(errors))
        order_errors.append(sum(errors) / len(errors))
    _check(max(alpha_errors) <= 1 / 255 + 1e-5, 'Sprite alpha did not survive PNG reimport')
    manifest = {'schemaVersion': 1, 'lab': 'BL-022', 'atlas': 'atlas.png', 'atlas_size': [width, size],
                'coordinate_origin': 'bottom-left', 'frame_order': 'left-to-right, ascending frame number',
                'frames': records, 'alpha_reimport_max_error': max(alpha_errors),
                'rgba_reimport_max_error': max(maximum_errors), 'rgba_reimport_tolerance': .01,
                'atlas_file_sha256': hashlib.sha256((directory / 'atlas.png').read_bytes()).hexdigest()}
    (directory / 'manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    atlas.pack()
    return {'frames': frames, 'cell_size': size, 'atlas_size': [width, size], 'distinct_pixel_frames': frames,
            'alpha_reimport_max_error': max(alpha_errors), 'frame_order_mean_errors': order_errors,
            'rgba_reimport_max_error': max(maximum_errors),
            'alpha_bounds': [record['alpha_bounds_bottom_left'] for record in records],
            'atlas': str(directory / 'atlas.png'), 'manifest': str(directory / 'manifest.json'),
            'sprite_camera': camera.name, 'frame_identity_and_crop': 'passed'}


def verify(scene, lab, params, output):
    bpy.context.view_layer.update()
    if lab == 'BL-019':
        return _verify_bench(scene, params, output)
    if lab == 'BL-020':
        return _verify_lighting(scene, params)
    if lab == 'BL-021':
        return _verify_assets(scene, params)
    if lab == 'BL-022':
        return _verify_sprites(scene, params, output)
    raise ValueError(f'No production verifier for {lab}')
