bl_info = {"name": "Blender Lab", "author": "Devin Thomas", "version": (0, 1, 0),
           "blender": (5, 2, 0), "location": "View3D > Sidebar > Blender Lab",
           "description": "Editable capability experiments with shared automation operations", "category": "3D View"}

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, StringProperty
from textwrap import wrap
from . import catalog, labs
from .operations import Request, perform


def reset_catalog_page(scene, context):
    scene.blender_lab_page = 1


class BLENDERLAB_OT_open(bpy.types.Operator):
    bl_idname = "blender_lab.open"
    bl_label = "Open experiment"
    bl_description = "Create a separate scene; preserve your existing scenes"
    lab: StringProperty(default="BL-001")

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        perform(Request('open', self.lab))
        context.scene.blender_lab_selected = self.lab
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.view_perspective = 'CAMERA'
                area.spaces.active.shading.type = 'MATERIAL'
        return {'FINISHED'}


class BLENDERLAB_OT_apply(bpy.types.Operator):
    bl_idname = "blender_lab.apply"
    bl_label = "Apply experiment value"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        perform(Request('apply', context.scene['blender_lab_id'], context.scene.blender_lab_value_control,
                        scene_id=context.scene['blender_lab_instance_id']), context.scene)
        self.report({'INFO'}, "Applied to the editable scene")
        return {'FINISHED'}


class BLENDERLAB_OT_reset(bpy.types.Operator):
    bl_idname = "blender_lab.reset"
    bl_label = "Reset this lab"
    bl_description = "Replace only the active lab scene; discard edits within that scene"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        perform(Request('reset', context.scene['blender_lab_id'], scene_id=context.scene['blender_lab_instance_id']), context.scene)
        return {'FINISHED'}


class BLENDERLAB_OT_inspect(bpy.types.Operator):
    bl_idname = 'blender_lab.inspect'
    bl_label = 'Inspect capability'
    lab: StringProperty()

    def execute(self, context):
        if self.lab not in catalog.BY_ID:
            raise ValueError(f'Unknown capability: {self.lab}')
        context.scene.blender_lab_selected = self.lab
        return {'FINISHED'}


class BLENDERLAB_OT_export(bpy.types.Operator):
    bl_idname = "blender_lab.export"
    bl_label = "Export verified glTF"
    bl_description = "Write selected lab artifact and roundtrip evidence to the chosen folder"

    def execute(self, context):
        from pathlib import Path
        from uuid import uuid4
        from .verification import roundtrip
        # A new directory per export keeps unrelated files and previous takes intact.
        output = Path(bpy.path.abspath(context.scene.blender_lab_output)) / f"artifact-{uuid4().hex[:12]}"
        output.mkdir(parents=True, exist_ok=False)
        result = roundtrip(context.scene, output)
        self.report({'INFO'}, f"Roundtrip passed: {result['vertices']} vertices; {output}")
        return {'FINISHED'}


