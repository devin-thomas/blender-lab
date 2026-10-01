"""Owned drivers, crane IK, reusable poses and evaluated visual-key baking.

Only the caller creates/removes scenes and tracks ownership. No window, editor,
network, external file or arbitrary scripted-driver context is required here.
"""
import hashlib
import json
import math
from uuid import uuid4

import bpy
from mathutils import Euler, Matrix, Vector

from .motion import (_armature, _check, _cube, _matrix_error, _mesh, _object,
                     _skin, _tube, _update)


DEFAULTS = {
    'BL-037': {'Control travel': 1.0, 'Constraint influence': 1.0},
    'BL-038': {'Target reach': 1.5, 'Pole angle': 0.0},
    'BL-039': {'Pose blend': .5, 'Bone scope': 'upper'},
    'BL-040': {'Sample step': 1, 'Bake range': 24},
}
BONES = ('Lower', 'Upper')
POSE_SCHEMA = 'copper-crane-two-joint-v1'
REACH_TOLERANCE = .015
BAKE_SAMPLE_TOLERANCE = 3e-5
BAKE_MOTION_TOLERANCE = .04


def _tag(obj, role):
    obj['kinematics_role'] = role
    obj['kinematics_identity'] = str(uuid4())
    return obj


def _role(scene, role):
    matches = [obj for obj in scene.objects if obj.get('kinematics_role') == role]
    _check(len(matches) == 1, f"Expected exactly one owned kinematics object: {role}")
    return matches[0]


def _empty(scene, name, role, location):
    obj = _tag(_object(scene, name, None, role, location), role)
    obj.empty_display_type = 'SPHERE'
    obj.empty_display_size = .16
    return obj


def _owned_cube(scene, name, role, location, scale, color='amber'):
    return _tag(_cube(scene, name, location, scale, role, color), role)


def _rig(scene, role, sentinel=False):
    rig = _tag(_armature(scene, role, (0, 0, .3)), role)
    for name in BONES:
        rig.pose.bones[name].rotation_mode = 'XYZ'
        rig.data.bones[name]['stable_bone_id'] = POSE_SCHEMA + '/' + name.lower()
    rig['bone_schema'] = POSE_SCHEMA
    if sentinel:
        with bpy.context.temp_override(scene=scene, view_layer=bpy.context.view_layer,
                                       object=rig, active_object=rig,
                                       selected_objects=[rig], selected_editable_objects=[rig]):
            bpy.ops.object.mode_set(mode='EDIT')
            try:
                bone = rig.data.edit_bones.new('Sentinel')
                bone.head, bone.tail = (-1.4, 0, 0), (-1.4, 0, .5)
            finally:
                bpy.ops.object.mode_set(mode='OBJECT')
        bone = rig.pose.bones['Sentinel']
        bone.rotation_mode = 'XYZ'
        bone.rotation_euler = (.17, .09, -.11)
        bone.location = (.07, -.03, .02)
        rig['sentinel_basis'] = json.dumps(_matrix_list(bone.matrix_basis))
    return rig


def _crane_skin(scene, rig, role):
    lower, lower_faces = _tube([0, 1.17], .16)
    upper, upper_faces = _tube([1.23, 2.4], .16)
    count = len(lower)
    obj = _tag(_mesh(scene, 'Crane / original segmented copper arm', lower + upper,
                     lower_faces + [tuple(i + count for i in face) for face in upper_faces],
                     role, location=tuple(rig.location)), role)
    _skin(obj, rig)
    obj.vertex_groups['Lower'].add(list(range(count)), 1, 'REPLACE')
    obj.vertex_groups['Upper'].add(list(range(count, count + len(upper))), 1, 'REPLACE')
    _owned_cube(scene, 'Crane / teal socket', role + '_socket', (0, 0, .15), (.42, .42, .15), 'teal')
    return obj


def _sum_driver(obj, path, index, control, property_name):
    curve = obj.driver_add(path, index)
    curve.driver.type = 'SUM'
    variable = curve.driver.variables.new()
    variable.name = 'owned_control'
    variable.type = 'SINGLE_PROP'
    variable.targets[0].id = control
    variable.targets[0].data_path = '["' + property_name + '"]'
    return curve


