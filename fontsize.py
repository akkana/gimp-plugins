#!/usr/bin/env python

from gimpfu import *

def python_change_font_size(img, fontsize) :
    pdb.gimp_image_undo_group_start(img)

    for l in img.layers:
        if not pdb.gimp_item_is_text_layer(l):
            continue
	pdb.gimp_text_layer_set_font_size(l, fontsize, 0)
        # You can also change font face, like this:
        # pdb.gimp_text_layer_set_font(l, font)

    pdb.gimp_image_undo_group_end(img)

register(
       	"python_fu_change_font_size",
	"Change every text layer in an image to a new font size",
	"Change every text layer in an image to a new font size",
	"Akkana Peck",
	"Akkana Peck",
	"2016",
	"Change Font Sizes...",
	"*",
	[
          (PF_IMAGE, "image", "Input image", None),
          (PF_SPINNER, "fontsize", "New Font Size",
           14, (1, 50, 1))
	],
	[],
	python_change_font_size,
        menu="<Image>/Filters/Generic")

main()
