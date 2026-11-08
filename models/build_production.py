"""Build the fitted production tray with editable frame and pocket sources.

Run with Blender 5.1 in background mode. Coordinates and exports use mm.
X runs across the bag, Y points upward, and Z points away from the leather.
"""
from pathlib import Path
import math
import sys

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "models"))
import frame_v2

BACK_THICKNESS = 1.2
ITEM_BACK = 1.5
PERFUME_CENTER_X = -30.2
PERFUME_THUMB_WIDTH = 32.0
PERFUME_THUMB_BOTTOM = 27.0
PERFUME_CHANNEL_BASE = 23.4
PERFUME_APRON_TOP = 39.0
ITEMS = (
    ("Anker 622", (105.0, 67.0, 13.0), (-29.5, -12.7)),
    ("Perfume", (66.4, 25.3, 16.2), (-30.2, 36.65)),
    ("Touchland", (55.0, 95.0, 17.0), (55.7, 2.5)),
)


def box(name, low, high, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.object
    obj.name = name
    obj.location = (Vector(low) + Vector(high)) / 2
    obj.dimensions = Vector(high) - Vector(low)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Soft contact edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 4
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    return obj


def rounded_rectangle(xmin, xmax, ymin, ymax, radius, steps=16):
    points = []
    corners = ((xmax-radius, ymax-radius), (xmin+radius, ymax-radius),
               (xmin+radius, ymin+radius), (xmax-radius, ymin+radius))
    for corner, (x, y) in enumerate(corners):
        for step in range(steps+1):
            angle = (corner + step/steps) * math.pi/2
            points.append((x + radius*math.cos(angle), y + radius*math.sin(angle)))
    return points


def extrude_xy(name, outline, low, high):
    rings = [[(x, y, z) for x, y in outline] for z in (low, high)]
    faces = [rings[0], rings[1]]
    for i in range(len(outline)):
        j = (i+1) % len(outline)
        faces.append((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
    return frame_v2.make_mesh(name, faces)


def boolean(target, other, operation="UNION"):
    bpy.context.view_layer.objects.active = target
    modifier = target.modifiers.new(operation.title(), "BOOLEAN")
    modifier.operation = operation
    modifier.solver = "MANIFOLD"
    modifier.object = other
    bpy.ops.object.modifier_apply(modifier=modifier.name)


def make_backing():
    backing = extrude_xy("Shared backing with three leather windows",
                         rounded_rectangle(-87, 87, -47, 47, 8), 0, BACK_THICKNESS)
    windows = [(-76, 18, -40, 15, 7), (32, 79, -40, 42, 7),
               (-59, -1, 27, 44, 5), (-82, -77, 26, 43, 2.4),
               (-73, -68, 26, 43, 2.4), (10, 15, 26, 43, 2.4),
               (19, 24, 26, 43, 2.4)]
    for bounds in windows:
        cutter = extrude_xy("Leather window cutter", rounded_rectangle(*bounds), -1, 3)
        boolean(backing, cutter, "DIFFERENCE")
        bpy.data.objects.remove(cutter, do_unlink=True)
    return backing


def pocket_ring(name, inner, outer, height):
    """A continuous rounded pocket wall with a rounded, variable-depth rim."""
    inner_points = rounded_rectangle(*inner, steps=24)
    outer_points = rounded_rectangle(*outer, steps=24)
    lower_inner = [(x, y, 0) for x, y in inner_points]
    lower_outer = [(x, y, 0) for x, y in outer_points]
    upper_inner = [(x, y, height(y)) for x, y in inner_points]
    upper_outer = [(x, y, height(y)) for x, y in outer_points]
    faces = []
    for i in range(len(inner_points)):
        j = (i+1) % len(inner_points)
        faces.extend(((lower_inner[i], lower_inner[j], upper_inner[j], upper_inner[i]),
                      (lower_outer[i], lower_outer[j], upper_outer[j], upper_outer[i]),
                      (lower_inner[i], lower_inner[j], lower_outer[j], lower_outer[i]),
                      (upper_inner[i], upper_inner[j], upper_outer[j], upper_outer[i])))
    obj = frame_v2.make_mesh(name, faces)
    bpy.context.view_layer.objects.active = obj
    bevel = obj.modifiers.new("Rounded pocket mouth", "BEVEL")
    bevel.width = .35
    bevel.segments = 4
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    return obj


def open_top_height(y, start, end, depth):
    t = max(0, min((y-start)/(end-start), 1))
    return (BACK_THICKNESS + .02) + (depth-BACK_THICKNESS-.02)*math.cos(t*math.pi/2)**2


def junction_fill():
    """Continuous outer junctions, with all three access cavities kept clear."""
    obj = extrude_xy("Continuous sculpted pocket junctions",
                     rounded_rectangle(-88, 88, -48, 48, 9, 32), 1.0, 19.8)
    cavities = [(-82.6, 23.6, -47.6, 65, 4.6),
                (-64, 3.6, 23.4, 65, .6),
                (27.6, 83.8, -45.3, 65, 6.6),
                (-82, -77, 26, 65, 2.4), (-73, -68, 26, 65, 2.4),
                (10, 15, 26, 65, 2.4), (19, 24, 26, 65, 2.4)]
    for bounds in cavities:
        xmin, xmax, ymin, ymax, radius = bounds
        cutter = extrude_xy("Junction cavity cutter", rounded_rectangle(
            xmin-.02, xmax+.02, ymin-.02, ymax+.02, radius+.02, steps=24), -1, 22)
        boolean(obj, cutter, "DIFFERENCE")
        bpy.data.objects.remove(cutter, do_unlink=True)
    return obj


def scallop(x, center, width, low, high):
    t = min(abs(x-center)/(width/2), 1)
    return low + (high-low)*math.sin(t*math.pi/2)**2


def apron(name, xmin, xmax, bottom, front, radius, rear_top, top_function):
    """Loft a smooth open U section across X with a scalloped front mouth."""
    rear = BACK_THICKNESS
    thickness = 1.2

    def section(top):
        lip_radius = 0.35
        def path(offset):
            r = radius + offset
            points = [(rear_top, rear-offset)]
            for i in range(17):
                angle = math.pi + i*math.pi/32
                points.append((bottom+radius+r*math.sin(angle),
                               rear+radius+r*math.cos(angle)))
            for i in range(17):
                angle = 1.5*math.pi + i*math.pi/32
                points.append((bottom+radius+r*math.sin(angle),
                               front-radius+r*math.cos(angle)))
            points.append((top-lip_radius, front+offset))
            return points
        lip = []
        for i in range(1, 9):
            angle = i*math.pi/16
            lip.append((top-lip_radius+lip_radius*math.sin(angle),
                        front+thickness-lip_radius+lip_radius*math.cos(angle)))
        lip.append((top, front+lip_radius))
        for i in range(1, 8):
            angle = math.pi/2+i*math.pi/16
            lip.append((top-lip_radius+lip_radius*math.sin(angle),
                        front+lip_radius+lip_radius*math.cos(angle)))
        return path(thickness) + lip + list(reversed(path(0)))

    rings = []
    for i in range(97):
        x = xmin + (xmax-xmin)*i/96
        rings.append([(x, y, z) for y, z in section(top_function(x))])
    faces = [rings[0], rings[-1]]
    for first, second in zip(rings, rings[1:]):
        for i in range(len(first)):
            j = (i+1) % len(first)
            faces.append((first[i], first[j], second[j], second[i]))
    return frame_v2.make_mesh(name, faces)


def front_curb(name, xmin, xmax, ymin, zmin, zmax, top_function):
    outline = [(xmin, ymin), (xmax, ymin)]
    outline += [(xmax-(xmax-xmin)*i/96, top_function(xmax-(xmax-xmin)*i/96))
                for i in range(97)]
    return extrude_xy(name, outline, zmin, zmax)


def build_frame():
    frame_v2.CORNER_STEPS = 32
    perimeter = frame_v2.perimeter()
    bpy.context.view_layer.objects.active = perimeter
    bevel = perimeter.modifiers.new("Rounded perimeter edges", "BEVEL")
    bevel.width = .2
    bevel.segments = 4
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    return [perimeter, make_backing()]


def build_organizer():
    parts = [
        pocket_ring("Rounded battery well", (-82.6, 23.6, -47.6, 22.2, 4.6),
                    (-84.2, 25.2, -49.2, 23.8, 6.2), lambda y: 15.7),
        box("Battery side web blended into frame", (-88, -39, 0), (-82.6, 17.6, 15.7), .7),
        box("Shared curved-pocket divider web", (23.6, -39, 0), (27.6, 17.6, 19.9), .7),
        front_curb("Battery curved lower curb", -82.6, 23.6, -48, 14.9, 16.1,
                   lambda x: scallop(x, -29.5, 54, -46.4, -45.2)),
        box("Perfume elevated ledge", (-65.2, 22.2, 0), (4.8, 23.4, 19.6), .2),
        pocket_ring("Rounded perfume pocket", (-64, 3.6, 23.4, 47.2, .6),
                    (-67, 6.6, 22.2, 48.4, 3),
                    lambda y: open_top_height(y, 39, 43, 19.6)),
        apron("Perfume saddle with central thumb scoop", -65.2, 4.8, 23.4, 18.4, 3,
              28.0, lambda x: scallop(x, PERFUME_CENTER_X, PERFUME_THUMB_WIDTH,
                                      PERFUME_THUMB_BOTTOM, PERFUME_APRON_TOP)),
        pocket_ring("Rounded Touchland well", (27.6, 83.8, -45.3, 47.2, 6.6),
                    (26.4, 85, -46.5, 48.4, 7.8),
                    lambda y: open_top_height(y, 25, 39, 20)),
        box("Touchland side web blended into frame", (83.8, -38.7, 0), (88, 25, 19.9), .55),
        box("Touchland lower ledge", (26.4, -46.5, 0), (81, -45.3, 19.9), .2),
        apron("Touchland sculpted lower pocket", 27.4, 84.0, -45.3, 18.8, .8,
              -42.0, lambda x: scallop(x, 55.7, 35, -33, -23)),
    ]
    # Carry the bottle's rounded outline through the lower apron and ledge.
    trim = extrude_xy("Touchland outer profile trim",
                      rounded_rectangle(26.4, 85, -46.5, 48.4, 7.8), -1, 21)
    for part in parts[-2:]:
        boolean(part, trim, "INTERSECT")
    bpy.data.objects.remove(trim, do_unlink=True)
    parts.append(junction_fill())
    thumb = extrude_xy("Full-depth perfume thumb channel",
                       rounded_rectangle(PERFUME_CENTER_X-PERFUME_THUMB_WIDTH/2,
                                         PERFUME_CENTER_X+PERFUME_THUMB_WIDTH/2,
                                         PERFUME_CHANNEL_BASE, 55, 3), 1.2, 22)
    boolean(parts[6], thumb, "DIFFERENCE")
    bpy.data.objects.remove(thumb, do_unlink=True)
    # Junction solid replaces redundant nested rings and separate side webs.
    # Battery has no upper crossbar; only the independent perfume shelf remains.
    removed = {0, 1, 2, 7, 8}
    for index in removed:
        bpy.data.objects.remove(parts[index], do_unlink=True)
    return [part for index, part in enumerate(parts) if index not in removed]


def move_to(obj, collection):
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)


def clean_mesh(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-5)
    bmesh.ops.dissolve_limit(bm, angle_limit=1e-5, verts=list(bm.verts),
                             edges=list(bm.edges), use_dissolve_boundaries=False)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=list(bm.edges))
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def check_mesh(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    assert all(edge.is_manifold for edge in bm.edges), f"{obj.name}: open/non-manifold edges"
    # Blender's float32 area cancellation can report zero for tiny valid slivers.
    # Compute triangle cross products in Python float64 for this validation.
    def precise_area(face):
        a, b, c = [tuple(v.co) for v in face.verts]
        u = [b[i]-a[i] for i in range(3)]
        v = [c[i]-a[i] for i in range(3)]
        cross = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
        return math.sqrt(sum(value*value for value in cross))/2
    assert all(precise_area(face) > 1e-12 for face in bm.faces), f"{obj.name}: degenerate faces"
    assert bm.calc_volume(signed=True) > 0, f"{obj.name}: invalid volume"
    remaining = set(bm.verts)
    count = 0
    while remaining:
        count += 1
        pending = [remaining.pop()]
        while pending:
            vertex = pending.pop()
            for edge in vertex.link_edges:
                neighbor = edge.other_vert(vertex)
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    pending.append(neighbor)
    assert count == 1, f"{obj.name}: {count} disconnected bodies"
    volume = bm.calc_volume()
    bm.free()
    return volume


def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    return mat


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = .001
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_cavity = True
    frame_mat = material("Charcoal frame", (.105, .12, .13))
    organizer_mat = material("Charcoal pockets", (.105, .12, .13))
    groups = (("FRAME - editable sources", build_frame(), frame_mat),
              ("ORGANIZER - editable sources", build_organizer(), organizer_mat))
    copies = []
    for name, parts, mat in groups:
        collection = bpy.data.collections.new(name)
        scene.collection.children.link(collection)
        for source in parts:
            bm = bmesh.new()
            bm.from_mesh(source.data)
            bmesh.ops.triangulate(bm, faces=list(bm.faces))
            bm.to_mesh(source.data)
            bm.free()
            source.data.materials.append(mat)
            move_to(source, collection)
            duplicate = source.copy()
            duplicate.data = source.data.copy()
            scene.collection.objects.link(duplicate)
            copies.append(duplicate)

    result = copies[0]
    for other in copies[1:]:
        boolean(result, other)
        bpy.data.objects.remove(other, do_unlink=True)
    result.name = "PRINT - production organizer"
    clean_mesh(result)
    volume = check_mesh(result)
    for collection in scene.collection.children:
        if "editable sources" in collection.name:
            collection.hide_render = True
            collection.hide_viewport = True
    bpy.ops.object.select_all(action="DESELECT")
    result.select_set(True)
    bpy.context.view_layer.objects.active = result
    stl_path = str(ROOT / "models/rimowa-production.stl")
    bpy.ops.wm.stl_export(filepath=stl_path, export_selected_objects=True, apply_modifiers=True)
    bpy.ops.wm.stl_import(filepath=stl_path)
    imported = bpy.context.object
    assert math.isclose(check_mesh(imported), volume, rel_tol=1e-6)
    assert (imported.dimensions-result.dimensions).length < 1e-4
    bpy.data.objects.remove(imported, do_unlink=True)
    bpy.context.view_layer.objects.active = result
    result.select_set(True)

    references = bpy.data.collections.new("ITEMS - hidden references")
    scene.collection.children.link(references)
    for name, size, center in ITEMS:
        w, h, depth = size
        x, y = center
        item = box(name, (x-w/2, y-h/2, ITEM_BACK),
                   (x+w/2, y+h/2, ITEM_BACK+depth))
        item.display_type = "WIRE"
        move_to(item, references)
    references.hide_render = True
    references.hide_viewport = True
    bpy.ops.object.select_all(action="DESELECT")
    result.select_set(True)
    bpy.context.view_layer.objects.active = result
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_distance = 240
                area.spaces.active.region_3d.view_location = (0, 0, 8)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "models/rimowa-production.blend"))
    print("PRODUCTION VERIFIED", tuple(round(d, 4) for d in result.dimensions),
          "volume mm3", round(volume, 2), "triangles", len(result.data.polygons))
    print("PERFUME THUMB CHANNEL", PERFUME_THUMB_WIDTH, "mm mouth, shelf Y",
          PERFUME_CHANNEL_BASE, "side top Y", PERFUME_APRON_TOP)


if __name__ == "__main__":
    build()