def _validate_driver(obj, index, control, property_name):
    _check(obj.animation_data is not None, "Missing trusted driver dependency: animation data")
    curves = [curve for curve in obj.animation_data.drivers
              if curve.data_path == 'location' and curve.array_index == index]
    _check(len(curves) == 1, "Missing trusted driver dependency: expected location channel")
    curve = curves[0]
    driver = curve.driver
    _check(driver.type == 'SUM' and len(driver.variables) == 1,
           "Untrusted scripted driver input: only the original single-variable SUM is allowed")
    variable = driver.variables[0]
    _check(variable.type == 'SINGLE_PROP' and len(variable.targets) == 1,
           "Driver variable no longer has its bounded SINGLE_PROP schema")
    target = variable.targets[0]
    _check(target.id == control and target.data_path == '["' + property_name + '"]',
           "Broken driver data path or target outside the owned schema")
    _check(property_name in control, "Missing trusted driver dependency: " + property_name)
    value = control.path_resolve(target.data_path)
    _check(isinstance(value, (int, float)) and math.isfinite(value), "Driver dependency is nonfinite")
    _check(driver.is_valid and not curve.mute, "Failed driver evaluation or muted trusted driver")
    return curve


def _drivers_build(scene):
    control = _empty(scene, 'Signal / separate travel control', 'travel_control', (-1.5, 0, .3))
    control['travel'] = 1.0
    control.id_properties_ui('travel').update(min=0, max=2, description='Owned non-scripted driver input')
    guide = _empty(scene, 'Signal / horizontal constraint target', 'constraint_target', (1.25, 0, 0))
    signal = _owned_cube(scene, 'Signal / driven copper lever', 'driven_signal', (0, 0, 0), (.2, .2, .3))
    _sum_driver(signal, 'location', 2, control, 'travel')
    follow = signal.constraints.new('COPY_LOCATION')
    follow.name = '01 / blend horizontal target'
    follow.target = guide
    follow.use_x, follow.use_y, follow.use_z = True, False, False
    follow.owner_space = follow.target_space = 'WORLD'
    limit = signal.constraints.new('LIMIT_LOCATION')
    limit.name = '02 / bounded horizontal and vertical travel'
    limit.use_min_x = limit.use_max_x = True
    limit.min_x, limit.max_x = 0, .9
    limit.use_min_z = limit.use_max_z = True
    limit.min_z, limit.max_z = .25, 1.75
    limit.owner_space = 'WORLD'
    _owned_cube(scene, 'Signal / original cream base', 'driver_socket', (0, 0, .08), (.6, .45, .08), 'cream')
    return signal


def _driver_data(scene):
    signal, control, guide = (_role(scene, role) for role in
                              ('driven_signal', 'travel_control', 'constraint_target'))
    curve = _validate_driver(signal, 2, control, 'travel')
    _check(len(signal.constraints) == 2, "Signal constraint order/schema changed")
    follow, limit = signal.constraints
    _check(follow.type == 'COPY_LOCATION' and follow.target == guide
           and follow.use_x and not follow.use_y and not follow.use_z
           and follow.owner_space == follow.target_space == 'WORLD' and not follow.mute,
           "Signal lost its owned horizontal Copy Location constraint")
    _check(limit.type == 'LIMIT_LOCATION' and limit.owner_space == 'WORLD' and not limit.mute
           and limit.use_min_z and limit.use_max_z
           and limit.use_min_x and limit.use_max_x
           and abs(limit.min_x) < 1e-6 and abs(limit.max_x - .9) < 1e-6
           and abs(limit.min_z - .25) < 1e-6 and abs(limit.max_z - 1.75) < 1e-6,
           "Signal lost its declared travel limits")
    return signal, control, guide, curve, follow


def _drivers_apply(scene, params):
    signal, control, _, _, follow = _driver_data(scene)
    control['travel'] = params['Control travel']
    control.update_tag()
    signal.update_tag()
    follow.influence = params['Constraint influence']
    scene.frame_set(scene.frame_current)


