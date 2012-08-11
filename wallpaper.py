#!/usr/bin/env python

# wallpaper.py v. 0.4: a script to aid in making desktop backgrounds.
# Start by making a selection (use Save Options in the Tool Options
# dialog to simplify choosing specific aspect ratios).
# The script knows a few common sizes (1680x1050, 1024x768 and so forth)
# and chooses one based on the aspect ratio of the selection.
# It will make a cropped, scaled copy which you can save as you choose.
#

# Copyright 2009 by Akkana Peck, http://www.shallowsky.com/software/
# You may use and distribute this plug-in under the terms of the GPL v2
# or, at your option, any later GPL version.

from gimpfu import *
import gtk
import os

#
# Wallpaperdir: Where you keep your wallpaper images. Change this!
# Wallpapers will be saved in subdirectories named by the
# horizontal resolution, e.g. $HOME/Backgrounds/1024/filename.jpg
#
wallpaperdir = os.path.join(os.getenv("HOME"), "Images/Backgrounds")

#
# Table of desired resolutions.
# The script will choose the size with the aspect ratio closest
# to the aspect ratio of the selection.
#
# WARNING! 1600x1200 and 1024x768 have the same 4x3 aspect ratio.
# Therefore, only one of them will work here. Choose one.
# If you want both, you'll have to write a little more code
# to produce two images in that case.
# It's probably best to comment out all but the resolutions
# you personally are interested in. (Ideally this would be configurable
# through some sort of nice gui, and saved in preferences. :-)
#
common_resolutions = [
    [ 1024, 768 ],
#    [ 1600, 1200 ],
    [ 1680, 1050 ],
    [ 1366, 768 ],
    [ 1039, 697 ],
#    [ 1280, 1024 ],
]

#
# End of user-specified changes.
# You shouldn't have to change anything below here.
#

def python_wallpaper(img, layer) :
    gimp.context_push()

    (x1,y1,x2,y2) = layer.mask_bounds
    sel_aspect = float(x2 - x1) / (y2 - y1)

    # Figure out which size we're targeting
    diff = 100
    width = 1600
    height = 1200
    for res in common_resolutions :
        res_aspect = float(res[0]) / res[1]
        if (abs(res_aspect - sel_aspect) < diff) :
            width = res[0]
            height = res[1]
            diff = abs(res_aspect - sel_aspect)
    if diff > .25 :    # That different, there's probably something wrong
        errdialog = gtk.MessageDialog(None, 0,
                                      gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                      "No preset size matches aspect ratio " + \
                                          str(sel_aspect))
        errdialog.show_all()
        errdialog.run()
        return
    #print "Making wallpaper of size", width, "x", height
            
    # If it's an XCF, save it as a JPG
    # However, in gimp 2.8, img.name is "Untitled" if the image
    # hasn't been saved as an XCF, which this image likely hasn't.
    # So test for that:
    if img.name.find('.') < 0 :
        name = os.path.basename(img.filename)
    else :
        name = img.name
    if name[-4:] == ".xcf" :
        name = name[0:-4] + ".jpg"
    elif name[-7:]  == ".xcf.gz" :
        name = name[0:-7] + ".jpg"
    elif name[-8:]  == ".xcf.bz2" :
        name = name[0:-8] + ".jpg"

    #print wallpaperdir, width, name
    #print img
    #print dir(img)
    #print " "
    dirpathname = os.path.join(wallpaperdir, str(width))
    pathname = os.path.join(dirpathname, name)
    #newimg.name = name
    #newimg.filename = pathname
    #print "Trying to set name, pathname to", name, pathname

    if not pdb.gimp_edit_copy_visible(img) :
        return
    newimg = pdb.gimp_edit_paste_as_new()

    # Paste-as-new creates an image with transparency,
    # which will warn if you try to save as jpeg, so:
    newimg.flatten()

    newimg.scale(width, height)

    # Check to make sure we won't be overwriting
    def check_overwrite_cb(widget) :
        newpath = os.path.join(pathentry.get_text(), fileentry.get_text())
        if os.access(newpath, os.R_OK) :
            msglabel.set_text(newpath + " already exists!")
            dialog.set_response_sensitive(gtk.RESPONSE_OK, False)
        else :
            msglabel.set_text(" ")
            dialog.set_response_sensitive(gtk.RESPONSE_OK, True)

    # want to bring up the save dialog interactively here --
    # but unfortunately there's no way to call save-as interactively
    # from python! So give the user a chance to change the directory:
    # or filename:
    #
    dialog = gtk.Dialog("Save as Wallpaper", None, 0,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         "Edit", gtk.RESPONSE_NONE,
                         gtk.STOCK_OK, gtk.RESPONSE_OK))
    #dialog.connect('destroy', lambda win: gtk.main_quit())

    label = gtk.Label("Wallpaper: " + str(width) + "x" + str(height))
    dialog.vbox.pack_start(label, True, True, 0)

    table = gtk.Table(3, 2)
    table.set_row_spacings(10)
    table.set_col_spacings(10)

    label = gtk.Label("Directory:")
    table.attach(label, 0, 1, 0, 1)
    pathentry = gtk.Entry()
    pathentry.set_width_chars(55)
    pathentry.set_text(dirpathname)
    table.attach(pathentry, 1, 2, 0, 1)

    label = gtk.Label("File name:")
    table.attach(label, 0, 1, 1, 2)
    fileentry = gtk.Entry()
    fileentry.set_width_chars(10)
    fileentry.set_text(name)
    table.attach(fileentry, 1, 2, 1, 2)

    msglabel = gtk.Label(" ")
    table.attach(msglabel, 0, 2, 2, 3)

    dialog.vbox.pack_start(table, True, True, 0)

    # set_default_response only marks the button visually --
    # it doesn't actually change behavior.
    dialog.set_default_response(gtk.RESPONSE_OK)

    # To make Enter really do something, use activate on the entry:
    def dialogRespond(entry, dialog, response) :
        dialog.response(response)

    fileentry.connect("activate", dialogRespond, dialog, gtk.RESPONSE_OK)
    pathentry.connect("changed", check_overwrite_cb)
    fileentry.connect("changed", check_overwrite_cb)
    check_overwrite_cb(None)

    dialog.show_all()
    fileentry.grab_focus()

    response = dialog.run()

    pathname = pathentry.get_text()
    newname = fileentry.get_text()
    pathname = os.path.join(pathname, newname)
    if newname != name :
        # Change the image name on the original -- so that if we make
        # backgrounds of any other sizes, the name will stay the same.
        pdb.gimp_image_set_filename(img, name)
        name = newname
    # Set name and dirpath for the new image, in case user choses "Edit"
    pdb.gimp_image_set_filename(newimg, pathname)

    if response == gtk.RESPONSE_OK :
        dialog.hide()
        dialog.destroy()
        # Neither hide nor destroy will work unless we collect
        # gtk events before proceeding:
        while gtk.events_pending() :
            gtk.main_iteration()

        try :
            pdb.gimp_file_save(newimg, newimg.active_layer, pathname, pathname,
                               run_mode=0)
            # If the save was successful, we don't need to show the new image,
            # so delete it:
            gimp.delete(newimg)
            gimp.context_pop()
            return
        except RuntimeError, e:
            print "Couldn't save!", str(e)
            # Is it worth bringing up a dialog here?

    elif response == gtk.RESPONSE_REJECT :
        # Cancel the whole operation -- don't show the image
        gimp.delete(newimg)
        gimp.context_pop()
        return

    # We didn't save (OK) or Cancel; user must have clicked Edit.
    # So display the image and let the user deal with it.
    gimp.Display(newimg)
    gimp.context_pop()

    #NewFileSelector(newimg, pathname)

