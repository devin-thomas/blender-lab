"""Validate public catalog, links and source-only add-on packaging."""
import ast
import json
from pathlib import Path
import re
import zipfile

root = Path(__file__).resolve().parents[1]
tree = ast.parse((root / 'blender_lab' / 'labs.py').read_text())
assignment = next(node for node in tree.body if isinstance(node, ast.Assign)
                  and any(isinstance(target, ast.Name) and target.id == 'LABS' for target in node.targets))
labs = ast.literal_eval(assignment.value)
catalog = json.loads((root / 'catalog.json').read_text())
assert {item['id'] for item in catalog['experiments']} == set(labs), 'Catalog/source lab IDs differ'
for item in catalog['experiments']:
    assert item['title'] == labs[item['id']][0], f"Wrong title for {item['id']}"
    assert (root / item['card']).is_file(), f"Missing card for {item['id']}"
for source in [root / 'README.md', root / 'AGENTS.md', *sorted((root / 'docs').rglob('*.md'))]:
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', source.read_text()):
        if '://' in target or target.startswith('#'):
            continue
        path = target.split('#', 1)[0]
        assert (source.parent / path).exists(), f'Broken link {source.name}: {target}'
package = root / 'dist' / 'blender-lab-0.1.0.zip'
with zipfile.ZipFile(package) as archive:
    expected = {f'blender_lab/{p.name}' for p in (root / 'blender_lab').glob('*.py')} | {'blender_lab/LICENSE'}
    assert set(archive.namelist()) == expected, 'ZIP contains unexpected or missing files'
    for p in (root / 'blender_lab').glob('*.py'):
        assert archive.read(f'blender_lab/{p.name}') == p.read_bytes(), 'ZIP source differs'
print('Catalog, document links and exact source-only ZIP checks passed')