def _drivers_verify(scene, params):
    signal, control, guide, curve, follow = _driver_data(scene)
    evaluated = signal.evaluated_get(bpy.context.evaluated_depsgraph_get())
    actual = evaluated.matrix_world.translation
    expected = Vector((min(.9, max(0, guide.matrix_world.translation.x * params['Constraint influence'])), 0,
                       min(1.75, max(.25, params['Control travel']))))
    error = (actual - expected).length
    _check(error < 2e-5, "Driven/constraint evaluated transform differs from the known control result")
    _check(abs(control['travel'] - params['Control travel']) < 1e-6
           and abs(follow.influence - params['Constraint influence']) < 1e-6,
           "Travel/influence controls missed their native mechanism")
    return {'evaluated_translation': list(actual), 'expected_translation': list(expected),
            'max_transform_error': error, 'authored_driver_z': signal.location.z,
            'driver_type': curve.driver.type, 'variable_type': curve.driver.variables[0].type,
            'target_identity': control['kinematics_identity'],
            'target_data_path': curve.driver.variables[0].targets[0].data_path,
            'constraint_order': [constraint.type for constraint in signal.constraints],
            'constraint_influence': follow.influence, 'horizontal_limits': [0, .9],
            'vertical_limits': [.25, 1.75],
            'automatic_script_execution_enabled': False}


def _ik_setup(scene, role):
    rig = _rig(scene, role)
    # A perfectly straight initial chain is a singular IK seed. A small authored
    # bend gives the solver a stable branch without changing the editable rest.
    rig.pose.bones['Upper'].rotation_euler.x = .25
    target = _empty(scene, 'Crane / owned effector', role + '_target', (1.2, 0, 1.2))
    pole = _empty(scene, 'Crane / owned bend pole', role + '_pole', (0, -2, 1.2))
    for name in BONES:
        bone = rig.pose.bones[name]
        bone.ik_stretch = 0
        for axis in 'xyz':
            setattr(bone, 'use_ik_limit_' + axis, True)
            setattr(bone, 'ik_min_' + axis, -math.pi)
            setattr(bone, 'ik_max_' + axis, math.pi)
    constraint = rig.pose.bones['Upper'].constraints.new('IK')
    constraint.name = 'Crane / bounded two-bone solve'
    constraint.target, constraint.pole_target = target, pole
    constraint.chain_count = 2
    constraint.use_stretch = False
    constraint.iterations = 128
    return rig, target, pole, constraint


def _ik_data(scene, role):
    rig, target, pole = (_role(scene, key) for key in (role, role + '_target', role + '_pole'))
    _check(rig.type == 'ARMATURE' and set(rig.data.bones.keys()) == set(BONES),
           "Invalid crane bone schema; expected the original two-bone chain")
    lower, upper = (rig.data.bones[name] for name in BONES)
    _check(upper.parent == lower and upper.use_connect and lower.parent is None,
           "Invalid connected two-bone IK hierarchy")
    constraints = rig.pose.bones['Upper'].constraints
    _check(len(constraints) == 1, "Invalid IK chain: expected exactly one owned constraint")
    constraint = constraints[0]
    _check(constraint.type == 'IK' and constraint.target == target and constraint.pole_target == pole
           and constraint.chain_count == 2 and not constraint.use_stretch
           and not constraint.mute and abs(constraint.influence - 1) < 1e-6,
           "Missing pole/target, invalid chain length or altered bounded IK solve")
    _check(not rig.pose.bones['Lower'].constraints, "Unexpected lower-bone constraint")
    for name in BONES:
        for axis in 'xyz':
            bone = rig.pose.bones[name]
            _check(getattr(bone, 'use_ik_limit_' + axis)
                   and abs(getattr(bone, 'ik_min_' + axis) + math.pi) < 1e-5
                   and abs(getattr(bone, 'ik_max_' + axis) - math.pi) < 1e-5
                   and bone.ik_stretch == 0,
                   "Crane joint limits/stretch settings changed")
    return rig, target, pole, constraint


def _ik_build(scene):
    rig, _, _, _ = _ik_setup(scene, 'reach_rig')
    return _crane_skin(scene, rig, 'reach_skin')


def _ik_apply(scene, params):
    rig, target, _, constraint = _ik_data(scene, 'reach_rig')
    direction = Vector((.8, 0, .6))
    target.location = rig.location + direction * params['Target reach']
    constraint.pole_angle = math.radians(params['Pole angle'])
    rig.update_tag()
    _update(scene)


