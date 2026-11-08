"""Render the generated production mesh without modifying its manufacturing file."""
from pathlib import Path
import math

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT / "models/rimowa-production.blend"))
scene = bpy.context.scene
product = next(obj for obj in scene.objects if obj.name.startswith("PRINT"))
for obj in scene.objects:
    obj.hide_render = obj != product
product.matrix_world = Matrix.Scale(0.001, 4) @ product.matrix_world
scene.unit_settings.scale_length = 1


def surface(name, color, roughness):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = next(node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Specular IOR Level"].default_value = 0.22
    return mat


charcoal = surface("Matte charcoal", (0.006, 0.008, 0.01), 0.55)
product.data.materials.clear()
product.data.materials.append(charcoal)
for polygon in product.data.polygons:
    polygon.material_index = 0
# Smooth curved facets while retaining the CAD's hard corners. No geometry change.
bpy.ops.object.select_all(action="DESELECT")
product.select_set(True)
bpy.context.view_layer.objects.active = product
bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30), keep_sharp_edges=True)

# The background provides contrast through the real openings in the mesh.
bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, -0.001))
ground = bpy.context.object
ground.data.materials.append(surface("Warm studio ground", (0.58, 0.55, 0.51), 0.85))

# A render-only leather surface illustrates the bag lining through the openings.
points = []
for corner, (x, y) in enumerate(((.077, .037), (-.077, .037),
                                (-.077, -.037), (.077, -.037))):
    for step in range(17):
        angle = (corner + step/16)*math.pi/2
        points.append((x + .011*math.cos(angle), y + .011*math.sin(angle), -.0002))
mesh = bpy.data.meshes.new("Lining reference")
mesh.from_pydata(points, [], [list(range(len(points)))])
lining = bpy.data.objects.new("Lining reference - rendering only", mesh)
scene.collection.objects.link(lining)
leather = surface("Dark leather reference", (.018, .012, .009), .8)
nodes = leather.node_tree.nodes
noise = nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 550
bump = nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = .22
bump.inputs["Distance"].default_value = .00006
shader = next(node for node in nodes if node.type == "BSDF_PRINCIPLED")
leather.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
leather.node_tree.links.new(bump.outputs["Normal"], shader.inputs["Normal"])
lining.data.materials.append(leather)
scene.world = bpy.data.worlds.new("Studio world")
scene.world.use_nodes = True
background = next(node for node in scene.world.node_tree.nodes if node.type == "BACKGROUND")
background.inputs["Color"].default_value = (0.8, 0.85, 1, 1)
background.inputs["Strength"].default_value = 0.3
for location, power, size in (((-.15, -.1, .3), 4, .25),
                               ((.18, .12, .2), 3, .18),
                               ((-.08, .2, .12), 2, .12)):
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.object
    light.data.energy = power
    light.data.shape = "DISK"
    light.data.size = size
    light.rotation_euler = (-light.location).to_track_quat("-Z", "Y").to_euler()

scene.render.engine = "CYCLES"
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.view_settings.exposure = -0.7
scene.render.resolution_x = 1400
scene.render.resolution_y = 950
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
bpy.ops.object.camera_add()
camera = bpy.context.object
camera.data.type = "ORTHO"
camera.data.clip_start = .001
scene.camera = camera


def render(name, target, eye, span):
    camera.location = eye
    forward = (Vector(target) - camera.location).normalized()
    right = forward.cross(Vector((0, 1, 0))).normalized()
    up = right.cross(forward).normalized()
    camera.rotation_euler = Matrix((right, up, -forward)).transposed().to_euler()
    camera.data.ortho_scale = span
    scene.render.filepath = str(ROOT / "docs" / name)
    bpy.ops.render.render(write_still=True)


render("production-angle.png", (0, 0, .007), (.025, -.10, .32), .225)
render("production-thumb-scoop.png", (-.0302, .034, .01), (-.025, -.065, .24), .095)

# Rounded item envelopes illustrate access; they are never saved into the CAD file.
for name, dimensions, center, color in (
    ("Battery reference", (105, 67, 13), (-29.5, -12.7, 8), (.12, .17, .21)),
    ("Perfume reference", (66.4, 25.3, 16.2), (-30.2, 36.65, 9.6), (.75, .69, .54)),
    ("Touchland reference", (55, 95, 17), (55.7, 2.5, 10), (.3, .52, .4)),
):
    bpy.ops.mesh.primitive_cube_add(size=1, location=Vector(center)*.001)
    item = bpy.context.object
    item.name = name
    item.dimensions = Vector(dimensions)*.001
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = item.modifiers.new("Reference corner rounding", "BEVEL")
    bevel.width = .003
    bevel.segments = 8
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    item.data.materials.append(surface(name, color, .4))
render("production-loaded.png", (0, 0, .007), (.025, -.10, .32), .225)
