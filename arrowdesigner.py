#!/usr/bin/env python

# Draw arrows in GIMP, using the selection as a guide for where to draw.
#
# Copyright 2010,2011 by Akkana Peck, http://www.shallowsky.com/software/
# plus contributions from Robert Brizard.
# You may use and distribute this plug-in under the terms of the GPL.

from gimpfu import *
import gtk, pango
from gobject import timeout_add

# Direction "enums"
DIREC_N, DIREC_NE, DIREC_E, DIREC_SE, DIREC_S, DIREC_SW, DIREC_W, DIREC_NW \
    = range(8)

def python_fu_arrow_from_selection(img, layer, arrowangle, arrowsize,
                                   x1, y1, x2, y2, cyc) :
    """
    Draw an arrow from (x1, y1) to (x2, y2) with the head at (x2, y2).
    The size of the arrowhead (isocele triangle and arrowsize is the length of the isoside)
    is controlled by 'arrowsize', and the angle of it by 'arrowangle'.
    'cyc' is the wanted integer number of gradient length in the shaft.
    """
    # Save the current selection:
    savesel = pdb.gimp_selection_save(img)
    pdb.gimp_selection_none(img)

    aangle = arrowangle * math.pi / 180.

    #
    # Draw the line first.
    # But don't go quite all the way to the end, because that
    # would make a rounded tip where the arrow point should be.
    #
    strokes = [ x1, y1, x2, y2 ]
    dy = y2 - y1
    dx = x2 - x1
    # length of arrowhead in the shaft direction
    l_head = arrowsize * math.cos(aangle)

    l_arrow = math.sqrt(dx*dx + dy*dy)
    # ratio is length_head/length_arrow, if >= 1 no line
    ratio = l_head / l_arrow * 0.5
    if ratio < 1.0 :
        # from similar triangles
        strokes[2] -= int(round(ratio*dx))
        strokes[3] -= int(round(ratio*dy))
        
        # compute the length of the gradient cycle wanted
        if cyc > 0: cycl_grad = int((l_arrow - l_head)/cyc)
        elif cyc == 0: cycl_grad = 0

        pdb.gimp_paintbrush(layer, 0, 4, strokes, 0, cycl_grad)

    #
    # Now make the arrowhead
    #
    theta = math.atan2(y2-y1, x2-x1)
    points = [ x2, y2,
               int(x2 - arrowsize * math.cos(theta - aangle)),
               int(y2 - arrowsize * math.sin(theta - aangle)),
               int(x2 - arrowsize * math.cos(theta + aangle)),
               int(y2 - arrowsize * math.sin(theta + aangle)) ]
    # Only draw the head if the 3 points aren't collinear.
    # Otherwise, it can fill the whole arrow layer:
    # e.g. try arrow size 1, arrow angle < 30.
    if int(l_head) > 1 and  points[2:4] != points[4:6] :
        # Select the arrowhead shape
        pdb.gimp_image_select_polygon(img, CHANNEL_OP_REPLACE, 6, points)
        # Fill the arrowhead
        pdb.gimp_edit_fill(layer, FOREGROUND_FILL)
        
    # Restore the old selection
    pdb.gimp_image_select_item(img, CHANNEL_OP_REPLACE, savesel)

def direc_to_coords(x1, y1, x2, y2, direction) :
    if direction == DIREC_N :
        return x1, y2, x1, y1
    elif direction == DIREC_NE :
        return x1, y2, x2, y1
    elif direction == DIREC_E :
        return x1, y1, x2, y1
    elif direction == DIREC_SE :
        return x1, y1, x2, y2
    elif direction == DIREC_S :
        return x1, y1, x1, y2
    elif direction == DIREC_SW :
        return x2, y1, x1, y2
    elif direction == DIREC_W :
        return x2, y1, x1, y1
    elif direction == DIREC_NW :
        return x2, y2, x1, y1
    
