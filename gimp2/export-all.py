#!/usr/bin/env python

# Offer to export all currently open GIMP images.

# WARNING: USE OF THIS PLUG-IN IN ITS CURRENT STATE IS DANGEROUS!
# It is untested and unfinished.
# It may overwrite your files without asking,
# burn your meatloaf, or do other bad things.
#
# This plug-in is currently just a skeleton! It is intended as a
# jumping-off point for further work, not as a usable plug-in yet.
# Please contribute to it and send github pull requests!

# Copyright 2013 by Akkana Peck, http://www.shallowsky.com/software/
# You may use and distribute this plug-in under the terms of the GPL v2
# or, at your option, any later GPL version.

from gimpfu import *
import gtk
import os

# A way to show errors to the user:
warning_label = None

# Text entries containing the filenames:
entries = []
# Save a list of images corresponding to each entry.
# Don't depend on gimp.image_list remaining unchanged.
images = []

def python_export_all() :
    dialog = gtk.Dialog("Export All", None, 0,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_OK))

    # set_default_response only marks the button visually --
    # it doesn't actually change behavior.
    dialog.set_default_response(gtk.RESPONSE_OK)

    def toggle_active(widget, which):
        entries[which].set_sensitive(widget.get_active())

    # Build the table of filenames:
    table = gtk.Table(2, len(gimp.image_list()))
    table.set_row_spacings(10)
    table.set_col_spacings(10)

    for i, img in enumerate(gimp.image_list()):
        entries.append(gtk.Entry())
        images.append(img)
        entries[i].set_text(img.filename)

        # entries[i].set_width_chars(10)
        # entries[i].connect("activate", ...)
        # entries[i].connect("changed", ...)

        table.attach(entries[i], 0, 1, i, i+1)

        # Toggle button so we can control which images get saved
        toggle = gtk.ToggleButton("Save")
        toggle.set_active(True)
        toggle.connect("toggled", toggle_active, i)
        table.attach(toggle, 1, 2, i, i+1)

    dialog.vbox.pack_start(table, True, True, 0)
    dialog.show_all()

    response = dialog.run()

    if response != gtk.RESPONSE_OK :
        return

    for i, entry in enumerate(entries):
        if entry.get_sensitive():
            # Save the image's active layer
            filename = entry.get_text()
            print "Saving", filename
            pdb.gimp_file_save(images[i], images[i].active_layer,
                               filename, filename)
            pdb.gimp_image_clean_all(img)

register(
    "python_fu_export_all",
    "Export all open images.",
    "Export all open images.",
    "Akkana Peck",
    "Akkana Peck",
    "2013",
    "Export all...",
    "*",
    [
    ],
    [],
    python_export_all,
    menu = "<Image>/File/Save/"
)

main()

