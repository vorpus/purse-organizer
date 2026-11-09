# Handoff to marzipan

## Current continuation

The user confirmed a good fit from the shared-base V2 test print and requested
the production model. The production direction follows the approved fitted
pocket concept. Latest feedback requires two organic perfume end cradles with
the middle completely open through the bottom, thin outer walls, a shorter
tapered divider, and a lower Touchland lip. The latest refinement narrows the
perfume opening to 15 mm, removes its reverse bottom return, and makes the
Touchland lip continuous with the sides. The perfume's mirrored rear panels
are removed so the purse lining supports it; opening edges must blend smoothly
from side walls into lower lips. Keep the tested outside fit.
See [production notes](PRODUCTION.md) and the production build commands in
the README. The earlier sections below record the initial scan handoff.

## Goal and scope

Create a 3D-printable organizer insert for the user's Rimowa crossbody bag.
The first deliverable is only a frame to test snugness of fit, for the side
WITHOUT the three large holes visible in the scan. Do not build the full
organizer or the other half yet.

The user is moving this work to desktop `marzipan`, which has Blender and Cura.

## Input and current state

- Original scan: `scans/Untitled Object.usdz`, created with Reality Composer.
- The user reports low resolution and a poorly scanned interior.
- Archive inspected: one USDC mesh plus color, normal, and ambient-occlusion textures.
- USD metadata reports RealityKit Object Capture, detail level `.mobile`,
  `metersPerUnit = 1`, and Y up. Metadata units do not prove dimensional accuracy.
- The scan has NOT been visually inspected by the agent. The requested half
  has NOT yet been identified, isolated, measured, or repaired.
- No CAD model, printable frame, STL, STEP, or slicer project exists yet.
- Private GitHub repository: https://github.com/vorpus/purse-organizer

## Proposed workflow discussed with the user

1. Import the USDZ into Blender; inspect orientation and geometry. Isolate the
   side without the three large holes and show it to the user to establish selection.
2. Examine interior cross-sections and identify reliable edges. Use the scan
   as dimensional reference where reliable; automatic hole filling cannot
   recover missing interior measurements.
3. Verify scale against physical inside width and height measurements from
   the user. These have not been supplied. Check depth/taper as needed.
4. Build a smooth, adjustable perimeter. CadQuery was recommended for
   parameterized dimensions, corner curves, clearance, taper, and STEP/STL
   export, with Blender for scan inspection. CadQuery availability on marzipan
   is unknown; choose practical tooling after inspecting the environment.
5. First print: a shallow open-center perimeter frame with rounded contact
   edges and a removal tab, for the selected half only. Keep it inexpensive
   to print and easy to revise. Actual dimensions and clearance remain undecided.
6. Check the mesh and slice in Cura using the user's real printer/material
   profile. Printer, nozzle, material, and print settings are not known.
7. Iterate based on tight/loose regions. A shallow frame tests the footprint;
   deeper fit/taper and closure need separate checks before a full organizer.

## Online reference

Possible matching product: Rimowa Personal Aluminium Cross-Body Bag.
Exact model match is NOT confirmed.

https://www.rimowa.com/gb/en/bags/all-personal/cross-body-bag/99011010.html

Official dimensions: 215 mm width x 130 mm height x 70 mm depth, EXTERNAL.
The page describes leather lining, two open compartments, a zipped pocket,
and three card slots. Do not equate card slots with the user's scan holes.
External dimensions and photographs are sanity checks, not interior CAD data;
do not assume either half has half the external depth.

## Suggested continuation prompt

Read AGENTS.md and docs/HANDOFF.md in this project. Inspect the USDZ scan in
Blender and identify the half without the three large holes. Help create a
parameterized, 3D-printable fit-test frame for that half only. Blender and Cura
are installed here. Show the selected half and assess scan scale/reliability
before choosing dimensions. Ask for physical measurements needed to validate
fit; do not invent missing interior geometry or claim the frame is fit-verified.

## Continuation

The provisional frame, Blender source, and STL are in `models/`. See
[fit-test notes](FIT-TEST.md) for scan views, the footprint estimate, and the
measurements needed to calibrate it.

## V2 continuation

The user printed V1 and confirmed its footprint. It seats approximately 5 mm
ahead of the back at the inward taper. User confirmed 20 mm usable depth,
Ender 3 V3 SE, 0.4 mm nozzle, and PLA. See [requirements](PRD.md) and
[V2 notes](ORGANIZER-V2.md). V2 combines a tapered frame and three item holders
into one printable STL, with separate source collections for future remodeling.
The physical fit of V2 remains to be tested.