class ArrowWindow(gtk.Window):
    def __init__ (self, img, *args):
        self.img = img
        self.x1, self.y1, self.x2, self.y2 = 0, 0, 0, 0

        self.direction = DIREC_N
        self.changed = False
        self.arrowsize = 30
        self.arrowangle = 25
        self.num_grad = 0

        # Make a new GIMP layer to draw on
        self.layer = gimp.Layer(img, "arrow", img.width, img.height,
                                RGBA_IMAGE, 100, NORMAL_MODE)
        img.add_layer(self.layer, 0)

        # Create the dialog
        win = gtk.Window.__init__(self, *args)
        self.set_title("GIMP arrow tool")
        #self.set_keep_above(True) # keep the window on top

        # Obey the window manager quit signal:
        self.connect("destroy", gtk.main_quit)

        # Make the UI
        self.set_border_width(10)
        vbox = gtk.VBox(spacing=10, homogeneous=False)
        self.add(vbox)
        label = gtk.Label("Arrow designer  by Akkana Peck\nMake a rectangular selection. Will use active colors, brush and gradient.")

        # Change color of the label first line R. B.
        attr = pango.AttrList()
        fg_color = pango.AttrForeground(0, 0, 65535, 0, 30)
        size = pango.AttrSize(17000, 0, 14)
        bold = pango.AttrWeight(pango.WEIGHT_ULTRABOLD, 0, 14)
        attr.insert(fg_color)
        attr.insert(size)
        attr.insert(bold)
        label.set_attributes(attr)

        vbox.add(label)
        label.show()

        table = gtk.Table(rows=3, columns=2, homogeneous=False)
        table.set_col_spacings(10)
        vbox.add(table)

        # Arrow size and sharpness
        label = gtk.Label("Arrowhead size (px)")
        label.set_alignment(xalign=0.0, yalign=1.0)
        table.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0)
        label.show()
        adj = gtk.Adjustment(self.arrowsize, 1, 200, 1)
        adj.connect("value_changed", self.arrowsize_cb)
        scale = gtk.HScale(adj)
        scale.set_digits(0)
        table.attach(scale, 1, 2, 0, 1)
        scale.show()

        label = gtk.Label("Arrowhead angle (°)")
        label.set_alignment(xalign=0.0, yalign=1.0)
        table.attach(label, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0)
        label.show()
        adj = gtk.Adjustment(self.arrowangle, 1, 80, 1)
        adj.connect("value_changed", self.arrowangle_cb)
        scale = gtk.HScale(adj)
        scale.set_digits(0)
        table.attach(scale, 1, 2, 1, 2)
        scale.show()

        label = gtk.Label("Gradient repetitions")
        label.set_alignment(xalign=0.0, yalign=1.0)
        table.attach(label, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0)
        label.show()
        adj = gtk.Adjustment(self.num_grad, 0, 50, 1)
        adj.connect("value_changed", self.num_grad_cb)
        scale = gtk.HScale(adj)
        scale.set_digits(0)
        table.attach(scale, 1, 2, 2, 3)
        scale.show()

        table.show()

        # Selector for arrow direction
        hbox = gtk.HBox(spacing=5)

        btn = gtk.RadioButton(None, "N")
        btn.set_active(True)
        btn.connect("toggled", self.direction_cb, DIREC_N)
        hbox.add(btn)
        btn.show()
        btn = gtk.RadioButton(btn, "NE")
        btn.connect("toggled", self.direction_cb, DIREC_NE)
        hbox.add(btn)
        btn.show()
        btn = gtk.RadioButton(btn, "E")
        btn.connect("toggled", self.direction_cb, DIREC_E)
        hbox.add(btn)
        btn.show()
        btn = gtk.RadioButton(btn, "SE")
        btn.connect("toggled", self.direction_cb, DIREC_SE)
        hbox.add(btn)
        btn.show()
        btn = gtk.RadioButton(btn, "S")
        btn.connect("toggled", self.direction_cb, DIREC_S)
        hbox.add(btn)
        btn.show()
        btn = gtk.RadioButton(btn, "SW")
        btn.connect("toggled", self.direction_cb, DIREC_SW)
        hbox.add(btn)
        btn.show()
        btn = gtk.RadioButton(btn, "W")
        btn.connect("toggled", self.direction_cb, DIREC_W)
        hbox.add(btn)
        btn.show()
        btn = gtk.RadioButton(btn, "NW")
        btn.connect("toggled", self.direction_cb, DIREC_NW)
        hbox.add(btn)
        btn.show()

        vbox.add(hbox)
        hbox.show()

        # Make the dialog buttons box
        hbox = gtk.HBox(spacing=20)
        
        btn = gtk.Button("Next arrow")
        btn.connect("pressed", self.next_arrow)
        hbox.add(btn)
        btn.show()
        
        btn = gtk.Button("Close")
        btn.connect("clicked", gtk.main_quit)
        hbox.add(btn)
        btn.show()

        vbox.add(hbox)
        hbox.show()
        vbox.show()
        self.show()

        timeout_add(300, self.update, self)    

        return win

    def direction_cb(self, widget, data=None) :
        self.direction = data
        self.changed = True

    def arrowsize_cb(self, val) :
        self.arrowsize = val.value
        self.changed = True

    def arrowangle_cb(self, val) :
        self.arrowangle = val.value
        self.changed = True

    def num_grad_cb(self, val) :
        self.num_grad = val.value
        self.changed = True

    def arrow(self, x1, y1, x2, y2) :
        python_fu_arrow_from_selection(self.img, self.layer,
                                       self.arrowangle, self.arrowsize,
                                       x1, y1, x2, y2, self.num_grad)

    def update(self, *args):
        exists, x1, y1, x2, y2 = pdb.gimp_selection_bounds(self.img)
        timeout_add(500, self.update, self)
        if not exists :
            return   # No selection, no arrow
        if (self.x1, self.y1, self.x2, self.y2) == (x1, y1, x2, y2) \
                and not self.changed :
            return
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.changed = False

        # Clear the layer, erasing the old arrow
        self.layer.fill(TRANSPARENT_FILL)

        # Draw the new arrow.
        # Order is from, to: arrowhead goes on second X, Y pair.
        x1, y1, x2, y2 = direc_to_coords(x1, y1, x2, y2, self.direction)
        self.arrow(x1, y1, x2, y2)

        pdb.gimp_displays_flush()

    def next_arrow(self, data=None):
        # pdb.gimp_selection_none(self.img)
        # Make a new GIMP layer to draw on
        self.layer = gimp.Layer(self.img, "arrow", self.img.width, self.img.height,
                                RGBA_IMAGE, 100, NORMAL_MODE)
        self.img.add_layer(self.layer, 0)
        pdb.gimp_displays_flush()
    