def _ik_measure(scene, role):
    rig, target, pole, constraint = _ik_data(scene, role)
    _update(scene)
    evaluated = rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
    bones = [evaluated.pose.bones[name] for name in BONES]
    root = evaluated.matrix_world @ bones[0].head
    elbow = evaluated.matrix_world @ bones[0].tail
    tip = evaluated.matrix_world @ bones[1].tail
    target_position = target.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation
    reach = (target_position - root).length
    lengths = [(elbow - root).length, (tip - elbow).length]
    rest_lengths = [rig.data.bones[name].length for name in BONES]
    _check(max(abs(a - b) for a, b in zip(lengths, rest_lengths)) < 2e-5,
           "IK exceeded its declared no-stretch segment lengths")
    residual = (tip - target_position).length
    reachable = abs(rest_lengths[0] - rest_lengths[1]) <= reach <= sum(rest_lengths)
    if reachable:
        _check(residual < REACH_TOLERANCE, "Reachable crane target exceeds the declared tip-error tolerance")
    else:
        _check(residual >= reach - sum(rest_lengths) - 2e-5,
               "Unreachable target produced a success-shaped residual")
    joint = (elbow - root).angle(tip - elbow)
    _check(math.isfinite(joint) and joint <= math.pi + 1e-5, "Crane joint angle exceeds its declared limits")
    return {'root': list(root), 'elbow': list(elbow), 'tip': list(tip),
            'target': list(target_position), 'pole': list(pole.matrix_world.translation),
            'target_distance': reach, 'segment_lengths': lengths, 'maximum_reach': sum(rest_lengths),
            'reachable': reachable, 'solve_status': 'reachable' if reachable else 'unreachable-residual',
            'tip_error': residual, 'tip_tolerance': REACH_TOLERANCE,
            'joint_bend_degrees': math.degrees(joint), 'pole_angle_degrees': math.degrees(constraint.pole_angle),
            'chain_count': constraint.chain_count,
            'joint_limits_degrees': {name: {axis: [-180, 180] for axis in 'xyz'} for name in BONES}}


def _ik_verify(scene, params):
    result = _ik_measure(scene, 'reach_rig')
    _check(abs(result['target_distance'] - params['Target reach']) < 1e-5
           and abs(result['pole_angle_degrees'] - params['Pole angle']) < 1e-5,
           "Reach/pole controls did not update the evaluated crane mechanism")
    return result


def _action(obj, name, role):
    action = bpy.data.actions.new(name)
    action['kinematics_action_role'] = role
    action['kinematics_action_identity'] = str(uuid4())
    slot = action.slots.new(id_type='OBJECT', name=obj.name)
    strip = action.layers.new('Original bounded channels').strips.new(type='KEYFRAME')
    bag = strip.channelbag(slot, ensure=True)
    obj[role + '_action_identity'] = action['kinematics_action_identity']
    obj[role + '_slot_identifier'] = slot.identifier
    return action, slot, bag


def _curve(bag, path, index, keys):
    curve = bag.fcurves.new(data_path=path, index=index)
    curve.keyframe_points.add(len(keys))
    for point, (frame, value) in zip(curve.keyframe_points, keys):
        point.co = (frame, value)
        point.interpolation = 'LINEAR'
    curve.update()
    return curve


def _action_data(obj, role):
    identity = obj.get(role + '_action_identity')
    matches = [action for action in bpy.data.actions
               if action.get('kinematics_action_identity') == identity]
    _check(identity is not None and len(matches) == 1, f"Named unavailable Action: {role}")
    action = matches[0]
    _check(action.get('kinematics_action_role') == role, "Action provenance role changed")
    slots = [slot for slot in action.slots if slot.identifier == obj.get(role + '_slot_identifier')
             and slot.target_id_type == 'OBJECT']
    _check(len(slots) == 1, f"Named unavailable pose/clip: missing compatible Action slot for {role}")
    slot = slots[0]
    bags = [strip.channelbag(slot) for layer in action.layers for strip in layer.strips
            if strip.type == 'KEYFRAME']
    bags = [bag for bag in bags if bag is not None]
    _check(len(bags) == 1, f"Named unavailable Action channelbag: {role}")
    return action, slot, bags[0]


