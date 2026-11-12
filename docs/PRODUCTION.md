# Production organizer

The user reported a good fit from the shared-base V2 print and approved the
fitted-pocket concept. This model develops those pockets around the tested
frame. The subsequent print exposed insufficient perfume retention and weak
rear attachments during support removal. This revision reinforces those roots;
its retention and support-removal strength still need physical confirmation.

## Geometry and access

- One connected body with solid side walls and a shared 1.2 mm rear backing.
- Three broad rounded windows reveal the leather behind the items. Smaller
  capsule openings flank the perfume pocket. Curved pocket borders join the
  frame, replacing the earlier slotted backing and separate straight fins.
- The accepted 2 mm rear inset and 5 mm taper length are retained. Corner curves
  are finer and contact edges have a 0.2 mm relief.
- The perfume remains horizontal above the battery, with its broad face
  parallel to the backing. Two curved end cradles support it. A centered 25 mm
  gap removes the entire middle, including the bottom supports. The backing
  opening extends below the gap so no central bridge obstructs the thumb.
  The longer halves follow a capsule contour and join the backing without an
  exposed reverse return or a separate projecting end plate.
  Rear panels that mirrored the front retainers are removed, together with
  the matching backing area. The purse lining supports the item from behind;
  reinforced end connections keep the cradles attached to the frame.
  Rear-opening corners have a 7 mm radius. Following print feedback, the
  pocket and item reference move down 1 mm. The front wall gains 1 mm of
  height relative to the pocket floor: its global top stays Y33.7, while
  the side rim is now Y35.7. Cavity and outer depth both increase 1 mm;
  the inner front is Z19.4 and the outer front reaches Z21.
  Each end has a 3 mm-wide square root extending 6 mm forward, a local
  6 x 14.5 x 3 mm landing, and R3 reinforcing fillets on both sides. The
  back remains flat at Z0. These replace the narrow tapered rear connection.
- The thick junction fill and duplicate outer guide walls are removed. Outer
  sides use the fitted 2.4 mm frame wall alone. Both outer walls and the center
  divider use the same depth taper from Y-5 to Y17. The lower seating contour
  remains unchanged; the upper outer walls now contact less of the bag.
- A single 2 mm divider replaces the thick full-height central wall. Its
  depth tapers smoothly down to the backing by Y17. It runs straight to the
  bottom wall at constant X, with no rightward return.
- The battery uses the frame bottom and shared backing. The extra lower plate
  and front curb are removed. Pull forward to remove it; the lowered perfume
  supports reduce the clearance available for tilting upward.
  Its upper edge has no enclosing wall; only the perfume's two independent
  end supports remain above it.
- Touchland's front lip and extra swept floor are removed. It uses the frame
  bottom and straight divider. Both lower compartments are open toward the
  front, so out-of-plane retention now depends on the bag and loaded fit.
  The rounded reference bottle can settle about 1.2 mm below its former
  position before contacting the frame; actual settling depends on its case.

Overall dimensions are approximately 180 x 98.47 x 21 mm. Edge rounding slightly
relieves the earlier frame height. The solid mesh volume is approximately
25.37 cubic centimeters; actual filament use also depends on slicing and support.

## Editing and rebuilding

Run `models/build_production.py` with Blender as documented in the README.
The production builder reuses the fitted perimeter from `models/frame_v2.py`
and defines the new backing and pockets separately.

In the Blender file, FRAME and ORGANIZER source collections are hidden by
default. Enable them for editing and hide the PRINT object while viewing source
geometry. The final PRINT object is the fused manufacturing mesh. Hidden item
references record dimensions and placement. Export PRINT only.

`PERFUME_CENTER_X` and `PERFUME_THUMB_WIDTH` define the center opening between
the two cradles. Changes to item sizes also require updating pocket geometry
and validating the removal path.

The preview script loads the manufacturing file and renders a temporary studio
scene. Loaded previews use rounded item envelopes to illustrate placement.
Curved facets use angle-based smooth shading; preview shading does not change
the manufacturing geometry.
The brown leather surface beneath the tray is a rendering reference for the
bag lining. These display objects are excluded from the STL.

## Mesh checks

The build verifies positive volume, a single connected body, manifold edges,
and nondegenerate triangles. It re-imports the STL and verifies those checks
again, along with dimensions and volume. Contact rounding is constructed on
source geometry, before the final union, to preserve a clean STL.

Removal checks sample rounded dimensional item proxies against the exported
STL: perfume and Touchland translate upward 60 mm; the battery translates
straight forward 40 mm without tilting. The former tilt-first path
now collides with the lowered perfume cradle and must not be used. These checks establish
nominal geometric clearance, not real friction, flexible-wall behavior, or
retention during movement. The proxy corners simplify the actual cases
(battery R4, perfume lower section R3, Touchland R6 mm).
An independent solid intersection probe also verifies that the 25 mm central
perfume opening contains no shelf or retaining material above the backing.
Another probe confirms the mirrored rear perfume panels are absent through
both the shell and backing.
Each reinforced attachment was probed independently: fully solid root cores
of at least 2.8 x 13.7 x 5.8 mm and landing cores of 5.4 x 13.7 x 2.5 mm
remain after the union. This verifies geometry, not fracture strength.

## Printing

Use the backing flat on the bed with pockets facing upward, as exported.
The target printer is the Ender 3 V3 SE with a 0.4 mm nozzle and PLA.
The perfume retainers require support. Support contacts lie inside accessible
pockets; remove them before inserting the items. Follow the filament maker's
temperature guidance if it differs from the preview profile.

Preview slicing uses 0.2 mm layers, three walls, four top/bottom layers,
10% cubic infill, normal support Everywhere at 45 degrees, 17% zigzag support
(2.35294 mm line spacing), zero support walls, and a 0.2 mm support Z gap.
The support interface uses 33.3% density and 0.8 mm thickness. PLA temperatures are
200 C nozzle / 60 C bed. Speeds are 60 mm/s print, 35 outer wall, 50 inner wall,
35 skin, 45 support, 30 support interface, and 20 first layer.

The headless Cura result is a geometry and support preview, not supplied
printer-ready G-code. Import the STL into Cura with the printer's profile and
review its preview before saving the printer file.

The final preview estimates 3 h 12 min / 34.1 g PLA,
including 2.6 g support, all beneath the perfume. The deposited skirt and part
fit inside the 220 mm
bed. Estimates assume PLA density 1.24 g/cm3. Verified STL SHA-256:
`2E11604B4771A060E462AB273193100634A6427C08AEB790AABE1A74D1145D6F`.

Inspect the perfume scoop and mouth edges after support removal. Confirm that
the perfume slides out as a complete case, the battery exits independently,
and the loaded bag closes normally. The frame's successful test fit does not
establish these revised pocket behaviors.
