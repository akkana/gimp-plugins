#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Draw arrows in GIMP, using the selection as a guide for where to draw.
# Updated for GIMP 3.0+ API.
#
# Copyright 2010,2011,2020,2022 by Akkana, http://www.shallowsky.com/software/
# plus contributions from Robert Brizard.
# You may use and distribute this plug-in under the terms of the GPL.

# GIMP 3 API: Still one problem left to figure out:
# gimp_plug_in_destroy_proxies: ERROR: GimpImage proxy with ID 1 was refed by plug-in, it MUST NOT do that!


import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
gi.require_version('Gegl', '0.4')
from gi.repository import Gegl
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Pango

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

import math
import sys, os

# Direction "enums"
DIREC_N, DIREC_NE, DIREC_E, DIREC_SE, DIREC_S, DIREC_SW, DIREC_W, DIREC_NW \
    = range(8)


class ArrowDesigner (Gimp.PlugIn):
    ## Parameters ##
    __gproperties__ = {
        "angle": (int,
                  "Angle",
                  "Arrowhead Angle",
                  0, 360, 40,
                  GObject.ParamFlags.READWRITE),
        "size": (int,
                 "Size",
                 "Arrowhead Size",
                 0, 80, 25,
                 GObject.ParamFlags.READWRITE),
        "direction": (int,
                      "Direction",
                      "Direction",
                      0, 8, 0,
                      GObject.ParamFlags.READWRITE),
    }

    ## GimpPlugIn virtual methods ##
    def do_set_i18n(self, procname):
        return True, 'gimp30-python', None

    def do_query_procedures(self):
        return [ "python-fu-arrow-designer" ]

    def do_create_procedure(self, name):
        """Register as a GIMP plug-in"""
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            self.show_arrowdesigner, None)

        procedure.set_image_types("*");

        procedure.set_menu_label("_Arrow Designer");
        procedure.set_icon_name(GimpUi.ICON_GEGL);
        procedure.add_menu_path('<Image>/Filters/Render/');

        # Add parameters
        procedure.add_argument_from_property(self, "angle")
        procedure.add_argument_from_property(self, "size")
        procedure.add_argument_from_property(self, "direction")

        procedure.set_documentation(
            "Draw an arrow based on the selection",
            "Draw an arrow based on the current selection, "
            "updating interactively as the selection changes",
            name);
        procedure.set_attribution("Akkana Peck", "Akkana Peck",
                                  "2010,2011,2022,2023");

        return procedure

    def show_arrowdesigner(self, procedure, run_mode, image, n_layers, layers,
                           config, data):
        angle = config.get_property("angle")
        size = config.get_property("size")
        direction = config.get_property("direction")

        if run_mode == Gimp.RunMode.INTERACTIVE:
            GimpUi.init("arrowdesigner")

            r = ArrowWindow(image, angle, size, direction)
            Gtk.main()
        else:
            print("Non-interactive arrow designer, I'm not sure what to do!",
                  file=sys.stderr)

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS,
                                           GLib.Error())


def python_fu_arrow_from_selection(img, layer, arrowangle, arrowsize,
                                   x1, y1, x2, y2, cyc) :
    """
    Draw an arrow from (x1, y1) to (x2, y2) with the head at (x2, y2).
    The the arrowhead is an isoceles triangle where arrowsize controls
    the length of the isoside; the tip angle is arrowangle.
    'cyc' is the wanted integer number of gradient length in the shaft.
    The arrow's shaft is whatever size and brush set for the Paintbrush tool.
    """

    # Save the current selection:
    savesel = img.get_selection().save(img)   # a Gimp.Channel object
    Gimp.Selection.none(img)
    sys.stdout.flush()

    aangle = arrowangle * math.pi / 360.

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

        # TypeError: Gimp.paintbrush() takes exactly 5 arguments (6 given)
        Gimp.paintbrush(layer, 0, strokes, Gimp.StrokeMethod.LINE,
                        cycl_grad)

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
        # XXX This doesn't work: if I pass just points, it raises
        # TypeError: Gimp.paintbrush() takes exactly 3 arguments (4 given)
        # but the signature definitely has 6 args, might be related to
        # https://gitlab.gnome.org/GNOME/gimp/-/issues/5312#note_947177
        # Trying Gimp.ValueArray errors saying that Gimp.ValueArray
        # expects one argument, a number, but it's not clear what
        # that number is supposed to be.
        img.select_polygon(Gimp.ChannelOps.REPLACE, points)

        # Fill the arrowhead
        layer.edit_fill(Gimp.FillType.FOREGROUND)
    else:
        print("Not filling, but tastes great")
        sys.stdout.flush()
        # Should stroke the selection

    # Restore the old selection
    img.select_item(Gimp.ChannelOps.REPLACE, savesel)

    savesel = None
    img = None


def direc_to_coords(x1, y1, x2, y2, direction):
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