def _matrix_list(matrix):
    return [[float(value) for value in row] for row in matrix]


def _pose_build(scene):
    rig = _rig(scene, 'pose_rig', sentinel=True)
    for role, angles in (('rest_pose', {'Lower': 0.0, 'Upper': 0.0}),
                         ('reach_pose', {'Lower': -.35, 'Upper': .9})):
        action, _, bag = _action(rig, 'Crane / original ' + role.replace('_', ' '), role)
        for name in BONES:
            for axis in range(3):
                _curve(bag, 'pose.bones["' + name + '"].rotation_euler', axis,
                       [(1, angles[name] if axis == 0 else 0.0)])
        action['bone_schema'] = POSE_SCHEMA
        action['bone_ids'] = json.dumps({name: rig.data.bones[name]['stable_bone_id'] for name in BONES})
        action.asset_mark()
        action.use_fake_user = True
        action.asset_data.author = 'Blender Lab original fixture'
        action.asset_data.description = 'Original crane pose; exact bone identity, scoped Euler channels; no retargeting.'
        action.asset_data.tags.new('Original')
        action.asset_data.tags.new('Copper Observatory')
    return _crane_skin(scene, rig, 'pose_skin')


def _pose_data(scene):
    rig = _role(scene, 'pose_rig')
    _check(rig.type == 'ARMATURE' and rig.get('bone_schema') == POSE_SCHEMA
           and set(rig.data.bones.keys()) == set(BONES) | {'Sentinel'},
           "Incompatible bone schema prevents automatic pose application")
    _check(rig.data.bones['Upper'].parent == rig.data.bones['Lower']
           and rig.data.bones['Upper'].use_connect
           and rig.data.bones['Lower'].parent is None,
           "Incompatible pose bone hierarchy")
    assets = {}
    for role in ('rest_pose', 'reach_pose'):
        action, slot, bag = _action_data(rig, role)
        _check(action.asset_data is not None and action.use_fake_user
               and action.asset_data.author == 'Blender Lab original fixture'
               and action.get('bone_schema') == POSE_SCHEMA,
               "Pose asset lost original provenance or retention metadata")
        _check(json.loads(action['bone_ids']) ==
               {name: rig.data.bones[name].get('stable_bone_id') for name in BONES},
               "Incompatible stable bone identifiers prevent automatic pose application")
        expected = {('pose.bones["' + name + '"].rotation_euler', axis)
                    for name in BONES for axis in range(3)}
        _check(len(bag.fcurves) == 6 and {(curve.data_path, curve.array_index) for curve in bag.fcurves} == expected
               and all(len(curve.keyframe_points) == 1 and not curve.mute for curve in bag.fcurves),
               "Pose Action channel filter includes missing, foreign or invalid bone channels")
        for curve in bag.fcurves:
            rig.path_resolve(curve.data_path)
        assets[role] = (action, slot, bag)
    return rig, assets


def _scope(params):
    scopes = {'upper': ('Upper',), 'lower': ('Lower',), 'all owned bones': BONES}
    _check(params['Bone scope'] in scopes, "Unavailable pose bone scope")
    return scopes[params['Bone scope']]


def _pose_values(bag):
    return {(curve.data_path, curve.array_index): curve.evaluate(1) for curve in bag.fcurves}


def _pose_apply(scene, params):
    rig, assets = _pose_data(scene)
    selected = _scope(params)
    untouched = {bone.name: _matrix_list(bone.matrix_basis) for bone in rig.pose.bones if bone.name not in selected}
    rest, target = (_pose_values(assets[role][2]) for role in ('rest_pose', 'reach_pose'))
    for name in selected:
        bone = rig.pose.bones[name]
        _check(bone.rotation_mode == 'XYZ' and not bone.constraints,
               "Pose application requires its original unconstrained XYZ bone channels")
        for axis in range(3):
            key = ('pose.bones["' + name + '"].rotation_euler', axis)
            bone.rotation_euler[axis] = rest[key] + params['Pose blend'] * (target[key] - rest[key])
    rig['untouched_basis'] = json.dumps(untouched, sort_keys=True)
    rig.update_tag()


