bl_info = {"name": "Blender Lab", "author": "Devin Thomas", "version": (0, 1, 0),
           "blender": (5, 2, 0), "location": "View3D > Sidebar > Blender Lab",
           "description": "Editable capability experiments with shared automation operations", "category": "3D View"}

import bpy
from bpy.props import FloatProperty, StringProperty
from textwrap import wrap
from . import labs


class BLENDERLAB_OT_open(bpy.types.Operator):
    bl_idname = "blender_lab.open"
    bl_label = "Open experiment"
    bl_description = "Create a separate scene; preserve your existing scenes"
    lab: StringProperty(default="BL-001")

    def execute(self, context):
        labs.build(self.lab)
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
        labs.apply_value(context.scene, context.scene.blender_lab_value_control)
        self.report({'INFO'}, "Applied to the editable scene")
        return {'FINISHED'}


class BLENDERLAB_OT_reset(bpy.types.Operator):
    bl_idname = "blender_lab.reset"
    bl_label = "Reset this lab"
    bl_description = "Replace only the active lab scene; discard edits within that scene"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        labs.reset(context.scene)
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
        for lab, (title, _) in labs.LABS.items():
            layout.operator("blender_lab.open", text=f"{lab}  {title}").lab = lab
        scene = context.scene
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


CLASSES = (BLENDERLAB_OT_open, BLENDERLAB_OT_apply, BLENDERLAB_OT_reset, BLENDERLAB_OT_export, BLENDERLAB_PT_catalog)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.blender_lab_value_control = FloatProperty(name="Experiment value", default=1, min=.1, max=2)
    bpy.types.Scene.blender_lab_output = StringProperty(name="Output folder", default="//blender-lab-export/", subtype='DIR_PATH')


def unregister():
    del bpy.types.Scene.blender_lab_value_control
    del bpy.types.Scene.blender_lab_output
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
