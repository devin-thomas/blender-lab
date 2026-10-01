"""Blender-native bounded motion evidence; FFmpeg can encode these PNGs."""
import argparse
from pathlib import Path
import sys
import json
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bpy
from blender_lab import labs, verification

parser = argparse.ArgumentParser()
parser.add_argument('--lab', choices=['BL-004', 'BL-005'], required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=True)
scene = labs.build(args.lab)
labs.apply_value(scene, 1)
metrics = verification.verify(scene, output)
scene.frame_set(1)
scene.cycles.samples = 8
scene.render.resolution_x = 640
scene.render.resolution_y = 480
scene.render.filepath = str(output / 'frame-')
bpy.ops.render.render(animation=True)
(output / 'evidence.json').write_text(json.dumps({'lab': args.lab, 'blender': bpy.app.version_string,
    'frames': scene.frame_end, 'fps': scene.render.fps, 'metrics': metrics, 'kind': 'native-render'}, indent=2) + '\n')