class ArrowWindow(Gtk.Window):
    def __init__ (self, img, angle, size, direction):
        self.img = img
        self.x1, self.y1, self.x2, self.y2 = 0, 0, 0, 0

        self.arrowangle = angle
        self.arrowsize = size
        self.direction = direction

        self.changed = False
        self.num_grad = 0

        self.bounds = None

        # Make a new GIMP layer to draw on
        self.layer = Gimp.Layer.new(img, "arrow",
                                    img.get_width(), img.get_height(),
                                    Gimp.ImageType.RGBA_IMAGE, 100,
                                    Gimp.LayerMode.NORMAL)
        # XXX layer needn't be img wxh, should be the size of the selection.
        img.insert_layer(self.layer, None, 0)

        # Create the dialog
        win = Gtk.Window.__init__(self)
        self.set_title("GIMP Arrow Designer")

        # Mac may have a problem with the window disappearing below
        # the image window. But on small screens, the window is big
        # enough that it can block a lot of the image window.
        # Ideally, it would be nice to make sure it's initially
        # on top, but then let the user hide it later.
        # Or make a checkbox for it in the dialog, but that would
        # make the dialog even bigger.
        #self.set_keep_above(True) # keep the window on top

        # Obey the window manager quit signal:
        self.connect("destroy", Gtk.main_quit)

        self.set_border_width(10)
        vbox = Gtk.VBox(spacing=10, homogeneous=False)
        self.add(vbox)
        label = Gtk.Label(label="""Arrow designer  by Akkana
Make a rectangular selection and adjust the arrowhead size and angle.
Uses the selection, Paintbrush brush foreground color and gradient.""")

        # Change color of the label first line R. B.
        # But nobody seems to know how to do this sort of thing
        # in the GI world.
        # attr = Pango.AttrList()
        # fg_color = Pango.AttrForeground(0, 0, 65535, 0, 30)
        # size = Pango.AttrSize(17000, 0, 14)
        # bold = Pango.AttrWeight(Pango.WEIGHT_ULTRABOLD, 0, 14)
        # attr.insert(fg_color)
        # attr.insert(size)
        # attr.insert(bold)
        # label.set_attributes(attr)

        vbox.add(label)
        label.show()

        table = Gtk.Table(n_rows=3, n_columns=2, homogeneous=False)
        # Deprecated:
        # table.set_col_spacings(10)
        vbox.add(table)

        # Arrow size and sharpness
        label = Gtk.Label(label="Arrowhead size (px)")
        # label.set_alignment(xalign=0.0, yalign=1.0)
        table.attach(label, 0, 1, 0, 1,
                     xoptions=Gtk.AttachOptions.FILL, yoptions=0)
        label.show()
        scale = Gtk.Scale.new_with_range(min=0, max=400, step=1.,
                                         orientation=Gtk.Orientation.HORIZONTAL)
        scale.set_digits(0)
        scale.set_value(self.arrowsize)
        scale.connect("value_changed", self.arrowsize_cb)
        table.attach(scale, 1, 2, 0, 1)
        scale.show()

        label = Gtk.Label(label="Arrowhead angle (°)")
        # label.set_alignment(xalign=0.0, yalign=1.0)
        table.attach(label, 0, 1, 1, 2,
                     xoptions=Gtk.AttachOptions.FILL, yoptions=0)
        label.show()
        scale = Gtk.Scale.new_with_range(min=1., max=80, step=1.,
                                         orientation=Gtk.Orientation.HORIZONTAL)
        scale.set_digits(0)
        scale.set_value(self.arrowangle)
        scale.connect("value_changed", self.arrowangle_cb)
        table.attach(scale, 1, 2, 1, 2)
        scale.show()

        label = Gtk.Label(label="Gradient repetitions")
        # XXX DeprecationWarning: Gtk.Misc.set_alignment is deprecated
        # and I haven't found a new way that works in GTK3.
        # label.set_alignment(xalign=0.0, yalign=1.0)
        table.attach(label, 0, 1, 2, 3,
                     xoptions=Gtk.AttachOptions.FILL, yoptions=0)
        label.show()
        scale = Gtk.Scale.new_with_range(min=1., max=50, step=1.,
                                         orientation=Gtk.Orientation.HORIZONTAL)
        scale.set_digits(0)
        scale.set_value(self.num_grad)
        scale.connect("value_changed", self.num_grad_cb)
        table.attach(scale, 1, 2, 2, 3)
        scale.show()

        table.show()

        # Selector for arrow direction
        hbox = Gtk.HBox(spacing=5)

        btn = Gtk.RadioButton(group=None, label="N")
        btn.set_active(True)
        btn.connect("toggled", self.direction_cb, DIREC_N)
        hbox.add(btn)
        btn.show()
        btn = Gtk.RadioButton(group=btn, label="NE")
        btn.connect("toggled", self.direction_cb, DIREC_NE)
        hbox.add(btn)
        btn.show()
        btn = Gtk.RadioButton(group=btn, label="E")
        btn.connect("toggled", self.direction_cb, DIREC_E)
        hbox.add(btn)
        btn.show()
        btn = Gtk.RadioButton(group=btn, label="SE")
        btn.connect("toggled", self.direction_cb, DIREC_SE)
        hbox.add(btn)
        btn.show()
        btn = Gtk.RadioButton(group=btn, label="S")
        btn.connect("toggled", self.direction_cb, DIREC_S)
        hbox.add(btn)
        btn.show()
        btn = Gtk.RadioButton(group=btn, label="SW")
        btn.connect("toggled", self.direction_cb, DIREC_SW)
        hbox.add(btn)
        btn.show()
        btn = Gtk.RadioButton(group=btn, label="W")
        btn.connect("toggled", self.direction_cb, DIREC_W)
        hbox.add(btn)
        btn.show()
        btn = Gtk.RadioButton(group=btn, label="NW")
        btn.connect("toggled", self.direction_cb, DIREC_NW)
        hbox.add(btn)
        btn.show()

        vbox.add(hbox)
        hbox.show()

        # Make the dialog buttons box
        hbox = Gtk.HBox(spacing=20)

        btn = Gtk.Button(label="Next arrow")
        btn.connect("pressed", self.next_arrow)
        hbox.add(btn)
        btn.show()

        btn = Gtk.Button(label="Close")
        btn.connect("clicked", self.close_window)
        hbox.add(btn)
        btn.show()

        vbox.add(hbox)
        hbox.show()
        vbox.show()
        self.show()

        GLib.timeout_add(300, self.update, self)

        return win

    def close_window(self, widget) :
        # Autocrop our new layer before closing.
        # autocrop_layer crops the current layer using the layer
        # passed in as its crop template -- not clear from the doc.
        self.img.active_layer = self.layer
        pdb = Gimp.get_pdb()
        pdb_proc = pdb.lookup_procedure('plug-in-autocrop-layer')
        pdb_config = pdb_proc.create_config()
        pdb_config.set_property('run-mode', Gimp.RunMode.NONINTERACTIVE)
        pdb_config.set_property('image', self.img)
        pdb_config.set_property('drawable', self.layer)
        result = pdb_proc.run(pdb_config)

        # Unreference image and layer references to try to avoid
        # gimp_plug_in_destroy_proxies: ERROR: GimpImage proxy with ID 1 was refed by plug-in, it MUST NOT do that!
        # and it does remove some of those lines, but there's still one left.
        self.img = None
        self.layer = None

        Gtk.main_quit()

    def direction_cb(self, widget, data=None) :
        self.direction = data
        self.changed = True

    def arrowsize_cb(self, val) :
        self.arrowsize = val.get_value()
        self.changed = True

    def arrowangle_cb(self, val) :
        self.arrowangle = val.get_value()
        self.changed = True

    def num_grad_cb(self, val) :
        self.num_grad = val.get_value()
        self.changed = True

    def arrow(self, x1, y1, x2, y2) :
        python_fu_arrow_from_selection(self.img, self.layer,
                                       self.arrowangle, self.arrowsize,
                                       x1, y1, x2, y2, self.num_grad)

    def update(self, *args):
        # print("Update")
        # sys.stdout.flush()
        # The docs don't say what the first arg from bounds is.
        newbounds = Gimp.Selection.bounds(self.img)
        dummy, exists, x1, y1, x2, y2 = newbounds
        if exists and (self.changed or newbounds != self.bounds):
            self.bounds = newbounds
            sys.stdout.flush()
            self.changed = False
            self.layer.fill(Gimp.FillType.TRANSPARENT)

            # Draw the new arrow.
            # Order is from, to: arrowhead goes on second X, Y pair.
            x1, y1, x2, y2 = direc_to_coords(x1, y1, x2, y2, self.direction)
            self.arrow(x1, y1, x2, y2)

            Gimp.displays_flush()

        # Whether just redrawn or not, schedule the next timeout
        GLib.timeout_add(500, self.update, self)

    def next_arrow(self, data=None):
        # pdb.gimp_selection_none(self.img)
        # Make a new GIMP layer to draw on
        self.layer = Gimp.Layer(self.img, "arrow",
                                self.img.get_width(), self.img.get_height(),
                                RGBA_IMAGE, 100, NORMAL_MODE)
        self.img.add_layer(self.layer, 0)
        Gimp.displays_flush()


def arrow_designer(image, layer):
    image.undo_group_start()

    r = ArrowWindow(image)
    Gtk.main()

    # pdb.gimp_selection_none(image)
    image.undo_group_end()


def arrow_from_selection(img, layer, angle, size, direction) :
    exists, x1, y1, x2, y2 = Gimp.selection.bounds(img)
    if not exists :
        return

    x1, y1, x2, y2 = direc_to_coords(x1, y1, x2, y2, direction)

    python_fu_arrow_from_selection(img, layer, angle, size, x1, y1, x2, y2, 0)


Gimp.main(ArrowDesigner.__gtype__, sys.argv)
