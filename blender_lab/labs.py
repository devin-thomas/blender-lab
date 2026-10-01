"""Original, editable experiments. No imported art or external dependencies."""
import math
import json
import bpy
from mathutils import Vector

LABS = {
    "BL-001": ("Silhouette Foundry", "Change the bevel. Compare the base mesh and evaluated geometry."),
    "BL-002": ("Pixel Surface Studio", "Change vertex shade strength. Inspect the UVs, packed atlas and shader."),
    "BL-003": ("Instance Conservatory", "Change the count. Inspect Mesh Line, instancing and realization nodes."),
    "BL-004": ("Motion Signal", "Change travel height. Scrub frames 1, 30 and 60; play the timeline."),
    "BL-005": ("Gravity Bench", "Change release height. Reset then play from frame 1 to see the fall."),
    "BL-006": ("Portable Artifact", "Change the artifact width. Export and reimport a selected mesh as glTF."),
}
PALETTE = {"navy": (0.025, 0.08, 0.12, 1), "teal": (0.08, 0.55, 0.50, 1),
           "amber": (0.95, 0.48, 0.09, 1), "cream": (0.80, 0.87, 0.66, 1)}
DATA_COLLECTIONS = ('collections', 'objects', 'meshes', 'curves', 'cameras', 'lights',
                    'actions', 'node_groups', 'materials', 'images', 'worlds', 'texts')


def snapshot():
    return {name: set(item.name for item in getattr(bpy.data, name)) for name in DATA_COLLECTIONS}


def created_since(before):
    return {name: list(set(item.name for item in getattr(bpy.data, name)) - before[name])
            for name in DATA_COLLECTIONS}


def remove_unused(assets):
    # Name allowlist plus user counts protects data reused by another scene.
    # Removing a collection, action or graph can release another owned datablock.
    while True:
        removed = False
        for name in DATA_COLLECTIONS:
            collection = getattr(bpy.data, name)
            for asset_name in assets.get(name, []):
                item = collection.get(asset_name)
                if item is not None and item.users == 0:
                    collection.remove(item)
                    removed = True
        if not removed:
            break


def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = 1
    shader.inputs["Specular IOR Level"].default_value = 0
    return mat


