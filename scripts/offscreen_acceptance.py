"""Background operator and reset checks; this does not qualify editor drawing."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import bpy
import blender_lab
from blender_lab import catalog, controls, labs, verification


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--labs', nargs='+', required=True)
    parser.add_argument('--output', type=Path, default=ROOT / 'build' / 'offscreen')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if not bpy.app.background:
        raise ValueError('Run this acceptance script with --background')
    if len(set(args.labs)) != len(args.labs) or set(args.labs) - set(labs.ADAPTERS):
        parser.error('Select distinct implemented typed adapters')
    output = args.output.resolve() / ('operators-' + uuid4().hex[:12])
    output.mkdir(parents=True, exist_ok=False)
    blender_lab.register()
    original = bpy.context.scene
    sentinel = bpy.data.objects.new('Offscreen user-content sentinel', None)
    original.collection.objects.link(sentinel)
    report = {'schemaVersion': 1, 'status': 'running', 'background': bpy.app.background,
              'blender': bpy.app.version_string, 'build_hash': bpy.app.build_hash.decode(),
              'source_sha256': hashlib.sha256(b''.join(p.read_bytes() for p in sorted((ROOT / 'blender_lab').glob('*.py')))).hexdigest(),
              'catalog_sha256': hashlib.sha256((ROOT / 'catalog.json').read_bytes()).hexdigest(),
              'acceptance_surface': 'background operators; editor/window drawing and human acceptance not run',
              'checks': []}
    path = output / 'evidence.json'
    path.write_text(json.dumps(report, indent=2) + '\n')
    for lab in args.labs:
        bpy.ops.blender_lab.open(lab=lab)
        scene = bpy.context.scene
        item = catalog.BY_ID[lab]['controls'][0]
        if item['type'] == 'enum':
            value = next(option for option in item['options'] if option != item['default'])
        else:
            value = item['minimum'] if item['minimum'] != item['default'] else item['maximum']
            value = int(value) if item['type'] == 'integer' else float(value)
        scene[controls.property_name(item['name'])] = value
        bpy.ops.blender_lab.apply()
        verification.check(json.loads(scene['blender_lab_controls'])[item['name']] == value,
                           'Background operator ignored its declared control widget')
        metrics = verification.verify(scene, output)
        bpy.ops.blender_lab.reset()
        before = {name: len(getattr(bpy.data, name)) for name in labs.DATA_COLLECTIONS}
        for _ in range(8):
            bpy.ops.blender_lab.reset()
        after = {name: len(getattr(bpy.data, name)) for name in labs.DATA_COLLECTIONS}
        verification.check(before == after, f'{lab} reset leaked data: {before} -> {after}')
        verification.check(sentinel.name in original.objects, 'Reset removed unrelated user content')
        report['checks'].append({'lab': lab, 'metrics': metrics, 'stable_reset_cycles': 8,
                                 'sentinel_preserved': True})
        path.write_text(json.dumps(report, indent=2) + '\n')
    report.update(status='passed', completed_at=datetime.now(timezone.utc).isoformat())
    path.write_text(json.dumps(report, indent=2) + '\n')
    print(f'Offscreen operator acceptance passed: {path}')


if __name__ == '__main__':
    main()