class BLENDERLAB_PT_catalog(bpy.types.Panel):
    bl_label = "Blender Lab / Copper Observatory"
    bl_idname = "BLENDERLAB_PT_catalog"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blender Lab"

    def draw(self, context):
        layout = self.layout
        layout.label(text="EDIT / INSPECT / AUTOMATE", icon='EXPERIMENTAL')
        scene = context.scene
        layout.prop(scene, 'blender_lab_search', text='Search')
        layout.prop(scene, 'blender_lab_category', text='Domain')
        layout.prop(scene, 'blender_lab_available_only', text='Implemented only')
        entries = catalog.filtered(scene.blender_lab_search, scene.blender_lab_category,
                                   set(labs.LABS) if scene.blender_lab_available_only else None)
        count = len(entries)
        pages = max(1, (count + 7) // 8)
        page = min(scene.blender_lab_page, pages)
        layout.label(text=f'{count} matches / {len(catalog.ENTRIES)} capabilities')
        layout.prop(scene, 'blender_lab_page', text=f'Page ({pages} total)')
        for entry in entries[(page - 1) * 8:page * 8]:
            row = layout.row(align=True)
            row.operator('blender_lab.inspect', text=f"{entry['id']} {entry['title']}").lab = entry['id']
        selected = catalog.BY_ID.get(scene.blender_lab_selected)
        if selected:
            box = layout.box()
            for line in wrap(f"{selected['id']} / {selected['title']}", width=34):
                box.label(text=line)
            box.label(text=f"State: {selected['implementation']}")
            states = selected.get('states', {})
            for label, key in (('Outcome', 'automated'), ('Editor', 'editor')):
                for line in wrap(f"{label}: {states.get(key, 'not-run')}", width=34):
                    box.label(text=line)
            for line in wrap(selected.get('moment', selected['mechanism']), width=34):
                box.label(text=line)
            if selected['id'] in labs.LABS:
                if context.mode != 'OBJECT':
                    box.label(text='Return to Object Mode to open')
                box.operator('blender_lab.open', text='Open editable experiment').lab = selected['id']
            else:
                box.label(text='Scene adapter is not implemented', icon='INFO')
                for line in wrap(selected.get('fallback', 'Read the experiment specification and qualification gates.'), width=34):
                    box.label(text=line)
            box.operator('wm.url_open', text='Full capability contract', icon='HELP').url = (
                f"https://github.com/devin-thomas/blender-lab/blob/main/docs/experiments/{selected['id']}.md")
            box.label(text=f"Plan: {selected.get('milestone', 'M0')}")
        lab = scene.get("blender_lab_id")
        if lab in labs.LABS:
            box = layout.box()
            box.label(text=labs.LABS[lab][0])
            for sentence in labs.LABS[lab][1].split('. '):
                for line in wrap(sentence, width=34):
                    box.label(text=line)
            box.prop(scene, "blender_lab_value_control", text="Experiment value")
            box.operator("blender_lab.apply")
            box.label(text=f"Applied: {scene.get('blender_lab_value', 1):.2f}")
            box.operator("blender_lab.reset", icon='FILE_REFRESH')
            if lab == "BL-006":
                box.prop(scene, "blender_lab_output", text="Output folder")
                box.operator("blender_lab.export", icon='EXPORT')
            box.label(text="Space: play timeline / Tab: edit mesh")
            box.label(text="Text Editor: lab Read me")
            if scene.get('blender_lab_receipt'):
                import json
                receipt = json.loads(scene['blender_lab_receipt'])
                box.label(text=receipt['summary'])
                box.label(text=f"Receipt: {receipt['request_id'][:8]}")


CLASSES = (BLENDERLAB_OT_open, BLENDERLAB_OT_apply, BLENDERLAB_OT_reset, BLENDERLAB_OT_inspect, BLENDERLAB_OT_export, BLENDERLAB_PT_catalog)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.blender_lab_value_control = FloatProperty(name="Experiment value", default=1, min=.1, max=2)
    bpy.types.Scene.blender_lab_output = StringProperty(name="Output folder", default="//blender-lab-export/", subtype='DIR_PATH')
    bpy.types.Scene.blender_lab_search = StringProperty(name='Search capability atlas', update=reset_catalog_page)
    bpy.types.Scene.blender_lab_category = EnumProperty(name='Capability domain', items=[('ALL', 'All domains', '')] + [(name, name, '') for name in catalog.CATEGORIES], update=reset_catalog_page)
    bpy.types.Scene.blender_lab_available_only = BoolProperty(default=False, update=reset_catalog_page)
    bpy.types.Scene.blender_lab_page = IntProperty(default=1, min=1, max=max(1, (len(catalog.ENTRIES) + 7) // 8))
    bpy.types.Scene.blender_lab_selected = StringProperty(default='BL-001')


def unregister():
    del bpy.types.Scene.blender_lab_value_control
    del bpy.types.Scene.blender_lab_output
    for name in ('blender_lab_search', 'blender_lab_category', 'blender_lab_available_only', 'blender_lab_page', 'blender_lab_selected'):
        delattr(bpy.types.Scene, name)
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
