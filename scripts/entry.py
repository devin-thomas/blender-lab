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
    selected = [args.lab] if args.lab else list(labs.LABS)
    source_hash = hashlib.sha256(b''.join(p.read_bytes() for p in sorted((ROOT / 'blender_lab').glob('*.py')))).hexdigest()
    report = {'schemaVersion': 1, 'blender': bpy.app.version_string, 'build_hash': bpy.app.build_hash.decode(),
              'source_sha256': source_hash, 'timestamp': datetime.now(timezone.utc).isoformat(), 'action': args.action, 'labs': []}
    sentinel = bpy.data.objects.new("Acceptance sentinel", None)
    bpy.context.scene.collection.objects.link(sentinel)
    original_scene = bpy.context.scene
    for lab in selected:
        scene = labs.build(lab)
        labs.apply_value(scene, args.value)
        lab_output = output if len(selected) == 1 else output / lab
        lab_output.mkdir(parents=True, exist_ok=True)
        metrics = verification.verify(scene, lab_output)
        if args.action == 'test':
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
        report['labs'].append({'id': lab, 'status': 'passed', 'value': args.value, 'metrics': metrics})
    (output / 'evidence.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
