"""Original editable rig, animation, staging, curve and typography fixtures.

Scene creation, ownership snapshots, persistence and reset belong to the caller.
Evaluated meshes are always released; Apply updates existing data in place.
"""
import math
from uuid import uuid4

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


DEFAULTS = {
    'BL-010': {'Bend angle': 45.0, 'Weight transition': .5},
    'BL-011': {'Blend frames': 8, 'Clip offset': 0},
    'BL-012': {'Field of view': 50.0, 'Subject distance': 8.0},
    'BL-029': {'Expression weight': .5, 'Secondary weight': 0.0},
    'BL-030': {'Path resolution': 8, 'Profile radius': .1},
    'BL-031': {'Extrusion': .02, 'Text width': 3.0},
}


def _check(condition, message):
    if not condition:
        raise AssertionError(message)


def _tag(obj, role):
    obj['motion_role'] = role
    return obj


def _role(scene, role):
    matches = [obj for obj in scene.objects if obj.get('motion_role') == role]
    _check(len(matches) == 1, f"Expected exactly one motion object: {role}")
    return matches[0]


def _object(scene, name, data, role, location=(0, 0, 0)):
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    return _tag(obj, role)


def _mesh(scene, name, vertices, faces, role, color='amber', location=(0, 0, 0)):
    from .labs import material, PALETTE
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(material(name + ' / ceramic', PALETTE[color]))
    return _object(scene, name, mesh, role, location)


def _cube(scene, name, location, scale, role, color='amber'):
    from .labs import cube, material, PALETTE
    return _tag(cube(scene, name, location, scale, material(name + ' / ceramic', PALETTE[color])), role)


def _update(scene):
    _check(bpy.context.scene == scene, "Motion adapter requires its provided scene to be active")
    bpy.context.view_layer.update()


def _vertices(scene, obj):
    _update(scene)
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    _check(mesh is not None, f"No evaluated geometry for {obj.name}")
    try:
        points = [vertex.co.copy() for vertex in mesh.vertices]
        _check(points and all(math.isfinite(value) for p in points for value in p),
               f"Empty or nonfinite evaluated geometry for {obj.name}")
        return points
    finally:
        evaluated.to_mesh_clear()


def _bounds(points):
    _check(bool(points), "Cannot measure empty geometry")
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]


def _matrix_error(first, second):
    return max(abs(first[row][column] - second[row][column])
               for row in range(4) for column in range(4))


def _copy_evaluated(scene, source, copy):
    """Reconcile a separately editable export mesh without creating orphan meshes."""
    _update(scene)
    evaluated = source.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    _check(mesh is not None and len(mesh.vertices) > 0, "Cannot convert an empty source")
    try:
        vertices = [tuple(v.co) for v in mesh.vertices]
        edges = [tuple(e.vertices) for e in mesh.edges]
        faces = [tuple(p.vertices) for p in mesh.polygons]
        copy.data.clear_geometry()
        copy.data.from_pydata(vertices, edges, faces)
        copy.data.update()
        copy.matrix_world = source.matrix_world.copy()
    finally:
        evaluated.to_mesh_clear()


def _export_copy(scene, source, role):
    mesh = bpy.data.meshes.new(source.name + ' / separate export geometry')
    mesh.materials.append(source.data.materials[0])
    copy = _object(scene, source.name + ' / export copy', mesh, role)
    copy.hide_render = True
    copy.hide_set(True)
    return copy


def _tube(rings, radius=.32, sides=6):
    vertices = [(radius * math.cos(i * 2 * math.pi / sides),
                 radius * math.sin(i * 2 * math.pi / sides), z)
                for z in rings for i in range(sides)]
    faces = [tuple(reversed(range(sides))),
             tuple(range((len(rings) - 1) * sides, len(rings) * sides))]
    faces.extend((r * sides + i, r * sides + (i + 1) % sides,
                  (r + 1) * sides + (i + 1) % sides, (r + 1) * sides + i)
                 for r in range(len(rings) - 1) for i in range(sides))
    return vertices, faces


def _armature(scene, role, location):
    from .labs import activate
    data = bpy.data.armatures.new('Limb / two-joint editable bones')
    rig = _object(scene, 'Limb / ' + role, data, role, location)
    rig.show_in_front = True
    _update(scene)
    _check(bpy.context.mode == 'OBJECT', "Rig construction requires Object Mode")
    activate(rig)
    with bpy.context.temp_override(scene=scene, view_layer=bpy.context.view_layer,
                                   object=rig, active_object=rig,
                                   selected_objects=[rig], selected_editable_objects=[rig]):
        bpy.ops.object.mode_set(mode='EDIT')
        try:
            lower = data.edit_bones.new('Lower')
            lower.head, lower.tail = (0, 0, 0), (0, 0, 1.2)
            upper = data.edit_bones.new('Upper')
            upper.head, upper.tail = (0, 0, 1.2), (0, 0, 2.4)
            upper.parent = lower
            upper.use_connect = True
        finally:
            bpy.ops.object.mode_set(mode='OBJECT')
    rig.pose.bones['Upper'].rotation_mode = 'XYZ'
    return rig


