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
PERFUME_THUMB_WIDTH = 25.0
PERFUME_CHANNEL_BASE = 23.4
PERFUME_APRON_TOP = 41.0
PERFUME_FRONT_TOP = 33.7
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
               (-64, 3.6, 23.4, 46, 7), (-82, -77, 26, 43, 2.4),
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


def wall_depth(y):
    """Shared depth profile for left outer wall, divider, and right outer wall."""
    t = max(0, min((y+5)/22, 1))
    return 1.2+18.8*math.cos(t*math.pi/2)**2


def build_frame():
    frame_v2.CORNER_STEPS = 32
    perimeter = frame_v2.perimeter()
    # Preserve the fitted XY outline while rolling the open upper ends down
    # to the rear rim, instead of terminating the tall side walls abruptly.
    outline = [(-5, 25), (51, 25), (51, 1.2), (17, 1.2)]
    for i in range(1, 49):
        y = 17-22*i/48
        outline.append((y, wall_depth(y)))
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


def perfume_capsule_halves():
    rings = []
    for i in range(65):
        z = 20*i/64
        if z < 4.2:
            ymin = 26.4-4.2*math.sqrt(max(0, 1-((z-4.2)/4.2)**2))
        elif z > 15.4:
            ymin = 26.4-4.2*math.sqrt(max(0, 1-((z-15.4)/4.6)**2))
        else:
            ymin = 22.2
        radius = (PERFUME_APRON_TOP-ymin)/2-.01
        # Retain the front/rear pill silhouette while providing enough exterior
        # material around the conservative square-ended item cavity. This only
        # thickens the two lower end corners; the inner fit stays unchanged.
        face_blend = max(0, 1-z/1.2, (z-18.4)/1.6)
        bottom_radius = 3+(radius-3)*face_blend
        outline = []
        corners = ((5.6-radius, PERFUME_APRON_TOP-radius, radius),
                   (-66+radius, PERFUME_APRON_TOP-radius, radius),
                   (-66+bottom_radius, ymin+bottom_radius, bottom_radius),
                   (5.6-bottom_radius, ymin+bottom_radius, bottom_radius))
        for corner, (cx, cy, r) in enumerate(corners):
            for step in range(33):
                a = (corner+step/32)*math.pi/2
                outline.append((cx+r*math.cos(a), cy+r*math.sin(a), z))
        rings.append(outline)
    faces = [rings[0], rings[-1]]
    for first, second in zip(rings, rings[1:]):
        for i in range(len(first)):
            j = (i+1) % len(first)
            faces.append((first[i], first[j], second[j], second[i]))
    outer = frame_v2.make_mesh("Continuous pill cradle shell", faces)
    # Open through the rear: the leather supports the item, rather than a
    # second capsule-shaped back wall. An outward inner fillet softens the
    # side-to-front opening without consuming the tested item clearance.
    cut_rings = []
    for i in range(129):
        z = -3+21.4*i/128
        bottom = 23.4 if z <= 15.4 else 26.4-math.sqrt(max(0, 9-(z-15.4)**2))
        fillet = 0 if z <= 17.8 else .6-math.sqrt(max(0, .36-(z-17.8)**2))
        xmin, xmax = -64-fillet, 3.6+fillet
        cut_rings.append([(xmin, bottom, z), (xmax, bottom, z),
                          (xmax, 65, z), (xmin, 65, z)])
    faces = [cut_rings[0], cut_rings[-1]]
    for first, second in zip(cut_rings, cut_rings[1:]):
        for i in range(4):
            j = (i+1) % 4
            faces.append((first[i], first[j], second[j], second[i]))
    cavity = frame_v2.make_mesh("Perfume rounded inner cavity", faces)
    boolean(outer, cavity, "DIFFERENCE")
    bpy.data.objects.remove(cavity, do_unlink=True)
    # Lower the front mouth to the outer side rim (Y33.7 at the front plane),
    # continuing across the side caps so no raised tips remain.
    profile = [(50, -2), (50, 22), (PERFUME_FRONT_TOP, 22),
               (PERFUME_FRONT_TOP, -2)]
    cut_rings = [[(x, y, z) for y, z in profile] for x in (-70, 10)]
    faces = [cut_rings[0], cut_rings[1]]
    for i in range(len(profile)):
        j = (i+1) % len(profile)
        faces.append((cut_rings[0][i], cut_rings[0][j], cut_rings[1][j], cut_rings[1][i]))
    trim = frame_v2.make_mesh("Lower flowing perfume front rim", faces)
    boolean(outer, trim, "DIFFERENCE")
    bpy.data.objects.remove(trim, do_unlink=True)
    halves = []
    for name, xmin, xmax in (("Perfume left pill cradle", -70, PERFUME_CENTER_X-PERFUME_THUMB_WIDTH/2),
                            ("Perfume right pill cradle", PERFUME_CENTER_X+PERFUME_THUMB_WIDTH/2, 10)):
        half = outer.copy()
        half.data = outer.data.copy()
        bpy.context.scene.collection.objects.link(half)
        half.name = name
        trim = box("Half shell trim", (xmin, 15, -1), (xmax, 50, 22))
        boolean(half, trim, "INTERSECT")
        bpy.data.objects.remove(trim, do_unlink=True)
        # Soften the exposed central cut and lowered mouth rim locally.
        cut_x = xmax if "left" in name else xmin
        bm = bmesh.new()
        bm.from_mesh(half.data)
        weights = bm.edges.layers.float.new("bevel_weight_edge")
        for edge in bm.edges:
            if edge.is_manifold and (all(abs(v.co.x-cut_x) < 1e-4 for v in edge.verts) or
                                     all(abs(v.co.y-PERFUME_FRONT_TOP) < 1e-4 for v in edge.verts)):
                if edge.calc_face_angle() > .15:
                    edge[weights] = 1
        bm.to_mesh(half.data)
        bm.free()
        bpy.context.view_layer.objects.active = half
        bevel = half.modifiers.new("Soft thumb contact rim", "BEVEL")
        bevel.limit_method = "WEIGHT"
        bevel.width = .35
        bevel.segments = 4
        bpy.ops.object.modifier_apply(modifier=bevel.name)
        halves.append(half)
    bpy.data.objects.remove(outer, do_unlink=True)
    return halves


def straight_divider():
    # Straight in XY all the way to the frame bottom, with no front return.
    outline = [(-48, 0), (17, 0)]
    for i in range(97):
        y = 17-65*i/96
        outline.append((y, wall_depth(y)))
    rings = [[(x, y, z) for y, z in outline] for x in (24.6, 26.6)]
    faces = [rings[0], rings[1]]
    for i in range(len(outline)):
        j = (i+1) % len(outline)
        faces.append((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
    obj = frame_v2.make_mesh("Straight thin divider", faces)
    bpy.context.view_layer.objects.active = obj
    bevel = obj.modifiers.new("Soft divider contact edges", "BEVEL")
    bevel.width = .35
    bevel.segments = 4
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    return obj


def build_organizer():
    return [straight_divider(), *perfume_capsule_halves()]


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
          PERFUME_CHANNEL_BASE, "front top Y", PERFUME_FRONT_TOP)


if __name__ == "__main__":
    build()
