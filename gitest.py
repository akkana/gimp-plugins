#!/usr/bin/env python3

# Minimal example of GObject Introspection based Python plug-in in 2.99.

import os

# For testing, import from locally built gimp
gimp_girpath = '/usr/local/gimp-git/lib/girepository-1.0/'
old_typelib_path = os.getenv('GI_TYPELIB_PATH')
if old_typelib_path:
    gimp_girpath += ':' + old_typelib_path
os.environ['GI_TYPELIB_PATH'] = gimp_girpath

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio

import sys

class TestPlugin (Gimp.PlugIn):

    ## Parameter: run-mode ##
    @GObject.Property(type=Gimp.RunMode,
                      default=Gimp.RunMode.NONINTERACTIVE,
                      nick="Run mode", blurb="The run mode")
    def run_mode(self):
        """Read-write integer property."""
        return self._run_mode


    @run_mode.setter
    def run_mode(self, run_mode):
        self._run_mode = run_mode


    ## GimpPlugIn virtual methods ##
    def do_query_procedures(self):
        # Localization
        self.set_translation_domain ("gimp30-python",
                                     Gio.file_new_for_path(Gimp.locale_directory()))

        return [ "python-fu-gi-test" ]


    def do_create_procedure(self, name):
        procedure = Gimp.Procedure.new(self, name,
                                       Gimp.PDBProcType.PLUGIN,
                                       self.run, None)
        if name == 'python-fu-gi-test':
            procedure.set_menu_label("_GI Test...")
            procedure.set_documentation("Test Python plug-in with GI",
                                        "No further documentation",
                                        "")
            procedure.set_attribution("Author Name",
                                      "(c) Copyright",
                                      "2019")
            procedure.add_argument_from_property(self, "run-mode")
            procedure.add_menu_path ('<Image>/Filters')
        else:
            procedure = None

        return procedure


    def run(self, procedure, args, data):
        palette = None
        amount  = 1

        # Get the parameters
        if args.length() < 1:
            error = 'No parameters given'
            return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR,
                                               GLib.Error(error))
        runmode = args.index(0)
        # Handle args here on a plug-in that takes them.

        # Gimp.image_list()

        # Make a new image:
        img = Gimp.image_new(400, 400, 0)

        # Make a new layer:
        layer = Gimp.layer_new(img,
                                  "newlayer",
                                  Gimp.image_width(img),
                                  Gimp.image_height(img),
                                  Gimp.ImageType.RGBA_IMAGE,
                                  100.0,
                                  Gimp.LayerMode.NORMAL
        )

        # Add the layer to the image:
        Gimp.image_insert_layer(img, layer, 0, -1)

        # Fill the layer:
        Gimp.drawable_fill(layer, Gimp.FillType.PATTERN)

        # Finally, display the image:
        Gimp.display_new(img)

        retval = procedure.new_return_values(Gimp.PDBStatusType.SUCCESS,
                                             GLib.Error())
        return retval


Gimp.main(TestPlugin.__gtype__, sys.argv)

