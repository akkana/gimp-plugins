#!/usr/bin/env python

from gimpfu import *

def python_blobify(img, layer, blur) :
    pdb.gimp_undo_push_group_start(img)

    # Alpha to selection:
    pdb.gimp_selection_layer_alpha(layer)
    # Invert the selection:
    pdb.gimp_selection_invert(img)
    # Make a dropshadow from the inverted selection
    pdb.script_fu_drop_shadow(img, layer, -3, -3, blur,
                              (0, 0, 0), 80.0, False)

    # Clean up
    pdb.gimp_selection_none(img)
    pdb.gimp_undo_push_group_end(img)


register(
    "python_fu_blobify",
    "Create a 3-D effect",
    "Create a blobby 3-D effect using inverse drop-shadow",
    "Akkana Peck",
    "Akkana Peck",
    "2009",
    "BlobiPy...",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input layer", None),
        (PF_SPINNER, "blur", "Blur amount",
         7, (0, 50, 1))
    ],
    [],
    python_blobify,
    menu="<Image>/Filters/Light and Shadow")


main()
