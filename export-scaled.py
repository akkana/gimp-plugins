#!/usr/bin/env python

# Export a copy of the current image, scaled to a different size.
# It's like "Save a copy" only it remembers to re-scale each time
# back to whatever scale you used on the last export --
# like if you want to keep a thumbnail or a
# smaller web version current as you're editing the master.

# Copyright 2012 by Akkana Peck, http://www.shallowsky.com/software/
# You may use and distribute this plug-in under the terms of the GPL v2
# or, at your option, any later GPL version.

from gimpfu import *
import gtk
import os
import collections

# Image original size
orig_width = 0
orig_height = 0

# The three gtk.Entry widgets we'll monitor:
percent_e = None
width_e = None
height_e = None

# A way to show errors to the user:
warning_label = None

# A way to turn off notifications while we're calculating
busy = False

# Doesn't work to compare entry against percent_e, etc.
# Must pass that info in a separate arg, darnit.
def entry_changed(entry, which) :
    global percent_e, width_e, height_e, orig_width, orig_height, busy
    if busy :
        return

    # Can't use get_value() or get_value_as_int() because they
    # don't work before an update(), but update() will usually
    # overwrite what the user typed. So define a function:
    def get_int_value(spinbox) :
        s = spinbox.get_text()
        if not s :
            return 0
        try :
            p = int(float(s))
            return p
        except :
            return 0

    if which == 'p' :
        p = get_int_value(percent_e)
        if not p : return
        busy = True
        w = int(orig_width * p / 100.)
        width_e.set_text(str(w))
        h = int(orig_height * p / 100.)
        height_e.set_text(str(h))
        busy = False

    elif which == 'w' :
        w = get_int_value(width_e)
        if not w : return
        p = int(orig_width / w * 100)
        percent_e.set_text(str(p))
        h = int(orig_height * p / 100.)
        height_e.set_text(str(h))

    elif which == 'h' :
        h = get_int_value(height_e)
        if not h : return
        p = int(orig_height / h * 100)
        percent_e.set_text(str(p))
        w = int(orig_width * p / 100.)
        width_e.set_text(str(w))
    else :
        print "I'm confused -- not width, height or percentage"

