#!/usr/bin/env python3

# wallpaper.py v. 0.9: a script to aid in making desktop backgrounds.
# Start by making a selection (use Save Options in the Tool Options
# dialog to simplify choosing specific aspect ratios).
# The script knows a few common sizes (1680x1050, 1024x768 and so forth)
# and chooses one based on the aspect ratio of the selection.
# It will make a cropped, scaled copy which you can save as you choose.
#

# Copyright 2009,2023 by Akkana Peck, http://www.shallowsky.com/software/
# You may use and distribute this plug-in under the terms of the GPL v2
# or, at your option, any later GPL version.

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

import os, sys

def N_(message): return message
def _(message): return GLib.dgettext(None, message)

###################### User-defined variables:
## You may want to change these according to your preferences

#
# Wallpaperdir: Where you keep your wallpaper images. Change this if needed!
# Wallpapers will be saved in subdirectories named by the
# horizontal resolution, e.g. $HOME/Backgrounds/1024/filename.jpg
#
wallpaperdir = os.path.join(os.getenv("HOME"), "Images/Backgrounds")

#
# Table of desired resolutions.
# The script will choose the size with the aspect ratio closest
# to the aspect ratio of the selection.
#
# WARNING! many of these have the same 4x3 aspect ratio.
# Therefore, only one of them will work here. Choose one.
# If you want both, you'll have to write a little more code
# to produce two images in that case.
# It's probably best to comment out all but the resolutions
# you personally are interested in. (Ideally this would be configurable
# through some sort of nice gui, and saved in preferences.:-)
#
common_resolutions = [
    [ 1920, 1200 ],
    [ 1920, 1080 ],
#    [ 1600, 1200 ],
    [ 1680, 1050 ],
#    [ 1366, 768 ],
#    [ 1280, 1024 ],
#    [ 1024, 768 ],
#    [ 1039, 697 ],

    [ 1080, 1920 ],  # galaxy s5
    [ 1080, 2220 ],  # pixel 3a
]

#
###################### End User-defined variables.
# You shouldn't have to change anything below here.


