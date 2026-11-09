# Production design plan

Proposed direction, pending feedback from the shared-base V2 test print.

## Appearance

Create a fitted tray with three sculpted pockets, a continuous rounded rim,
and deliberate openings that show the leather. Use the same curves and edge
treatment for dividers, finger recesses, and pocket mouths.

The aluminum shell suggests restrained geometry and repeated parallel details.
Use broad smooth surfaces and a few elongated backing openings aligned with
the bag's visible details. These replace the visually busy crisscross ribs.
Select color against the actual lining; matte charcoal is a proposed palette.
Keep solid side walls for the next revision.

## Gridfinity principles

Borrow dedicated cavities, repeatable seating, shared walls, and finger access.
Adapt those principles to this custom footprint and its approximately 20 mm
depth. The user wants one connected print. Preserve separate FRAME and
ORGANIZER CAD definitions and fuse them for export. Future item changes should
reuse the accepted perimeter and rear contour.

References reviewed

- [Original Gridfinity divider bins](https://thangs.com/designer/ZackFreedman/3d-model/Gridfinity%20Divider%20Bins-60721)
- [Gridfinity Rebuilt implementation](https://github.com/kennetek/gridfinity-rebuilt-openscad)

The pocket designs below are our proposed adaptation.

## Battery pocket

Preserve its horizontal position and support it on the frame bottom. Blend
side guides into shallow pocket walls. A low continuous front curb follows
its lower edge. Add a broad finger scallop so the upper edge tips forward and
the battery lifts clear. Its rear support is the shared frame backing.

Verify the entire removal sweep with perfume installed. The perfume shelf
restricts straight upward extraction. Check the closed folding stand and its
seam so the pocket contacts the case without snagging the stand.

## Perfume saddle

Keep its long axis horizontal and broad face parallel to the tray back.
Replace the isolated straps with a smooth, low saddle/front apron blended
into the end walls. Use a regularized bamboo-section case profile.

A small raised stop carries its weight above the battery. Broad end cheeks
limit sideways movement. A short front return integrated into the lower rim
limits forward movement. A central finger recess and exposed upper portion
provide a pinch grip. The shared backing supports the rear face.

The complete case slides upward to release. The mouth and returns must clear
its widest section throughout that sweep. Check cap seams so removal does not
open the case. Tune clearance before adding any spring retention.

## Touchland pocket

Use a rounded lower pocket with a continuous low front wall and curved side
walls. Keep its upper portion exposed for grip and upward removal. Match its
actual rounded corners using the test result. Locate the bottle through its
body and leave clearance around the spray head, including when the bag closes.

## Retention

Pocket walls, rear support, and bottom stops control movement. Integrated front
returns add forward restraint. The selected exit direction remains open, so
the first design targets upright carry and ordinary movement. Inversion
retention needs a separate test and may require a shallow internal detent.

Start with rigid smooth pockets and controlled clearance. If testing reveals
rattle or unintended release, trial an internal relief/detent on a small coupon.
PLA spring behavior and removal force need physical verification. Optional soft
contact layers must be included in the dimensional budget.

## Space budget

The original tested footprint is 180 x 100 mm. V2 is 180 x 98.48 x 20 mm with
an open upper edge and a provisional rear taper.

| Item | Across frame | Up frame | Forward depth |
| --- | ---: | ---: | ---: |
| Battery | 105 mm | 67 mm | 13 mm |
| Perfume | 66.4 mm | 25.3 mm | 16.2 mm |
| Touchland | 55 mm | 95 mm | 17 mm |

An illustrative Touchland allocation is 1.2 mm backing + 0.3 mm rear gap +
17 mm bottle + 0.3 mm front gap + 1.2 mm front wall = 20 mm. This uses the
entire approximate depth allowance. Closure, print tolerances, and any padding
can change feasibility.

Battery and perfume together use 92.3 mm vertically before their separator
and clearances. Shared supporting features and the open upper edge remain
essential. Determine seating from the print before enlarging divider fillets.
Every fillet must clear both the stored item and its removal path.

Trial 0.3, 0.5, and 0.7 mm per-side clearances on small coupons. These are
experiment values, not established production tolerances.

## Manufacturing

Use consistent rounded contact edges and smooth wall junctions. Place seams
and support contact away from the visible rim and frequent hand-contact areas
where practical. Provide broad access for cleaning and support removal.

Start the slicer comparison with the backing flat on the plate. Solid side
walls and a flat open backing suit this orientation. Front returns and the
perfume saddle may still need localized support. Compare support area and
removal access before choosing their final profiles. Chamfers can reduce
overhangs where they also clear the contents. A continuous apron must be checked
in the slicer before promising support-free printing.

Retain one connected body, separate source collections, smooth item references,
and named pocket parameters. Validate the exported STL by re-importing it and
inspect Cura layers using the Ender 3 V3 SE and 0.4 mm nozzle profile.

## Feedback from the current print

- First contact locations, rocking, remaining rear gap, and seated depth.
- Loaded closure and any pressure on Touchland or the cases.
- Tight, loose, or hard-to-reach areas.
- Battery removal with perfume installed.
- Perfume release without catching its cap or lifting the tray.
- Rattle or movement during upright carry and controlled tilting.
- Rough edges and difficult support removal.

## Design sequence

1. Incorporate fit feedback into the frame contour and item envelopes. Preserve
   a named version of the accepted frame.
2. Produce front and angled concept previews with the items visible, including
   pocket mouths, finger recesses, and removal paths.
3. Develop the three pocket profiles and shared walls. Check swept volumes
   during insertion and removal.
4. Print small clearance/retention coupons for uncertain features.
5. Build the full tray, compare orientation/supports in Cura, and print one
   refined prototype.
6. Accept the production candidate after seating, closure, independent
   one-handed access, quiet retention, smooth contact surfaces, and repeated
   insertion/removal have been checked.
