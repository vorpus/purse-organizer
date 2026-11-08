# Production organizer

The user reported a good fit from the shared-base V2 print and approved the
fitted-pocket concept. This model develops those pockets around the tested
frame. The revised retention and thumb access still need checking in the print.

## Geometry and access

- One connected body with solid side walls and a shared 1.2 mm rear backing.
- Three broad rounded windows reveal the leather behind the items. Smaller
  capsule openings flank the perfume pocket. Curved pocket borders join the
  frame, replacing the earlier slotted backing and separate straight fins.
- The accepted 2 mm rear inset and 5 mm taper length are retained. Corner curves
  are finer and contact edges have a 0.2 mm relief.
- The perfume remains horizontal above the battery, with its broad face
  parallel to the backing. A centered 32 mm thumb channel extends all the way
  down to the shelf at Y23.4, splitting the front retainer into two side
  sections. Rounded lower corners leave 26 mm clear at the very bottom.
- The perfume shelf remains at Y22.2 to Y23.4. Its end cheeks and remaining
  retainers locate the case while the middle is accessible. Pocket mouth edges
  have a 0.35 mm rounded profile.
- The battery uses the frame bottom and shared backing. Its front curb is low
  to permit forward tilting below the perfume shelf. Tilt forward about 20
  degrees, lift 3 mm, then pull forward. A large straight upward lift hits the
  shelf; excessive tilting can meet the lower curb.
  Its upper edge has no enclosing wall; only the perfume's independent shelf
  remains above it.
- Touchland uses a continuous rounded lower apron with a central finger scoop
  and side walls. Its upper portion remains exposed for upward removal.

Overall dimensions are approximately 180 x 98.42 x 20 mm. Edge rounding slightly
relieves the earlier frame height. The solid mesh volume is approximately
52.56 cubic centimeters; actual filament use also depends on slicing and support.

## Editing and rebuilding

Run `models/build_production.py` with Blender as documented in the README.
The production builder reuses the fitted perimeter from `models/frame_v2.py`
and defines the new backing and pockets separately.

In the Blender file, FRAME and ORGANIZER source collections are hidden by
default. Enable them for editing and hide the PRINT object while viewing source
geometry. The final PRINT object is the fused manufacturing mesh. Hidden item
references record dimensions and placement. Export PRINT only.

The perfume thumb opening is cut through the apron down to
`PERFUME_CHANNEL_BASE`; its rounded cutter defines the 32 mm overall width.
`PERFUME_APRON_TOP` controls the remaining side retainers. Changes to item sizes
also require updating pocket geometry and validating the removal path.

The preview script loads the manufacturing file and renders a temporary studio
scene. Loaded previews use rounded item envelopes to illustrate placement.
The brown leather surface beneath the tray is a rendering reference for the
bag lining. These display objects are excluded from the STL.

## Mesh checks

The build verifies positive volume, a single connected body, manifold edges,
and nondegenerate triangles. It re-imports the STL and verifies those checks
again, along with dimensions and volume. Contact rounding is constructed on
source geometry, before the final union, to preserve a clean STL.

Removal checks sample rounded dimensional item proxies against the exported
STL: perfume and Touchland translate upward 60 mm; the battery tilts forward
20 degrees, lifts 3 mm, then translates forward 40 mm. These checks establish
nominal geometric clearance, not real friction, flexible-wall behavior, or
retention during movement. The proxy corners simplify the actual cases
(battery R4, perfume lower section R3, Touchland R6 mm).

## Printing

Use the backing flat on the bed with pockets facing upward, as exported.
The target printer is the Ender 3 V3 SE with a 0.4 mm nozzle and PLA.
The front aprons require support. Support contacts lie inside accessible
pockets; remove them before inserting the items. Follow the filament maker's
temperature guidance if it differs from the preview profile.

Preview slicing uses 0.2 mm layers, three walls, four top/bottom layers,
10% cubic infill, normal support Everywhere at 45 degrees, 20% support density,
support interface enabled, and a 0.2 mm support Z gap. PLA temperatures are
200 C nozzle / 60 C bed. Speeds are 60 mm/s print, 35 outer wall, 50 inner wall,
35 skin, 45 support, 30 support interface, and 20 first layer.

The headless Cura result is a geometry and support preview, not supplied
printer-ready G-code. Import the STL into Cura with the printer's profile and
review its preview before saving the printer file.

The final preview has 100 layers and estimates 5 h 28 min / 55.3 g PLA,
including 10.2 g support. The deposited skirt and part fit inside the 220 mm
bed. Estimates assume PLA density 1.24 g/cm3. Verified STL SHA-256:
`2C1A00816BA2BC9C1569A2C951C30FC314BD1248322D5F438CAE4E6C40E5EAEE`.

Inspect the perfume scoop and mouth edges after support removal. Confirm that
the perfume slides out as a complete case, the battery exits independently,
and the loaded bag closes normally. The frame's successful test fit does not
establish these revised pocket behaviors.
