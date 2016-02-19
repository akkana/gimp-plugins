A collection of GIMP scripts and plug-ins by Akkana Peck.

These are all licensed under the GPL v2 or (at your option) any later GPL.
There's further discussion of some of them on my software page:
http://www.shallowsky.com/software/#gimp

===============
SAVE/EXPORT PLUG-INS (PYTHON):

More info: http://www.shallowsky.com/software/gimp-save/

saver.py
  Meant to be the One True Save/Export plug-in, on ctrl-S and ctrl-Shift-S.
  It saves whether the type is XCF or other, it can automatically save
  a copy in a different format, and it can even scale that copy and
  remember the scaling.

save-export-clean.py
  Save or export, marking the current image clean.
  This was an initial quick hack for people who dislike the Save vs. Export
  split introduced in GIMP 2.8; it's mostly obsoleted now by Saver.

===============
OTHER PYTHON PLUG-INS:

arclayer.py
  Bend a layer (e.g. a text layer) in a circular arc.
  Also a good demo of how to use pixel regions in Python.

arrowdesigner.py
  Interactively draw an arrow in a new layer, using a rectangular
  selection as a guide.

blobi.py
  Text effect similar to bevel and drop shadow, but different.

changefont.py
  Change font face and size for all text layers in the current image.

export-scaled.py
  Export a scaled version of the current image, remembering name & scale
  for the next export.

export-all.py
  Show a dialog offering to export all open images.
  Currently this is just a skeleton for other people to build on.

life.py
  Conway's Game of Life (more or less, with colors added).
  No, there's no practical use for it. It's just a silly demo.

migrate-gimp-presets.py
  Migrate 2.6 tool presets to 2.8 (which doesn't happen automatically).

pyui.py
  Demonstrate all possible UI options for pygimp registration dialogs.

wallpaper.py
  Make wallpaper from the selection, based on aspect ratio.
  Has a few screen size presets (e.g. 1366x768, 1680x1050) and
  saves to a known place, e.g. ~/Backgrounds/1366/.
  It's recommended that you set rect select presets for aspect ratios
  like 16:8, 4:3, 1366:768 etc. in order to use this.

===============
SCRIPT-FU:

arclayer.scm
  Bend a layer (e.g. a text layer) in a circular arc.
  Much much slower than the Python version, due to lack of pixel regions.
  Nore info: http://www.shallowsky.com/software/arclayer/

fibonacci.scm
  Draw a Fibonacci (golden ratio) spiral around Fibonacci number boxes.

gimplabels/
  Create label/businesscard templates, and pages of them, based on
  Avery and similar templates imported from glabels.
  Fiddly to use since you have to figure out your printer's "slop factor".
  More info: http://www.shallowsky.com/software/gimplabels/

pandora-combine.scm
  Stitch a series of images (loaded as layers in one image) into a panorama.
  Doesn't do any smart matching based on the image contents; it just gives
  you initial fixed spacing and layer masks; then you can drag the images
  around to choose final placement, and edit the layer masks as needed.
  More info: http://www.shallowsky.com/software/pandora/

stack.scm
  Make an averaged image stack:
  combine all the layers with opacity 1/num_images.

sf-helloworld.scm
  A simple script-fu demonstration (used in GIMP scripting talks).
