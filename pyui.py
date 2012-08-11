#!/usr/bin/env python

# GIMP Python plug-in template showing all UI elements.
# Copyright 2010 Akkana Peck <akkana@shallowsky.com>
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
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

#
# Note: gimpfu.py is the most up-to-date list of UI items.

from gimpfu import *

def show_py_ui(number, angle, word, text, bgcolor,
               newimg, newlayer, channel, drawable,
               shadowp, ascendingp, imgfmt, option,
               size, opacity, imagefile, dir,
               font, brush, pattern, gradient, palette ) :
    return

register(
    "python_fu_ui_options",
    "Show all Python-Fu UI options",
    "Longer description of doing stuff",
    "Your Name",
    "Your Name",
    "2010",
    "Show UI Options...",
    "",      # Alternately use RGB, RGB*, GRAY*, INDEXED etc.
    [
        (PF_INT, "number", "Number?", 50),
        (PF_FLOAT, "angle", "Angle", 3.14159),
        # you can also use PF_INT8, PF_INT16, PF_INT32
        (PF_STRING, "word", "Word", "Zebrafish!"),
        # PF_VALUE is another term for PF_STRING
        (PF_TEXT, "text", "Some Text",
          "The quick red fox jumped over the lazy dog"),

        (PF_COLOR, "bg-color", "Background", (1.0, 0.0, 0.0)),
        # or you can spell it PF_COLOUR

        (PF_IMAGE, "image", "Input image", None),
        (PF_LAYER, "layer", "Input layer", None),
        (PF_CHANNEL, "channel", "Which channel", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),

        (PF_TOGGLE, "shadow", "Shadow?", 1),
        (PF_BOOL,   "ascending", "_Ascending", True),
        (PF_RADIO, "imagefmt", "Image format", "jpg",
          (("png", "png"), ("jpg", "jpg"))),
        (PF_OPTION, "option", "Option", 2, ("Mouse", "Cat", "Dog", "Horse")),

        (PF_SPINNER, "size", "Pixel Size", 50, (1, 8000, 1)),
        (PF_SLIDER, "opacity",  "Op_acity", 100, (0, 100, 1)),
        # (PF_ADJUSTMENT is the same as PF_SPINNER

        (PF_FILE, "imagefile", "Image file", ""),
        (PF_DIRNAME, "dir", "Directory", "/tmp"),

        (PF_FONT, "font", "Font", "Sans"),
        (PF_BRUSH, "brush", "Brush", None),
        (PF_PATTERN, "pattern", "Pattern", None),
        (PF_GRADIENT, "gradient", "Gradient", None),
        (PF_PALETTE, "palette",  "Palette", ""),

        # New items that don't quite work yet:
        #(PF_VECTORS, "vectors", "Vectors", None),
        #(PF_DISPLAY, "display", "Display", None),
    ],
    [],
    show_py_ui, menu="<Image>/Filters/Languages/Python-Fu" )

main()
