#!/usr/bin/env python3

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp

from gi.repository import GObject

def run_plug_in(name, *args):

    # run-mode, if present, must be the first argument.
    if type(args[0]) is gi.repository.Gimp.RunMode:
        run_mode = args[0]
        args = args[1:]
    else:
        run_mode = Gimp.RunMode.NONINTERACTIVE

    pdb_args = [ run_mode ]

    # Add the rest of the args
    for arg in args:
        if type(arg) is float:
            pdb_args.append(GObject.Value(GObject.TYPE_DOUBLE, arg))
        elif type(arg) is int:
            pdb_args.append(GObject.Value(GObject.TYPE_DOUBLE, arg))
        elif type(arg) is bool:
            pdb_args.append(GObject.Value(GObject.TYPE_BOOLEAN, arg))

        # At least some functions, such as drop shadow, expect drawables
        # and don't work if you pass it in as a layer:
        elif type(arg) is Gimp.Layer:
            pdb_args.append(GObject.Value(Gimp.Drawable, arg))

        else:
            pdb_args.append(GObject.Value(type(arg), arg))

    Gimp.get_pdb().run_procedure(name, pdb_args)