def cube(scene, name, location, scale, mat):
    vertices = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    faces = [(0, 4, 6, 2), (1, 3, 7, 5), (0, 1, 5, 4),
             (2, 6, 7, 3), (0, 2, 3, 1), (4, 5, 7, 6)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    obj.location = location
    # Bake dimensions into the base mesh, keeping rigid bodies at unit scale.
    for vertex in mesh.vertices:
        vertex.co.x *= scale[0]
        vertex.co.y *= scale[1]
        vertex.co.z *= scale[2]
    mesh.materials.append(mat)
    return obj


def activate(obj):
    for other in bpy.context.view_layer.objects:
        other.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def setup(lab):
    if lab not in LABS:
        raise ValueError(f"Unknown lab: {lab}")
    scene = bpy.data.scenes.new(f"Blender Lab | {LABS[lab][0]}")
    scene["blender_lab_id"] = lab
    scene["blender_lab_owned"] = True
    bpy.context.window.scene = scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.render.resolution_x = 800
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.fps = 24
    scene.frame_end = 90
    scene.world = bpy.data.worlds.new("Lab night")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = PALETTE["navy"]
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.5
    scene.view_settings.view_transform = "Standard"
    floor = cube(scene, "Workshop plinth", (0, 0, -0.25), (4, 3, 0.25), material("Deep ink", PALETTE["navy"]))
    floor["lab_environment"] = True
    for x in (-3.6, 3.6):
        cube(scene, "Copper rail", (x, 0, 0.05), (0.06, 2.8, 0.06), material("Rail", PALETTE["amber"]))
    camera_data = bpy.data.cameras.new("Lab camera")
    camera = bpy.data.objects.new("Lab camera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = (9, -12, 9)
    camera.rotation_euler = (Vector((0, 0, 1)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera_data.type = 'ORTHO'
    camera_data.ortho_scale = 11
    scene.camera = camera
    for name, location, energy, color in [("Warm key", (1, -4, 7), 1500, (1, .72, .4)),
                                           ("Cool fill", (-4, 1, 5), 1000, (.3, .9, 1))]:
        data = bpy.data.lights.new(name, 'AREA')
        data.energy = energy
        data.color = color
        data.shape = 'DISK'
        data.size = 6
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = location
        light.rotation_euler = (-light.location).to_track_quat('-Z', 'Y').to_euler()
    curve = bpy.data.curves.new("Station heading", 'FONT')
    curve.body = f"{lab}  /  {LABS[lab][0].upper()}"
    curve.size = .24
    heading = bpy.data.objects.new("Station heading", curve)
    scene.collection.objects.link(heading)
    heading.location = (-3.3, -2.7, .015)
    curve.materials.append(material("Lettering", PALETTE["cream"]))
    instructions = bpy.data.texts.new(f"{lab} - Read me")
    instructions.use_fake_user = False
    instructions.write(f"{LABS[lab][0]}\n\n{LABS[lab][1]}\n\nN sidebar > Blender Lab. Open creates a separate scene. Reset replaces only this lab scene.\nObjects, materials and graphs are editable. Source: blender_lab/labs.py.\n")
    scene["blender_lab_notes"] = instructions.name
    return scene, floor


def pixel_surface(obj, portable=False):
    mesh = obj.data
    uv = mesh.uv_layers.new(name="Atlas UV")
    for polygon in mesh.polygons:
        for corner, loop_index in enumerate(polygon.loop_indices):
            uv.data[loop_index].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][corner]
    colors = mesh.color_attributes.new(name="AuthoredShade", type='FLOAT_COLOR', domain='CORNER')
    for loop in mesh.loops:
        z = mesh.vertices[loop.vertex_index].co.z
        colors.data[loop.index].color = (.22, .38, .54, 1) if z < 0 else (1, .93, .7, 1)
    image = bpy.data.images.new("Original 32px copper tiles", width=32, height=32)
    pixels = []
    for y in range(32):
        for x in range(32):
            mortar = y % 8 == 0 or (x + (4 if (y // 8) % 2 else 0)) % 16 == 0
            pixels.extend((.13, .22, .27, 1) if mortar else (.85, .44, .17, 1))
    image.pixels = pixels
    image.pack()
    mat = obj.data.materials[0]
    tree = mat.node_tree
    tex = tree.nodes.new('ShaderNodeTexImage')
    tex.image = image
    tex.interpolation = 'Closest'
    vertex = tree.nodes.new('ShaderNodeVertexColor')
    vertex.layer_name = "AuthoredShade"
    mix = tree.nodes.new('ShaderNodeMixRGB')
    mix.name = "Vertex shade strength"
    mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = 1
    tree.links.new(tex.outputs["Color"], mix.inputs[1])
    tree.links.new(vertex.outputs["Color"], mix.inputs[2])
    # glTF supports an image base color plus COLOR_0, not arbitrary Blender graphs.
    color_output = tex.outputs["Color"] if portable else mix.outputs[0]
    tree.links.new(color_output, tree.nodes["Principled BSDF"].inputs["Base Color"])
    tex.location = (-600, 100)
    vertex.location = (-600, -150)
    mix.location = (-300, 100)


def geometry_nodes(obj):
    group = bpy.data.node_groups.new("Conservatory row", 'GeometryNodeTree')
    group.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    line = group.nodes.new('GeometryNodeMeshLine')
    line.name = "Editable count"
    line.inputs["Count"].default_value = 5
    line.inputs["Start Location"].default_value = (-2.8, 0, .8)
    line.inputs["Offset"].default_value = (1.4, 0, 0)
    shape = group.nodes.new('GeometryNodeMeshCone')
    shape.inputs["Vertices"].default_value = 6
    shape.inputs["Radius Top"].default_value = .15
    shape.inputs["Radius Bottom"].default_value = .5
    shape.inputs["Depth"].default_value = 1.6
    assign = group.nodes.new('GeometryNodeSetMaterial')
    assign.inputs["Material"].default_value = obj.data.materials[0]
    instances = group.nodes.new('GeometryNodeInstanceOnPoints')
    realize = group.nodes.new('GeometryNodeRealizeInstances')
    output = group.nodes.new('NodeGroupOutput')
    for src, out, dst, inp in [(shape, 'Mesh', assign, 'Geometry'), (line, 'Mesh', instances, 'Points'),
                               (assign, 'Geometry', instances, 'Instance'), (instances, 'Instances', realize, 'Geometry'),
                               (realize, 'Geometry', output, 'Geometry')]:
        group.links.new(src.outputs[out], dst.inputs[inp])
    for node, pos in [(line, (-600, 200)), (shape, (-600, -100)), (assign, (-350, -100)),
                       (instances, (-100, 200)), (realize, (150, 200)), (output, (400, 200))]:
        node.location = pos
    mod = obj.modifiers.new("Geometry Nodes / editable row", 'NODES')
    mod.node_group = group


def build(lab):
    before = snapshot()
    scene, floor = setup(lab)
    obj = cube(scene, "Lab artifact", (0, 0, 1.2), (1.2, .7, 1.2), material("Copper ceramic", PALETTE["amber"]))
    obj["blender_lab_subject"] = True
    if lab == "BL-001":
        # A deliberately stepped outline instead of a generic high-density sphere.
        for vertex in obj.data.vertices:
            if vertex.co.z > 0:
                vertex.co.x *= .65
        bevel = obj.modifiers.new("Silhouette bevel", 'BEVEL')
        bevel.width = .08
        bevel.segments = 1
    elif lab == "BL-002":
        pixel_surface(obj)
    elif lab == "BL-003":
        obj.location = (0, 0, 0)
        geometry_nodes(obj)
    elif lab == "BL-004":
        for frame, z, angle in [(1, 1.2, 0), (30, 3.2, math.pi), (60, 1.2, 2 * math.pi)]:
            obj.location.z = z
            obj.rotation_euler.z = angle
            obj.keyframe_insert(data_path="location", frame=frame)
            obj.keyframe_insert(data_path="rotation_euler", frame=frame)
        scene.frame_end = 60
        scene.frame_set(1)
    elif lab == "BL-005":
        activate(floor)
        bpy.ops.rigidbody.object_add()
        floor.rigid_body.type = 'PASSIVE'
        floor.rigid_body.collision_shape = 'BOX'
        activate(obj)
        bpy.ops.rigidbody.object_add()
        obj.rigid_body.collision_shape = 'BOX'
        obj.rigid_body.mass = 1
        obj.location.z = 4
        scene.rigidbody_world.point_cache.frame_end = 90
    elif lab == "BL-006":
        pixel_surface(obj, portable=True)
    scene["blender_lab_subject_name"] = obj.name
    scene["blender_lab_value"] = 1.0
    activate(obj)
    apply_value(scene, 1.0)
    scene["blender_lab_assets"] = json.dumps(created_since(before))
    return scene


def subject(scene):
    return scene.objects[scene["blender_lab_subject_name"]]


def apply_value(scene, value):
    lab = scene.get("blender_lab_id")
    if lab not in LABS or not .1 <= value <= 2:
        raise ValueError("Open a lab and use a value between 0.1 and 2.0")
    obj = subject(scene)
    if lab == "BL-001":
        obj.modifiers[0].width = .08 * value
    elif lab == "BL-002":
        obj.data.materials[0].node_tree.nodes["Vertex shade strength"].inputs[0].default_value = value / 2
    elif lab == "BL-003":
        line = obj.modifiers[0].node_group.nodes["Editable count"]
        count = max(1, round(value * 5))
        line.inputs["Count"].default_value = count
        line.inputs["Start Location"].default_value = (-(count - 1) * .7, 0, .8)
        scene.camera.data.ortho_scale = max(11, count * 1.9)
    elif lab == "BL-004":
        for frame, z in [(1, 1.2), (30, 1.2 + value * 2), (60, 1.2)]:
            obj.location.z = z
            obj.keyframe_insert(data_path="location", frame=frame)
        scene.frame_set(1)
    elif lab == "BL-005":
        scene.frame_set(1)
        obj.location.z = 2 + value * 2
        cache = scene.rigidbody_world.point_cache
        if cache.is_baked:
            with bpy.context.temp_override(point_cache=cache):
                bpy.ops.ptcache.free_bake()
    elif lab == "BL-006":
        obj.scale.x = value
    scene["blender_lab_value"] = value
    bpy.context.view_layer.update()


def reset(scene):
    if not scene.get("blender_lab_owned"):
        raise ValueError("Reset only applies to a lab-owned scene")
    lab = scene["blender_lab_id"]
    assets = json.loads(scene["blender_lab_assets"])
    new_scene = build(lab)
    bpy.data.scenes.remove(scene)
    remove_unused(assets)
    return new_scene