def _pose_verify(scene, params):
    rig, assets = _pose_data(scene)
    selected = _scope(params)
    rest, target = (_pose_values(assets[role][2]) for role in ('rest_pose', 'reach_pose'))
    evaluated = rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
    errors, angles, basis_errors = [], {}, []
    for name in selected:
        bone = evaluated.pose.bones[name]
        expected = []
        for axis in range(3):
            key = ('pose.bones["' + name + '"].rotation_euler', axis)
            expected.append(rest[key] + params['Pose blend'] * (target[key] - rest[key]))
            errors.append(abs(bone.rotation_euler[axis] - expected[-1]))
        expected_basis = Matrix.LocRotScale(rig.pose.bones[name].location,
                                          Euler(expected, 'XYZ').to_quaternion(),
                                          rig.pose.bones[name].scale)
        basis_errors.append(_matrix_error(bone.matrix_basis, expected_basis))
        angles[name] = list(bone.rotation_euler)
    unchanged = json.loads(rig['untouched_basis'])
    unchanged_error = max((_matrix_error(rig.pose.bones[name].matrix_basis, Matrix(matrix))
                           for name, matrix in unchanged.items()), default=0)
    sentinel_error = _matrix_error(rig.pose.bones['Sentinel'].matrix_basis, Matrix(json.loads(rig['sentinel_basis'])))
    _check(max(errors + basis_errors) < 2e-5 and unchanged_error < 2e-5 and sentinel_error < 2e-5,
           "Scoped pose blend differs from its assets or modified unrelated bone channels")
    return {'selected_bones': list(selected), 'evaluated_rotations_radians': angles,
            'max_blend_error': max(errors), 'max_evaluated_basis_error': max(basis_errors),
            'unselected_channel_error': unchanged_error, 'sentinel_basis_error': sentinel_error,
            'pose_assets': [{'role': role, 'identity': action['kinematics_action_identity'],
                             'slot_identifier': slot.identifier, 'channels': len(bag.fcurves),
                             'author': action.asset_data.author, 'description': action.asset_data.description,
                             'bone_schema': action['bone_schema']}
                            for role, (action, slot, bag) in assets.items()]}


def _bake_build(scene):
    rig, target, pole, _ = _ik_setup(scene, 'bake_source')
    dependency = _empty(scene, 'Crane / trusted lateral dependency', 'bake_dependency', (-1.3, 0, .3))
    dependency['lateral'] = -.15
    # Keep the driven pole separate from the Action's animated location vector.
    # Mixing driver and Action components on that vector can yield stale IK
    # dependencies in this runtime even after a view-layer update.
    _sum_driver(pole, 'location', 0, dependency, 'lateral')
    action, slot, bag = _action(target, 'Crane / bounded original target clip', 'target_clip')
    _curve(bag, 'location', 0, [(1, .9), (20, 1.55), (40, .75), (60, 1.4)])
    _curve(bag, 'location', 2, [(1, 1.5), (20, 1.0), (40, 1.65), (60, 1.25)])
    target.animation_data_create()
    target.animation_data.action = action
    target.animation_data.action_slot = slot
    stage = _rig(scene, 'baked_copy')
    stage.hide_render = True
    baked, baked_slot, _ = _action(stage, 'Crane / separate visual-key bake', 'visual_bake')
    stage.animation_data_create()
    stage.animation_data.action = baked
    stage.animation_data.action_slot = baked_slot
    scene.frame_end = 60
    return _crane_skin(scene, rig, 'bake_skin')


