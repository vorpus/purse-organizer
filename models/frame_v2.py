"""Build the tapered V2 perimeter and open back lattice in millimeters."""
from math import cos, pi, sin

import bmesh
import bpy
from mathutils import Vector


BACK_THICKNESS = 1.2
TAPER_END = 5.0
FRAME_DEPTH = 20.0
RAIL_WIDTH = 2.4
REAR_INSET = 2.0
CORNER_STEPS = 8
SIDE_WINDOW_WIDTH = 0.0


def perimeter_cells():
    """Return consecutive plan segments with optional window widths."""
    cells = []
    nodes = []
    for corner, (x, y) in enumerate(((79, 39), (79, -39), (-79, -39), (-79, 39))):
        start = (1 - corner) * pi / 2
        arc = [
            (x, y, cos(start - step * pi / (2 * CORNER_STEPS)), sin(start - step * pi / (2 * CORNER_STEPS)))
            for step in range(CORNER_STEPS + 1)
        ]
        if nodes:
            previous = nodes[-1]
            count = (5, 9, 5)[corner - 1]
            for step in range(1, count):
                fraction = step / count
                nodes.append(tuple(a + (b - a) * fraction for a, b in zip(previous, arc[0])))
                cells.append((nodes[-2], nodes[-1], SIDE_WINDOW_WIDTH if corner != 2 else 0.0))
            cells.append((nodes[-1], arc[0], SIDE_WINDOW_WIDTH if corner != 2 else 0.0))
        nodes.extend(arc)
        cells.extend((a, b, 0.0) for a, b in zip(arc, arc[1:]))
    cells.append((nodes[-1], nodes[0], 0.0))
    return cells


def wall_point(node, z, inner=False):
    x, y, dx, dy = node
    inset = REAR_INSET * max(0.0, 1.0 - z / TAPER_END)
    radius = 11.0 - inset - (RAIL_WIDTH if inner else 0.0)
    return (x + radius * dx, y + radius * dy, z)


def make_mesh(name, polygons):
    vertices = []
    indices = {}
    faces = []
    for polygon in polygons:
        face = []
        for point in polygon:
            key = tuple(round(component, 6) for component in point)
            if key not in indices:
                indices[key] = len(vertices)
                vertices.append(key)
            face.append(indices[key])
        faces.append(face)

    bm = bmesh.new()
    verts = [bm.verts.new(point) for point in vertices]
    for face in faces:
        bm.faces.new([verts[index] for index in face])
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    assert all(edge.is_manifold for edge in bm.edges), f"{name} is not manifold"
    assert bm.calc_volume(signed=True) > 0, f"{name} has invalid winding"
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def side_cell(faces, start, end, low, high, window_width=0):
    """Add both sides of one perimeter segment and the reveal of any opening."""
    rings = [
        [wall_point(node, z, inner) for node, z in (
            (start, low), (end, low), (end, high), (start, high)
        )]
        for inner in (False, True)
    ]
    if not window_width:
        faces.extend(rings)
        return

    length = (Vector(wall_point(end, high)) - Vector(wall_point(start, high))).length
    half_span = window_width / (2 * length)
    openings = []
    for inner in (False, True):
        opening = []
        for fraction, z in ((0.5 - half_span, 12), (0.5, 7), (0.5 + half_span, 12), (0.5, 17)):
            node = tuple(a + (b - a) * fraction for a, b in zip(start, end))
            opening.append(wall_point(node, z, inner))
        openings.append(opening)

    for ring, opening in zip(rings, openings):
        for i in range(4):
            j = (i + 1) % 4
            faces.append((ring[i], ring[j], opening[j], opening[i]))
    for i in range(4):
        j = (i + 1) % 4
        faces.append((openings[0][i], openings[0][j], openings[1][j], openings[1][i]))


def perimeter():
    cells = perimeter_cells()
    faces = []
    for i, (start, end, window_width) in enumerate(cells):
        faces.append((wall_point(start, 0), wall_point(end, 0),
                      wall_point(end, 0, True), wall_point(start, 0, True)))
        side_cell(faces, start, end, 0, BACK_THICKNESS)

        top = i < CORNER_STEPS or i >= len(cells) - CORNER_STEPS - 1
        cap_z = BACK_THICKNESS if top else FRAME_DEPTH
        faces.append((wall_point(start, cap_z), wall_point(end, cap_z),
                      wall_point(end, cap_z, True), wall_point(start, cap_z, True)))
        if not top:
            side_cell(faces, start, end, BACK_THICKNESS, TAPER_END)
            side_cell(faces, start, end, TAPER_END, FRAME_DEPTH, window_width)

    for end in (cells[CORNER_STEPS][0], cells[-CORNER_STEPS - 1][0]):
        for low, high in ((BACK_THICKNESS, TAPER_END), (TAPER_END, FRAME_DEPTH)):
            faces.append((wall_point(end, low), wall_point(end, high),
                          wall_point(end, high, True), wall_point(end, low, True)))
    return make_mesh("Tapered perimeter", faces)


def lattice_bar(start, end):
    """A back-plane diagonal with ends buried in the perimeter rail."""
    normal = Vector((start[1] - end[1], end[0] - start[0])).normalized() * 1.2
    corners = [Vector(start) + normal, Vector(start) - normal,
               Vector(end) - normal, Vector(end) + normal]
    bottom, top = [[(*point, z) for point in corners] for z in (0.0, BACK_THICKNESS)]
    faces = [bottom, top]
    for i in range(4):
        j = (i + 1) % 4
        faces.append((bottom[i], bottom[j], top[j], top[i]))
    return make_mesh("Back lattice rib", faces)


def build_frame():
    """Return overlapping manifold meshes to union with the organizer."""
    parts = [perimeter()]
    for x in (-70, -42, -14, 14, 42, 70):
        shift = 20 if x < 0 else -20
        parts.append(lattice_bar((x, -46.8), (x + shift, 46.8)))
        parts.append(lattice_bar((x + shift, -46.8), (x, 46.8)))
    return parts
