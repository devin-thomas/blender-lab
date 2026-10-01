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
from blender_lab import labs, verification
from blender_lab.operations import Request, perform


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', choices=['build', 'test', 'render', 'export', 'scenario'], default='build')
    parser.add_argument('--lab', choices=list(labs.LABS))
    parser.add_argument('--output', type=Path, default=ROOT / 'build')
    parser.add_argument('--value', type=float, default=1)
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
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
        request = Request('open', lab, args.value)
        receipt = perform(request)
        scene = bpy.context.scene
        lab_output = output if len(selected) == 1 else output / lab
        lab_output.mkdir(parents=True, exist_ok=True)
        metrics = verification.verify(scene, lab_output)
        if args.action == 'test':
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
        report['labs'].append({'id': lab, 'status': 'passed', 'value': args.value, 'metrics': metrics,
                              'operation_request_id': json.loads(scene['blender_lab_receipt'])['request_id'],
                              'open_request_id': receipt.request_id})
    (output / 'evidence.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
