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
from gi.repository import Gegl
# from gi.repository import Babl
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio
import time
import sys

from gimphelpers import pdb_run

def N_(message): return message
def _(message): return GLib.dgettext(None, message)


def blobipy(procedure, run_mode, image, drawables, config, data):
    if run_mode == Gimp.RunMode.INTERACTIVE:
        GimpUi.init('python-fu-blobipy')
        dialog = GimpUi.ProcedureDialog(procedure=procedure, config=config)
        dialog.fill(None)
        if not dialog.run():
            dialog.destroy()
            return procedure.new_return_values(Gimp.PDBStatusType.CANCEL,
                                               GLib.Error())
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
    pdb_run('gimp-image-select-item', {
        'image': image,
        'operation': Gimp.ChannelOps.REPLACE,
        'item': drawables[0]
        })

    # Invert the selection:
    pdb_run('gimp-selection-invert', {
        'image': image
    })

    # Make a dropshadow from the inverted selection.
    # I hope these parameter labels change to real names instead of types.
    pdb_run('script-fu-drop-shadow', {
        'run-mode': Gimp.RunMode.NONINTERACTIVE,
        'image': image,
        'drawables': drawables,  # cast to Gimp.ObjectArray by gimphelpers
        'adjustment': -3,        # offset X
        'adjustment-2': -3,      # offset Y
        'adjustment-3': blur,
        'color': color,
        'adjustment-4': 80,      # opacity
        'toggle': False,         # allow resizing
        })

    # Finish and clean up
    Gimp.Selection.none(image)
    Gimp.displays_flush()
    image.undo_group_end()
    Gimp.context_pop()

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
        Gegl.init(None)

        black = Gegl.Color.new("black")
        black.set_rgba(0, 0, 0, 1)

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
        procedure.set_attribution("Akkana Peck", "Akkana Peck", "2009,2022,2024")
        procedure.add_menu_path ("<Image>/Filters/Light and Shadow")

        procedure.add_double_argument("blur", _("_Blur"), _("Blur"),
                                       0.0, 50.0, 7.0,
                                      GObject.ParamFlags.READWRITE)
        procedure.add_color_argument ("color",
                                      _("Shado_w color"), _("Shadow color"),
                                      True, black, GObject.ParamFlags.READWRITE)
        return procedure


Gimp.main(BlobiPy.__gtype__, sys.argv)
