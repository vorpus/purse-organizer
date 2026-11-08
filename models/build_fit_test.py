"""Generate a shallow rounded perimeter with an inward pull tab in Blender."""
import argparse
import math
from pathlib import Path
import sys

import bmesh
import bpy


def outline(width, height, radius, tab=False):
    points = []
    corners = [
        (width / 2 - radius, height / 2 - radius),
        (-width / 2 + radius, height / 2 - radius),
        (-width / 2 + radius, -height / 2 + radius),
        (width / 2 - radius, -height / 2 + radius),
    ]
    for corner, (x, y) in enumerate(corners):
        for step in range(17):
            angle = (corner + step / 16) * math.pi / 2
            points.append((x + radius * math.cos(angle), y + radius * math.sin(angle)))
        if corner == 0:
            for step in range(13):
                x = 11 - step * 22 / 12
                inset = 7 * math.cos(math.pi * x / 22) ** 2 if tab else 0
                points.append((x, height / 2 - inset))
    return points


parser = argparse.ArgumentParser()
parser.add_argument("--width", type=float, default=182, help="Inside long dimension, mm")
parser.add_argument("--height", type=float, default=102, help="Inside short dimension, mm")
parser.add_argument("--clearance", type=float, default=1, help="Clearance per side, mm")
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])

wall = 2.4
depth = 3
radius = 12 - args.clearance
width = args.width - 2 * args.clearance
height = args.height - 2 * args.clearance
if not (
    all(math.isfinite(x) for x in (width, height, args.clearance))
    and 0 <= args.clearance < 12 - wall
    and width / 2 - radius > 11
    and height / 2 > radius + 7
):
    parser.error("Dimensions and clearance must leave space for the corners and pull tab.")

outer = outline(width, height, radius)
inner = outline(width - 2 * wall, height - 2 * wall, radius - wall, tab=True)
count = len(outer)
vertices = [(x, y, z) for z in (0, depth) for loop in (outer, inner) for x, y in loop]
faces = []
for i in range(count):
    j = (i + 1) % count
    faces.extend([
        (i, j, j + 2 * count, i + 2 * count),
        (i + count, i + 3 * count, j + 3 * count, j + count),
        (i, i + count, j + count, j),
        (i + 2 * count, j + 2 * count, j + 3 * count, i + 3 * count),
    ])

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 0.001
mesh = bpy.data.meshes.new("Perimeter")
mesh.from_pydata(vertices, [], faces)
mesh.update()
frame = bpy.data.objects.new("Rimowa fit test", mesh)
scene.collection.objects.link(frame)
bpy.context.view_layer.objects.active = frame
frame.select_set(True)

bevel = frame.modifiers.new("Rounded edges", "BEVEL")
bevel.width = 0.45
bevel.segments = 4
bpy.ops.object.modifier_apply(modifier=bevel.name)

bm = bmesh.new()
bm.from_mesh(frame.data)
assert all(edge.is_manifold for edge in bm.edges), "Frame has non-manifold edges"
assert bm.calc_volume(signed=True) > 0, "Frame must enclose a positive volume"
assert all(face.calc_area() > 0 for face in bm.faces), "Frame has degenerate faces"
bm.free()
print("Frame extents in mm:", tuple(round(d, 3) for d in frame.dimensions))

for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == "VIEW_3D":
            view = area.spaces.active.region_3d
            view.view_distance = 235
            view.view_location = (0, 0, 0)

output = Path(__file__).resolve().parent
bpy.ops.wm.save_as_mainfile(filepath=str(output / "rimowa-fit-test.blend"))
bpy.ops.wm.stl_export(filepath=str(output / "rimowa-fit-test.stl"),
                      export_selected_objects=True, apply_modifiers=True)