class WallpaperPlugin(Gimp.PlugIn):
    ## Parameters ##
    __gproperties__ = {
    }

    ## GimpPlugIn virtual methods ##
    def do_set_i18n(self, procname):
        return True, 'gimp30-python', None

    def do_query_procedures(self):
        return [ "python-fu-wallpaper" ]

    def do_create_procedure(self, name):
        """Register as a GIMP plug-in"""

        print("Trying to register wallpaper plugin")

        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            self.wallpaper_dialog, None)
        procedure.set_menu_label("Selection to _Wallpaper");

        procedure.set_image_types("*");

        # procedure.set_icon_name(GimpUi.ICON_GEGL);
        procedure.add_menu_path('<Image>/Image')

        procedure.set_documentation(
            "Create desktop wallpaper from selection",
            "Crop and resize the current image according to the selection, "
                "to make desktop wallpaper",
            name);
        procedure.set_attribution("Akkana Peck", "Akkana Peck", "2009,2023");

        return procedure

    def wallpaper_dialog(self, procedure, run_mode, img,
                         n_drawables, drawables,
                         args, data):
        # Get bounds of selection.
        dummy, exists, x1, y1, x2, y2 = Gimp.Selection.bounds(img)
        sel_aspect = float(x2 - x1) / (y2 - y1)

        # Figure out which size we're targeting
        diff = 100
        width = 1600
        height = 1200
        for res in common_resolutions:
            res_aspect = float(res[0]) / res[1]
            if (abs(res_aspect - sel_aspect) < diff):
                width = res[0]
                height = res[1]
                diff = abs(res_aspect - sel_aspect)
        if diff > .25:    # That different, there's probably something wrong
            errortext = "No known wallpaper size matches aspect ratio " \
                     + str(sel_aspect)
            # This works, but isn't needed since we can return a CALLING_ERROR
            # errdialog = Gtk.MessageDialog(
            #     None, 0,
            #     message_type=Gtk.MessageType.ERROR,
            #     buttons=Gtk.ButtonsType.OK,
            #     text=errortext)
            # errdialog.show_all()
            # errdialog.run()
            return procedure.new_return_values(
                Gimp.PDBStatusType.CALLING_ERROR, GLib.Error(errortext))

        print("Making wallpaper of size", width, "x", height)

        # Get the image's filename
        imgfilename = img.get_file()
        # this returns a GLocalFile, which is undocumented.
        # Get the basename to use as a filename
        if imgfilename:
            name = imgfilename.get_basename()
        else:
            # If no pathname --
            # e.g. it was created, or dragged/pasted from a browser --
            # use a placeholder and hope the user notices and changes it.
            # In gimp 2.x, we used the image's name, but in API 3 this
            # tends to be ugly, like '[PXL_20230920_181601862] (imported)'
            name = "wallpaper.jpg"

        lname = name.lower()
        if lname.endswith(".xcf"):
            name = name[0:-4] + ".jpg"
        elif lname.endswith(".xcf.gz"):
            name = name[0:-7] + ".jpg"
        elif lname.endswith(".xcf.bz2"):
            name = name[0:-8] + ".jpg"

        dirpathname = os.path.join(wallpaperdir, "%dx%d" % (width, height))
        if not os.path.exists(dirpathname):
            fulldirpathname = dirpathname
            dirpathname = os.path.join(wallpaperdir, str(width))
            if not os.path.exists(dirpathname):
                return procedure.new_return_values(
                    Gimp.PDBStatusType.CALLING_ERROR, GLib.Error(
                        "Neither %s nor %s exists" %
                            (fulldirpathname, dirpathname)))

        pathname = os.path.join(dirpathname, name)
        print("will save to:", pathname)

        pdb = Gimp.get_pdb()

        pdb_proc = pdb.lookup_procedure('gimp-edit-copy-visible')
        pdb_config = pdb_proc.create_config()
        # pdb_config.set_property('run-mode', Gimp.RunMode.NONINTERACTIVE)
        pdb_config.set_property('image', img)
        if not pdb_proc.run(pdb_config):
            return procedure.new_return_values(
                Gimp.PDBStatusType.CALLING_ERROR, GLib.Error(
                    "Couldn't copy visible!"))

        pdb_proc = pdb.lookup_procedure('gimp-edit-paste-as-new-image')
        pdb_config = pdb_proc.create_config()
        # pdb_config.set_property('run-mode', Gimp.RunMode.NONINTERACTIVE)
        valarray = pdb_proc.run(pdb_config)
        # valarray.index(0) is return status, hopefully 1 is the new image
        newimg = valarray.index(1)

        # Paste-as-new may create an image with transparency,
        # which will warn if you try to save as jpeg, so:
        newimg.flatten()

        newimg.scale(width, height)

        pdb_proc = pdb.lookup_procedure('gimp-image-get-metadata')
        pdb_config = pdb_proc.create_config()
        # pdb_config.set_property('run-mode', Gimp.RunMode.NONINTERACTIVE)
        pdb_config.set_property('image', img)
        valarray = pdb_proc.run(pdb_config)
        if valarray.index(0) == Gimp.PDBStatusType.SUCCESS:
            metadata = valarray.index(1)
            # print("Read metadata", metadata)

            pdb_proc = pdb.lookup_procedure('gimp-image-set-metadata')
            pdb_config = pdb_proc.create_config()
            # pdb_config.set_property('run-mode', Gimp.RunMode.NONINTERACTIVE)
            pdb_config.set_property('image', newimg)
            pdb_config.set_property('metadata-string', metadata)
            pdb_proc.run(pdb_config)
        else:
            print("Couldn't get image metadata")

        # Check to make sure we won't be overwriting
        def check_overwrite_cb(widget):
            newpath = os.path.join(pathentry.get_text(), fileentry.get_text())
            if os.access(newpath, os.R_OK):
                msglabel.set_text(newpath + " already exists!")
                dialog.set_response_sensitive(Gtk.ResponseType.OK, False)
            else:
                msglabel.set_text(" ")
                dialog.set_response_sensitive(Gtk.ResponseType.OK, True)

        # would have liked to bring up a GIMP save dialog interactively here --
        # but unfortunately there's no way to call save-as interactively
        # from python! So make a custom dialog that at least gives the
        # user a chance to change the directory or filename:
        dialog = Gtk.Dialog("Save as Wallpaper", None, 0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                           # I don't remember what this Edit button was for
                           # "Edit", Gtk.ResponseType.NONE,
                           Gtk.STOCK_OK, Gtk.ResponseType.OK)

        label = Gtk.Label(label="Wallpaper: " + str(width) + "x" + str(height))
        dialog.vbox.pack_start(label, expand=True, fill=True, padding=0)

        table = Gtk.Table(n_rows=3, n_columns=2)
        # set_row_spacings is deprecated
        # table.set_row_spacings(10)
        # table.set_col_spacings(10)

        label = Gtk.Label(label="Directory:")
        table.attach(label, 0, 1, 0, 1)
        pathentry = Gtk.Entry()
        pathentry.set_width_chars(55)
        pathentry.set_text(dirpathname)
        table.attach(pathentry, 1, 2, 0, 1)

        label = Gtk.Label(label="File name:")
        table.attach(label, 0, 1, 1, 2)
        fileentry = Gtk.Entry()
        fileentry.set_width_chars(10)
        fileentry.set_text(name)
        table.attach(fileentry, 1, 2, 1, 2)

        msglabel = Gtk.Label(label=" ")
        table.attach(msglabel, 0, 2, 2, 3)

        dialog.vbox.pack_start(table, True, True, 0)

        # set_default_response only marks the button visually --
        # it doesn't actually change behavior.
        dialog.set_default_response(Gtk.ResponseType.OK)

        # To make Enter really do something, use activate on the entry:
        def dialogRespond(entry, dialog, response):
            dialog.response(response)

        fileentry.connect("activate", dialogRespond, dialog,
                          Gtk.ResponseType.OK)
        pathentry.connect("changed", check_overwrite_cb)
        fileentry.connect("changed", check_overwrite_cb)
        check_overwrite_cb(None)

        dialog.show_all()
        fileentry.grab_focus()

        response = dialog.run()

        pathname = pathentry.get_text()
        newname = fileentry.get_text()
        pathname = os.path.join(pathname, newname)
        if newname != name:
            # Change the image name on the original -- so that if we make
            # backgrounds of any other sizes, the name will stay the same.
            # pdb.gimp_image_set_filename(img, newname)
            print("WARNING: can't set filename on original")
            name = newname
        # Set name and dirpath for the new image, in case user choses "Edit"
        # pdb.gimp_image_set_filename(newimg, pathname)

        if response == Gtk.ResponseType.OK:
            dialog.hide()
            dialog.destroy()
            # Neither hide nor destroy will work unless we collect
            # gtk events before proceeding:
            while Gtk.events_pending():
                Gtk.main_iteration()

            try:
                pdb = Gimp.get_pdb()
                pdb_proc = pdb.lookup_procedure('gimp-file-save')
                pdb_config = pdb_proc.create_config()
                pdb_config.set_property('run-mode', Gimp.RunMode.NONINTERACTIVE)
                pdb_config.set_property('image', newimg)
                layers = img.list_selected_layers()
                pdb_config.set_property('num-drawables', len(layers))
                pdb_config.set_property('drawables',
                                        Gimp.ObjectArray.new(Gimp.Drawable,
                                                             layers, False))
                '''
                pdb_config.set_property('num-drawables', 1)
                pdb_config.set_property('drawables',
                                        Gimp.ObjectArray.new(
                                            Gimp.Drawable,
                                            # images no longer have active_layer
                                            # or, apparently, any other way to
                                            # get that, despite spyro-plus still
                                            # using it (as write-only, though)
                                            #newimg.active_layer,
                                            # temporarily, use this insteada:
                                            img.list_layers()[0],
                                            False))
                '''
                pdb_config.set_property('file', Gio.File.new_for_path(pathname))
                vals = pdb_proc.run(pdb_config)
                if vals.index(0) == Gimp.PDBStatusType.SUCCESS:
                    # If the save was successful, no need to show the new img,
                    # so delete it:
                    # Gimp.delete(newimg)
                    newimg.delete()
                    # gimp.context_pop()
                    return procedure.new_return_values(
                        Gimp.PDBStatusType.SUCCESS, GLib.Error())
                else:
                    return procedure.new_return_values(
                        Gimp.PDBStatusType.EXECUTION_ERROR,
                        GLib.Error("Error saving: %s" % vals.index(0)))

            except RuntimeError as e:
                print("Couldn't save!", str(e))
                # Is it worth bringing up a dialog here?

        elif response == Gtk.ResponseType.CANCEL:
            # Cancel the whole operation -- don't show the image
            Gimp.delete(newimg)
            Gimp.context_pop()
            return procedure.new_return_values(Gimp.PDBStatusType.CANCEL,
                                               GLib.Error())

        # NOTREACHED
        return procedure.new_return_values(Gimp.PDBStatusType.CANCEL,
                                           GLib.Error())

Gimp.main(WallpaperPlugin.__gtype__, sys.argv)


