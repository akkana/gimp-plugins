#!/usr/bin/env python

'''Change font size, face and color for every text layer in a GIMP image.
   Only affects images at the top level: does not descend into layer groups.
'''

from gimpfu import *

def python_change_font(img, changesize, fontsize, changeface, fontface, changecolor, fontcolor):
    pdb.gimp_image_undo_group_start(img)

    for l in img.layers:
        if not pdb.gimp_item_is_text_layer(l):
            continue
        if changesize:
            pdb.gimp_text_layer_set_font_size(l, fontsize, 0)
        if changeface:
            pdb.gimp_text_layer_set_font(l, fontface)
        if changecolor:
            pdb.gimp_text_layer_set_color(l, fontcolor)

    pdb.gimp_image_undo_group_end(img)

register(
    "python_fu_change_font",
    "Change every text layer in an image to a new font and size",
    "Change every text layer in an image to a new font and size",
    "Akkana Peck",
    "Akkana Peck",
    "2016,2019",
    "Change Font in all Text Layers...",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_BOOL, "changesize", "Change Font Size", FALSE),
        (PF_SPINNER, "fontsize", "New Font Size",
         14, (1, 250, 1)),
        (PF_BOOL, "changeface", "Change Font", FALSE),
        (PF_FONT, "fontface", "New Font", "Sans"),
        (PF_BOOL, "changecolor", "Change Color", FALSE),
        (PF_COLOR, "fontcolor", "Color", (1.0, 1.0, 0.0)),
    ],
    [],
    python_change_font,
    menu="<Image>/Filters/Generic")

main()