def _skin(obj, rig):
    obj.vertex_groups.new(name='Lower')
    obj.vertex_groups.new(name='Upper')
    modifier = obj.modifiers.new('Editable bone deformation', 'ARMATURE')
    modifier.object = rig
    modifier.use_vertex_groups = True
    modifier.use_bone_envelopes = False


def _rig(scene):
    smooth_rig = _armature(scene, 'weighted_rig', (-1.05, 0, .15))
    rigid_rig = _armature(scene, 'rigid_rig', (1.05, 0, .15))
    vertices, faces = _tube([i * .3 for i in range(9)])
    sleeve = _mesh(scene, 'Limb / organic hexagonal sleeve', vertices, faces,
                   'weighted_limb', 'teal', tuple(smooth_rig.location))
    _skin(sleeve, smooth_rig)
    lower_v, lower_f = _tube([0, 1.17], .27)
    upper_v, upper_f = _tube([1.23, 2.4], .27)
    count = len(lower_v)
    rigid = _mesh(scene, 'Limb / rigid segmented mechanism', lower_v + upper_v,
                  lower_f + [tuple(index + count for index in f) for f in upper_f],
                  'rigid_limb', location=tuple(rigid_rig.location))
    _skin(rigid, rigid_rig)
    rigid.vertex_groups['Lower'].add(list(range(count)), 1, 'REPLACE')
    rigid.vertex_groups['Upper'].add(list(range(count, count + len(upper_v))), 1, 'REPLACE')
    for x in (-1.05, 1.05):
        _cube(scene, 'Limb / socket plinth', (x, 0, .08), (.48, .48, .08),
              'socket_' + str(x), 'cream')
    return sleeve


def _rig_apply(scene, params):
    angle = math.radians(params['Bend angle'])
    for role in ('weighted_rig', 'rigid_rig'):
        rig = _role(scene, role)
        _check(rig.type == 'ARMATURE' and rig.pose.bones.get('Upper') is not None,
               "Rig is missing its upper deform bone")
        rig.pose.bones['Upper'].rotation_euler.x = angle
    sleeve = _role(scene, 'weighted_limb')
    center = .8 + .8 * params['Weight transition']
    for name in ('Lower', 'Upper'):
        _check(sleeve.vertex_groups.get(name) is not None, f"Missing deform group: {name}")
    for vertex in sleeve.data.vertices:
        upper = min(1.0, max(0.0, (vertex.co.z - center) / .6 + .5))
        sleeve.vertex_groups['Lower'].add([vertex.index], 1 - upper, 'REPLACE')
        sleeve.vertex_groups['Upper'].add([vertex.index], upper, 'REPLACE')


