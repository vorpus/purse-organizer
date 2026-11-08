# Rimowa fit-test frame

The target is the near half in the [view of both halves](scan-both-halves.png).
The three large holes are in the far half. The [isolated target view](scan-target-half.png)
keeps the positive-X side of the imported scan for inspection. The cut crosses
the divider, so edges exposed by the cut are scan artifacts for this purpose.

The face-on view spans 240 scan mm across 960 pixels. The visible inside lip
spans approximately 730 pixels lengthwise and 410 pixels across, or roughly
182 × 102 scan mm. The divider and end gussets are distorted, particularly near
the hinge. The short dimension uses the visible shell envelope there and is
less reliable. The scan supplies a footprint estimate and has no physical scale
check. The frame uses a regular rounded rectangle with an estimated 12 mm
inside bag corner radius.

The supplied STL is 180 × 100 × 3 mm with 1 mm clearance per side from the
estimated footprint. The rails are 2.4 mm wide. The pull tab points into the
opening so it leaves the outer contact perimeter clear.

Measure the long and short lining-to-lining spans just below the rigid lip.
If the gussets narrow the seating area, record the narrowest usable span and
its location. Use the build command in the README to update the footprint.

Import the STL into Cura in millimeters and confirm the dimensions. Keep the
frame flat on the plate and use the printer and material profile for the actual
fit test. The inward tab prints in the same plane as the frame. Test the frame
gently and record which edges or corners touch first. This shallow frame tests
the footprint at one seating depth.
