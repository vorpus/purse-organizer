# purse-organizer

Design a 3D-printable organizer insert for a Rimowa crossbody bag, starting with a frame to test the fit in one half.

## Continue on another computer

Clone the private repository with an authenticated GitHub CLI:

```sh
gh repo clone vorpus/purse-organizer
cd purse-organizer
```

Read [the handoff](docs/HANDOFF.md) for requirements, scan details, references, and next steps. The original scan is included in `scans/Untitled Object.usdz`.

## Build the fit-test frame

From the repository root in PowerShell, run Blender with the measured inside
width and height in millimeters. This replaces the generated Blender and STL
files in `models/`.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' -b --factory-startup --python-exit-code 1 --python models/build_fit_test.py -- --width 182 --height 102 --clearance 1
```

The numbers above are provisional scan estimates. Take both measurements at
the intended seating plane, just below the rigid lip on the side without the
three large holes. Measure lining to lining with the liner relaxed. Clearance
is per side. See [the fit-test notes](docs/FIT-TEST.md) for scan views and Cura
setup.
