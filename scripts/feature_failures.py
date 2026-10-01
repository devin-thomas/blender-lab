"""Prove each implemented feature verifier detects a bounded mechanism failure.

Run inside Blender with: blender --background --python scripts/feature_failures.py -- --labs BL-013,BL-014
Each case gets a fresh owned scene, a disposable mutation, a scoped reset, and
an unrelated-scene sentinel check. This is negative evidence, not a render suite.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import bmesh
import bpy
from blender_lab import labs, verification


ADAPTER_LABS = (
    'BL-010', 'BL-011', 'BL-012', 'BL-013', 'BL-014', 'BL-015',
    'BL-019', 'BL-020', 'BL-021', 'BL-022',
    'BL-025', 'BL-026', 'BL-027', 'BL-028',
    'BL-029', 'BL-030', 'BL-031',
)


def _role(scene, key, role):
    matches = [obj for obj in scene.objects if obj.get(key) == role]
    if len(matches) != 1:
        raise AssertionError(f'Expected one {key}={role!r}; found {len(matches)}')
    return matches[0]


def _mutate(lab, scene):
    if lab == 'BL-010':
        from blender_lab import motion
        obj = motion._role(scene, 'weighted_limb')
        obj.vertex_groups.remove(obj.vertex_groups['Upper'])
        return 'removed weighted_limb Upper vertex group'
    if lab == 'BL-011':
        from blender_lab import motion
        obj = motion._role(scene, 'signal')
        lift = next(strip for track in obj.animation_data.nla_tracks for strip in track.strips
                    if strip.action and strip.action.get('motion_action_role') == 'lift')
        lift.action_slot = None
        return 'cleared lift NLA action slot'
    if lab == 'BL-012':
        scene.camera = None
        return 'cleared scene gameplay camera reference'
    if lab == 'BL-013':
        obj = _role(scene, 'geometry_role', 'scatter_surface')
        graph = obj.modifiers[-1].node_group
        instance = next(node for node in graph.nodes if node.bl_idname == 'GeometryNodeInstanceOnPoints')
        link = next(link for link in graph.links if link.to_node == instance and link.to_socket == instance.inputs['Points'])
        graph.links.remove(link)
        return 'disconnected seeded scatter points from Instance on Points'
    if lab == 'BL-014':
        mesh = _role(scene, 'geometry_role', 'field_mesh').data
        mesh.attributes.remove(mesh.attributes['ProbeValue'])
        return 'removed required point-domain ProbeValue attribute'
    if lab == 'BL-015':
        panel = _role(scene, 'geometry_role', 'uv_panel_a')
        for loop in panel.data.uv_layers.active.data:
            loop.uv = (0.25, 0.25)
        return 'collapsed reference UV island to zero area'
    if lab == 'BL-019':
        graph = scene.compositing_node_group
        treatment, scale = graph.nodes['Treatment'], graph.nodes['Output size']
        link = next(link for link in graph.links
                    if link.from_node == treatment and link.to_node == scale
                    and link.to_socket == scale.inputs['Image'])
        graph.links.remove(link)
        return 'disconnected compositor treatment output path'
    if lab == 'BL-020':
        scene.camera = None
        return 'cleared observatory camera reference'
    if lab == 'BL-021':
        from blender_lab import production
        target = production._asset_targets(scene)['module']
        target.asset_clear()
        return 'cleared selected module asset metadata'
    if lab == 'BL-022':
        from blender_lab import production
        subject = production._role(scene, 'sprite_subject')
        subject.rotation_euler.z = .25
        subject.keyframe_insert(data_path='rotation_euler', index=2, frame=1)
        scene.frame_set(1)
        return 'changed sprite subject frame-1 rotation key from its authored identity'
    if lab == 'BL-025':
        obj = _role(scene, 'geometry_role', 'topology_wedge')
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            face = next(iter(bm.faces), None)
            if face is None:
                raise AssertionError('Topology fixture unexpectedly has no faces')
            bmesh.ops.delete(bm, geom=[face], context='FACES_ONLY')
            bm.to_mesh(obj.data)
            obj.data.update()
        finally:
            bm.free()
        return 'deleted one wedge face to create a boundary'
    if lab == 'BL-026':
        obj = _role(scene, 'geometry_role', 'boolean_wall')
        modifier = next(mod for mod in obj.modifiers if mod.type == 'BOOLEAN')
        obj.modifiers.remove(modifier)
        return 'removed the exact Boolean operation from the wall'
    if lab == 'BL-027':
        obj = _role(scene, 'geometry_role', 'projection_cage')
        modifier = next(mod for mod in obj.modifiers if mod.type == 'SHRINKWRAP')
        modifier.target = None
        return 'cleared shrinkwrap target reference'
    if lab == 'BL-028':
        mesh = _role(scene, 'geometry_role', 'attribute_mesh').data
        mesh.attributes.remove(mesh.attributes['LabContractValue'])
        return 'removed required LabContractValue mesh attribute'
    if lab == 'BL-029':
        from blender_lab import motion
        obj = motion._role(scene, 'expression_mask')
        obj.shape_key_remove(obj.data.shape_keys.key_blocks['Raised brow'])
        return 'removed the required Raised brow shape key'
    if lab == 'BL-030':
        from blender_lab import motion
        source = motion._role(scene, 'rail_source')
        source.data.bevel_object = None
        return 'cleared the rail curve sweep-profile reference'
    if lab == 'BL-031':
        from blender_lab import motion
        text = motion._role(scene, 'station_text')
        del text['font_provenance']
        return 'removed bundled-font provenance metadata'
    raise ValueError(f'No negative fixture for {lab}')


def _source_hash():
    digest = hashlib.sha256()
    paths = sorted((ROOT / 'blender_lab').glob('*.py')) + [Path(__file__).resolve()]
    for path in paths:
        digest.update(path.relative_to(ROOT).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _fresh_job(requested):
    if requested is None:
        return Path(tempfile.mkdtemp(prefix='blender-lab-feature-failures-')).resolve()
    parent = requested.expanduser().resolve()
    parent.mkdir(parents=True, exist_ok=True)
    job = parent / ('feature-failures-' + uuid.uuid4().hex[:12])
    job.mkdir(exist_ok=False)
    return job


def _run_case(lab, original_scene, sentinel, job):
    scene = labs.build(lab)
    case_output = job / lab
    case_output.mkdir(exist_ok=False)
    baseline = verification.verify(scene, case_output)
    condition = _mutate(lab, scene)
    try:
        verification.verify(scene, case_output)
    except (AssertionError, ValueError) as error:
        detected = {'type': type(error).__name__, 'message': str(error)}
    else:
        raise AssertionError(f'{lab} verifier accepted negative feature fixture: {condition}')

    old_instance = scene['blender_lab_instance_id']
    reset_scene = labs.reset(scene)
    if reset_scene['blender_lab_instance_id'] == old_instance:
        raise AssertionError(f'{lab} reset reused its mutated scene instance')
    if sentinel.name not in original_scene.objects:
        raise AssertionError(f'{lab} reset deleted the unrelated-scene sentinel')
    reset_metrics = verification.verify(reset_scene, case_output)
    reset_assets = json.loads(reset_scene.get('blender_lab_assets', '{}'))
    bpy.data.scenes.remove(reset_scene)
    labs.remove_unused(reset_assets)
    bpy.context.window.scene = original_scene
    return {
        'id': lab,
        'baseline_metrics': baseline,
        'mutated_condition': condition,
        'detected_error': detected,
        'reset_instance_replaced': True,
        'sentinel_preserved': True,
        'reset_metrics': reset_metrics,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--labs', help='Comma-separated implemented adapter IDs; default is all 17 new adapters')
    parser.add_argument('--output', type=Path, help='Parent directory for a new unique feature-failures job')
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    args = parser.parse_args(argv)
    selected = ADAPTER_LABS if not args.labs else tuple(value.strip() for value in args.labs.split(',') if value.strip())
    if not selected or len(set(selected)) != len(selected):
        parser.error('--labs must contain unique implemented adapter IDs')
    unknown = set(selected) - set(ADAPTER_LABS)
    if unknown:
        parser.error(f'Unsupported adapter IDs: {sorted(unknown)}')

    job = _fresh_job(args.output)
    original_scene = bpy.context.scene
    sentinel = bpy.data.objects.new('Feature failure unrelated-scene sentinel', None)
    original_scene.collection.objects.link(sentinel)
    results = []
    report = {
        'schema_version': 1,
        'runtime': {
            'version': bpy.app.version_string,
            'build_hash': bpy.app.build_hash.decode('ascii', errors='replace'),
            'background': bpy.app.background,
        },
        'source_sha256': _source_hash(),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'job_directory': str(job),
        'selected_labs': list(selected),
        'status': 'running',
        'passed': 0,
        'results': results,
    }
    report_path = job / 'feature-failures.json'

    def save_report():
        report['passed'] = len(results)
        report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n', encoding='utf-8')

    save_report()
    try:
        for lab in selected:
            results.append(_run_case(lab, original_scene, sentinel, job))
            save_report()
        report['status'] = 'passed'
        save_report()
    except Exception as error:
        report['status'] = 'failed'
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        save_report()
        raise
    finally:
        bpy.context.window.scene = original_scene
        bpy.data.objects.remove(sentinel, do_unlink=True)
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
