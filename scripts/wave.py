"""Serialized fresh-process qualification with per-lab budgets and retained logs."""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import math
import os
import platform
from pathlib import Path
import shutil
import subprocess
import sys
import time
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]


def _registry():
    """Read literal registry assignments without importing Blender on the host."""
    tree = ast.parse((ROOT / 'blender_lab' / 'labs.py').read_text(encoding='utf-8'))
    result = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('LABS', 'ADAPTERS'):
                    result[target.id] = ast.literal_eval(node.value)
    if set(result) != {'LABS', 'ADAPTERS'}:
        raise ValueError('Expected literal LABS and ADAPTERS registries in labs.py')
    return result


def _sources():
    paths = sorted([*(ROOT / 'blender_lab').glob('*.py'), *(ROOT / 'scripts').glob('*.py'),
                    ROOT / 'catalog.json', ROOT / 'specs' / 'experiments.json'])
    files = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    module_hash = hashlib.sha256(b''.join(path.read_bytes() for path in sorted((ROOT / 'blender_lab').glob('*.py')))).hexdigest()
    return {'files': files, 'source_sha256': module_hash,
            'catalog_sha256': files['catalog.json'],
            'manifest_sha256': hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()}


def _write(path, document):
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(document, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    temporary.replace(path)


def _process(command, folder, name, deadline):
    started = time.monotonic()
    stdout, stderr = folder / f'{name}.stdout.log', folder / f'{name}.stderr.log'
    record = {'command': command, 'stdout': stdout.name, 'stderr': stderr.name}
    remaining = deadline - started
    if remaining <= 0:
        record.update(status='timed-out', error='Per-lab process budget exhausted before launch', elapsed_seconds=0)
        return record
    try:
        with stdout.open('w', encoding='utf-8') as out, stderr.open('w', encoding='utf-8') as err:
            completed = subprocess.run(command, stdout=out, stderr=err, timeout=remaining,
                                       cwd=ROOT, check=False)
        record.update(return_code=completed.returncode,
                      status='passed' if completed.returncode == 0 else 'failed')
    except subprocess.TimeoutExpired:
        record.update(status='timed-out', error='Blender exceeded the remaining per-lab process budget')
    except OSError as error:
        record.update(status='failed', error=f'Cannot launch Blender: {error}')
    record['elapsed_seconds'] = round(time.monotonic() - started, 3)
    return record


def _read_evidence(path):
    if not path.is_file():
        return None, f'Expected evidence file is missing: {path.name}'
    try:
        evidence = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as error:
        return None, f'Cannot read evidence {path.name}: {error}'
    if not isinstance(evidence, dict):
        return None, f'Evidence {path.name} must contain a JSON object'
    return evidence, None


def main():
    registry = _registry()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['test', 'build', 'render'])
    parser.add_argument('--blender', default=os.environ.get('BLENDER_BIN') or shutil.which('blender'))
    parser.add_argument('--labs', nargs='+', help='Selected implemented IDs; defaults to the new adapter wave')
    parser.add_argument('--lab', action='append', default=[], help='Select one lab; repeatable')
    parser.add_argument('--output', type=Path, default=ROOT / 'build' / 'waves', help='Parent of a new unique wave directory')
    parser.add_argument('--timeout', type=float, default=120, help='Per-lab seconds, including fresh reopen for test')
    parser.add_argument('--value', type=float, default=1)
    parser.add_argument('--controls-file', type=Path, help='Typed JSON display-name controls; requires exactly one lab')
    args = parser.parse_args()
    if not args.blender:
        parser.error('Set BLENDER_BIN or pass --blender /path/to/blender')
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error('--timeout must be a finite positive number of seconds')
    if not math.isfinite(args.value) or not .1 <= args.value <= 2:
        parser.error('--value must be finite and between 0.1 and 2.0')
    selected = (args.labs or []) + args.lab
    selected = selected or sorted(registry['ADAPTERS'])
    if not selected or len(selected) != len(set(selected)):
        parser.error('Select a nonempty list of distinct lab IDs')
    unknown = set(selected) - set(registry['LABS'])
    if unknown:
        parser.error(f'Labs have no implemented adapter: {sorted(unknown)}')
    if args.controls_file and len(selected) != 1:
        parser.error('--controls-file requires exactly one selected lab')
    controls_path = None
    if args.controls_file:
        controls_path = args.controls_file.resolve()
        supplied = json.loads(controls_path.read_text(encoding='utf-8-sig'))
        if not isinstance(supplied, dict):
            parser.error('--controls-file must contain a JSON object')
    parent = args.output.resolve()
    parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    directory = parent / f'wave-{stamp}-{uuid4().hex[:10]}'
    directory.mkdir(exist_ok=False)
    source = _sources()
    report = {'schemaVersion': 1, 'action': args.action, 'selected_labs': selected,
              'started_at': datetime.now(timezone.utc).isoformat(), 'status': 'running',
              'output': str(directory), 'timeout_seconds_per_lab': args.timeout,
              'source': source, 'labs': [], 'acceptance_surface': 'headless; editor, artist and receiving-engine acceptance remain separate'}
    report['launcher_host'] = {'hostname': platform.node(), 'platform': platform.platform(),
                               'python': platform.python_version()}
    if controls_path:
        snapshot_path = directory / 'requested-controls.json'
        snapshot_path.write_text(json.dumps(supplied, indent=2, allow_nan=False) + '\n', encoding='utf-8')
        controls_path = snapshot_path
        report['controls_file_sha256'] = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
    manifest = directory / 'manifest.json'
    _write(manifest, report)
    prefix = [args.blender, '--background', '--factory-startup', '--disable-autoexec', '--python-exit-code', '1', '--python']
    for lab in selected:
        folder = directory / lab
        folder.mkdir(exist_ok=False)
        started = time.monotonic()
        deadline = started + args.timeout
        command = prefix + [str(ROOT / 'scripts' / 'entry.py'), '--', '--action', args.action,
                            '--lab', lab, '--output', str(folder), '--value', str(args.value)]
        if controls_path:
            command.extend(['--controls-file', str(controls_path)])
        record = {'id': lab, 'output': lab, 'status': 'running', 'processes': []}
        process = _process(command, folder, 'entry', deadline)
        record['processes'].append(process)
        record['status'] = process['status']
        if process['status'] == 'passed':
            evidence, error = _read_evidence(folder / 'evidence.json')
            if error:
                record.update(status='failed', error=error)
            elif (evidence.get('action') != args.action
                  or evidence.get('source_sha256') != source['source_sha256']
                  or evidence.get('catalog_sha256') != source['catalog_sha256']
                  or len(evidence.get('labs', [])) != 1
                  or evidence['labs'][0].get('id') != lab
                  or evidence['labs'][0].get('status') != 'passed'):
                record.update(status='failed', error='Evidence action, source identity or selected-lab assertion does not match this wave')
            else:
                record['evidence'] = 'evidence.json'
                record['blender'] = evidence.get('blender')
                record['build_hash'] = evidence.get('build_hash')
        if record['status'] == 'passed' and args.action == 'test':
            reopen = prefix + [str(ROOT / 'scripts' / 'reopen_check.py'), '--', '--lab', lab, '--output', str(folder)]
            process = _process(reopen, folder, 'reopen', deadline)
            record['processes'].append(process)
            record['status'] = process['status']
            if process['status'] == 'passed':
                evidence, error = _read_evidence(folder / 'reopen-evidence.json')
                if error:
                    record.update(status='failed', error=error)
                elif (evidence.get('passed') is not True or len(evidence.get('checks', [])) != 1
                      or evidence['checks'][0].get('lab') != lab):
                    record.update(status='failed', error='Fresh-process reopen receipt does not prove the selected saved lab')
                else:
                    record['fresh_process_reopen'] = 'passed'
                    record['reopen_evidence'] = 'reopen-evidence.json'
        record['elapsed_seconds'] = round(time.monotonic() - started, 3)
        report['labs'].append(record)
        _write(manifest, report)
        print(f"{lab}: {record['status']} ({record['elapsed_seconds']:.1f}s)", flush=True)
    report['status'] = 'passed' if all(record['status'] == 'passed' for record in report['labs']) else 'failed'
    report['completed_at'] = datetime.now(timezone.utc).isoformat()
    report['passed_labs'] = sum(record['status'] == 'passed' for record in report['labs'])
    report['failed_labs'] = len(report['labs']) - report['passed_labs']
    _write(manifest, report)
    print(f"Wave {report['status']}: {manifest}", flush=True)
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    sys.exit(main())
