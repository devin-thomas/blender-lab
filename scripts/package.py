"""Create a source-only installable add-on ZIP."""
from pathlib import Path
import zipfile
root = Path(__file__).resolve().parents[1]
output = root / 'dist' / 'blender-lab-0.1.0.zip'
output.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
    for source in sorted((root / 'blender_lab').glob('*.py')):
        archive.write(source, source.relative_to(root))
    archive.write(root / 'LICENSE', 'blender_lab/LICENSE')
    archive.write(root / 'catalog.json', 'blender_lab/catalog.json')
print(output)
