"""Automated real-window package acceptance; no global preference save."""
from pathlib import Path
import json
import traceback
import os
import sys
import hashlib
from datetime import datetime, timezone
import bpy

# Suppress first-run splash only in this process; never save user preferences.
bpy.context.preferences.view.show_splash = False

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'build' / 'ui'
OUTPUT.mkdir(parents=True, exist_ok=True)


def run():
    try:
        bpy.ops.preferences.addon_install(filepath=str(ROOT / 'dist' / 'blender-lab-0.1.0.zip'))
        bpy.ops.preferences.addon_enable(module='blender_lab')
        import blender_lab
        from blender_lab import labs, verification
        from blender_lab import catalog
        verification.check(len(catalog.ENTRIES) == 96, 'Installed package did not load the full atlas')
        verification.check(catalog.filtered('BL-096')[0]['id'] == 'BL-096', 'Planned lab search failed')
        verification.check({entry['id'] for entry in catalog.filtered(available=labs.LABS)} == set(labs.LABS),
                           'Available-only atlas filter lost an implemented adapter')
        bpy.ops.blender_lab.inspect(lab='BL-096')
        verification.check(bpy.context.scene.blender_lab_selected == 'BL-096', 'Planned card inspection failed')
        original = bpy.context.scene
        sentinel = bpy.data.objects.new('User content sentinel', None)
        original.collection.objects.link(sentinel)
        checks = []
        for lab in labs.LABS:
            bpy.ops.blender_lab.open(lab=lab)
            scene = bpy.context.scene
            scene.blender_lab_value_control = 1.25
            bpy.ops.blender_lab.apply()
            metrics = verification.verify(scene, OUTPUT)
            bpy.ops.blender_lab.reset()
            verification.check(sentinel.name in original.objects, 'UI reset lost user content')
            before = {name: len(getattr(bpy.data, name)) for name in labs.DATA_COLLECTIONS}
            for _ in range(8):
                bpy.ops.blender_lab.reset()
            after = {name: len(getattr(bpy.data, name)) for name in labs.DATA_COLLECTIONS}
            verification.check(before == after, f'{lab} reset leaked datablocks: {before} -> {after}')
            checks.append({'lab': lab, 'metrics': metrics, 'reset_preserved_user_scene': True})
        bpy.ops.blender_lab.open(lab='BL-006')
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.show_region_ui = True
                area.spaces.active.region_3d.view_perspective = 'CAMERA'
        bpy.context.scene.render.filepath = str(OUTPUT / 'package-preview.png')
        bpy.context.scene.blender_lab_output = str(OUTPUT)
        bpy.ops.blender_lab.export()
        bpy.ops.blender_lab.export()
        exports = list(OUTPUT.glob('artifact-*'))
        verification.check(len(exports) >= 2 and all((p / 'artifact.glb').is_file() for p in exports), 'UI exports overwrote a prior take')
        bpy.ops.render.render(write_still=True)
        (OUTPUT / 'evidence.json').write_text(json.dumps({'passed': True, 'timestamp': datetime.now(timezone.utc).isoformat(), 'blender': bpy.app.version_string,
            'installed_module': blender_lab.__file__, 'atlas_entries': len(catalog.ENTRIES),
            'catalog_sha256': hashlib.sha256((Path(blender_lab.__file__).parent / 'catalog.json').read_bytes()).hexdigest(),
            'checks': checks, 'reset_datablocks_stable': True}, indent=2) + '\n')
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                region = next(item for item in area.regions if item.type == 'WINDOW')
                with bpy.context.temp_override(area=area, region=region):
                    bpy.ops.wm.call_panel(name='BLENDERLAB_PT_catalog', keep_open=True)
                break
        bpy.app.timers.register(finish, first_interval=3)
    except Exception:
        diagnostic = traceback.format_exc()
        (OUTPUT / 'failure.txt').write_text(diagnostic)
        (OUTPUT / 'evidence.json').write_text(json.dumps({'passed': False, 'error': diagnostic}) + '\n')
        print(diagnostic, file=sys.stderr, flush=True)
        os._exit(1)
    return None


def finish():
    bpy.ops.screen.screenshot(filepath=str(OUTPUT / 'blender-window.png'))
    bpy.ops.wm.quit_blender()
    return None


bpy.app.timers.register(run, first_interval=2)
