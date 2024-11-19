#!/usr/bin/env python3

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp

from gi.repository import GObject

def pdb_run(name, argdic):
    """Run something from the GIMP PDB.
       args should be a dictionary of the properties for the given PDB proc.
    """
    pdb_proc = Gimp.get_pdb().lookup_procedure(name)
    pdb_config = pdb_proc.create_config()
    for key in argdic:
        if type(argdic[key]) is list:
            pdb_config.set_core_object_array(key, argdic[key])
        else:
            pdb_config.set_property(key, argdic[key])
    pdb_proc.run(pdb_config)

