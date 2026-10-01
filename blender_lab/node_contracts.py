"""Repeat-zone and typed node-interface teaching fixtures.

Scene setup, asset snapshots and lifecycle remain owned by the shared lab host.
"""
import json
import math

import bpy


_LABS = {'BL-033', 'BL-035'}
_REPEAT_DEFAULTS = {'Iterations': 4, 'Step offset': 0.2}
_INTERFACE_DEFAULTS = {'Width': 1.0, 'Count': 3}
_REPEAT_STATE = 'tower_state_geometry'
_REPEAT_IDS = {'Iterations': 'blender_lab_repeat_iterations_identifier',
               'Step offset': 'blender_lab_repeat_step_identifier'}
_INTERFACE_IDS = {'Width': 'blender_lab_width_identifier',
                  'Count': 'blender_lab_count_identifier'}
_GEOMETRY_ID = 'blender_lab_geometry_identifier'
_SHADER_IDS = {'Roughness': 'blender_lab_shader_roughness_identifier',
               'Base Color': 'blender_lab_shader_color_identifier'}


def _check(condition, message):
    if not condition:
        raise AssertionError(message)


def _tag(obj, role):
    obj['node_contract_role'] = role
    return obj


def _role(scene, role):
    objects = [obj for obj in scene.objects if obj.get('node_contract_role') == role]
    if len(objects) != 1:
        raise AssertionError(f"Expected exactly one node-contract object for role {role!r}")
    return objects[0]


def _new_group(name):
    group = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    group.is_modifier = True
    return group


def _node(group, kind, name, location):
    node = group.nodes.new(kind)
    node.name = name
    node.label = name
    node.location = location
    return node


def _link(group, source, source_name, target, target_name):
    group.links.new(source.outputs[source_name], target.inputs[target_name])


def _socket_by_identifier(sockets, identifier):
    matches = [socket for socket in sockets if socket.identifier == identifier]
    if len(matches) != 1:
        raise ValueError(f'Node socket identifier {identifier!r} is missing or duplicated')
    return matches[0]


