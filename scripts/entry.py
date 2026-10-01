"""Run with Blender's --python; failures set a nonzero process exit code."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import bpy
import blender_lab
from blender_lab import catalog, controls, labs, verification
from blender_lab.operations import Request, perform


# These select measured outcomes, excluding echoed controls and artifact paths.
OUTCOMES = {
    'BL-016': {'Bake size': ('image_dimensions',), 'Margin': ('baked_pixel_sha256',)},
    'BL-033': {'Iterations': ('evaluated_vertices', 'bounds'), 'Step offset': ('bounds',)},
    'BL-035': {'Width': ('measured_width',), 'Count': ('evaluated_vertices',)},
    'BL-036': {'Schema version': ('schema_version', 'migrated_reference_rgb'), 'Tint strength': ('migrated_reference_rgb',)},
    'BL-037': {'Control travel': ('evaluated_translation',), 'Constraint influence': ('evaluated_translation',)},
    'BL-038': {'Target reach': ('tip', 'tip_error'), 'Pole angle': ('elbow',)},
    'BL-039': {'Pose blend': ('evaluated_rotations_radians',), 'Bone scope': ('evaluated_rotations_radians',)},
    'BL-040': {'Sample step': ('sample_frames',), 'Bake range': ('sample_frames',)},
    'BL-058': {'World strength': ('rendered_preview_sha256',), 'Rotation': ('rendered_preview_sha256',)},
    'BL-059': {'Pattern scale': ('preview.preview_sha256',), 'Roughness': ('preview.preview_sha256',)},
    'BL-010': {'Bend angle': ('weighted.max_displacement', 'weighted.tip_vertex'),
               'Weight transition': ('weighted.middle_vertex',)},
    'BL-011': {'Blend frames': ('samples', 'strip_bounds'), 'Clip offset': ('samples', 'strip_bounds')},
    'BL-012': {'Field of view': ('gameplay.coverage',), 'Subject distance': ('gameplay.coverage',)},
    'BL-013': {'Density': ('evaluated_instance_count', 'evaluated_vertices'), 'Seed': ('position_signature',)},
    'BL-014': {'Domain': ('attribute_count', 'sample_range'), 'Threshold': ('selected_count',)},
    'BL-015': {'Target density': ('measured_densities',), 'Margin pixels': ('margin_pixels',)},
    'BL-019': {'Treatment amount': ('clean_requested_max_error',), 'Output width': ('output_height',)},
    'BL-020': {'Key energy': ('key_energy',), 'Renderer': ('renderer',)},
    'BL-021': {'Asset role': ('asset_id',), 'Preview size': ('preview_size',)},
    'BL-022': {'Frames': ('atlas_size', 'distinct_pixel_frames'), 'Cell size': ('atlas_size', 'alpha_bounds')},
    'BL-025': {'Cut position': ('edited_geometry_signature',), 'Dissolve angle': ('vertices', 'edges', 'faces')},
    'BL-026': {'Opening width': ('evaluated_volume',), 'Operation': ('evaluated_volume',)},
    'BL-027': {'Surface offset': ('distance_range',), 'Cage density': ('cage_vertices', 'cage_faces')},
    'BL-028': {'Attribute domain': ('element_count',), 'Data type': ('sample',)},
    'BL-029': {'Expression weight': ('brow_vertex',), 'Secondary weight': ('mouth_vertex',)},
    'BL-030': {'Path resolution': ('evaluated_vertices',), 'Profile radius': ('cross_section_radius', 'bounds')},
    'BL-031': {'Extrusion': ('evaluated_thickness',), 'Text width': ('text_width',)},
}


def _outcome(lab, name, metrics):
    verification.check(lab in OUTCOMES and name in OUTCOMES[lab],
                       f'{lab} / {name} has no declared measured outcome selector')
    result = {}
    for path in OUTCOMES[lab][name]:
        value = metrics
        for key in path.split('.'):
            verification.check(isinstance(value, dict) and key in value,
                               f'{lab} / {name} is missing measured metric {path}')
            value = value[key]
        if path == 'samples':
            value = [{'hinge_radians': sample['hinge_radians'], 'world_tip': sample['world_tip']}
                     for sample in value]
        result[path] = value
    return result


def _candidates(item):
    kind, default = item['type'], item['default']
    if kind == 'enum':
        return list(item['options'])
    if kind == 'boolean':
        return [not default]
    if kind in ('integer', 'number'):
        low, high = item['minimum'], item['maximum']
        values = [low, high, (low + high) / 2]
        if kind == 'integer':
            values = [int(round(value)) for value in values]
        return list(dict.fromkeys(values))
    raise AssertionError(f'No bounded alternate scenario for control type {kind}')


def _apply(scene, lab, supplied, value=1):
    return perform(Request('apply', lab, value, scene_id=scene['blender_lab_instance_id'],
                           controls_json=json.dumps(supplied, allow_nan=False)), scene)


def _admission_state(scene):
    return {'controls': scene.get('blender_lab_controls'), 'value': scene['blender_lab_value'],
            'instance': scene['blender_lab_instance_id'], 'assets': labs.snapshot(),
            'scenes': tuple(bpy.data.scenes.keys()), 'active': bpy.context.scene.as_pointer()}


def _case_metrics(scene, lab, output):
    metrics = verification.verify(scene, output)
    if lab == 'BL-025':
        mesh = labs.subject(scene).data
        geometry = {'vertices': [list(vertex.co) for vertex in mesh.vertices],
                    'faces': [list(polygon.vertices) for polygon in mesh.polygons]}
        metrics['edited_geometry_signature'] = hashlib.sha256(json.dumps(geometry, sort_keys=True).encode()).hexdigest()
    return metrics


def _feature_regressions(scene, lab, output, defaults):
    if lab == 'BL-016':
        from blender_lab import surfaces
        image = surfaces._owned_image(scene, 'bake_image')
        pixels = surfaces._pixels(image)
        owner = bpy.data.materials.new('User-owned shared bake image sentinel')
        owner.use_nodes = True
        owner.node_tree.nodes.new('ShaderNodeTexImage').image = image
        old_name = image.name
        try:
            _apply(scene, lab, defaults)
            verification.check(surfaces._owned_image(scene, 'bake_image') != image
                               and image.users > 0 and surfaces._pixels(image) == pixels,
                               'Bake replacement changed or duplicated a shared image')
            _apply(scene, lab, defaults)
            verification.verify(scene, output)
        finally:
            bpy.data.materials.remove(owner)
            labs.remove_unused({'images': [old_name]})
        return {'shared_bake_image_replacement': 'passed'}
    if lab == 'BL-035':
        obj = labs.subject(scene)
        graph = obj.modifiers[-1].node_group
        baseline = verification.verify(scene, output)
        count = next(socket for socket in graph.interface.items_tree
                     if getattr(socket, 'identifier', None) == graph['blender_lab_count_identifier'])
        graph.interface.move(count, 0)
        graph.interface_update(bpy.context)
        _apply(scene, lab, defaults)
        after = verification.verify(scene, output)
        verification.check(all(after[key] == baseline[key] for key in ('evaluated_vertices', 'measured_width', 'bounds')),
                           'Socket display reordering changed the identifier-based recipe')
        return {'socket_display_reorder': 'passed'}
    if lab == 'BL-036':
        from blender_lab import surfaces
        material = surfaces._role(scene, 'migration_subject').data.materials[0]
        graph = material.node_tree
        link = next(link for link in graph.links if link.to_socket == graph.nodes['Principled BSDF'].inputs['Base Color'])
        source, target = link.from_socket, link.to_socket
        graph.links.remove(link)
        before = _admission_state(scene)
        try:
            try:
                _apply(scene, lab, defaults)
            except (AssertionError, ValueError):
                pass
            else:
                raise AssertionError('Migration admitted an unsupported current graph')
            verification.check(_admission_state(scene) == before,
                               'Rejected migration leaked staging data or changed applied controls')
        finally:
            graph.links.new(source, target)
        verification.verify(scene, output)
        return {'unsupported_migration_without_staging_leak': 'passed'}
    return {}


def _typed_test(scene, lab, output, request, receipt, sentinel, original_scene):
    requested = json.loads(scene['blender_lab_controls'])
    defaults = controls.validate(lab)
    schema = catalog.BY_ID[lab]['controls']
    _apply(scene, lab, defaults)
    baseline = _case_metrics(scene, lab, output)
    feature_regressions = _feature_regressions(scene, lab, output, defaults)
    before = _admission_state(scene)
    verification.check(perform(request) == receipt and _admission_state(scene) == before,
                       'Repeated typed request produced duplicate scene state')
    invalid = [('unknown-name', {'Undeclared control': 1}), ('null-root', None), ('array-root', []), ('boolean-root', True)]
    for item in schema:
        name, kind = item['name'], item['type']
        if kind in ('integer', 'number'):
            invalid.extend([(name + '/boolean', {name: True}), (name + '/nonfinite', {name: float('nan')}),
                            (name + '/below-minimum', {name: item['minimum'] - 1}),
                            (name + '/above-maximum', {name: item['maximum'] + 1})])
            if kind == 'integer':
                invalid.append((name + '/fraction', {name: item['default'] + .5}))
        elif kind == 'enum':
            invalid.extend([(name + '/unknown-choice', {name: '__unavailable__'}), (name + '/boolean', {name: True})])
        elif kind == 'boolean':
            invalid.extend([(name + '/integer', {name: 1}), (name + '/string', {name: 'true'})])
    rejection_records = []
    for label, supplied in invalid:
        rejected = Request('apply', lab, scene_id=scene['blender_lab_instance_id'], controls_json=json.dumps(supplied))
        try:
            perform(rejected, scene)
        except ValueError as error:
            rejection_records.append({'case': label, 'error': str(error)})
        else:
            raise AssertionError(f'{lab} admitted invalid typed control: {label}')
        verification.check(_admission_state(scene) == before, f'{lab} rejected {label} after mutating scene/data')
    for rejected in (Request('open', lab, 1.5, request_id=request.request_id),
                     Request('apply', lab, scene_id='different-instance'), Request('open', 'BL-096')):
        try:
            perform(rejected, scene)
        except ValueError:
            pass
        else:
            raise AssertionError('Conflicting retry, wrong scope or planned adapter was admitted')
        verification.check(_admission_state(scene) == before, 'Rejected request changed owned scene state')
    after_rejection = _case_metrics(scene, lab, output)
    for item in schema:
        verification.check(_outcome(lab, item['name'], baseline) == _outcome(lab, item['name'], after_rejection),
                           'Rejected typed control altered the measured mechanism')
    cases, alternates = [], {}
    for item in schema:
        name = item['name']
        observed_change = False
        for candidate in _candidates(item):
            _apply(scene, lab, defaults)
            _apply(scene, lab, {name: candidate})
            expected = dict(defaults, **{name: candidate})
            verification.check(json.loads(scene['blender_lab_controls']) == expected,
                               f'{lab} partial {name} Apply lost another control')
            measured = _case_metrics(scene, lab, output)
            outcome = _outcome(lab, name, measured)
            changed = outcome != _outcome(lab, name, baseline)
            cases.append({'control': name, 'value': candidate, 'measured_outcome': outcome, 'changed': changed})
            if candidate != item['default'] and changed:
                observed_change = True
                alternates.setdefault(name, candidate)
        verification.check(observed_change, f'{lab} / {name} has no measured effect for its bounded alternatives')
    # Independent cases above keep other inputs at defaults. This checks sequential merging.
    _apply(scene, lab, defaults)
    combined = dict(defaults)
    for item in schema:
        name = item['name']
        _apply(scene, lab, {name: alternates[name]})
        combined[name] = alternates[name]
        verification.check(json.loads(scene['blender_lab_controls']) == combined,
                           f'{lab} partial-control merge reverted a prior input')
    verification.verify(scene, output)
    shared_data = labs.subject(scene).data
    shared = bpy.data.objects.new('Shared owned-data acceptance sentinel', shared_data)
    original_scene.collection.objects.link(shared)
    old_assets = json.loads(scene['blender_lab_assets'])
    old_instance = scene['blender_lab_instance_id']
    perform(Request('reset', lab, scene_id=old_instance), scene)
    scene = bpy.context.scene
    verification.check(scene['blender_lab_instance_id'] != old_instance and sentinel.name in original_scene.objects,
                       'Reset reused its instance or destroyed user scene content')
    verification.check(shared.name in original_scene.objects and shared.data == shared_data and shared_data.users > 0,
                       'Reset deleted owned data shared by a user scene')
    verification.check(json.loads(scene['blender_lab_controls']) == defaults, 'Typed reset did not restore card defaults')
    verification.verify(scene, output)
    bpy.data.objects.remove(shared, do_unlink=True)
    labs.remove_unused(old_assets)
    _apply(scene, lab, requested)
    metrics = verification.verify(scene, output)
    return scene, metrics, {'default_metrics': baseline, 'feature_regressions': feature_regressions, 'control_cases': cases,
                            'rejected_inputs': rejection_records, 'partial_merge': 'passed',
                            'owned_and_shared_sentinels': 'passed', 'reset_defaults': 'passed',
                            'fresh_process_reopen': 'requires-wave-or-reopen-check'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', choices=['build', 'test', 'render', 'export', 'scenario'], default='build')
    parser.add_argument('--lab', choices=list(labs.LABS))
    parser.add_argument('--output', type=Path, default=ROOT / 'build')
    parser.add_argument('--value', type=float, default=1)
    parser.add_argument('--controls-file', type=Path, help='JSON object keyed by exact displayed control names; requires --lab')
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    if args.controls_file and not args.lab:
        parser.error('--controls-file requires one selected --lab')
    supplied = None
    if args.controls_file:
        supplied = json.loads(args.controls_file.read_text(encoding='utf-8-sig'))
        if not isinstance(supplied, dict):
            parser.error('--controls-file must contain a JSON object keyed by exact displayed control names')
        controls.validate(args.lab, supplied)
    supplied_json = json.dumps(supplied, sort_keys=True, allow_nan=False) if supplied is not None else ''
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    blender_lab.register()
    if args.action == 'export' and args.lab and args.lab != 'BL-006':
        parser.error('Verified glTF export is implemented only for BL-006')
    selected = [args.lab] if args.lab else (['BL-006'] if args.action == 'export' else list(labs.LABS))
    source_hash = hashlib.sha256(b''.join(p.read_bytes() for p in sorted((ROOT / 'blender_lab').glob('*.py')))).hexdigest()
    report = {'schemaVersion': 1, 'blender': bpy.app.version_string, 'build_hash': bpy.app.build_hash.decode(),
              'source_sha256': source_hash, 'catalog_sha256': hashlib.sha256((ROOT / 'catalog.json').read_bytes()).hexdigest(),
              'timestamp': datetime.now(timezone.utc).isoformat(), 'action': args.action, 'labs': []}
    sentinel = bpy.data.objects.new("Acceptance sentinel", None)
    bpy.context.scene.collection.objects.link(sentinel)
    original_scene = bpy.context.scene
    for lab in selected:
        request = Request('open', lab, args.value, controls_json=supplied_json)
        receipt = perform(request)
        scene = bpy.context.scene
        lab_output = output if len(selected) == 1 else output / lab
        lab_output.mkdir(parents=True, exist_ok=True)
        metrics = verification.verify(scene, lab_output)
        test_cases = None
        if args.action == 'test' and lab in labs.ADAPTERS:
            scene, metrics, test_cases = _typed_test(scene, lab, lab_output, request, receipt, sentinel, original_scene)
        elif args.action == 'test':
            scene_count = len(bpy.data.scenes)
            verification.check(perform(request) == receipt and len(bpy.data.scenes) == scene_count,
                               'Repeated request produced duplicate scene state')
            for invalid in (True, float('nan'), 2.1):
                try:
                    perform(Request('apply', lab, invalid, scene_id=scene['blender_lab_instance_id']), scene)
                except ValueError:
                    pass
                else:
                    raise AssertionError('Invalid input was admitted by the operation boundary')
            verification.check(scene['blender_lab_value'] == args.value, 'Rejected request mutated scene input')
            for rejected in (Request('open', lab, 1.5, request_id=request.request_id),
                             Request('apply', lab, 1.5, scene_id='different-instance'),
                             Request('open', 'BL-096')):
                try:
                    perform(rejected, scene)
                except ValueError:
                    pass
                else:
                    raise AssertionError('Conflicting retry, wrong scope or planned adapter was admitted')
            verification.check(scene['blender_lab_value'] == args.value and len(bpy.data.scenes) == scene_count,
                               'Rejected request changed owned scene state')
            for endpoint in (.1, 2.0):
                perform(Request('apply', lab, endpoint, scene_id=scene['blender_lab_instance_id']), scene)
                verification.verify(scene, lab_output)
            # Compare two controls against evaluated output, then exercise the UI operators.
            labs.apply_value(scene, .5)
            alternate = verification.verify(scene, lab_output)
            labs.apply_value(scene, 1.5)
            changed = verification.verify(scene, lab_output)
            verification.check(alternate != changed, f'{lab} value has no observable effect')
            context_scene = labs.reset(scene)
            verification.check(sentinel.name in original_scene.objects, 'Reset destroyed user scene content')
            context_scene.blender_lab_value_control = args.value
            bpy.ops.blender_lab.apply()
            metrics = verification.verify(context_scene, lab_output)
            scene = context_scene
        scene.frame_set(1)
        if args.action == 'render' or args.render:
            if lab == 'BL-004':
                scene.frame_set(30)
            scene.render.filepath = str(lab_output / f'{lab}.png')
            bpy.ops.render.render(write_still=True)
        path = lab_output / f'{lab}.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        verification.check(sentinel.name in original_scene.objects, 'Operation destroyed user scene sentinel')
        report['labs'].append({'id': lab, 'status': 'passed', 'value': scene['blender_lab_value'], 'metrics': metrics,
                              'requested_value': args.value,
                              'controls': json.loads(scene.get('blender_lab_controls', '{}')), 'test_cases': test_cases,
                              'operation_request_id': json.loads(scene['blender_lab_receipt'])['request_id'],
                              'open_request_id': receipt.request_id})
    (output / 'evidence.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