def _source_fingerprint(scene):
    rig, target, pole, constraint = _ik_data(scene, 'bake_source')
    dependency = _role(scene, 'bake_dependency')
    driver = _validate_driver(pole, 0, dependency, 'lateral')
    action, slot, bag = _action_data(target, 'target_clip')
    _check(target.animation_data.action == action and target.animation_data.action_slot == slot
           and len(bag.fcurves) == 2
           and {(curve.data_path, curve.array_index) for curve in bag.fcurves} == {('location', 0), ('location', 2)},
           "Editable source target Action/slot/channel contract changed")
    signature = {
        'rig': rig['kinematics_identity'], 'matrix': _matrix_list(rig.matrix_world),
        'rest': {name: _matrix_list(rig.data.bones[name].matrix_local) for name in BONES},
        'pose_basis': {name: _matrix_list(rig.pose.bones[name].matrix_basis) for name in BONES},
        'target': target['kinematics_identity'], 'pole': pole['kinematics_identity'],
        'pole_matrix': _matrix_list(pole.matrix_world),
        'constraint': [constraint.type, constraint.chain_count, constraint.pole_angle,
                       constraint.use_stretch, constraint.iterations, constraint.influence],
        'driver': [driver.driver.type, driver.driver.variables[0].type,
                   dependency['kinematics_identity'], driver.driver.variables[0].targets[0].data_path,
                   dependency['lateral']],
        'action': action['kinematics_action_identity'], 'slot': slot.identifier,
        'curves': [(curve.data_path, curve.array_index,
                    [(list(point.co), point.interpolation, list(point.handle_left), list(point.handle_right))
                     for point in curve.keyframe_points]) for curve in bag.fcurves],
    }
    return hashlib.sha256(json.dumps(signature, sort_keys=True).encode('ascii')).hexdigest()


def _sample_frames(params):
    step, end = params['Sample step'], params['Bake range']
    _check(type(step) is int and type(end) is int and 1 <= step <= 4 and 12 <= end <= 60,
           "Bake requires bounded integer Sample step and Bake range")
    return sorted(set(range(1, end + 1, step)) | {end})


def _evaluated_pose(scene, rig):
    _update(scene)
    evaluated = rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return {name: evaluated.pose.bones[name].matrix.copy() for name in BONES}


def _bake_apply(scene, params):
    frames = _sample_frames(params)
    source, _, _, _ = _ik_data(scene, 'bake_source')
    stage = _role(scene, 'baked_copy')
    action, slot, bag = _action_data(stage, 'visual_bake')
    _check(stage.type == 'ARMATURE' and set(stage.data.bones.keys()) == set(BONES)
           and stage.animation_data.action == action and stage.animation_data.action_slot == slot
           and all(not bone.constraints for bone in stage.pose.bones),
           "Visual-key stage lost its separate editable, constraint-free rig/Action")
    before = _source_fingerprint(scene)
    old_frame = scene.frame_current
    values = {name: {'location': [], 'rotation_quaternion': [], 'scale': []} for name in BONES}
    previous_quaternions = {}
    try:
        for frame in frames:
            scene.frame_set(frame)
            matrices = _evaluated_pose(scene, source)
            for name in BONES:
                bone = source.data.bones[name]
                kwargs = {}
                if bone.parent is not None:
                    kwargs = {'parent_matrix': matrices[bone.parent.name],
                              'parent_matrix_local': bone.parent.matrix_local}
                basis = bone.convert_local_to_pose(matrices[name], bone.matrix_local, invert=True, **kwargs)
                location, quaternion, scale = basis.decompose()
                if name in previous_quaternions and quaternion.dot(previous_quaternions[name]) < 0:
                    quaternion.negate()
                previous_quaternions[name] = quaternion.copy()
                for channel, value in (('location', location), ('rotation_quaternion', quaternion), ('scale', scale)):
                    values[name][channel].append((frame, list(value)))
        for curve in list(bag.fcurves):
            bag.fcurves.remove(curve)
        for name in BONES:
            stage.pose.bones[name].rotation_mode = 'QUATERNION'
            for channel, samples in values[name].items():
                for axis in range(len(samples[0][1])):
                    _curve(bag, 'pose.bones["' + name + '"].' + channel, axis,
                           [(frame, value[axis]) for frame, value in samples])
        stage['bake_frames'] = json.dumps(frames)
        stage['source_digest'] = before
        stage['sample_step'] = params['Sample step']
        stage['bake_range'] = params['Bake range']
        stage.update_tag()
    finally:
        scene.frame_set(old_frame)
        _update(scene)
    _check(_source_fingerprint(scene) == before, "Visual-key baking modified the editable source rig/Action")


