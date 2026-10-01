"""Validate public catalog, links and source-only add-on packaging."""
import ast
import json
from pathlib import Path
import re
import zipfile
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(root / 'scripts' / 'generate_catalog.py'), '--check'], check=True)
tree = ast.parse((root / 'blender_lab' / 'labs.py').read_text())
assignment = next(node for node in tree.body if isinstance(node, ast.Assign)
                  and any(isinstance(target, ast.Name) and target.id == 'LABS' for target in node.targets))
labs = ast.literal_eval(assignment.value)
catalog = json.loads((root / 'catalog.json').read_text())
implemented = {item['id'] for item in catalog['experiments'] if item['implementation'] == 'implemented'}
assert implemented == set(labs), 'Implemented catalog/source lab IDs differ'
adapter = (root / 'capture' / 'adapter.mjs').read_text()
scenario_block = adapter.split('export const scenarios = [', 1)[1].split('].map(', 1)[0]
assert set(re.findall(r"'((?:BL-)\d{3})'", scenario_block)) == implemented, 'Cappy scenarios/implemented registry differ'
for item in catalog['experiments']:
    if item['id'] in labs:
        assert item['title'] == labs[item['id']][0], f"Wrong title for {item['id']}"
    assert (root / item['card']).is_file(), f"Missing card for {item['id']}"
for source in [*root.glob('*.md'), *sorted((root / 'docs').rglob('*.md')), *sorted((root / 'tickets').rglob('*.md'))]:
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', source.read_text()):
        if '://' in target or target.startswith('#'):
            continue
        path = target.split('#', 1)[0]
        assert (source.parent / path).exists(), f'Broken link {source.name}: {target}'
package = root / 'dist' / 'blender-lab-0.1.0.zip'
with zipfile.ZipFile(package) as archive:
    expected = {f'blender_lab/{p.name}' for p in (root / 'blender_lab').glob('*.py')} | {'blender_lab/LICENSE', 'blender_lab/catalog.json'}
    assert set(archive.namelist()) == expected, 'ZIP contains unexpected or missing files'
    for p in (root / 'blender_lab').glob('*.py'):
        assert archive.read(f'blender_lab/{p.name}') == p.read_bytes(), 'ZIP source differs'
    assert archive.read('blender_lab/catalog.json') == (root / 'catalog.json').read_bytes(), 'ZIP catalog differs'
print('Catalog, document links and exact source-only ZIP checks passed')
