#!/usr/bin/env python3

# A port of pandora-combine.scm for GIMP 3.0 Python
# Copyright 2025 by Akkana Peck, share and enjoy under the GPL v2 or later.

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import Gegl
from gi.repository import GObject
from gi.repository import GLib
# from gi.repository import Gio

import sys


def N_(message): return message
def _(message): return GLib.dgettext(None, message)


class Pandora (Gimp.PlugIn):
    ## GimpPlugIn virtual methods ##
    def do_set_i18n(self, procname):
        return True, 'gimp30-python', None

    def do_query_procedures(self):
        return [ 'python-fu-pandora-combine' ]

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            self.pandora_combine, None)
        procedure.set_image_types("RGB*, GRAY*");

        procedure.set_sensitivity_mask (Gimp.ProcedureSensitivityMask.DRAWABLE |
                                        Gimp.ProcedureSensitivityMask.DRAWABLES)
        procedure.set_documentation (_("Arrange layers as a panorama"),
                                     _("Arrange layers as a panorama"),
                                     name)
        procedure.set_menu_label(_("_Pandora combine..."))
        procedure.set_attribution("Akkana Peck",
                                  "Akkana Peck",
                                  "2025")
        procedure.add_menu_path ("<Image>/Filters/Combine")

        procedure.add_int_argument("overlap",
                                   _("How much (percent) should layers overlap?"),
                                   _("How much (percent) should layers overlap?"),
                                   0, 100, 50, GObject.ParamFlags.READWRITE)
        procedure.add_boolean_argument("right_on_top",
                                       _("Rightmost layer on top?"),
                                       _("Should the rightmost layer be on top?"),
                                       True, GObject.ParamFlags.READWRITE)
        procedure.add_boolean_argument("use_masks",
                                       _("Use layer masks"),
                                       _("Use layer masks to fade each layer into the next"),
                                       True, GObject.ParamFlags.READWRITE)

        return procedure

    def pandora_combine(self, procedure, run_mode, image, drawables,
                        config, data):
        if run_mode == Gimp.RunMode.INTERACTIVE:
            GimpUi.init('python-fu-pandora-combine')

            dialog = GimpUi.ProcedureDialog(procedure=procedure, config=config)
            dialog.fill(None)
            if not dialog.run():
                dialog.destroy()
                return procedure.new_return_values(Gimp.PDBStatusType.CANCEL,
                                                   GLib.Error())
            else:
                dialog.destroy()

        overlap      = config.get_property('overlap')
        right_on_top = config.get_property('right_on_top')
        use_masks    = config.get_property('use_masks')

        Gimp.context_push()
        image.undo_group_start()

        # Get a list of all real (non-floating) layers
        layers = [ l for l in image.get_layers() if not l.is_floating_sel() ]
        num_layers = len(layers)

        bottomlayer = layers[-1]

        # Pandora assumes that all layers are the same size as the first:
        # XXX change this eventually.
        layer_width = bottomlayer.get_width()
        layer_height = bottomlayer.get_height()
        overlap_frac = overlap / 100.
        extra_frac = (1 - overlap_frac)

        pan_img_w = layer_width * (1 + (num_layers - .3) * (1 - overlap_frac))
        pan_img_h = layer_height * 1.5
        # print("New image will be", pan_img_w, pan_img_h)
        image.resize(pan_img_w, pan_img_h, 0, 0)
        newy = layer_height * .25

        black = Gegl.Color.new("black")
        white = Gegl.Color.new("white")

        for i, thislayer in reversed(list(enumerate(layers))):
            this_w = thislayer.get_width()
            if right_on_top:
                newx = ((num_layers - i) - 1) * this_w * extra_frac
            else:
                newx = i * this_w * extra_frac

            thislayer.transform_translate(newx, newy)

            # Don't create the mask on the last image, or if the
            # image already has a mask
            if use_masks and not thislayer.get_mask() and i < num_layers - 1:
                masklayer = thislayer.create_mask(0)
                grad_w = this_w * overlap_frac * .5
                if right_on_top:
                    grad_start = grad_w
                    grad_end = 0
                else:
                    grad_start = this_w - grad_w
                    grad_end = this_w

                thislayer.add_alpha()
                thislayer.add_mask(masklayer)
                Gimp.context_set_foreground(white)
                Gimp.context_set_background(black)

                masklayer.edit_gradient_fill(0, # gradient-type GRADIENT_LINEAR
                                             0, # offset
                                             False, 0, 0, # supersample
                                             False,       # dither
                                             grad_start, 0, grad_end, 0)
                thislayer.set_edit_mask(False)

        # Finish and clean up
        Gimp.Selection.none(image)
        Gimp.displays_flush()
        image.undo_group_end()
        Gimp.context_pop()

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS,
                                           GLib.Error())


Gimp.main(Pandora.__gtype__, sys.argv)