def _cube(scene, name, dimensions, material):
    mesh = bpy.data.meshes.new(name + ' source mesh')
    vertices = [(-dimensions[0] / 2, -dimensions[1] / 2, -dimensions[2] / 2),
                ( dimensions[0] / 2, -dimensions[1] / 2, -dimensions[2] / 2),
                ( dimensions[0] / 2,  dimensions[1] / 2, -dimensions[2] / 2),
                (-dimensions[0] / 2,  dimensions[1] / 2, -dimensions[2] / 2),
                (-dimensions[0] / 2, -dimensions[1] / 2,  dimensions[2] / 2),
                ( dimensions[0] / 2, -dimensions[1] / 2,  dimensions[2] / 2),
                ( dimensions[0] / 2,  dimensions[1] / 2,  dimensions[2] / 2),
                (-dimensions[0] / 2,  dimensions[1] / 2,  dimensions[2] / 2)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    return obj


def _material(name):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (0.84, 0.34, 0.12, 1.0)
    material.use_nodes = True
    shader = material.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = material.diffuse_color
    shader.inputs['Roughness'].default_value = 0.72
    material[_SHADER_IDS['Roughness']] = shader.inputs['Roughness'].identifier
    material[_SHADER_IDS['Base Color']] = shader.inputs['Base Color'].identifier
    return material


def _mesh_snapshot(obj):
    data = obj.data
    record = {'name': obj.name, 'type': obj.type,
              'location': [round(float(v), 7) for v in obj.location],
              'rotation': [round(float(v), 7) for v in obj.rotation_euler],
              'scale': [round(float(v), 7) for v in obj.scale],
              'data': data.name if data else None}
    if obj.type == 'MESH':
        record['vertices'] = [[round(float(c), 7) for c in vertex.co] for vertex in data.vertices]
        record['faces'] = [list(poly.vertices) for poly in data.polygons]
    elif obj.type == 'CAMERA':
        record['camera'] = [obj.data.type, float(obj.data.lens), float(obj.data.ortho_scale)]
    return record


def _protected_scene_state(scene, subject):
    return {'camera': scene.camera.name if scene.camera else None,
            'objects': [_mesh_snapshot(obj) for obj in sorted(scene.objects, key=lambda item: item.name)
                        if obj != subject]}


def _ensure_protected_unchanged(scene, expected):
    actual = _protected_scene_state(scene, _role(scene, 'primary'))
    _check(actual == expected, 'A protected scene object, plinth, or camera changed')


def _repeat_graph(material):
    group = _new_group('BL-033 / paired repeat tower')
    iterations = group.interface.new_socket(name='Iterations', in_out='INPUT', socket_type='NodeSocketInt')
    iterations.default_value = _REPEAT_DEFAULTS['Iterations']
    iterations.min_value, iterations.max_value = 0, 12
    step = group.interface.new_socket(name='Step offset', in_out='INPUT', socket_type='NodeSocketFloat')
    step.default_value = _REPEAT_DEFAULTS['Step offset']
    step.min_value, step.max_value = 0.05, 0.5
    output_geometry = group.interface.new_socket(name='Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    group[_REPEAT_STATE] = 'Geometry'
    group[_REPEAT_IDS['Iterations']] = iterations.identifier
    group[_REPEAT_IDS['Step offset']] = step.identifier
    group['blender_lab_repeat_output_identifier'] = output_geometry.identifier

    nodes = group.nodes
    input_node = _node(group, 'NodeGroupInput', 'Repeat controls', (-900, 200))
    output_node = _node(group, 'NodeGroupOutput', 'Tower output', (900, 200))
    seed = _node(group, 'GeometryNodeMeshCube', 'Initial tower module', (-900, -150))
    seed.inputs['Size'].default_value = (0.42, 0.42, 0.2)
    seed_material = _node(group, 'GeometryNodeSetMaterial', 'Copper ceramic module', (-660, -150))
    seed_material.inputs['Material'].default_value = material
    repeat_in = _node(group, 'GeometryNodeRepeatInput', 'Repeat input / state', (-380, 260))
    repeat_out = _node(group, 'GeometryNodeRepeatOutput', 'Repeat output / state', (680, 260))
    repeat_in.pair_with_output(repeat_out)
    template = _node(group, 'GeometryNodeMeshCube', 'One new tower module', (-300, -170))
    template.inputs['Size'].default_value = (0.42, 0.42, 0.2)
    module_material = _node(group, 'GeometryNodeSetMaterial', 'Module material', (-80, -170))
    module_material.inputs['Material'].default_value = material
    multiply = _node(group, 'ShaderNodeMath', 'Iteration times step', (-300, -450))
    multiply.operation = 'MULTIPLY'
    multiply.inputs[1].default_value = 1.0
    increment = _node(group, 'ShaderNodeMath', 'Next module index', (-500, -450))
    increment.operation = 'ADD'
    increment.inputs[1].default_value = 1.0
    combine = _node(group, 'ShaderNodeCombineXYZ', 'Vertical step', (-80, -420))
    position = _node(group, 'GeometryNodeSetPosition', 'Place next module', (150, -150))
    join = _node(group, 'GeometryNodeJoinGeometry', 'Accumulate modules', (420, 200))

    _link(group, seed, 'Mesh', seed_material, 'Geometry')
    _link(group, seed_material, 'Geometry', repeat_in, 'Geometry')
    group.links.new(_socket_by_identifier(input_node.outputs, iterations.identifier),
                    repeat_in.inputs['Iterations'])
    group.links.new(repeat_in.outputs['Iteration'], increment.inputs[0])
    _link(group, increment, 0, multiply, 0)
    group.links.new(_socket_by_identifier(input_node.outputs, step.identifier), multiply.inputs[1])
    _link(group, multiply, 0, combine, 'Z')
    _link(group, template, 'Mesh', module_material, 'Geometry')
    _link(group, module_material, 'Geometry', position, 'Geometry')
    _link(group, combine, 'Vector', position, 'Offset')
    _link(group, repeat_in, 'Geometry', join, 'Geometry')
    _link(group, position, 'Geometry', join, 'Geometry')
    _link(group, join, 'Geometry', repeat_out, 'Geometry')
    _link(group, repeat_out, 'Geometry', output_node, 'Geometry')
    return group


def _interface_graph(material):
    group = _new_group('BL-035 / typed rail interface')
    geometry_out = group.interface.new_socket(name='Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    width = group.interface.new_socket(name='Width', in_out='INPUT', socket_type='NodeSocketFloat')
    width.default_value, width.min_value, width.max_value = 1.0, 0.2, 3.0
    count = group.interface.new_socket(name='Count', in_out='INPUT', socket_type='NodeSocketInt')
    count.default_value, count.min_value, count.max_value = 3, 1, 12
    group[_GEOMETRY_ID] = geometry_out.identifier
    group[_INTERFACE_IDS['Width']] = width.identifier
    group[_INTERFACE_IDS['Count']] = count.identifier

    group_input = _node(group, 'NodeGroupInput', 'Named controls', (-700, 180))
    group_output = _node(group, 'NodeGroupOutput', 'Rail output', (570, 180))
    line = _node(group, 'GeometryNodeMeshLine', 'Rail positions', (-430, 240))
    line.inputs['Start Location'].default_value = (-0.8, 0, 0)
    line.inputs['Offset'].default_value = (0.8, 0, 0)
    bar = _node(group, 'GeometryNodeMeshCube', 'Rail cross section', (-430, -100))
    bar.inputs['Size'].default_value = (0.62, 1.0, 0.16)
    bar_material = _node(group, 'GeometryNodeSetMaterial', 'Typed shader surface', (-200, -100))
    bar_material.inputs['Material'].default_value = material
    instances = _node(group, 'GeometryNodeInstanceOnPoints', 'One bar per position', (40, 220))
    realize = _node(group, 'GeometryNodeRealizeInstances', 'Editable rail mesh', (300, 220))
    group.links.new(_socket_by_identifier(group_input.outputs, count.identifier), line.inputs['Count'])
    # Keep width on the bar's Y dimension through a separate typed vector field.
    combine = _node(group, 'ShaderNodeCombineXYZ', 'Width dimension', (-200, -350))
    combine.inputs['X'].default_value = 0.62
    combine.inputs['Z'].default_value = 0.16
    group.links.new(_socket_by_identifier(group_input.outputs, width.identifier), combine.inputs['Y'])
    group.links.new(combine.outputs['Vector'], bar.inputs['Size'])
    _link(group, bar, 'Mesh', bar_material, 'Geometry')
    _link(group, line, 'Mesh', instances, 'Points')
    _link(group, bar_material, 'Geometry', instances, 'Instance')
    _link(group, instances, 'Instances', realize, 'Geometry')
    _link(group, realize, 'Geometry', group_output, 'Geometry')
    return group


def _set_group_value(modifier, group, name, value):
    identifier = group.get(name_key(name), '')
    socket = _interface_socket(group, identifier)
    expected_type = ('NodeSocketFloat' if name in ('Width', 'Step offset')
                     else 'NodeSocketInt')
    if socket.in_out != 'INPUT' or socket.socket_type != expected_type:
        raise ValueError(f"Node interface contract type drift for {name}")
    input_value = _modifier_input(modifier, socket.identifier, expected_type, name)
    input_value.value = value


def name_key(name):
    if name in _INTERFACE_IDS:
        return _INTERFACE_IDS[name]
    if name in _REPEAT_IDS:
        return _REPEAT_IDS[name]
    raise ValueError(f"Unknown typed interface field: {name}")


def _interface_socket(group, identifier):
    if not identifier:
        raise ValueError('Node interface migration error: stored socket identifier is missing')
    items = [item for item in group.interface.items_tree
             if getattr(item, 'item_type', None) == 'SOCKET' and item.identifier == identifier]
    if len(items) != 1:
        raise ValueError(f'Node interface migration error: socket identifier {identifier!r} is missing or duplicated')
    return items[0]


def _typed_socket(node, identifier, expected_type, label, direction='inputs'):
    sockets = getattr(node, direction)
    matches = [socket for socket in sockets if socket.identifier == identifier]
    if len(matches) != 1:
        raise ValueError(f'Node interface migration error: {label} socket identifier is missing')
    socket = matches[0]
    if socket.bl_idname != expected_type:
        raise ValueError(f'Node interface migration error: {label} socket changed type to {socket.bl_idname}')
    return socket


def _modifier_input(modifier, identifier, expected_socket_type, label):
    if not identifier:
        raise ValueError(f'Node modifier migration error: {label} identifier is missing')
    input_value = getattr(modifier.properties.inputs, identifier, None)
    if input_value is None:
        raise ValueError(f'Node modifier migration error: {label} input identifier is missing')
    expected_value_type = 'FLOAT' if expected_socket_type == 'NodeSocketFloat' else 'INT'
    value_property = input_value.bl_rna.properties.get('value')
    if value_property is None or value_property.type != expected_value_type or input_value.type != 'VALUE':
        raise ValueError(f'Node modifier migration error: {label} input has the wrong RNA type')
    return input_value


def _validate_interface(group):
    expected = {'Width': 'NodeSocketFloat', 'Count': 'NodeSocketInt'}
    for name, socket_type in expected.items():
        socket = _interface_socket(group, group.get(name_key(name), ''))
        if socket.in_out != 'INPUT' or socket.socket_type != socket_type:
            raise ValueError(f'Node interface migration error: {name} expected {socket_type}')
        if socket.name != name:
            raise ValueError(f'Node interface migration error: identifier for {name} was renamed')
        expected_default, expected_min, expected_max = (1.0, 0.2, 3.0) if name == 'Width' else (3, 1, 12)
        def close(actual, expected):
            if isinstance(expected, int):
                return actual == expected
            return math.isclose(float(actual), expected, rel_tol=0.0, abs_tol=1e-6)
        if (not close(socket.default_value, expected_default) or not close(socket.min_value, expected_min)
                or not close(socket.max_value, expected_max)):
            raise ValueError(f'Node interface migration error: {name} defaults or bounds changed')
    geometry = _interface_socket(group, group.get(_GEOMETRY_ID, ''))
    if geometry.in_out != 'OUTPUT' or geometry.socket_type != 'NodeSocketGeometry':
        raise ValueError('Node interface migration error: geometry output identifier or type changed')
    return {name: _interface_socket(group, group.get(name_key(name), '')) for name in expected}


def _number(params, name, minimum, maximum, integer=False):
    value = params[name]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{name} must be a finite number')
    if integer and not isinstance(value, int):
        raise ValueError(f'{name} must be an integer')
    if not minimum <= value <= maximum:
        raise ValueError(f'{name} must be between {minimum} and {maximum}')
    return value


def _validated(lab, params):
    expected = _REPEAT_DEFAULTS if lab == 'BL-033' else _INTERFACE_DEFAULTS
    if not isinstance(params, dict) or set(params) != set(expected):
        raise ValueError(f'{lab} controls must have exactly these names: {sorted(expected)}')
    if lab == 'BL-033':
        return {'Iterations': _number(params, 'Iterations', 0, 12, integer=True),
                'Step offset': float(_number(params, 'Step offset', 0.05, 0.5))}
    return {'Width': float(_number(params, 'Width', 0.2, 3.0)),
            'Count': _number(params, 'Count', 1, 12, integer=True)}


def _evaluated_mesh(obj):
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    if mesh is None:
        raise AssertionError('Node group produced no evaluated mesh')
    return evaluated, mesh


def _measure(obj):
    evaluated, mesh = _evaluated_mesh(obj)
    try:
        points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
        _check(bool(points), 'Node group evaluated to empty geometry')
        bounds = [[min(point[axis] for point in points), max(point[axis] for point in points)]
                  for axis in range(3)]
        return {'vertices': len(mesh.vertices), 'faces': len(mesh.polygons), 'bounds': bounds}
    finally:
        evaluated.to_mesh_clear()


def _attach(obj, group, name):
    modifier = obj.modifiers.new(name, 'NODES')
    modifier.node_group = group
    return modifier


def build(scene, lab, base_subject):
    if lab not in _LABS:
        raise ValueError(f'No node-contract builder for {lab}')
    if base_subject is None or scene.objects.get(base_subject.name) != base_subject:
        raise ValueError('Expected the disposable base subject inside the owned lab scene')
    if len(base_subject.users_scene) != 1:
        raise ValueError('Refusing to replace a base subject shared outside this scene')
    guarded = _protected_scene_state(scene, base_subject)
    material = _material(lab + ' / copper ceramic')
    if lab == 'BL-033':
        obj = _cube(scene, 'Repeat machine / editable subject', (0.42, 0.42, 0.2), material)
        group = _repeat_graph(material)
        _attach(obj, group, 'Repeat machine / paired state')
    else:
        obj = _cube(scene, 'Typed interface / editable rail', (0.62, 1.0, 0.16), material)
        group = _interface_graph(material)
        modifier = _attach(obj, group, 'Typed interface / rail generator')
        for name, value in _INTERFACE_DEFAULTS.items():
            _set_group_value(modifier, group, name, value)
    obj.location = (0, 0, 0.38)
    _tag(obj, 'primary')
    obj['blender_lab_subject'] = True
    scene['node_contract_protected_scene'] = json.dumps(guarded, sort_keys=True, separators=(',', ':'))
    bpy.data.objects.remove(base_subject, do_unlink=True)
    return obj


def _apply_repeat(obj, params):
    group = obj.modifiers[-1].node_group
    repeat_in = next((node for node in group.nodes if node.bl_idname == 'GeometryNodeRepeatInput'), None)
    repeat_out = next((node for node in group.nodes if node.bl_idname == 'GeometryNodeRepeatOutput'), None)
    if repeat_in is None or repeat_out is None or repeat_in.paired_output != repeat_out:
        raise ValueError('Repeat zone state is unpaired; repair the input/output pair before evaluation')
    states = [item for item in repeat_out.repeat_items if item.socket_type == 'GEOMETRY']
    if len(states) != 1 or states[0].name != 'Geometry':
        raise ValueError('Repeat zone state socket is missing or has drifted')
    iteration = next((socket for socket in repeat_in.outputs if socket.name == 'Iteration'), None)
    iteration_input = next((socket for socket in repeat_in.inputs if socket.name == 'Iterations'), None)
    state_in = next((socket for socket in repeat_in.inputs if socket.name == 'Geometry'), None)
    state_out = next((socket for socket in repeat_in.outputs if socket.name == 'Geometry'), None)
    paired_state_in = next((socket for socket in repeat_out.inputs if socket.name == 'Geometry'), None)
    paired_state_out = next((socket for socket in repeat_out.outputs if socket.name == 'Geometry'), None)
    if not all((iteration, iteration_input, state_in, state_out, paired_state_in, paired_state_out)):
        raise ValueError('Repeat zone state socket is incomplete or has drifted')
    group_input = next(node for node in group.nodes if node.bl_idname == 'NodeGroupInput')
    iter_identifier = group.get(_REPEAT_IDS['Iterations'], '')
    step_identifier = group.get(_REPEAT_IDS['Step offset'], '')
    iter_socket = _interface_socket(group, iter_identifier)
    step_socket = _interface_socket(group, step_identifier)
    if iter_socket.in_out != 'INPUT' or iter_socket.socket_type != 'NodeSocketInt':
        raise ValueError('Repeat interface migration error: Iterations identifier/type changed')
    if step_socket.in_out != 'INPUT' or step_socket.socket_type != 'NodeSocketFloat':
        raise ValueError('Repeat interface migration error: Step offset identifier/type changed')
    _typed_socket(group_input, iter_identifier, 'NodeSocketInt', 'Iterations', 'outputs')
    _typed_socket(group_input, step_identifier, 'NodeSocketFloat', 'Step offset', 'outputs')
    if iteration_input.bl_idname != 'NodeSocketInt' or state_in.bl_idname != 'NodeSocketGeometry' or paired_state_in.bl_idname != 'NodeSocketGeometry':
        raise ValueError('Repeat zone input socket type drift detected')
    if not state_in.is_linked or not state_out.is_linked or not paired_state_in.is_linked:
        raise ValueError('Repeat zone state socket is unpaired or disconnected')
    modifier = next((item for item in obj.modifiers if item.type == 'NODES'), None)
    if modifier is None:
        raise ValueError('Repeat machine modifier is missing')
    _set_group_value(modifier, group, 'Iterations', params['Iterations'])
    _set_group_value(modifier, group, 'Step offset', params['Step offset'])


def _apply_interface(obj, params):
    modifier = next((item for item in obj.modifiers if item.type == 'NODES'), None)
    if modifier is None or modifier.node_group is None:
        raise ValueError('Typed interface modifier is missing')
    group = modifier.node_group
    sockets = _validate_interface(group)
    # Resolve every contract and node socket before changing a modifier value.
    group_input = next((node for node in group.nodes if node.bl_idname == 'NodeGroupInput'), None)
    if group_input is None:
        raise ValueError('Typed interface group input node is missing')
    for name, contract in sockets.items():
        group_socket = _socket_by_identifier(group_input.outputs, contract.identifier)
        if group_socket.bl_idname != contract.socket_type:
            raise ValueError(f'Node interface migration error: {name} group-input socket drifted')
    _set_group_value(modifier, group, 'Width', params['Width'])
    _set_group_value(modifier, group, 'Count', params['Count'])


def apply_controls(scene, lab, params):
    if lab not in _LABS:
        raise ValueError(f'No node-contract controls for {lab}')
    values = _validated(lab, params)
    obj = _role(scene, 'primary')
    if lab == 'BL-033':
        _apply_repeat(obj, values)
    else:
        _apply_interface(obj, values)
    obj.update_tag()
    bpy.context.view_layer.update()


def _verify_repeat(scene, params, obj):
    group = obj.modifiers[-1].node_group
    modifier = obj.modifiers[-1]
    repeat_in = next((node for node in group.nodes if node.bl_idname == 'GeometryNodeRepeatInput'), None)
    repeat_out = next((node for node in group.nodes if node.bl_idname == 'GeometryNodeRepeatOutput'), None)
    if repeat_in is None or repeat_out is None or repeat_in.paired_output != repeat_out:
        raise ValueError('Repeat zone state is unpaired; evaluation is blocked')
    for name, value in params.items():
        identifier = group.get(_REPEAT_IDS[name], '')
        socket = _interface_socket(group, identifier)
        expected_type = 'NodeSocketInt' if name == 'Iterations' else 'NodeSocketFloat'
        if socket.in_out != 'INPUT' or socket.socket_type != expected_type:
            raise ValueError(f'Repeat interface migration error: {name} identifier/type changed')
        input_value = _modifier_input(modifier, identifier, expected_type, name)
        if expected_type == 'NodeSocketInt':
            persisted = input_value.value == value
        else:
            persisted = math.isclose(float(input_value.value), value, rel_tol=0.0, abs_tol=1e-6)
        _check(persisted, f'Repeat modifier input {name} did not persist its value')
    for node in (repeat_in, repeat_out):
        geometry = [socket for socket in (*node.inputs, *node.outputs) if socket.name == 'Geometry']
        if not geometry or any(socket.bl_idname != 'NodeSocketGeometry' for socket in geometry):
            raise ValueError('Repeat zone state socket has changed type')
    measure = _measure(obj)
    expected_modules = params['Iterations'] + 1
    _check(measure['vertices'] == expected_modules * 8 and measure['faces'] == expected_modules * 6,
           'Repeat zone produced an unexpected module count')
    z_extent = measure['bounds'][2][1] - measure['bounds'][2][0]
    expected_z = 0.2 + params['Iterations'] * params['Step offset']
    _check(abs(z_extent - expected_z) < 1e-5, 'Repeat zone vertical extent does not match its iteration state')
    if params['Iterations'] == 0:
        _check(abs(z_extent - 0.2) < 1e-5, 'Zero iterations changed the initial module')
    _ensure_protected_unchanged(scene, json.loads(scene['node_contract_protected_scene']))
    return {'module_count': expected_modules, 'evaluated_vertices': measure['vertices'],
            'evaluated_faces': measure['faces'], 'bounds': measure['bounds'],
            'zero_iteration_identity': params['Iterations'] != 0 or abs(z_extent - 0.2) < 1e-5,
            'paired_state_sockets': True}


def _shader_contract(material):
    shader = material.node_tree.nodes.get('Principled BSDF')
    if shader is None:
        raise ValueError('Typed shader contract migration error: Principled shader is missing')
    roughness = next((socket for socket in shader.inputs
                      if socket.identifier == material.get(_SHADER_IDS['Roughness'], '')), None)
    color = next((socket for socket in shader.inputs
                  if socket.identifier == material.get(_SHADER_IDS['Base Color'], '')), None)
    if roughness is None or roughness.bl_idname != 'NodeSocketFloatFactor':
        raise ValueError('Typed shader contract migration error: Roughness identifier/type changed')
    if color is None or color.bl_idname != 'NodeSocketColor':
        raise ValueError('Typed shader contract migration error: Base Color identifier/type changed')
    return roughness, color


def _verify_interface(scene, params, obj):
    modifier = next((item for item in obj.modifiers if item.type == 'NODES'), None)
    if modifier is None or modifier.node_group is None:
        raise ValueError('Typed interface modifier is missing')
    group = modifier.node_group
    sockets = _validate_interface(group)
    expected_values = {'Width': params['Width'], 'Count': params['Count']}
    for name, expected in expected_values.items():
        socket = sockets[name]
        expected_type = 'NodeSocketFloat' if name == 'Width' else 'NodeSocketInt'
        actual = _modifier_input(modifier, socket.identifier, expected_type, name).value
        _check(abs(float(actual) - float(expected)) < 1e-6,
               f'Modifier input {name} did not persist its typed value')
    material = next((mat for mat in obj.data.materials if mat), None)
    if material is None:
        material = next((node.inputs['Material'].default_value for node in group.nodes
                         if node.bl_idname == 'GeometryNodeSetMaterial'), None)
    _check(material is not None, 'Typed shader material is missing')
    roughness, color = _shader_contract(material)
    _check(abs(float(roughness.default_value) - 0.72) < 1e-6, 'Typed shader Roughness value drifted')
    _check(tuple(round(float(value), 5) for value in color.default_value) == (0.84, 0.34, 0.12, 1.0),
           'Typed shader Base Color value drifted')

    group_input = next(node for node in group.nodes if node.bl_idname == 'NodeGroupInput')
    line = next(node for node in group.nodes if node.bl_idname == 'GeometryNodeMeshLine')
    bar = next(node for node in group.nodes if node.bl_idname == 'GeometryNodeMeshCube')
    count_node = _typed_socket(group_input, sockets['Count'].identifier, 'NodeSocketInt', 'Count', 'outputs')
    width_node = _typed_socket(group_input, sockets['Width'].identifier, 'NodeSocketFloat', 'Width', 'outputs')
    _check(count_node.bl_idname == 'NodeSocketInt' and width_node.bl_idname == 'NodeSocketFloat',
           'Typed group input socket type drifted')
    _check(any(link.from_socket == count_node and link.to_socket == line.inputs['Count'] for link in group.links),
           'Stable Count socket is disconnected from the rail generator')
    width_link = next((link for link in group.links if link.from_socket == width_node), None)
    _check(width_link is not None and width_link.to_socket.node.bl_idname == 'ShaderNodeCombineXYZ',
           'Stable Width socket is disconnected from the rail generator')
    measure = _measure(obj)
    expected_vertices = params['Count'] * 8
    _check(measure['vertices'] == expected_vertices and measure['faces'] == params['Count'] * 6,
           'Evaluated rail count differs from the typed Count input')
    width = measure['bounds'][1][1] - measure['bounds'][1][0]
    _check(abs(width - params['Width']) < 1e-5, 'Evaluated rail width differs from the typed Width input')
    _ensure_protected_unchanged(scene, json.loads(scene['node_contract_protected_scene']))
    return {'rail_count': params['Count'], 'measured_width': width,
            'evaluated_vertices': measure['vertices'], 'evaluated_faces': measure['faces'],
            'bounds': measure['bounds'], 'interface_identifiers': {
                'Width': sockets['Width'].identifier, 'Count': sockets['Count'].identifier,
                'Geometry': group.get(_GEOMETRY_ID)},
            'modifier_inputs_persisted': True, 'shader_socket_types': {
                'Roughness': roughness.bl_idname, 'Base Color': color.bl_idname}}


def verify(scene, lab, params, output):
    if lab not in _LABS:
        raise ValueError(f'No node-contract verifier for {lab}')
    values = _validated(lab, params)
    obj = _role(scene, 'primary')
    if lab == 'BL-033':
        return _verify_repeat(scene, values, obj)
    return _verify_interface(scene, values, obj)