def python_export_scaled(img, drawable) :
    global percent_e, width_e, height_e, orig_width, orig_height, warning_label
    orig_filename = img.filename

    orig_width = img.width
    orig_height = img.height

    # Do we already have defaults?
    para = img.parasite_find('export-scaled')
    if para :
        [ init_filename, init_percent, init_width, init_height ] = \
            para.data.split('\n')
    else :
        init_filename = orig_filename
        init_percent = 100
        init_width = img.width
        init_height = img.height

    chooser = gtk.FileChooserDialog(title=None,
                                    action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                    buttons=(gtk.STOCK_CANCEL,
                                             gtk.RESPONSE_CANCEL,
                                             gtk.STOCK_SAVE,
                                             gtk.RESPONSE_OK))

    chooser.set_current_name(os.path.basename(init_filename))
    chooser.set_current_folder(os.path.dirname(init_filename))

    vbox = gtk.VBox(spacing=8)

    hbox = gtk.HBox(spacing=8)

    l = gtk.Label("Export size:")
    l.set_alignment(1, 0)
    l.show()
    hbox.pack_start(l)

    l = gtk.Label("Percent")
    l.set_alignment(1, 0)
    hbox.pack_start(l)
    l.show()
    adj = gtk.Adjustment(float(init_percent), 1, 10000, 1, 10, 0)
    percent_e = gtk.SpinButton(adj)   #, 0, 0)

    #percent_e = gtk.Entry()
    #percent_e.set_width_chars(5)
    #percent_e.set_text("100")   # XXX Later, remember size from last time

    percent_e.connect("changed", entry_changed, 'p');
    percent_e.show()
    hbox.pack_start(percent_e)
    l = gtk.Label("%")
    l.set_alignment(0, 1)
    hbox.pack_start(l)
    l.show()

    l = gtk.Label("Width")
    l.set_alignment(1, 0)
    hbox.pack_start(l)
    l.show()
    adj = gtk.Adjustment(float(init_width), 1, 10000, 1, 10, 0)
    width_e = gtk.SpinButton(adj)
    #width_e = gtk.Entry()
    #width_e.set_width_chars(7)
    #width_e.set_text(str(img.width))
    # XXX Later, remember size from previous run
    width_e.connect("changed", entry_changed, 'w');
    width_e.show()
    hbox.pack_start(width_e)

    l = gtk.Label("Height")
    l.set_alignment(1, 0)
    hbox.pack_start(l)
    l.show()
    adj = gtk.Adjustment(float(init_height), 1, 10000, 1, 10, 0)
    height_e = gtk.SpinButton(adj)
    #height_e = gtk.Entry()
    #height_e.set_width_chars(7)
    #height_e.set_text(str(img.height))
    height_e.connect("changed", entry_changed, 'h');
    hbox.pack_start(height_e)
    height_e.show()

    hbox.show()
    vbox.pack_start(hbox)

    warning_label = gtk.Label("")
    warning_label.show()
    vbox.pack_start(warning_label)

    chooser.set_extra_widget(vbox)

    # Oh, cool, we could have shortcuts to image folders,
    # and maybe remove the stupid fstab shortcuts GTK adds for us.
        #chooser.add_shortcut_folder(folder)
        #chooser.remove_shortcut_folder(folder)

    # Loop to catch errors/warnings:
    while True :
        response = chooser.run()
        if response != gtk.RESPONSE_OK:
            chooser.destroy()
            return

        percent = int(percent_e.get_text())
        width = int(width_e.get_text())
        height = int(height_e.get_text())

        filename = chooser.get_filename()
        if filename == orig_filename :
            warning_label.set_text("Change the name or the directory -- don't overwrite original file!")
            continue

        # Whew, it's not the original filename, so now we can export.

        #print "export from", orig_filename, "to", filename, \
        #    "at", width, "x", height

        # Is there any point to pushing and popping the context?
        #gimp.context_pop()

        newimg = pdb.gimp_image_duplicate(img)

        # If it's XCF, we don't need to flatten or process it further,
        # just scale it:
        base, ext = os.path.splitext(filename)
        ext = ext.lower()
        if ext == '.gz' or ext == '.bz2' :
            base, ext = os.path.splitext(base)
            ext = ext.lower()
        if ext != '.xcf' :
            newimg.flatten()
            # XXX This could probably be smarter about flattening. Oh, well.

        newimg.scale(width, height)

        # Find any image type settings parasites (e.g. jpeg settings)
        # that got set during save, so we'll be able to use them
        # next time.
        def copy_settings_parasites(fromimg, toimg) :
            for pname in fromimg.parasite_list() :
                if pname[-9:] == '-settings' or pname[-13:] == '-save-options' :
                    para = fromimg.parasite_find(pname)
                    if para :
                        toimg.attach_new_parasite(pname, para.flags, para.data)

        # Copy any settings parasites we may have saved from previous runs:
        copy_settings_parasites(img, newimg)

        # gimp-file-save insists on being passed a valid layer,
        # even if saving to a multilayer format such as XCF. Go figure.
        try :
            # I don't get it. What's the rule for whether gimp_file_save
            # will prompt for jpg parameters? Saving back to an existing
            # file doesn't seem to help.
            # run_mode=RUN_WITH_LAST_VALS is supposed to prevent prompting,
            # but actually seems to do nothing. Copying the -save-options
            # parasites is more effective.
            dpy = chooser.get_display()
            chooser.hide()
            dpy.sync()
            pdb.gimp_file_save(newimg, newimg.active_layer, filename, filename,
                               run_mode=RUN_WITH_LAST_VALS)
        except RuntimeError, e :
            #warning_label.set_text("Didn't save to " + filename
            #                       + ":" + str(e))
            markup = '<span foreground="red" size="larger" weight=\"bold">'
            markup_end = '</span>'
            warning_label.set_markup(markup + "Didn't save to " + filename
                                   + ":" + str(e) + markup_end)
            gimp.delete(newimg)
            chooser.show()
            continue

        chooser.destroy()

        #gimp.context_pop()

        copy_settings_parasites(newimg, img)

        gimp.delete(newimg)
        #gimp.Display(newimg)

        # Save parameters as a parasite, even if saving failed,
        # so we can default to them next time.
        # Save: percent, width, height
        # I have no idea what the flags are -- the doc doesn't say.
        para = img.attach_new_parasite('export-scaled', 0,
                                       '%s\n%d\n%d\n%d' % (filename, percent,
                                                           width, height))
        # img.parasite_attach(para)

        return

register(
    "python_fu_export_scaled",
    "Export a copy of the current image, scaled to a different size.",
    "Export a copy of the current image, scaled to a different size.",
    "Akkana Peck",
    "Akkana Peck",
    "2012",
    "Export scaled...",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
    ],
    [],
    python_export_scaled,
    menu = "<Image>/File/Save/"
)

main()

