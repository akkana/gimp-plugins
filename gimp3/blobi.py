#!/usr/bin/env python3
#   Copyright (C) 2022 Akkana Peck <akkana@shallowsky.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio
import time
import sys

def N_(message): return message
def _(message): return GLib.dgettext(None, message)


def blobipy(procedure, run_mode, image, n_drawables, drawables, args, data):
    config = procedure.create_config()
    config.begin_run(image, run_mode, args)

    if run_mode == Gimp.RunMode.INTERACTIVE:
        GimpUi.init('python-fu-blobipy')
        dialog = GimpUi.ProcedureDialog(procedure=procedure, config=config)
        dialog.fill(None)
        if not dialog.run():
            dialog.destroy()
            config.end_run(Gimp.PDBStatusType.CANCEL)
            return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, GLib.Error())
        else:
            dialog.destroy()

    color      = config.get_property('color')
    blur       = config.get_property('blur')

    Gimp.context_push()
    image.undo_group_start()

    # Alpha to selection. pdb.gimp_selection_layer_alpha(layer)
    # is deprecated and replaced by gimp-image-select-item.
    # The arguments are image (GimpImage), operation (GimpChannelOps)
    # and item (GimpItem).
    Gimp.get_pdb().run_procedure('gimp-image-select-item', [
        GObject.Value(Gimp.Image, image),
        # Gimp.ChannelOps.REPLACE is an enum
        GObject.Value(GObject.TYPE_INT, Gimp.ChannelOps.REPLACE),
        GObject.Value(Gimp.Drawable, drawables[0])
    ])

    # Invert the selection:
    Gimp.get_pdb().run_procedure('gimp-selection-invert', [
        GObject.Value(Gimp.Image, image),
    ])

    # Make a dropshadow from the inverted selection
    Gimp.get_pdb().run_procedure('script-fu-drop-shadow', [
        GObject.Value(Gimp.RunMode, Gimp.RunMode.NONINTERACTIVE),
        GObject.Value(Gimp.Image, image),
        GObject.Value(Gimp.Drawable, drawables[0]),
        GObject.Value(GObject.TYPE_INT, -3),      # offset X
        GObject.Value(GObject.TYPE_INT, -3),      # offset Y
        GObject.Value(GObject.TYPE_INT, blur),    # blur in pixels
        # Should color be cast into some GObject type? What type?
        # There is no GObject.TYPE_COLOR
        color,
        GObject.Value(GObject.TYPE_INT, 80), # opacity
        GObject.Value(GObject.TYPE_BOOLEAN, False) # allow resizing
    ])

    # Finish and clean up
    Gimp.Selection.none(image)
    image.undo_group_end()
    Gimp.context_pop()

    config.end_run(Gimp.PDBStatusType.SUCCESS)

    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


class BlobiPy(Gimp.PlugIn):
    ## Parameters ##
    __gproperties__ = {
        "blur": (int,
                 _("Blur amout"),
                 _("Blur amount"),
                 0, 50, 7,
                 GObject.ParamFlags.READWRITE),
    }

    ## GimpPlugIn virtual methods ##
    def do_set_i18n(self, procname):
        return True, 'gimp30-python', None

    def do_query_procedures(self):
        return [ 'python-fu-blobipy' ]

    def do_create_procedure(self, name):
        # Workaround copied from foggify.py until GIMP can handle color args
        # in the regular __gproperties__ list
        black = Gimp.RGB()
        black.set(0, 0, 0)
        color = GObject.Property(type =Gimp.RGB, default=black,
                                 nick =_("_Shadow color"),
                                 blurb=_("Shadow color"))

        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            blobipy, None)
        procedure.set_image_types("RGB*, GRAY*");
        procedure.set_sensitivity_mask (Gimp.ProcedureSensitivityMask.DRAWABLE |
                                        Gimp.ProcedureSensitivityMask.DRAWABLES)
        procedure.set_documentation(_("Create a 3-D effect"),
                                    _("Create a blobby 3-D effect "
                                      "using an inverse drop-shadow."),
                                    name)
        procedure.set_menu_label(_("_BlobiPy..."))
        procedure.set_attribution("Akkana Peck", "Akkana Peck", "2009,2022")
        procedure.add_menu_path ("<Image>/Filters/Light and Shadow")

        procedure.add_argument_from_property(self, "blur")
        procedure.add_argument_from_property(self, "color")
        return procedure


Gimp.main(BlobiPy.__gtype__, sys.argv)
