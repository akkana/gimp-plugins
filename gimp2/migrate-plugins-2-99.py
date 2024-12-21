#!/usr/bin/env python3

# A little script to take plug-ins that GIMP 2.99 incorrectly put
# in ~/.config/GIMP/2.99/plug-ins/ and create the subdirectory for
# each plug-in that GIMP now requires before it will see them.
# Run this after you've run GIMP 2.99 for the first time and noticed
# that none of your plug-ins are there.

import os
import shutil
import tempfile

new_plugins_dir = os.path.expanduser("~/.config/GIMP/2.99/plug-ins/")

def make_new_plugin(oldpath):
    fname = os.path.basename(oldpath)
    base, ext = os.path.splitext(fname)

    # If the plug-in has an extension, like foo.py,
    # it will end up in foo/foo.py.
    # But if it has no extension, the directory name will be
    # the same as the plug-in name.
    if not ext:
        plugindir = tempfile.mkdtemp(prefix=os.path.join(new_plugins_dir, base))
        print("Made temporary directory", plugindir)
    else:
        plugindir = os.path.join(new_plugins_dir, base)
        os.mkdir(plugindir)
        print("Made directory", plugindir)

    newpath = os.path.join(plugindir, fname)

    # If it's something GIMP has already copied, move it.
    # If it's from somewhere else, just copy it.
    if oldpath.startswith(new_plugins_dir):
        print("Rename", oldpath, newpath)
        os.rename(oldpath, newpath)
    else:
        print("COPY", oldpath, newpath)
        shutil.copy(oldpath, newpath)

    # If we had to make a temporary directory before, move it now
    # back to the original name:
    if ext:
        print("Renaming", plugindir, os.path.join(new_plugins_dir, base))
        os.rename(plugindir, os.path.join(new_plugins_dir, base))

def move_migrated_plugins():
    for f in os.listdir(new_plugins_dir):
        fullf = os.path.join(new_plugins_dir, f)
        if not os.path.isfile(fullf):
            continue
        make_new_plugin(fullf)

if __name__ == '__main__':
    move_migrated_plugins()

