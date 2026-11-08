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
    thumb = extrude_xy("Backing opening under perfume thumb gap",
                       rounded_rectangle(PERFUME_CENTER_X-PERFUME_THUMB_WIDTH/2,
                                         PERFUME_CENTER_X+PERFUME_THUMB_WIDTH/2,
                                         20.8, 45, 3), -1, 3)
    boolean(backing, thumb, "DIFFERENCE")
    bpy.data.objects.remove(thumb, do_unlink=True)
    return backing


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
    # Preserve the fitted XY outline while rolling the open upper ends down
    # to the rear rim, instead of terminating the tall side walls abruptly.
    outline = [(31, 25), (51, 25), (51, 1.2), (39, 1.2)]
    for i in range(1, 49):
        y = 39-8*i/48
        t = (y-31)/8
        outline.append((y, 1.2+18.8*math.cos(t*math.pi/2)**2))
    rings = [[(x, y, z) for y, z in outline] for x in (-95, 95)]
    faces = [rings[0], rings[1]]
    for i in range(len(outline)):
        j = (i+1) % len(outline)
        faces.append((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
    cutter = frame_v2.make_mesh("Upper side termination roll-off", faces)
    boolean(perimeter, cutter, "DIFFERENCE")
    bpy.data.objects.remove(cutter, do_unlink=True)
    bpy.context.view_layer.objects.active = perimeter
    bevel = perimeter.modifiers.new("Rounded perimeter edges", "BEVEL")
    bevel.width = .2
    bevel.segments = 4
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    return [perimeter, make_backing()]


def rounded_end_cap(name, xmin, xmax):
    outline = rounded_rectangle(22.2, 39, 0, 19.6, 6, 32)
    rings = [[(x, y, z) for y, z in outline] for x in (xmin, xmax)]
    faces = [rings[0], rings[1]]
    for i in range(len(outline)):
        j = (i+1) % len(outline)
        faces.append((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
    obj = frame_v2.make_mesh(name, faces)
    bpy.context.view_layer.objects.active = obj
    bevel = obj.modifiers.new("Rolled end contact edges", "BEVEL")
    bevel.width = .65
    bevel.segments = 6
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    return obj


def tapered_divider():
    outline = [(-46, 0), (17, 0)]
    for i in range(97):
        y = 17-63*i/96
        t = max(0, min((y+5)/22, 1))
        depth = 1.2+18.3*math.cos(t*math.pi/2)**2
        outline.append((y, depth))
    rings = [[(x, y, z) for y, z in outline] for x in (24.6, 26.6)]
    faces = [rings[0], rings[1]]
    for i in range(len(outline)):
        j = (i+1) % len(outline)
        faces.append((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
    obj = frame_v2.make_mesh("Single thin flowing divider", faces)
    bpy.context.view_layer.objects.active = obj
    bevel = obj.modifiers.new("Rounded divider contact edges", "BEVEL")
    bevel.width = .65
    bevel.segments = 6
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    return obj


def build_organizer():
    left_edge = PERFUME_CENTER_X-PERFUME_THUMB_WIDTH/2
    right_edge = PERFUME_CENTER_X+PERFUME_THUMB_WIDTH/2
    def cup_top(x, edge, outer):
        t = min(abs(x-edge)/abs(outer-edge), 1)
        return PERFUME_THUMB_BOTTOM+(PERFUME_APRON_TOP-PERFUME_THUMB_BOTTOM)*math.sin(t*math.pi/2)**2
    parts = [
        tapered_divider(),
        front_curb("Low battery front curb", -83.2, 24.8, -48, 14.9, 16.1,
                   lambda x: scallop(x, -29.5, 54, -46.4, -45.2)),
        apron("Perfume left curved end cradle", -65.2, left_edge, 23.4, 18.4, 3,
              28, lambda x: cup_top(x, left_edge, -64)),
        apron("Perfume right curved end cradle", right_edge, 4.8, 23.4, 18.4, 3,
              28, lambda x: cup_top(x, right_edge, 3.6)),
        rounded_end_cap("Perfume rounded left capsule end", -66, -64),
        rounded_end_cap("Perfume rounded right capsule end", 3.6, 5.6),
        apron("Touchland low curved front lip", 26.4, 86, -45.3, 18.8, .8,
              -42, lambda x: scallop(x, 55.7, 38, -39, -32)),
    ]
    trim = extrude_xy("Touchland rounded lower silhouette",
                      rounded_rectangle(26.4, 86, -46.5, 48.4, 8.0), -1, 21)
    boolean(parts[-1], trim, "INTERSECT")
    bpy.data.objects.remove(trim, do_unlink=True)
    # Sculpt each whole end cradle rather than stacking a plate on a cap.
    for cup, cap, xmin, xmax in ((parts[2], parts[4], -65.2, left_edge),
                                (parts[3], parts[5], right_edge, 4.8)):
        boolean(cup, cap)
        trim = extrude_xy("Capsule plan silhouette",
                          rounded_rectangle(-66, 5.6, 22.2, 39, 4, 32), -1, 22)
        boolean(cup, trim, "INTERSECT")
        bpy.data.objects.remove(trim, do_unlink=True)
        outline = rounded_rectangle(-66, 5.6, 0, 19.6, 3, 32)
        rings = [[(x, y, z) for x, z in outline] for y in (15, 50)]
        faces = [rings[0], rings[1]]
        for i in range(len(outline)):
            j = (i+1) % len(outline)
            faces.append((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
        trim = frame_v2.make_mesh("Rounded capsule front-end wrap", faces)
        boolean(cup, trim, "INTERSECT")
        bpy.data.objects.remove(trim, do_unlink=True)
        for vertex in cup.data.vertices:
            t = max(0, min((vertex.co.x-xmin)/(xmax-xmin), 1))
            front_factor = max(0, min((vertex.co.z-15.4)/3, 1))
            vertex.co.z += .4*math.sin(t*math.pi)**2*front_factor
        cup.data.update()
    bpy.data.objects.remove(parts[4], do_unlink=True)
    bpy.data.objects.remove(parts[5], do_unlink=True)
    parts = [part for index, part in enumerate(parts) if index not in (4, 5)]
    return parts


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
    print("PERFUME THUMB CHANNEL", PERFUME_THUMB_WIDTH, "mm clear through floor; end seats Y",
          PERFUME_CHANNEL_BASE, "side top Y", PERFUME_APRON_TOP)


if __name__ == "__main__":
    build()
