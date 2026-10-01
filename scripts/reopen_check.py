"""Verify saved Blender files in fresh loaded state, including packed assets."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bpy
import blender_lab
from blender_lab import labs, verification

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--lab', choices=list(labs.LABS), help='Reopen a selected-lab runner output')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
blender_lab.register()
checks = []
for lab in ([args.lab] if args.lab else labs.LABS):
    folder = args.output.resolve() if args.lab else args.output.resolve() / lab
    bpy.ops.wm.open_mainfile(filepath=str(folder / f'{lab}.blend'))
    scene = bpy.context.scene
    verification.check(scene['blender_lab_id'] == lab, 'Saved file opens to the wrong experiment')
    checks.append({'lab': lab, 'metrics': verification.verify(scene, folder)})
(args.output / 'reopen-evidence.json').write_text(json.dumps({'passed': True, 'blender': bpy.app.version_string, 'checks': checks}, indent=2) + '\n')
print(f'{len(checks)} saved .blend experiments passed after reopening')