def _bake_verify(scene, params):
    frames = _sample_frames(params)
    source, _, _, _ = _ik_data(scene, 'bake_source')
    stage = _role(scene, 'baked_copy')
    action, slot, bag = _action_data(stage, 'visual_bake')
    _check(json.loads(stage.get('bake_frames', '[]')) == frames and len(bag.fcurves) == 20
           and stage.animation_data.action == action and stage.animation_data.action_slot == slot
           and all(not bone.constraints for bone in stage.pose.bones),
           "Visual-key copy is missing declared samples or retains source constraints")
    expected_channels = {('pose.bones["' + name + '"].' + channel, axis)
                         for name in BONES for channel, count in
                         (('location', 3), ('rotation_quaternion', 4), ('scale', 3)) for axis in range(count)}
    _check({(curve.data_path, curve.array_index) for curve in bag.fcurves} == expected_channels
           and all([int(round(point.co.x)) for point in curve.keyframe_points] == frames
                   and not curve.mute for curve in bag.fcurves),
           "Visual-key Action channel/sample contract changed")
    _check(stage.get('source_digest') == _source_fingerprint(scene),
           "Editable source changed after the declared bake")
    old_frame = scene.frame_current
    comparisons = []
    try:
        for frame in range(1, params['Bake range'] + 1):
            scene.frame_set(frame)
            original, baked = _evaluated_pose(scene, source), _evaluated_pose(scene, stage)
            error = max(_matrix_error(original[name], baked[name]) for name in BONES)
            comparisons.append({'frame': frame, 'matrix_error': error, 'keyed_sample': frame in frames})
    finally:
        scene.frame_set(old_frame)
        _update(scene)
    sampled = max(row['matrix_error'] for row in comparisons if row['keyed_sample'])
    interpolated = max(row['matrix_error'] for row in comparisons)
    _check(sampled < BAKE_SAMPLE_TOLERANCE,
           "Visual-key baked copy differs from source evaluated transforms at declared samples")
    status = 'within-tolerance' if interpolated <= BAKE_MOTION_TOLERANCE else 'sparse-sampling-tolerance-exceeded'
    return {'bake_method': 'evaluated visual transforms to explicit local-basis slotted Action keys',
            'sample_frames': frames, 'sample_step': stage['sample_step'], 'bake_range': stage['bake_range'],
            'channels': len(bag.fcurves), 'source_constraints_retained': True, 'copy_constraints': 0,
            'source_digest': stage['source_digest'], 'source_unchanged': _source_fingerprint(scene) == stage['source_digest'],
            'max_sample_matrix_error': sampled, 'sample_tolerance': BAKE_SAMPLE_TOLERANCE,
            'max_all_frame_matrix_error': interpolated, 'motion_tolerance': BAKE_MOTION_TOLERANCE,
            'sampling_status': status, 'interchange_ready': False,
            'export_state': 'pending', 'downstream_state': 'not-run',
            'interchange_limitation': 'Visual-key comparison is measured in Blender; format export/reimport and named receiving-engine interpolation/skinning remain pending.',
            'frame_comparisons': comparisons}


def build(scene, lab, base_subject):
    builders = {'BL-037': _drivers_build, 'BL-038': _ik_build,
                'BL-039': _pose_build, 'BL-040': _bake_build}
    _check(lab in builders, f"No kinematics builder for {lab}")
    _update(scene)
    _check(base_subject is not None and scene.objects.get(base_subject.name) == base_subject
           and len(base_subject.users_scene) == 1, "Disposable base subject is missing or shared outside this scene")
    bpy.data.objects.remove(base_subject, do_unlink=True)
    subject = builders[lab](scene)
    subject['blender_lab_subject'] = True
    apply_controls(scene, lab, DEFAULTS[lab])
    return subject


def apply_controls(scene, lab, params):
    handlers = {'BL-037': _drivers_apply, 'BL-038': _ik_apply,
                'BL-039': _pose_apply, 'BL-040': _bake_apply}
    _check(lab in handlers, f"No kinematics controls for {lab}")
    _check(set(params) == set(DEFAULTS[lab]), "Kinematics requires exactly the card's two named controls")
    _update(scene)
    handlers[lab](scene, params)
    _update(scene)


def verify(scene, lab, params, output):
    verifiers = {'BL-037': _drivers_verify, 'BL-038': _ik_verify,
                 'BL-039': _pose_verify, 'BL-040': _bake_verify}
    _check(lab in verifiers, f"No kinematics verifier for {lab}")
    _update(scene)
    return verifiers[lab](scene, params)