# GIMP python doesn't have any way to call up the Save As dialog!
# pdb.gimp_file_save would do it if there were some way to call it
# with run_mode = interactive ...
# class OldFileSelector:
#     # Get the selected filename and print it to the console
#     def file_ok_sel(self, w):
#         print "%s" % self.filew.get_filename()

#     def destroy(self, widget):
#         gtk.main_quit()

#     def __init__(self, img, pathname):
#         # Create a new file selection widget
#         print "old file sel dialog for", img, pathname
#         self.filew = gtk.FileSelection("File selection")

#         self.filew.connect("destroy", self.destroy)
#         # Connect the ok_button to file_ok_sel method
#         self.filew.ok_button.connect("clicked", self.file_ok_sel)

#         # Connect the cancel_button to destroy the widget
#         self.filew.cancel_button.connect("clicked",
#                                          lambda w: self.filew.destroy())

#         # Lets set the filename, as if this were a save dialog,
#         # and we are giving a default filename
#         self.filew.set_filename(pathname)

#         print "showing"
#         self.filew.show()

# def NewFileSelector(img, pathname) :
#     # Create a new file selection widget
#     print "new file sel dialog for", img, pathname
#     chooser = gtk.FileChooserDialog(title=None,
#                                     action=gtk.FILE_CHOOSER_ACTION_SAVE,
#                                     buttons=(gtk.STOCK_CANCEL,
#                                              gtk.RESPONSE_CANCEL,
#                                              gtk.STOCK_OPEN,
#                                              gtk.RESPONSE_OK))
#     chooser.set_current_name(os.path.basename(pathname))
#     chooser.set_current_folder(os.path.dirname(pathname))
#     response = chooser.run()
#     if response == gtk.RESPONSE_OK :
#         print "Would save to", chooser.get_filename()
#     else :
#         print "cancelled"

register(
        "python_fu_wallpaper",
        "Crop and resize to make wallpaper",
        "Crop and resize the current image according to the select, to make desktop wallpaper",
        "Akkana Peck",
        "Akkana Peck",
        "2009",
        "Selection to Wallpaper",
        "*",
        [
            (PF_IMAGE, "image", "Input image", None),
            (PF_DRAWABLE, "drawable", "Input drawable", None),
        ],
        [],
        python_wallpaper,
        menu = "<Image>/Image/"
)

main()

