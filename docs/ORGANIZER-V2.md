# V2 organizer

The user confirmed the successful V1 footprint, approximately 5 mm rear gap at
the side taper, approximately 20 mm usable depth, and PLA on an Ender 3 V3 SE
with a 0.4 mm nozzle.

The model has one fused printable body. In the Blender file, hidden source
collections separate FRAME from ORGANIZER. Enable those collections for editing
and hide PRINT to avoid displaying overlapping copies. The measured item
envelopes are also stored in a hidden reference collection. Export PRINT only.

Frame geometry is in `models/frame_v2.py`. Holder geometry, item sizes,
assembly, validation, export, and previews are in `models/build_organizer_v2.py`.
Changing the item-size constants updates reference envelopes. Holder coordinates
are explicit and must also be adjusted when changing items.

The frame has a 2 mm rear inset, expanding over the rear 5 mm to the successful
180 mm width. Overall modeled depth is 20 mm. The upper front perimeter is
open so the tall Touchland and perfume can lift out. The remaining frame
measures 180 × 98.48 × 20 mm. The rear lattice is 1.2 mm thick, with 2.4 mm
perimeter rails and solid side walls for this prototype. Blue source geometry is the reusable
frame and tan geometry is the item layout. Both are fused for the single-material
print.

Perfume has two rounded cradle straps, end guides, and a lower stop. The front
straps reach only partway up the case, leaving the upper portion accessible.
The battery uses short side guides and a shallow lower front stop, allowing it
to tilt toward the opening and lift out. Touchland has short side guides and two
front straps, leaving its upper portion accessible. Its seat has a small 0.8 mm
inside corner radius to accommodate a nearly square lower cross-section.

The 2 mm rear inset is a trial value. The scan cannot establish the leather
contour accurately enough to promise a flush seat. Keep the first deeper print
as a fitting prototype. Check seating before loading items, then verify that the
bag closes without pressing on the contents. Check the perfume sliding path
and battery tilt-out path with the bag open.

## Dimension references

Anker lists 105 × 66.5 × 12.8 mm for the upgraded 622 A1614. Its original A1611
listing rounds to 105 × 67 × 13 mm. The user confirmed the rounded dimensions,
which this model uses.

- https://service.anker.com/ca/product-description/a085g000004zVNEAA2
- https://www.ankerjapan.com/collections/mobilebattery/products/a1611

Touchland 55 × 95 × 17 mm is the user's measurement. Online packaging dimensions
were excluded. The perfume scan PCA bounds are 66.38 × 25.28 × 16.15 mm.
The reference retailer's photos show the smooth bamboo-shaped case.

- https://tosummer.shop/products/eastern-scents-solid-perfume-2g

The measured envelopes fit with little vertical margin. V2 uses an open upper
edge and shared supporting features instead of adding full-height pocket walls.

## Latest revision

Side windows are disabled through SIDE_WINDOW_WIDTH = 0 in frame_v2.py.
The updated exported mesh passes the same single-component, closed-mesh,
nondegenerate-face and STL round-trip checks.

The user clarified the perfume orientation. Its 66.4 mm long axis stays
horizontal, its 25.3 mm dimension runs up the organizer, and its 16.2 mm
thickness projects forward. The broad face is parallel to the organizer back.
This is the orientation used by the existing cradle. The earlier 185.3 mm
packing objection concerned a different orientation and does not apply.

The loaded preview shows simple item envelopes to clarify placement and face
orientation. These references are excluded from the printable STL.
