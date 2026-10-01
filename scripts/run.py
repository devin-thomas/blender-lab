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
parser.add_argument('--controls-file', type=Path, help='JSON controls keyed by exact displayed names; requires --lab')
args = parser.parse_args()
if not args.blender:
    parser.error('Set BLENDER_BIN or pass --blender /path/to/blender')
if args.controls_file and not args.lab:
    parser.error('--controls-file requires one selected --lab')
command = [args.blender, '--background', '--factory-startup', '--disable-autoexec', '--python-exit-code', '1', '--python',
           str(ROOT / 'scripts' / 'entry.py'), '--', '--action', args.action, '--output', str(args.output.resolve()), '--value', str(args.value)]
if args.lab:
    command.extend(['--lab', args.lab])
if args.controls_file:
    command.extend(['--controls-file', str(args.controls_file.resolve())])
subprocess.run(command, check=True)
