#!/usr/bin/env python

import os, re
from gimpfu import *

def python_fu_migrate_tool_presets() :
    tool_options_dir_2_6 = os.path.join(re.sub('2.8', '2.6', gimp.directory),
                                        'tool-options')
    tool_preset_dir_2_8 = os.path.join(gimp.directory, 'tool-presets')

    presetfiles = os.listdir(tool_options_dir_2_6)

    for filename in presetfiles :
        # filename is something like gimp-rect-select-tool.presets
        # So the part before the extension is the tool name.

        f = open(os.path.join(tool_options_dir_2_6, filename))
        toolname = os.path.splitext(filename)[0]
        optionsname = None
        presetname = None
        parenlevel = 0
        cur_preset_str = ''
        for line in f :
            left_parens = len(re.findall("\(", line))
            right_parens = len(re.findall("\)", line))

            if parenlevel <= 0 and left_parens <= 0 :
                # not in an s-expression, nothing to do
                parenlevel += left_parens - right_parens
                continue

            # Are we finishing an existing preset? Then write it.
            if parenlevel > 0 and parenlevel + left_parens - right_parens == 0 :
                cur_preset_str += line

                outf = open(os.path.join(tool_preset_dir_2_8, presetname) + '.gtp',
                            'w')
                print >>outf, '# GIMP tool preset file, migrated from 2.6\n'
                print >>outf, '(stock-id "%s")' % toolname
                print >>outf, '(name "%s")' % presetname
                print >>outf, '(tool-options "%s"' % optionsname
                print >>outf, cur_preset_str
                print >>outf, '# end of GIMP tool preset file'
                outf.close()

                cur_preset_str = ''
                presetname = None
                parenlevel = 0
                continue

            # Are we just continuing an existing preset?
            if parenlevel > 0 :
                cur_preset_str += line
                parenlevel += left_parens - right_parens
                continue

            # We're starting a new preset. Find its name:
            match = re.match('\W*(\w*?Options)\s*[\"\'](.*)[\"\'].*', line)
            if not match :
                continue
            optionsname = match.group(1)
            presetname = match.group(2)

            parenlevel += left_parens - right_parens

        f.close()

register(
    "python_fu_migrate_tool_presets",
    "Migrate 2.6 tool presets to 2.8",
    "Migrate 2.6 tool presets to 2.8",
    "Akkana Peck",
    "Akkana Peck",
    "2012",
    "Migrate 2.6 Tool Presets...",
    "",
    [],
    [],
    python_fu_migrate_tool_presets, menu="<Image>/File")

main()