def arrow_designer(image, layer):
    image.undo_group_start()
    
    r = ArrowWindow(image)
    gtk.main()
        
    # pdb.gimp_selection_none(image)
    image.undo_group_end()

def arrow_from_selection(img, layer, angle, size, direction) :
    exists, x1, y1, x2, y2 = pdb.gimp_selection_bounds(img)
    if not exists :
        return

    x1, y1, x2, y2 = direc_to_coords(x1, y1, x2, y2, direction)

    python_fu_arrow_from_selection(img, layer, angle, size, x1, y1, x2, y2, 0)

register(
         "python_fu_arrow_interactive",
         "Draw an arrow following the selection (interactive).",
             # + "From: " + str(__file__),
         "Draw an arrow following the current selection, updating as the selection changes",
         "Akkana Peck", "Akkana Peck",
         "2010,2011",
         "<Image>/Filters/Render/Arrow designer...",
         "*",
         [
         ],
         [],
         arrow_designer)

register(
         "python_fu_arrow_from_selection",
         "Draw an arrow following the current selection",
         "Draw an arrow following the current selection",
         "Akkana Peck", "Akkana Peck",
         "2010,2011",
         "<Image>/Filters/Render/Arrow from selection...",
         "*",
         [
           (PF_SLIDER, "angle",  "Arrow angle", 30, (0, 200, 1)),
           (PF_SLIDER, "size",  "Arrow size", 25, (0, 80, 1)),
           (PF_OPTION, "direction", "Direction", 2,
            ("N", "NE", "E", "SE", "S", "SW", "W", "NW")),
         ],
         [],
         arrow_from_selection)

main()
