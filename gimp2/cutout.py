#!/usr/bin/env python

# Cut out a selected band an image, either vertically or horizontally,
# resizing the canvas appropriately afterward.
# The selection must extend all the way across the image either
# vertically or horizontally, but not both.

from gimpfu import *

def python_fu_cutout(img, drawable):
    pdb.gimp_message_set_handler(MESSAGE_BOX)
    exists, x1, y1, x2, y2 = pdb.gimp_selection_bounds(img)
    orient = None

    # Figure out whether we're cutting vertically or horizontally.
    # It's ridiculously hard to make a selectin exactly the width or
    # height of the image, so figure that 95% is close enough.
    thresh = .05
    if x1 < thresh * img.width and x2 > img.width * (1. - thresh):
        orient = 'h'
    if y1 <= thresh * img.height and y2 > img.height * (1. - thresh):
        if orient:
            pdb.gimp_message("Error: selection can't encompass entire image")
            return
        orient = 'v'
    if not orient:
        pdb.gimp_message("Must have a selection spanning entire width or height")
        print "Selection is %d-%d x %d-%d" % (x1, x2, y1, y2)
        return

    # Now orient is either 'h' or 'v'.

    img.undo_group_start()

    if orient == 'h':
        pdb.gimp_image_select_rectangle(img, CHANNEL_OP_REPLACE,
                                        0, y2, img.width, img.height)
        pdb.gimp_edit_cut(drawable)

        pdb.gimp_image_select_rectangle(img, CHANNEL_OP_REPLACE,
                                        0, y1, img.width, img.height - y2)
        flayer = pdb.gimp_edit_paste(drawable, True)

        pdb.gimp_floating_sel_anchor(flayer)
        pdb.gimp_image_resize(img, img.width, y1 + img.height - y2, 0, 0)
        pdb.gimp_selection_none(img)

    elif orient == 'v':
        pdb.gimp_image_select_rectangle(img, CHANNEL_OP_REPLACE,
                                        x2, 0, img.width - x2, img.height)
        pdb.gimp_edit_cut(drawable)

        pdb.gimp_image_select_rectangle(img, CHANNEL_OP_REPLACE,
                                        x1, 0, img.width - x2, img.height)
        flayer = pdb.gimp_edit_paste(drawable, True)

        pdb.gimp_floating_sel_anchor(flayer)
        pdb.gimp_image_resize(img, x1 + img.width - x2, img.height, 0, 0)
        pdb.gimp_selection_none(img)

    img.undo_group_end()

register(
    "python_fu_cutout",
    "Cut a selected band from an image, either vertically or horizontally",
    "Cut a selected band from an image, either vertically or horizontally",
    "Akkana Peck",
    "Akkana Peck",
    "2013",
    "Cut out selected band",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
    ],
    [],
    python_fu_cutout,
    menu = "<Image>/Filters/Distorts/"
)

main()
