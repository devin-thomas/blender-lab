"""Outcome checks run by both the UI and batch automation."""
import json
import bpy
from . import labs


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def bounds(obj):
    from mathutils import Vector
    points = [obj.matrix_world @ Vector(point) for point in obj.bound_box]
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]


def roundtrip(scene, output):
    obj = labs.subject(scene)
    labs.activate(obj)
    bpy.context.view_layer.update()
    original_bounds = bounds(obj)
    path = output / "artifact.glb"
    result = bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', use_selection=True,
                                       export_apply=True, export_yup=True, use_active_scene=True,
                                       export_vertex_color='ACTIVE', export_all_vertex_colors=True)
    check(result == {'FINISHED'} and path.stat().st_size > 100, "glTF export did not produce a file")
    # Import into an isolated scene, so a probe never adds copies to the user's lab.
    probe = bpy.data.scenes.new("Roundtrip verification")
    before_import = labs.snapshot()
    bpy.context.window.scene = probe
    try:
        result = bpy.ops.import_scene.gltf(filepath=str(path))
        check(result == {'FINISHED'}, "glTF import failed")
        meshes = [item for item in probe.objects if item.type == 'MESH']
        check(len(meshes) == 1, "Expected one exported artifact")
        imported = meshes[0]
        bpy.context.view_layer.update()
        imported_bounds = bounds(imported)
        check(all(abs(a - b) < 1e-4 for pair_a, pair_b in zip(original_bounds, imported_bounds)
                  for a, b in zip(pair_a, pair_b)), "glTF transform or bounds changed")
        obj.data.calc_loop_triangles()
        check(len(imported.data.polygons) == len(obj.data.loop_triangles), "glTF triangle count changed")
        check(imported.data.uv_layers and imported.data.color_attributes, "glTF dropped UV or vertex colors")
        check(imported.data.materials and imported.data.materials[0].use_nodes, "glTF material missing")
        imported_tree = imported.data.materials[0].node_tree
        images = [n.image for n in imported_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
        check(images and images[0].size[:] == (32, 32), "glTF lost the original pixel image")
        evidence = {"vertices": len(imported.data.vertices), "faces": len(imported.data.polygons),
                    "bounds": imported_bounds, "uv": True, "vertex_colors": True, "file_bytes": path.stat().st_size}
    finally:
        bpy.context.window.scene = scene
        bpy.data.scenes.remove(probe)
        labs.remove_unused(labs.created_since(before_import))
    (output / "roundtrip.json").write_text(json.dumps(evidence, indent=2) + "\n")
    return evidence


def verify(scene, output):
    implementation = labs.adapter(scene.get('blender_lab_id'))
    if implementation:
        return implementation.verify(scene, scene['blender_lab_id'], json.loads(scene['blender_lab_controls']), output)
    lab = scene["blender_lab_id"]
    obj = labs.subject(scene)
    value = scene["blender_lab_value"]
    bpy.context.view_layer.update()
    graph = bpy.context.evaluated_depsgraph_get()
    if lab == "BL-001":
        evaluated = obj.evaluated_get(graph)
        check(len(evaluated.data.vertices) > len(obj.data.vertices), "Bevel has no evaluated effect")
        check(abs(obj.modifiers[0].width - .08 * value) < 1e-5, "Bevel control was not applied")
        return {"base_vertices": len(obj.data.vertices), "evaluated_vertices": len(evaluated.data.vertices),
                "evaluated_coordinate_sum": sum(v.co.length for v in evaluated.data.vertices)}
    if lab == "BL-002":
        image = obj.data.materials[0].node_tree.nodes.get("Image Texture")
        check(image.image.size[:] == (32, 32) and image.interpolation == 'Closest', "Pixel texture contract failed")
        check(image.image.packed_file is not None, "Texture is not portable")
        shades = obj.data.color_attributes['AuthoredShade'].data
        check(len({tuple(round(v, 2) for v in entry.color) for entry in shades}) > 1, "Vertex shades are uniform")
        check(obj.data.uv_layers.active is not None, "Missing UV map")
        strength = obj.data.materials[0].node_tree.nodes['Vertex shade strength'].inputs[0].default_value
        check(abs(strength - value / 2) < 1e-5, "Vertex shade strength was not applied")
        tree = obj.data.materials[0].node_tree
        mix = tree.nodes['Vertex shade strength']
        vertex = next(n for n in tree.nodes if n.type == 'VERTEX_COLOR')
        check(any(link.from_node == image and link.to_socket == mix.inputs[1] for link in tree.links)
              and any(link.from_node == vertex and link.to_socket == mix.inputs[2] for link in tree.links)
              and any(link.from_node == mix and link.to_socket == tree.nodes['Principled BSDF'].inputs['Base Color']
                      for link in tree.links), 'Pixel/vertex shader graph is disconnected')
        return {"atlas_size": list(image.image.size), "filter": image.interpolation,
                "color_domain": 'CORNER', "shade_strength": strength}
    if lab == "BL-003":
        evaluated = obj.evaluated_get(graph)
        count = obj.modifiers[0].node_group.nodes['Editable count'].inputs['Count'].default_value
        check(len(evaluated.data.vertices) == count * 12, "Geometry Nodes did not realize all requested six-sided cones")
        extent = bounds(evaluated)[0]
        check(extent[1] - extent[0] > (count - 1) * 1.3, "Instances do not span their requested row")
        return {"instances": count, "evaluated_vertices": len(evaluated.data.vertices), "x_extent": extent}
    if lab == "BL-004":
        scene.frame_set(1)
        start = obj.matrix_world.translation.z
        scene.frame_set(30)
        peak = obj.matrix_world.translation.z
        scene.frame_set(60)
        end = obj.matrix_world.translation.z
        check(abs(peak - start - value * 2) < 1e-4 and abs(end - start) < 1e-4, "Animation samples missed target motion")
        scene.frame_set(30)
        return {"start_z": start, "peak_z": peak, "end_z": end}
    if lab == "BL-005":
        scene.frame_set(1)
        start = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation.z
        for frame in range(2, 91):
            scene.frame_set(frame)
        end = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation.z
        check(start - end > .8 and 1.0 < end < 1.5, "Rigid body did not settle on plinth within tolerance")
        return {"release_z": start, "settled_z": end, "frames": 90, "tolerance": [1, 1.5]}
    if lab == "BL-006":
        return roundtrip(scene, output)
    if lab in ('BL-007', 'BL-008', 'BL-009'):
        from . import authoring
        return authoring.verify(scene, lab, value)
    raise ValueError(f"No verifier for {lab}")
