#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 by Michael Schönitzer, Akkana Peck
# You may use and distribute this plug-in under the terms of the GPL v2
# or, at your option, any later GPL version.

from gimpfu import *
import gtk
import os
import collections
import re

def python_savemod_clean(img, drawable) :
    filename = img.filename
    
    # If the file has no filename yet, ask user
    if not filename :
        chooser = gtk.FileChooserDialog(title=None,
                                        action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                        buttons=(gtk.STOCK_CANCEL,
                                                 gtk.RESPONSE_CANCEL,
                                                 gtk.STOCK_OPEN,
                                                 gtk.RESPONSE_OK))
        # Might want to set a current folder:
        save_dir = choose_likely_save_dir()
        if save_dir :
            chooser.set_current_folder(save_dir)
        
        response = chooser.run()
        if response != gtk.RESPONSE_OK:
            return
        
        filename = chooser.get_filename()
        img.filename = filename
        chooser.destroy()
    # Otherwise we appand a string to the filename 
    else:
        # We don't want to save it in xcf format
        if os.path.splitext(filename)[1] == ".xcf" :
           filename = os.path.splitext(filename)[0] + ".png"
        
        filenamewoext = os.path.splitext(filename)[0] # filename without extension
        filenameext = os.path.splitext(filename)[1] # filenameextension
        # ToDo: Improve, so that mor than 9 versions are possible
        # Add -mod-attachement to filename
        if not re.search('-mod[0-9]?$' , filenamewoext):
           filename = filenamewoext + "-mod" + filenameext
        elif re.search('-mod$' , filenamewoext):
           filename = filenamewoext + "2" + filenameext
        # Increment number of the -mod-attachement
        else:
           num = int(filenamewoext[-1]) + 1
           filename = filenamewoext[0:-1] + str(num) + filenameext
    
    # We want to save all layers,
    # so first duplicate the picture, then merge all layers
    exportimg = pdb.gimp_image_duplicate(img)
    layer = pdb.gimp_image_merge_visible_layers(exportimg, CLIP_TO_IMAGE)
    
    # save file and unset the 'unsaved'-flag
    pdb.gimp_file_save(exportimg, layer, filename, filename)
    pdb.gimp_image_clean_all(img)
    img.filename = filename

# Guess the save directory
def choose_likely_save_dir() :
    counts = collections.Counter()
    for img in gimp.image_list() :
        if img.filename :
            counts[os.path.dirname(img.filename)] += 1
    
    try :
        return counts.most_common(1)[0][0]
    except :
        return None

register(
        "python_fu_savemod_clean",
        "Save current image with mod extension, then mark it clean.",
        "Save current image with mod extension, then mark it clean.",
        "Michael Schoenitzer, Akkana Peck",
        "Michael Schoenitzer, Akkana Peck",
        "2013",
        "Save with -mod & clean",
        "*",
        [
            (PF_IMAGE, "image", "Input image", None),
            (PF_DRAWABLE, "drawable", "Input drawable", None),
        ],
        [],
        python_savemod_clean,
        menu = "<Image>/File/Save/"
)

main()