def _rig_verify(scene, params):
    result = {}
    for mode in ('weighted', 'rigid'):
        obj, rig = _role(scene, mode + '_limb'), _role(scene, mode + '_rig')
        _check(obj.type == 'MESH' and rig.type == 'ARMATURE', "Limb/armature data is missing")
        modifiers = [m for m in obj.modifiers if m.type == 'ARMATURE']
        _check(len(modifiers) == 1 and modifiers[0].object == rig
               and modifiers[0].show_viewport and modifiers[0].use_vertex_groups,
               "Limb lost its evaluated vertex-group Armature modifier")
        for name in ('Lower', 'Upper'):
            _check(obj.vertex_groups.get(name) is not None and rig.data.bones.get(name) is not None,
                   f"Missing deform group or bone: {name}")
        evaluated = _vertices(scene, obj)
        _check(len(evaluated) == len(obj.data.vertices), "Limb topology changed unexpectedly")
        _update(scene)
        evaluated_rig = rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
        matrices = {name: evaluated_rig.pose.bones[name].matrix @ rig.data.bones[name].matrix_local.inverted()
                    for name in ('Lower', 'Upper')}
        errors, displacement = [], []
        group_totals = {name: 0.0 for name in matrices}
        for vertex, actual in zip(obj.data.vertices, evaluated):
            weights = {name: next((g.weight for g in vertex.groups
                                   if g.group == obj.vertex_groups[name].index), 0.0)
                       for name in matrices}
            _check(abs(sum(weights.values()) - 1) < 1e-5, "Limb has an unweighted or over-weighted vertex")
            if mode == 'weighted':
                expected_weight = min(1.0, max(0.0, (vertex.co.z - (.8 + .8 * params['Weight transition'])) / .6 + .5))
                _check(abs(weights['Upper'] - expected_weight) < 1e-5, "Weight transition missed a sleeve vertex")
            expected = sum((matrices[name] @ vertex.co * weight for name, weight in weights.items()), Vector())
            errors.append((actual - expected).length)
            displacement.append((actual - vertex.co).length)
            for name in weights:
                group_totals[name] += weights[name]
        _check(all(total > 0 for total in group_totals.values()), "A deform group has no contributing vertices")
        _check(max(errors) < 2e-5, "Evaluated weighted vertices do not follow their bones")
        actual_angle = evaluated_rig.pose.bones['Upper'].rotation_euler.x
        _check(abs(actual_angle - math.radians(params['Bend angle'])) < 1e-5,
               "Evaluated bone bend differs from the requested angle")
        world = [obj.matrix_world @ point for point in evaluated]
        bounds = _bounds(world)
        _check(bounds[0][0] > -4 and bounds[0][1] < 4 and bounds[1][0] > -3
               and bounds[1][1] < 3 and bounds[2][0] >= -.25 and bounds[2][1] < 3.5,
               "Extreme rig pose leaves the declared Copper Observatory envelope")
        result[mode] = {'vertices': len(evaluated), 'max_deformation_error': max(errors),
                        'max_displacement': max(displacement), 'world_bounds': bounds,
                        'middle_vertex': list(evaluated[len(evaluated) // 2]),
                        'tip_vertex': list(evaluated[-1]), 'bend_degrees': math.degrees(actual_angle)}
        if mode == 'rigid':
            # Every within-piece pair must retain its authored distance.
            distances = []
            for indices in (range(12), range(12, 24)):
                for a in indices:
                    for b in indices:
                        distances.append(abs((evaluated[a] - evaluated[b]).length
                                             - (obj.data.vertices[a].co - obj.data.vertices[b].co).length))
            _check(max(distances) < 2e-5, "Rigid segment changed shape under the matched bend")
            result[mode]['max_segment_distance_error'] = max(distances)
    result['weight_transition'] = params['Weight transition']
    return result


def _channelbag(action, slot):
    _check(slot is not None and slot.target_id_type == 'OBJECT', "Empty or incompatible Action slot")
    bags = [strip.channelbag(slot) for layer in action.layers for strip in layer.strips
            if strip.type == 'KEYFRAME']
    bags = [bag for bag in bags if bag is not None]
    _check(len(bags) == 1 and len(bags[0].fcurves) == 1, "Action slot is empty or has unexpected channels")
    curve = bags[0].fcurves[0]
    _check(curve.data_path == 'rotation_euler' and curve.array_index == 1
           and len(curve.keyframe_points) >= 2, "Action lost its editable hinge rotation keys")
    return curve


def _action(obj, name, role, keys):
    obj.animation_data_create()
    obj.rotation_mode = 'XYZ'
    action = bpy.data.actions.new(name)
    slot = action.slots.new(id_type='OBJECT', name=obj.name)
    key_strip = action.layers.new('Editable hinge keys').strips.new(type='KEYFRAME')
    channelbag = key_strip.channelbag(slot, ensure=True)
    curve = channelbag.fcurves.new(data_path='rotation_euler', index=1)
    curve.keyframe_points.add(len(keys))
    for point, (frame, angle) in zip(curve.keyframe_points, keys):
        point.co = (frame, angle)
        point.interpolation = 'LINEAR'
    curve.update()
    action['motion_action_role'] = role
    action['motion_action_identity'] = str(uuid4())
    _channelbag(action, slot)
    obj[role + '_action_identity'] = action['motion_action_identity']
    obj.animation_data.action = None
    return action, slot


def _nla(scene):
    vertices, faces = _tube([0, .15, 1.4, 1.7], .19)
    obj = _mesh(scene, 'Signal / hinged hexagonal paddle', vertices, faces, 'signal', location=(0, 0, .3))
    _cube(scene, 'Signal / hinge socket', (0, 0, .15), (.55, .45, .15), 'signal_socket', 'teal')
    idle, idle_slot = _action(obj, 'Signal / Idle', 'idle', [(1, 0), (17, .12), (33, 0), (49, -.12), (65, 0)])
    lift, lift_slot = _action(obj, 'Signal / Lift', 'lift', [(1, 0), (17, .9), (33, 1.25)])
    for action, slot, name in ((idle, idle_slot, 'Idle / base'), (lift, lift_slot, 'Lift / overlap')):
        track = obj.animation_data.nla_tracks.new()
        track.name = name
        strip = track.strips.new(name, 1 if action == idle else 25, action)
        strip.action_slot = slot
        strip.blend_type = 'REPLACE'
        strip.use_auto_blend = False
        strip.extrapolation = 'NOTHING' if action == idle else 'HOLD_FORWARD'
    obj.animation_data.use_nla = True
    obj.rotation_euler.y = 0
    scene.frame_end = 96
    return obj


def _strips(scene):
    obj = _role(scene, 'signal')
    data = obj.animation_data
    _check(data is not None and data.action is None and data.use_nla,
           "Signal requires NLA evaluation without an overriding active Action")
    _check(len(data.nla_tracks) == 2 and all(len(track.strips) == 1 and not track.mute
                                           and not track.is_solo for track in data.nla_tracks),
           "Signal lost its two unmuted editable NLA tracks")
    strips = {}
    for track in data.nla_tracks:
        strip = track.strips[0]
        _check(strip.action is not None and not strip.mute, "Signal has an empty or muted Action strip")
        role = strip.action.get('motion_action_role')
        _check(role in ('idle', 'lift') and role not in strips, "Signal Action identity is missing or duplicated")
        _check(strip.action.get('motion_action_identity') == obj.get(role + '_action_identity'),
               "Signal's saved Action identity changed")
        _channelbag(strip.action, strip.action_slot)
        strips[role] = strip
    _check(set(strips) == {'idle', 'lift'}, "Signal is missing an idle or lift Action")
    return obj, strips


def _nla_apply(scene, params):
    blend, offset = params['Blend frames'], params['Clip offset']
    _check(0 <= blend <= 24 and 0 <= offset <= 30, "NLA overlap/offset exceeds the bounded frame budget")
    _, strips = _strips(scene)
    idle, lift = strips['idle'], strips['lift']
    end = 33 + offset
    idle.action_frame_start, idle.action_frame_end = 1, end
    idle.frame_start = 1
    idle.frame_end = end
    idle.blend_in, idle.blend_out = 0, 0
    lift.frame_start = end - blend
    lift.action_frame_start, lift.action_frame_end = 1, 33
    lift.frame_end = lift.frame_start + 32
    lift.blend_in, lift.blend_out = blend, 0
    idle.influence, lift.influence = 1, 1
    scene.frame_set(1)


def _nla_verify(scene, params):
    obj, strips = _strips(scene)
    idle, lift = strips['idle'], strips['lift']
    blend, offset = params['Blend frames'], params['Clip offset']
    _check(abs(idle.frame_end - (33 + offset)) < 1e-5
           and abs(lift.frame_start - (33 + offset - blend)) < 1e-5
           and abs(lift.frame_end - (65 + offset - blend)) < 1e-5
           and abs(lift.blend_in - blend) < 1e-5
           and lift.frame_end <= scene.frame_end, "NLA timing differs from declared overlap/offset")
    for strip in strips.values():
        _check(strip.blend_type == 'REPLACE' and not strip.use_auto_blend
               and not strip.use_animated_influence and not strip.use_animated_time
               and abs(strip.scale - 1) < 1e-5 and abs(strip.repeat - 1) < 1e-5,
               "Signal strips lost their bounded linear timing/influence mechanism")
    idle_curve, lift_curve = (_channelbag(strip.action, strip.action_slot) for strip in (idle, lift))
    frames = [max(1, lift.frame_start - 1), lift.frame_start + (blend / 2 if blend else 1),
              idle.frame_end + 1, lift.frame_end - 1]
    saved_frame, saved_subframe = scene.frame_current, scene.frame_subframe
    samples = []
    try:
        for frame in frames:
            scene.frame_set(int(frame), subframe=frame - int(frame))
            _update(scene)
            evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
            angle = evaluated.rotation_euler.y
            if frame < lift.frame_start:
                influence, expected = 0, idle_curve.evaluate(frame)
            else:
                influence = min(1, (frame - lift.frame_start) / blend) if blend else 1
                time = min(33, frame - lift.frame_start + 1)
                base = idle_curve.evaluate(frame) if frame <= idle.frame_end else 0
                expected = base * (1 - influence) + lift_curve.evaluate(time) * influence
            _check(abs(angle - expected) < 3e-5, "NLA evaluated transition differs from strip bounds/influence")
            tip = evaluated.matrix_world @ Vector((0, 0, 1.7))
            samples.append({'frame': frame, 'lift_influence': influence,
                            'hinge_radians': angle, 'expected_radians': expected, 'world_tip': list(tip)})
    finally:
        scene.frame_set(saved_frame, subframe=saved_subframe)
    _check(max(s['hinge_radians'] for s in samples) - min(s['hinge_radians'] for s in samples) > .3,
           "Signal NLA evaluation produced no meaningful lift")
    return {'action_identities': {role: strip.action['motion_action_identity'] for role, strip in strips.items()},
            'action_slots': {role: strip.action_slot.identifier for role, strip in strips.items()},
            'strip_bounds': {role: [strip.frame_start, strip.frame_end] for role, strip in strips.items()},
            'blend_frames': lift.blend_in, 'samples': samples}


def _camera(scene):
    board = _cube(scene, 'Staging / copper identity sign', (0, 0, 1.3), (.5, .08, .35), 'staging_sign')
    _cube(scene, 'Staging / broad identity stroke', (-.18, -.095, 1.3), (.065, .02, .23), 'large_motif', 'cream')
    _cube(scene, 'Staging / broad identity crossbar', (0, -.095, 1.36), (.23, .02, .055), 'large_crossbar', 'cream')
    for index in range(3):
        _cube(scene, 'Staging / small identity pixel', (.16 + index * .065, -.105, 1.12),
              (.018, .018, .018), 'small_motif_' + str(index), 'teal')
    _cube(scene, 'Staging / sign stem', (0, .02, .5), (.07, .07, .5), 'sign_stem', 'teal')
    _check(scene.camera is not None, "Staging requires the provided inspection camera")
    _tag(scene.camera, 'inspection_camera')
    scene.camera.data.type = 'ORTHO'
    scene.camera.data.ortho_scale = 3.2
    scene.camera.location = (3, -5, 3)
    scene.camera.rotation_euler = (Vector((0, 0, 1.3)) - scene.camera.location).to_track_quat('-Z', 'Y').to_euler()
    data = bpy.data.cameras.new('Staging / gameplay perspective')
    gameplay = _object(scene, 'Staging / gameplay camera', data, 'gameplay_camera')
    data.type = 'PERSP'
    data.sensor_fit = 'HORIZONTAL'
    data.clip_start, data.clip_end = .1, 100
    scene.camera = gameplay
    return board


def _camera_apply(scene, params):
    camera = _role(scene, 'gameplay_camera')
    _check(camera.type == 'CAMERA' and camera.data.type == 'PERSP', "Gameplay camera is missing its perspective data")
    target = Vector((0, 0, 1.3))
    camera.location = target + Vector((.15, -1, .22)).normalized() * params['Subject distance']
    camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.angle = math.radians(params['Field of view'])
    scene.camera = camera


def _projection(scene, camera, points):
    _check(camera.type == 'CAMERA' and 0 < camera.data.clip_start < camera.data.clip_end,
           "Camera clipping planes are missing or inverted")
    projected = [world_to_camera_view(scene, camera, point) for point in points]
    _check(all(camera.data.clip_start < point.z < camera.data.clip_end for point in projected),
           "Subject crosses a camera clipping plane")
    bounds = _bounds(projected)
    _check(bounds[0][0] >= 0 and bounds[0][1] <= 1 and bounds[1][0] >= 0 and bounds[1][1] <= 1,
           "Subject is off-camera or overflows the declared framing")
    return {'normalized_bounds': bounds, 'coverage': (bounds[0][1] - bounds[0][0]) * (bounds[1][1] - bounds[1][0]),
            'width_pixels': (bounds[0][1] - bounds[0][0]) * scene.render.resolution_x * scene.render.resolution_percentage / 100,
            'height_pixels': (bounds[1][1] - bounds[1][0]) * scene.render.resolution_y * scene.render.resolution_percentage / 100}


def _camera_verify(scene, params):
    camera, inspection = _role(scene, 'gameplay_camera'), _role(scene, 'inspection_camera')
    _check(scene.camera == camera and camera.data.type == 'PERSP' and inspection.data.type == 'ORTHO',
           "Staging lost its gameplay/inspection projection pair")
    board = _role(scene, 'staging_sign')
    world = [board.matrix_world @ p for p in _vertices(scene, board)]
    center = Vector((0, 0, 1.3))
    distance = (camera.matrix_world.translation - center).length
    _check(abs(distance - params['Subject distance']) < 1e-5
           and abs(math.degrees(camera.data.angle) - params['Field of view']) < 1e-4,
           "Camera FOV/distance differs from controls")
    gameplay = _projection(scene, camera, world)
    _check(gameplay['coverage'] > 1e-5, "Gameplay preview has no measurable subject coverage")
    motifs = {}
    for role in ('large_motif', 'small_motif_0'):
        obj = _role(scene, role)
        motifs[role] = _projection(scene, camera, [obj.matrix_world @ p for p in _vertices(scene, obj)])
    return {'field_of_view_degrees': math.degrees(camera.data.angle), 'subject_distance': distance,
            'gameplay': gameplay, 'inspection': _projection(scene, inspection, world), 'motifs': motifs}


def _mask(scene):
    # A thick faceted mask with actual eye/mouth openings, all topology preserved by keys.
    vertices = [(x / 3 - 1, y, .3 + z / 3) for y in (-.22, .12) for z in range(7) for x in range(7)]
    holes = {(1, 4), (4, 4), (2, 1), (3, 1)}
    faces = []
    front_faces = []
    for z in range(6):
        for x in range(6):
            if (x, z) in holes:
                continue
            a = z * 7 + x
            face = (a, a + 1, a + 8, a + 7)
            front_faces.append(face)
            faces.extend([face, tuple(index + 49 for index in reversed(face))])
    edge_counts = {}
    for face in front_faces:
        for a, b in zip(face, face[1:] + face[:1]):
            key = tuple(sorted((a, b)))
            edge_counts[key] = edge_counts.get(key, 0) + 1
    for (a, b), count in edge_counts.items():
        if count == 1:
            faces.append((a, a + 49, b + 49, b))
    obj = _mesh(scene, 'Expression / original geometric mask', vertices, faces, 'expression_mask', 'teal')
    basis = obj.shape_key_add(name='Basis')
    brow = obj.shape_key_add(name='Raised brow')
    mouth = obj.shape_key_add(name='Wide mouth')
    obj.data.shape_keys.use_relative = True
    for index, point in enumerate(basis.data):
        row, column = (index % 49) // 7, index % 7
        if row in (4, 5) and column in (1, 2, 4, 5):
            brow.data[index].co.z += .22 if row == 5 else .12
            brow.data[index].co.y -= .045
        if row in (1, 2) and column in (2, 3, 4):
            mouth.data[index].co.x *= 1.4
            mouth.data[index].co.z += -.16 if row == 1 else .06
            mouth.data[index].co.y -= .07
    return obj


def _keys(obj):
    _check(obj.type == 'MESH' and obj.data.shape_keys is not None, "Expression is missing its shape-key datablock")
    keys = obj.data.shape_keys
    _check(keys.use_relative, "Expression requires relative shape keys")
    blocks = [keys.key_blocks.get(name) for name in ('Basis', 'Raised brow', 'Wide mouth')]
    _check(all(block is not None for block in blocks) and len(keys.key_blocks) == 3,
           "Expression is missing its Basis or authored expression key")
    _check(all(len(block.data) == len(obj.data.vertices) for block in blocks),
           "Shape-key topology does not match the authored mask")
    _check(all(block.relative_key == blocks[0] and not block.mute for block in blocks[1:]),
           "Expression targets lost their relative Basis or are muted")
    return blocks


def _mask_apply(scene, params):
    _, brow, mouth = _keys(_role(scene, 'expression_mask'))
    brow.value, mouth.value = params['Expression weight'], params['Secondary weight']


def _mask_verify(scene, params):
    obj = _role(scene, 'expression_mask')
    basis, brow, mouth = _keys(obj)
    _check(abs(brow.value - params['Expression weight']) < 1e-5
           and abs(mouth.value - params['Secondary weight']) < 1e-5, "Expression weights missed their target keys")
    actual = _vertices(scene, obj)
    errors, displacement = [], []
    target_motion = [0.0, 0.0]
    for index, point in enumerate(actual):
        base = basis.data[index].co
        _check((base - obj.data.vertices[index].co).length < 1e-6, "Expression Basis no longer matches the authored topology positions")
        deltas = [brow.data[index].co - base, mouth.data[index].co - base]
        expected = base + deltas[0] * params['Expression weight'] + deltas[1] * params['Secondary weight']
        errors.append((point - expected).length)
        displacement.append((point - base).length)
        target_motion = [max(old, delta.length) for old, delta in zip(target_motion, deltas)]
    _check(max(errors) < 2e-5 and all(value > .1 for value in target_motion),
           "Expression evaluation missed authored offsets or a target is empty")
    return {'vertices': len(actual), 'key_names': [key.name for key in (basis, brow, mouth)],
            'weights': [brow.value, mouth.value], 'max_displacement': max(displacement),
            'max_evaluation_error': max(errors), 'target_max_offsets': target_motion,
            'brow_vertex': list(actual[36]), 'mouth_vertex': list(actual[9]), 'bounds': _bounds(actual)}


def _rail(scene):
    from .labs import material, PALETTE
    profile = bpy.data.curves.new('Rail / editable octagonal profile', 'CURVE')
    profile.dimensions = '2D'
    spline = profile.splines.new('POLY')
    spline.points.add(7)
    spline.use_cyclic_u = True
    for index, point in enumerate(spline.points):
        point.co = (.1 * math.cos(index * math.pi / 4), .1 * math.sin(index * math.pi / 4), 0, 1)
    profile_obj = _object(scene, 'Rail / separate profile', profile, 'rail_profile', (-2.8, -1.1, .3))
    profile_obj.hide_render = True
    path = bpy.data.curves.new('Rail / asymmetric editable centerline', 'CURVE')
    path.dimensions = '3D'
    path.bevel_mode = 'OBJECT'
    path.bevel_object = profile_obj
    path.use_fill_caps = True
    path.twist_mode = 'Z_UP'
    spline = path.splines.new('BEZIER')
    spline.bezier_points.add(4)
    for point, co in zip(spline.bezier_points,
                         [(-2.2, 0, .65), (-1.2, .55, 1.4), (.15, -.15, 1.8),
                          (1.25, .5, 1.05), (2.2, -.4, .8)]):
        point.co = co
        point.handle_left_type = point.handle_right_type = 'AUTO'
    first = spline.bezier_points[0]
    first.handle_left_type = first.handle_right_type = 'FREE'
    first.handle_left, first.handle_right = (-2.6, 0, .65), (-1.8, 0, .65)
    path.materials.append(material('Rail / copper', PALETTE['amber']))
    source = _object(scene, 'Rail / swept source', path, 'rail_source')
    _export_copy(scene, source, 'rail_export')
    return source


def _rail_data(scene):
    source, profile = _role(scene, 'rail_source'), _role(scene, 'rail_profile')
    _check(source.type == 'CURVE' and len(source.data.splines) == 1
           and source.data.splines[0].type == 'BEZIER', "Rail is missing its editable Bezier path")
    points = source.data.splines[0].bezier_points
    _check(len(points) == 5 and sum((b.co - a.co).length for a, b in zip(points, points[1:])) > .1,
           "Rail path is empty, zero-length or has changed control-point topology")
    _check(profile.type == 'CURVE' and source.data.bevel_mode == 'OBJECT'
           and source.data.bevel_object == profile and len(profile.data.splines) == 1,
           "Rail is missing its sweep profile")
    shape = profile.data.splines[0]
    _check(shape.type == 'POLY' and shape.use_cyclic_u and len(shape.points) == 8,
           "Rail requires its closed editable octagonal profile")
    return source, profile, points


def _rail_apply(scene, params):
    source, profile, _ = _rail_data(scene)
    source.data.resolution_u = params['Path resolution']
    source.data.splines[0].resolution_u = params['Path resolution']
    radius = params['Profile radius']
    for index, point in enumerate(profile.data.splines[0].points):
        point.co = (radius * math.cos(index * math.pi / 4), radius * math.sin(index * math.pi / 4), 0, 1)
    _copy_evaluated(scene, source, _role(scene, 'rail_export'))


def _rail_verify(scene, params):
    source, profile, points = _rail_data(scene)
    _check(source.data.resolution_u == params['Path resolution']
           and source.data.splines[0].resolution_u == params['Path resolution'], "Rail resolution control missed its path")
    radii = [Vector(point.co[:2]).length for point in profile.data.splines[0].points]
    _check(max(abs(radius - params['Profile radius']) for radius in radii) < 1e-6,
           "Rail profile points do not match the requested radius")
    evaluated = _vertices(scene, source)
    first = points[0]
    tangent = (first.handle_right - first.co).normalized()
    endpoint = [point for point in evaluated if abs((point - first.co).dot(tangent)) < 2e-5]
    _check(len(endpoint) >= 8, "Swept rail lacks a measurable endpoint cross-section")
    measured = max((point - first.co).length for point in endpoint)
    _check(abs(measured - params['Profile radius']) < 2e-5, "Evaluated rail cross-section differs from profile radius")
    copy = _role(scene, 'rail_export')
    _check(copy.type == 'MESH' and len(copy.data.vertices) == len(evaluated), "Rail export copy topology is stale")
    copy_error = max((point - vertex.co).length for point, vertex in zip(evaluated, copy.data.vertices))
    transform_error = _matrix_error(copy.matrix_world, source.matrix_world)
    _check(copy_error < 2e-5 and transform_error < 1e-5,
           "Separate converted rail copy differs from the evaluated source")
    _check(len(evaluated) < 100000, "Rail conversion exceeds the declared geometry budget")
    return {'source_control_points': [list(p.co) for p in points], 'resolution': source.data.resolution_u,
            'evaluated_vertices': len(evaluated), 'converted_vertices': len(copy.data.vertices),
            'cross_section_radius': measured, 'cross_section_vertices': len(endpoint),
            'max_copy_error': copy_error, 'max_copy_transform_error': transform_error, 'bounds': _bounds(evaluated)}


def _typography(scene):
    from .labs import material, PALETTE
    text = bpy.data.curves.new('Typography / editable bundled-font lettering', 'FONT')
    text.body = 'COPPER\nOBSERVATORY'
    text.align_x = 'CENTER'
    text.align_y = 'CENTER'
    text.size = .72
    text.space_line = 1.05
    text.bevel_depth = 0
    text.resolution_u = 4
    text.materials.append(material('Typography / cream lettering', PALETTE['cream']))
    obj = _object(scene, 'Typography / station name', text, 'station_text', (0, -.13, 1.3))
    obj.rotation_euler.x = math.pi / 2
    obj['font_provenance'] = 'Blender bundled Bfont'
    _cube(scene, 'Typography / original copper sign', (0, .08, 1.3), (1.7, .12, .85), 'text_sign')
    _export_copy(scene, obj, 'text_export')
    return obj


def _font(obj):
    _check(obj.type == 'FONT' and obj.data.body.strip(), "Station text is empty or its editable Text Curve is missing")
    font = obj.data.font
    _check(font is not None, "Station text is missing its explicit font dependency")
    _check(font.filepath == '<builtin>', "Station text requires the Blender bundled font; an external font dependency is unavailable")
    _check(obj.get('font_provenance') == 'Blender bundled Bfont', "Station text lost its bundled font provenance")


def _text_apply(scene, params):
    obj = _role(scene, 'station_text')
    _font(obj)
    obj.data.extrude = params['Extrusion']
    local = _vertices(scene, obj)
    width = _bounds(local)[0][1] - _bounds(local)[0][0]
    _check(width > 1e-6, "Station text has no measurable width")
    obj.scale.x = params['Text width'] / width
    _role(scene, 'text_sign').scale.x = (params['Text width'] + .4) / 3.4
    _update(scene)
    _copy_evaluated(scene, obj, _role(scene, 'text_export'))


def _text_verify(scene, params):
    obj, sign = _role(scene, 'station_text'), _role(scene, 'text_sign')
    _font(obj)
    _check(abs(obj.data.extrude - params['Extrusion']) < 1e-6 and obj.data.bevel_depth == 0,
           "Station text extrusion differs from its bounded plain geometry contract")
    local = _vertices(scene, obj)
    bounds = _bounds(local)
    thickness = bounds[2][1] - bounds[2][0]
    _check(abs(thickness - 2 * params['Extrusion']) < 2e-5, "Evaluated text thickness does not follow extrusion")
    world = [obj.matrix_world @ point for point in local]
    world_bounds, sign_bounds = _bounds(world), _bounds([sign.matrix_world @ point for point in _vertices(scene, sign)])
    width = world_bounds[0][1] - world_bounds[0][0]
    _check(abs(width - params['Text width']) < 2e-5, "Evaluated text width differs from its fitting control")
    _check(world_bounds[0][0] >= sign_bounds[0][0] + .1 and world_bounds[0][1] <= sign_bounds[0][1] - .1
           and world_bounds[2][0] >= sign_bounds[2][0] + .05 and world_bounds[2][1] <= sign_bounds[2][1] - .05,
           "Station lettering overflows its declared sign bounds")
    copy = _role(scene, 'text_export')
    _check(copy.type == 'MESH' and len(copy.data.vertices) == len(local), "Separate typography conversion is missing or stale")
    error = max((point - vertex.co).length for point, vertex in zip(local, copy.data.vertices))
    transform_error = _matrix_error(copy.matrix_world, obj.matrix_world)
    _check(error < 2e-5 and transform_error < 1e-5 and len(local) < 100000,
           "Typography conversion differs from source or exceeds its budget")
    return {'body': obj.data.body, 'font_source': obj.data.font.filepath,
            'font_provenance': obj['font_provenance'], 'text_width': width, 'evaluated_thickness': thickness,
            'evaluated_vertices': len(local), 'converted_vertices': len(copy.data.vertices),
            'max_copy_error': error, 'max_copy_transform_error': transform_error,
            'world_bounds': world_bounds, 'sign_bounds': sign_bounds,
            'camera_projection': _projection(scene, scene.camera, world)}


def build(scene, lab, base_subject):
    builders = {'BL-010': _rig, 'BL-011': _nla, 'BL-012': _camera,
                'BL-029': _mask, 'BL-030': _rail, 'BL-031': _typography}
    if lab not in builders:
        raise ValueError(f"No motion builder for {lab}")
    _update(scene)
    _check(base_subject is not None and scene.objects.get(base_subject.name) == base_subject
           and len(base_subject.users_scene) == 1, "Disposable base subject is missing or shared outside this scene")
    bpy.data.objects.remove(base_subject, do_unlink=True)
    obj = builders[lab](scene)
    obj['blender_lab_subject'] = True
    apply_controls(scene, lab, DEFAULTS[lab])
    return obj


def apply_controls(scene, lab, params):
    handlers = {'BL-010': _rig_apply, 'BL-011': _nla_apply, 'BL-012': _camera_apply,
                'BL-029': _mask_apply, 'BL-030': _rail_apply, 'BL-031': _text_apply}
    if lab not in handlers:
        raise ValueError(f"No motion controls for {lab}")
    _update(scene)
    handlers[lab](scene, params)
    _update(scene)


def verify(scene, lab, params, output):
    verifiers = {'BL-010': _rig_verify, 'BL-011': _nla_verify, 'BL-012': _camera_verify,
                 'BL-029': _mask_verify, 'BL-030': _rail_verify, 'BL-031': _text_verify}
    if lab not in verifiers:
        raise ValueError(f"No motion verifier for {lab}")
    _update(scene)
    return verifiers[lab](scene, params)
