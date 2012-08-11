#!/usr/bin/env python

# life.py: Play Conway's Game of Life on your image.

# Copyright 2010 by Akkana Peck, http://www.shallowsky.com/software/
# You may use and distribute this plug-in under the terms of the GPL.
#
# Thanks to Joao Bueno for some excellent tips on speeding up
# pixel ops in gimp-python!

import math
import time
from gimpfu import *
from array import array
import sys   # only needed for debugging

# FACTOR should be 256. * 3. if you want to use only black and white.
# Needs to be adjusted for colors, though.
# And also for image type (currently assumes nchannels == 3).
#FACTOR = 255 * 3.
# Life rules, adjusted for RGB (each neighbor can contribute up to 255*3)
NOTALIVE = 600
LONELY = 1230
NEWBORN = 1600
OVERCROWDED = 2295

NEWPXL = array("B", [ 180, 255, 180 ])
DYINGPXL = array("B", [ 80, 30, 30 ])
BLACK = array("B", [ 0, 0, 0 ])

def CA_rule(pixels, x, y, pos, width, height, nchannels=3) :
    oldval = pixels[pos : pos + nchannels]
    sumoldval = float(sum(oldval))
    #print pos, sumoldval

    # Calculate new value based on Life rules
    neighbors = 0
    for xx in range(x-1, x+2) :
        for yy in range(y-1, y+2) :
            if xx == x and yy == y : continue  # don't include self in sum
            dpos = (xx + width * yy) * nchannels
            s = int(sum(pixels[dpos : dpos + nchannels]) + .5)
            neighbors += s

    #print "(%d, %d): [%-3d %-3d %-3d]=%-3d, neighbors %-4d" % \
    #    (x, y, oldval[0], oldval[1], oldval[2], sumoldval, neighbors)
    #sys.stdout.flush()

    if neighbors < LONELY or neighbors > OVERCROWDED :
        # Pixel dies
        if sumoldval > NOTALIVE :
            return DYINGPXL
        else :
            # It is so ridiculous that python arrays can't handle
            # mathematical ops like oldval / 2
            return array("B", [ oldval[0]/2, oldval[1]/2, oldval[2]/2 ])

    elif sumoldval < NOTALIVE and neighbors > NEWBORN :
        # New one born
        return NEWPXL

    else :
        # pixel stays the same
        return oldval

def python_life_step(img, layer) :
    sys.stdout.flush()
    gimp.progress_init("Playing life ...")
    pdb.gimp_image_undo_group_start(img)

    width, height = layer.width, layer.height

    src_rgn = layer.get_pixel_rgn(0, 0, width, height, False, False)
    nchannels = len(src_rgn[0,0])
    src_pixels = array("B", src_rgn[0:width, 0:height])

    dst_rgn = layer.get_pixel_rgn(0, 0, width, height, True, True)
    dst_pixels = array("B", "\x00" * (width * height * nchannels))

    # Loop over the region:
    for x in xrange(0, width - 1) :
        for y in xrange(0, height) :
            pos = (x + width * y) * nchannels
            dst_pixels[pos : pos + nchannels] = CA_rule(src_pixels, x, y, pos,
                                                        width, height,
                                                        nchannels)

        progress = float(x)/layer.width
        if (int(progress * 100) % 20 == 0) :
            gimp.progress_update(progress)

    # Copy the whole array back to the pixel region:
    dst_rgn[0:width, 0:height] = dst_pixels.tostring() 

    layer.flush()
    layer.merge_shadow(True)
    layer.update(0, 0, width, height)

    pdb.gimp_image_undo_group_end(img)
    pdb.gimp_progress_end()

    pdb.gimp_displays_flush()

import gtk

class LifeWindow(gtk.Window):
    def __init__ (self, img, layer, *args):
        self.running = False
        self.img = img
        self.layer = layer
        win = gtk.Window.__init__(self, *args)
        self.set_border_width(10)

        # Obey the window manager quit signal:
        self.connect("destroy", gtk.main_quit)

        # Make the UI
        vbox = gtk.VBox(spacing=10, homogeneous=True)
        self.add(vbox)
        label = gtk.Label("Conway's Game of Life")
        vbox.add(label)
        label.show()
        hbox = gtk.HBox(spacing=20)

        btn = gtk.Button("Run")
        hbox.add(btn)
        btn.show()
        btn.connect("clicked", self.runstoplife)

        btn = gtk.Button("Single step")
        hbox.add(btn)
        btn.show()
        btn.connect("clicked", self.steplife)

        btn = gtk.Button("Cancel")
        hbox.add(btn)
        btn.show()
        btn.connect("clicked", gtk.main_quit)

        vbox.add(hbox)
        hbox.show()
        vbox.show()
        self.show()
        return win

    def steplife(self, widget) :
        python_life_step(self.img, self.layer)

    def runstoplife(self, widget) :
        if self.running :
            widget.set_label("Run")
            self.running = False
            return
        self.running = True
        widget.set_label("Stop")

        while self.running :
            python_life_step(self.img, self.layer)
            # Handle any button presses that have happened while we were busy
            while gtk.events_pending() :
                gtk.main_iteration()
 
def python_life(img, layer) :
    l = LifeWindow(img, layer)
    gtk.main()

register(
        "python_fu_life",
        "Conway's game of Life",
        "Conway's game of Life",
        "Akkana Peck",
        "Akkana Peck",
        "2010",
        "<Image>/Filters/Map/Life...",
        "RGB",        # Adjust for other types when code is more flexible
        [
        ],
        [],
        python_life)

main()
