#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    This program is free software: you can redistribute it and/or modify
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
gi.require_version('Gegl', '0.4')
from gi.repository import Gegl
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio
import sys, os

# goat-exercise imports these only if INTERACTIVE,
# but when I try that, I get an exception because Gtk isn't defined.
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

import gettext
_ = gettext.gettext
def N_(message): return message


class BlobiPy (Gimp.PlugIn):
    def do_query_procedures(self):
        # Localization
        self.set_translation_domain("gimp30-python",
                                    Gio.file_new_for_path(Gimp.locale_directory()))

        return [ "blobipy" ]

    def do_create_procedure(self, name):
        """Register as a GIMP plug-in"""
        procedure = Gimp.ImageProcedure.new(self, name,
                                       Gimp.PDBProcType.PLUGIN,
                                       self.run, None)

        procedure.set_image_types("*");

        procedure.set_menu_label("BlobiPy");
        procedure.set_icon_name(GimpUi.ICON_GEGL);
        # procedure.add_menu_path('<Image>/Image/Light and Shadow/');
        procedure.add_menu_path('<Image>/Filters/');

        procedure.set_documentation("Make a layer look blobby and puffed out",
                                    "Make a layer look blobby and puffed out",
                                    name);
        procedure.set_attribution("Akkana Peck", "Akkana Peck", "2003,2020");

        return procedure

    def python_blobify(self, img, layer, blur):
        """The function that actually does the work"""

        Gimp.get_pdb().run_procedure('gimp-image-undo-group-start',
                                     [GObject.Value(Gimp.Image, img)])

        Gimp.get_pdb().run_procedure('gimp-image-select-item',
                                     [ GObject.Value(Gimp.Image, img),
                                       Gimp.ChannelOps.REPLACE,
                                       GObject.Value(Gimp.Item, layer) ])

        Gimp.get_pdb().run_procedure('gimp-selection-invert',
                                     [GObject.Value(Gimp.Image, img)])
        c = Gimp.RGB()
        c.r = 0
        c.g = 0
        c.b = 0
        c.a = 1
        Gimp.get_pdb().run_procedure('script-fu-drop-shadow',
                                     [ Gimp.RunMode.NONINTERACTIVE,
                                       GObject.Value(Gimp.Image, img),
                                       GObject.Value(Gimp.Drawable, layer),
                                       GObject.Value(GObject.TYPE_DOUBLE, -3),
                                       GObject.Value(GObject.TYPE_DOUBLE, -3),
                                       GObject.Value(GObject.TYPE_DOUBLE,blur),
                                       # GObject.Value(Gimp.RGB, (0, 0, 0)),
                                       c,
                                       GObject.Value(GObject.TYPE_DOUBLE, 80.0),
                                       GObject.Value(GObject.TYPE_BOOLEAN, False)
                                     ])
        Gimp.get_pdb().run_procedure('gimp-selection-none', [img])

        Gimp.get_pdb().run_procedure('gimp-image-undo-group-end', [img])


    def run(self, procedure, run_mode, image, drawable, args, run_data):
        """Called when the user invokes the plug-in from the menu,
           or when another plug-in calls it.
        """
        if run_mode == Gimp.RunMode.INTERACTIVE:
            GimpUi.init("blobi.py")

            dialog = self.blob_dialog()

            while (True):
                response = dialog.run()
                if response == Gtk.ResponseType.OK:
                    dialog.destroy()
                    self.python_blobify(image, drawable, 8)
                    break
                else:
                    dialog.destroy()
                    return procedure.new_return_values(
                        Gimp.PDBStatusType.CANCEL, GLib.Error())

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS,
                                           GLib.Error())

    # Eventually GIMP will create a parameter dialog automatically,
    # but until then, need to build it here.
    def blob_dialog(self):
        """Bring up a dialog prompting for blobipy options"""
        dialog = GimpUi.Dialog(use_header_bar=True,
                               title=_("Make a layer look blobby"),
                               role="blobypy")

        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_OK", Gtk.ResponseType.OK)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        dialog.get_content_area().add(box)
        box.show()

        head_text=("This plug-in makes things look blobby")
        label = Gtk.Label(label=head_text)
        box.pack_start(label, False, False, 1)
        label.show()

        return dialog


Gimp.main(BlobiPy.__gtype__, sys.argv)
