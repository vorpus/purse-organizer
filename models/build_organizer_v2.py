"""Build one printable organizer while preserving separate frame/holder sources."""
from pathlib import Path
import sys
import math

import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "models"))
import frame_v2

# Millimeters. Upright bag coordinates: X across, Y up, Z away from leather.
BATTERY = (105.0, 67.0, 13.0)
PERFUME = (66.4, 25.3, 16.2)
TOUCHLAND = (55.0, 95.0, 17.0)
ITEM_BACK = 1.5


def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    return mat


def box(name, low, high):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.object
    obj.name = name
    obj.location = (Vector(low) + Vector(high)) / 2
    obj.dimensions = Vector(high) - Vector(low)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def cuff(name, x, bottom, top, front, width=4.8, radius=3.0):
    """Rounded U section, open upward, with 1.2 mm walls and a 3 mm seat radius."""
    inner_rear = 1.2
    thickness = 1.2
    # Trace rear upper end, lower rear quarter, floor, lower front quarter, upper front.
    def path(offset):
        rear = inner_rear - offset
        forward = front + offset
        r = radius + offset
        points = [(top, rear)]
        for step in range(9):
            angle = math.pi + step * math.pi / 16
            points.append((bottom + radius + r * math.sin(angle),
                           inner_rear + radius + r * math.cos(angle)))
        for step in range(9):
            angle = 1.5 * math.pi + step * math.pi / 16
            points.append((bottom + radius + r * math.sin(angle),
                           front - radius + r * math.cos(angle)))
        points.append((top, forward))
        return points
    section = path(thickness) + list(reversed(path(0)))
    n = len(section)
    faces = []
    rings = [[(xx, y, z) for y, z in section] for xx in (x-width/2, x+width/2)]
    faces.extend(rings)
    for i in range(n):
        j = (i+1) % n
        faces.append((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
    return frame_v2.make_mesh(name, faces)


def build_organizer():
    parts = []
    def add(name, low, high):
        parts.append(box(name, low, high))
    # Battery rests on a shallow foot, tilts forward, then lifts clear.
    add("Battery foot", (-84, -46.5, 0), (25.2, -45.3, 16.1))
    add("Battery front stop", (-78, -45.4, 14.9), (19, -42.5, 16.1))
    for y in (-35, 10):
        add("Battery back tie", (-84, y-4, 0), (25.2, y+4, 1.2))
        for x in (-83.8, 23.6):
            add("Battery side guide", (x, y-4, 0), (x+1.2, y+4, 15.7))

    # Perfume lower cradle follows smooth corner curves; end guides restrain X.
    # The top stays open for upward extraction. Two front straps restrain Z.
    add("Perfume shelf", (-65.2, 22.2, 0), (4.8, 23.4, 19.6))
    add("Perfume back tie", (-65.2, 30, 0), (4.8, 35, 1.2))
    for x in (-49, -14):
        parts.append(cuff("Perfume rounded cradle", x, 23.4, 39, 18.4))
    for x in (-65.2, 3.6):
        add("Perfume end guide", (x, 22.2, 0), (x+1.2, 39, 19.6))

    # Upright Touchland. Short guides leave the spray head unobstructed.
    add("Touchland foot", (26.4, -46.5, 0), (81, -45.3, 19.9))
    for y in (-35, 5):
        add("Touchland back tie", (26.4, y-4, 0), (85, y+4, 1.2))
        for x in (26.4, 83.8):
            add("Touchland side guide", (x, y-4, 0), (x+1.2, y+4, 19.9))
    for x in (42, 70):
        parts.append(cuff("Touchland rounded cradle", x, -45.3, -30, 18.8, radius=0.8))
    return parts


def move_to(obj, collection):
    for previous in list(obj.users_collection):
        previous.objects.unlink(obj)
    collection.objects.link(obj)


def check_mesh(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    assert all(edge.is_manifold for edge in bm.edges), "Non-manifold result"
    assert all(face.calc_area() > 1e-10 for face in bm.faces), "Degenerate face"
    assert bm.calc_volume(signed=True) > 0
    unseen = set(bm.verts)
    components = 0
    while unseen:
        components += 1
        pending = [unseen.pop()]
        while pending:
            vertex = pending.pop()
            for edge in vertex.link_edges:
                other = edge.other_vert(vertex)
                if other in unseen:
                    unseen.remove(other)
                    pending.append(other)
    assert components == 1, f"Found {components} disconnected pieces"
    volume = bm.calc_volume()
    bm.free()
    return volume


bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 0.001
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = "BOTH"
scene.display.shading.background_type = "WORLD"
scene.world = bpy.data.worlds.new("Background")
scene.world.color = (0.18, 0.18, 0.18)
frame_color = material("Reusable frame", (.25, .43, .51))
holder_color = material("Item holders", (.71, .49, .28))
frame_parts = frame_v2.build_frame()
holder_parts = build_organizer()
for name, parts, mat in (("FRAME - editable sources", frame_parts, frame_color),
                         ("ORGANIZER - editable sources", holder_parts, holder_color)):
    collection = bpy.data.collections.new(name)
    scene.collection.children.link(collection)
    for part in parts:
        move_to(part, collection)
        part.data.materials.append(mat)

# Union manifold copies, retaining editable source geometry.
copies = []
for source in frame_parts + holder_parts:
    duplicate = source.copy()
    duplicate.data = source.data.copy()
    scene.collection.objects.link(duplicate)
    copies.append(duplicate)
result = copies[0]
bpy.context.view_layer.objects.active = result
for other in copies[1:]:
    modifier = result.modifiers.new("Join solids", "BOOLEAN")
    modifier.operation = "UNION"
    modifier.solver = "MANIFOLD"
    modifier.object = other
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(other, do_unlink=True)
result.name = "PRINT - single connected organizer"
# Weld coincident Boolean vertices before triangulating for STL export.
bm = bmesh.new()
bm.from_mesh(result.data)
bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-5)
bmesh.ops.triangulate(bm, faces=list(bm.faces))
bm.to_mesh(result.data)
bm.free()
volume = check_mesh(result)
for collection in list(scene.collection.children):
    if "editable sources" in collection.name:
        collection.hide_render = True
        collection.hide_viewport = True
bpy.ops.object.select_all(action="DESELECT")
result.select_set(True)
bpy.context.view_layer.objects.active = result
stl_path = str(ROOT / "models/rimowa-organizer-v2.stl")
bpy.ops.wm.stl_export(filepath=stl_path, export_selected_objects=True, apply_modifiers=True)
bpy.ops.wm.stl_import(filepath=stl_path)
round_trip = bpy.context.object
assert math.isclose(check_mesh(round_trip), volume, rel_tol=1e-6), "STL volume changed"
assert (round_trip.dimensions - result.dimensions).length < 1e-4, "STL dimensions changed"
bpy.data.objects.remove(round_trip, do_unlink=True)
result.select_set(True)
bpy.context.view_layer.objects.active = result
print("V2 checked", tuple(round(d, 3) for d in result.dimensions), "volume mm3", round(volume))

bpy.ops.object.camera_add()
camera = bpy.context.object
scene.camera = camera
camera.data.type = "ORTHO"
camera.data.ortho_scale = 245
scene.render.resolution_x = 1200
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
for name, direction in (("front", (0, 0, 1)), ("angle", (0.35, -0.65, 1.4))):
    d = Vector(direction)
    camera.location = Vector((0, 0, 8)) + d * 300
    camera.rotation_euler = (0, 0, 0) if name == "front" else (-d).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(ROOT / f"docs/organizer-v2-{name}.png")
    bpy.ops.render.render(write_still=True)

references = bpy.data.collections.new("ITEMS - measured envelopes, hidden")
scene.collection.children.link(references)
for name, size, location in (
    ("Anker 622", BATTERY, (-29.5, -11.5)),
    ("Perfume", PERFUME, (-30.2, 36.65)),
    ("Touchland", TOUCHLAND, (55.7, 2.5)),
):
    x, y = location
    w, h, depth = size
    item = box(name, (x-w/2, y-h/2, ITEM_BACK), (x+w/2, y+h/2, ITEM_BACK+depth))
    item.display_type = "WIRE"
    move_to(item, references)
references.hide_render = True
references.hide_viewport = True
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == "VIEW_3D":
            area.spaces.active.region_3d.view_distance = 240
            area.spaces.active.region_3d.view_location = (0, 0, 8)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "models/rimowa-organizer-v2.blend"))
