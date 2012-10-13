#!/usr/bin/env python

# Simplify the steps to create filled text from the current text layer
# following the current path.
#
# Copyright 2012 by Akkana Peck, http://www.shallowsky.com/software/
# Share and enjoy under the terms of the GPL v.2 or later.

from gimpfu import *

def python_fu_visible_text_along_path(img, textlayer, filled) :
    """
    Create a new layer containing text from the current (text) layer,
    filled with the current fg color, following the current path.
    """
    vectors = pdb.gimp_vectors_new_from_text_layer(img, textlayer)

    # Make a new GIMP layer for the filled or stroked text.
    # XXX Make a more sensible layer name from the text layer name.
    #newlayer = gimp.Layer(img, "text", img.width, img.height,
    newlayer = gimp.Layer(img, "path-" + textlayer.name,
                          img.width, img.height,
                          RGBA_IMAGE, 100, NORMAL_MODE)
    img.add_layer(newlayer, 0)
    pdb.gimp_image_set_active_layer(img, newlayer)

    if filled :
        pdb.gimp_image_select_item(img, CHANNEL_OP_REPLACE, vectors)
        #pdb.gimp_vectors_to_selection(vectors, CHANNEL_OP_REPLACE,
        #                              True, False, 0, 0)
        pdb.gimp_edit_fill(newlayer, FOREGROUND_FILL)
    else :
        pdb.gimp_edit_stroke_vectors(newlayer, vectors)

register(
         "python_fu_visible_text_along_path",
         "Draw an arrow following the current selection",
         "Draw an arrow following the current selection",
         "Akkana Peck", "Akkana Peck",
         "2012",
         "<Image>/Filters/Render/Text on path",
         "*",
         [
            (PF_BOOL, "filled",  "Filled", True),
         ],
         [],
         python_fu_visible_text_along_path)

main()
