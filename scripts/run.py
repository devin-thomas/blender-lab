"""Portable launcher; Blender itself executes the source and checks."""
import argparse
from pathlib import Path
import shutil
import subprocess
import os

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('action', choices=['build', 'test', 'render', 'export'])
parser.add_argument('--blender', default=os.environ.get('BLENDER_BIN') or shutil.which('blender'))
parser.add_argument('--lab')
parser.add_argument('--output', type=Path, default=ROOT / 'build')
parser.add_argument('--value', type=float, default=1)
args = parser.parse_args()
if not args.blender:
    parser.error('Set BLENDER_BIN or pass --blender /path/to/blender')
command = [args.blender, '--background', '--factory-startup', '--python-exit-code', '1', '--python',
           str(ROOT / 'scripts' / 'entry.py'), '--', '--action', args.action, '--output', str(args.output.resolve()), '--value', str(args.value)]
if args.lab:
    command.extend(['--lab', args.lab])
subprocess.run(command, check=True)
