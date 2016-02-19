#!/usr/bin/env python

from gimpfu import *

def python_change_font(img, fontsize, fontface) :
    pdb.gimp_image_undo_group_start(img)

    for l in img.layers:
        if not pdb.gimp_item_is_text_layer(l):
            continue
	pdb.gimp_text_layer_set_font_size(l, fontsize, 0)
        pdb.gimp_text_layer_set_font(l, fontface)

    pdb.gimp_image_undo_group_end(img)

register(
       	"python_fu_change_font",
	"Change every text layer in an image to a new font and size",
	"Change every text layer in an image to a new font and size",
	"Akkana Peck",
	"Akkana Peck",
	"2016",
	"Change Font in all Text Layers...",
	"*",
	[
          (PF_IMAGE, "image", "Input image", None),
          (PF_SPINNER, "fontsize", "New Font Size",
           14, (1, 50, 1)),
          (PF_FONT, "font", "New Font", "Sans"),
	],
	[],
	python_change_font,
        menu="<Image>/Filters/Generic")

main()
