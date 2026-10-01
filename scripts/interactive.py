"""blender --python scripts/interactive.py: load the same editable add-on."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import blender_lab
from blender_lab import labs
blender_lab.register()
labs.build('BL-001')
