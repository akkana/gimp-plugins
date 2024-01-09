#!/usr/bin/env python

# Performes tree times a unsharp-mask wiht diffrent stengths and sizes

# Copyright 2015 by Michael F. Schoenitzer 
# You may use and distribute this plug-in under the terms of the GPL v2
# or, at your option, any later GPL version.

from gimpfu import *
import gtk
import os
import collections

class MyWindow(gtk.Dialog):
    
    def __init__(self, parent=None, filename="Filename.jpg"):
        gtk.Dialog.__init__(self, "Triple USM", parent, 0,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
             gtk.STOCK_OK, gtk.RESPONSE_OK))
        if not filename:
          filename="Filename.jpg"
        
        table = gtk.Table(4,2, True)
        
        self.set_default_size(150, 100)
        box = self.get_content_area()
        box.set_homogeneous(False)
        box.set_spacing(False)
        box.add(table)
        
        self.size_label = gtk.Label("Size")
        self.strength_label = gtk.Label("Strength")

        table.attach(self.size_label, 0,1,0,1)
        table.attach(self.strength_label, 1, 2, 0, 1)

        size1 = gtk.Adjustment(value=10, lower=0, upper=100, step_incr=0.1, page_incr=0, page_size=0)
        strength1 = gtk.Adjustment(value=0.20, lower=0, upper=100, step_incr=0.01, page_incr=0, page_size=0)
        self.size1 = gtk.SpinButton(size1, digits=2)
        self.strength1 = gtk.SpinButton(strength1, digits=2)
        table.attach(self.size1, 0,1,1,2)
        table.attach(self.strength1, 1,2,1,2)

        size2 = gtk.Adjustment(value=10, lower=0, upper=100, step_incr=0.1, page_incr=0, page_size=0)
        strength2 = gtk.Adjustment(value=0.20, lower=0, upper=100, step_incr=0.01, page_incr=0, page_size=0)
        self.size2 = gtk.SpinButton(size2, digits=2)
        self.strength2 = gtk.SpinButton(strength2, digits=2)
        self.size2.set_text("10") 
        self.strength2.set_text("0.20") 
        table.attach(self.size2, 0,1,2,3)
        table.attach(self.strength2, 1,2,2,3)

        size3 = gtk.Adjustment(value=10, lower=0, upper=100, step_incr=0.1, page_incr=0, page_size=0)
        strength3 = gtk.Adjustment(value=0.20, lower=0, upper=100, step_incr=0.01, page_incr=0, page_size=0)
        self.size3 = gtk.SpinButton(size3, digits=2)
        self.strength3 = gtk.SpinButton(strength3, digits=2)
        self.size3.set_text("5") 
        self.strength3.set_text("0.20") 
        table.attach(self.size3, 0,1,3,4)
        table.attach(self.strength3, 1,2,3,4)

        self.show_all()


def python_triple_usm(img, drawable) :
    dialog = MyWindow(filename=os.path.basename(img.filename))
    response = dialog.run()
    if response != gtk.RESPONSE_OK:
       return


    pdb.plug_in_unsharp_mask(img, drawable, dialog.size1.get_text(), dialog.strength1.get_text(), 0)
    pdb.plug_in_unsharp_mask(img, drawable, dialog.size2.get_text(), dialog.strength2.get_text(), 0)
    pdb.plug_in_unsharp_mask(img, drawable, dialog.size3.get_text(), dialog.strength3.get_text(), 0)

register(
        "python_fu_triple_usm",
        "triple Unsharp mask",
        "triple Unsharp mask",
        "Michael Schoenitzer",
        "Michael Schoenitzer",
        "2015",
        "TripleUSM",
        "*",
        [
            (PF_IMAGE, "image", "Input image", None),
            (PF_DRAWABLE, "drawable", "Input drawable", None),
        ],
        [],
        python_triple_usm,
        menu = "<Image>/Filters/Enhance"
)

main()

