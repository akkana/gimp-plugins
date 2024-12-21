#! /usr/bin/env python

# Script to generate label templates from glabels XML template files,
# for a GIMP label script-fu.
# Copyright (C) 2005,2009 by Akkana Peck.
# You are free to use, share or modify this program under
# the terms of the GPL.

import os, xml.dom.minidom, re, sys

def handleTemplate(templ) :
    rect = templ.getElementsByTagName("Label-rectangle")
    if len(rect) <= 0 : return
    rect = rect[0]
    layout = rect.getElementsByTagName("Layout")[0]
    brand = templ.getAttribute("brand")
    part = templ.getAttribute("part")
    description = templ.getAttribute("description")
    if description == "" :
        description = templ.getAttribute("_description")
    #print "brand=", brand, "part=", part, "descript=", description
    name = " ".join([brand, part])
    #print "becomes:", name

    # Markup margin: the glabels doc isn't clear what this is,
    # but I'm guessing it gets added around the edge of each label.
#    markupMargin = rect.getElementsByTagName("Markup-margin")
#    if len(markupMargin) > 0 :
#        margin = float(markupMargin[0].getAttribute("size"))*2
#    else : margin = 0

    # Try to add double the margin to the width and height.
    # But if the width or height is in a nontrivial format,
    # e.g. 3.13in, then skip it and just save the string.
#    try :
#        width = float(rect.getAttribute("width")) + margin
#    except ValueError, e:
#        width = rect.getAttribute("width")
#    try :
#        height = rect.getAttribute("height")
#    except ValueError, e:
#        height = float(rect.getAttribute("height")) + margin

    # glabels now specifies sizes and positions like ".75in" or "22pt".
    # So we need to parse the units and do something appropriate.
    # Return in points.
    def getNumAtt(node, attname) :
        lenstr = node.getAttribute(attname)
        unit = re.compile("[a-zA-Z]")
        #print "Searching for unit in", lenstr
        match = unit.search(lenstr)
        if not match :
            #print "No match in", lenstr
            return lenstr
        num = float(lenstr[0:match.start()])
        unit = lenstr[match.start():]
        if unit == "pt" :
            return str(num)
        if unit == "in" :
            return str(num * 72)
        if unit == "mm" :
            return str(num * 2.8346457)
        if unit == "cm" :
            return str(num * 28.346457)

        # oops, no idea
        print ";; don't know the unit for", lenstr
        return str(num)

    width = getNumAtt(rect, "width")
    height = getNumAtt(rect, "height")

    # Print out the template, in script-fu format
    print "    (",
    print "\"" + name + "\"",
    print "\"" + description + "\"",
    print "(", width, height, ")",
    print "(" + layout.getAttribute("nx"), layout.getAttribute("ny"),
    print getNumAtt(layout, "x0"), getNumAtt(layout, "y0"),
    print getNumAtt(layout, "dx"), getNumAtt(layout, "dy") + "))"

def handleTemplateFile(tfdom) :
    templates = tfdom.getElementsByTagName("Template")
    # Loop over the templates in reverse, because script-fu (SIOD)
    # can't append to the end of a list only to the beginning;
    # so the template list will end up being the reverse of the
    # order in which we list them here.
    for i in range (len(templates)-1, -1, -1) :
        handleTemplate(templates[i])

def parseTemplateFile(fnam) :
    print "\n;; File:", fnam
    dom = xml.dom.minidom.parse(fnam)
    handleTemplateFile(dom)
    dom.unlink()

print "; labeltemplates.scm: Templates for labels.scm.\n\
; Copyright (C) 2005,2009 by Akkana Peck, akkana@shallowsky.com.\n\
; \n\
; This program is free software; you can redistribute it and/or modify\n\
; it under the terms of the GNU General Public License as published by\n\
; the Free Software Foundation; either version 2 of the License, or\n\
; (at your option) any later version.\n\
; \n\
; This program is distributed in the hope that it will be useful,\n\
; but WITHOUT ANY WARRANTY; without even the implied warranty of\n\
; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n\
; GNU General Public License for more details.\n\
; \n\
; You should have received a copy of the GNU General Public License\n\
; along with this program; if not, write to the Free Software\n\
; Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.\n\
\n\
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n\
;; LABEL TEMPLATES\n\
;; Eventually these should move to a separate, auto-generated file.\n\
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n\
\n\
;; Rectangular labels: (name comment (w h) (nx ny x0 y0 dx dy))\n\
(define label-templates-rectangular\n\
  '("

parseTemplateFile("/usr/share/glabels/templates/misc-us-templates.xml")
parseTemplateFile("/usr/share/glabels/templates/avery-us-templates.xml")

# Also parse anything in ~/.glabels
mytemplatedir = os.environ["HOME"] + "/.glabels"
try:
    mytemplatefiles = os.listdir(mytemplatedir)
    for templidx in range (0, len(mytemplatefiles)) :
        templ = mytemplatedir + "/" + mytemplatefiles[templidx]
        parseTemplateFile(templ)
except OSError, e:
    print ";; No personal glabels templates:", e
    pass

print "    ) )\n\
\n\
;; CD Labels: (name comment (radius hole) (nx ny x0 y0 dx dy))\n\
(define label-templates-cd\n\
  '(\n\
    (\"Avery 5931\" \"CD Labels, 2 per sheet\" (166.5 58.5) (1 2 139.5 49.5 0 360))\n\
    ) )\n\
\n\
;; Paper sizes we recognize:\n\
;; Note, this is currently somewhat bogus because the label templates are\n\
;; specific to a particular paper size.\n\
(define page-sizes\n\
  '(\n\
    (\"a4\" 595.276 841.89)\n\
    (\"us-letter\" 612 792)\n\
    ))\n\
\n\
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n\
;; END LABEL TEMPLATES\n\
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n\
\n\
"
