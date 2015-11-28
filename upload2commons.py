#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 by Michael Schönitzer, other
# You may use and distribute this plug-in under the terms of the GPL v3
# or, at your option, any later GPL version.
#ToDo:
#- 'progressbar'
#- Success-Dialog
#- remember Usr/Pw
#- i18n

from gimpfu import *
import gtk
import os
import collections
import wikitools
import tempfile
import time

DEFAULT_WIKITEXT = '''{{Information 
|Description={{en|}}
{{de| }}
|Source=
|Date=
|Author=
|Permission=
|other_versions=
}}
'''
WIKI_URL = "https://commons.wikimedia.org/w/api.php"

class MyWindow(gtk.Dialog):
    
    def __init__(self, parent=None, filename="Filename.jpg"):
        gtk.Dialog.__init__(self, "Upload2Commons", parent, 0,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
             gtk.STOCK_OK, gtk.RESPONSE_OK))
        if not filename:
          filename="Filename.jpg"
        
        table = gtk.Table(2,2, True)
        
        self.set_default_size(150, 100)
        box = self.get_content_area()
        box.set_homogeneous(False)
        box.set_spacing(False)
        box.add(table)
        
        self.usr_label = gtk.Label("User-Name:\t")
        self.usr_entry = gtk.Entry()
        table.attach(self.usr_label, 0,1,0,1)
        table.attach(self.usr_entry, 1, 2, 0, 1)

        self.pw_label = gtk.Label("Password:\t")
        self.pw_entry = gtk.Entry()
        self.pw_entry.set_visibility(False)
        table.attach(self.pw_label, 0,1,1,2)
        table.attach(self.pw_entry, 1,2,1,2)
        
        self.filename_entry = gtk.Entry()
        self.filename_entry.set_text(filename)
        box.add(self.filename_entry)
        
        self.textview = gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.textview.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.textbuffer.set_text(DEFAULT_WIKITEXT)
        box.add(self.textview)
        
        
        self.license = gtk.combo_box_new_text()
        self.license.append_text("{{self|GFDL|cc-by-sa-all|migration=redundant}}")
        self.license.append_text("{{self|cc-by-sa-3.0}}")
        self.license.append_text("{{self|Cc-zero}}")
        self.license.append_text("{{cc-by-sa-3.0}}")
        self.license.append_text("{{PD-old-100}}")
        self.license.append_text("{{PD-old-70}}")
        self.license.append_text("{{PD-Art}}")
        box.add(self.license)
        
        self.cat_box = gtk.HBox()
        self.cat_label = gtk.Label("Categories:\t")
        self.category_entry = gtk.Entry()
        self.cat_box.add(self.cat_label)
        self.cat_box.add(self.category_entry)
        box.add(self.cat_box)
        
        self.feedbackbox = gtk.HBox()
        box.add(self.feedbackbox)
        self.spinner = gtk.Spinner()
        
        self.show_all()
    
    def startspinner(self):
        self.feedbackbox.add(self.spinner)
        self.spinner.start()


def python_upload2commons(img, drawable) :
    use_tempfile=False
    
    if pdb.gimp_image_is_dirty(img) or not img.filename:
      ### save file in temporary file ###
      use_tempfile=True
      file = tempfile.mkstemp(prefix='gimp_upload2commons-', suffix=".jpg")
      local_file_name = file[1]
      fd = file[0]
      exportimg = pdb.gimp_image_duplicate(img)
      layer = pdb.gimp_image_merge_visible_layers(exportimg, CLIP_TO_IMAGE)
      pdb.gimp_file_save(exportimg, layer, local_file_name, local_file_name)
    else:
      local_file_name = img.filename
    
    ### Open Dialog ###
    dialog = MyWindow(filename=os.path.basename(img.filename))
    response = dialog.run()
    if response != gtk.RESPONSE_OK:
       return

    dialog.startspinner()
    wiki_username = dialog.usr_entry.get_text()
    wiki_password = dialog.pw_entry.get_text()
    
    if wiki_username == "" or wiki_password == "":
       print("No ursername or password given")
       return
    
    remote_file_name = dialog.filename_entry.get_text()
    wikitext = dialog.textbuffer.get_text(dialog.textbuffer.get_bounds()[0],
    									  dialog.textbuffer.get_bounds()[1])
    wikitext += "\n" + dialog.license.get_active_text() + "\n"
    for cat in dialog.category_entry.get_text().split('|'):
      wikitext += "\n[[Category:" + cat + "]]"
    comment = "File uploaded from Gimp by upload2commons"
    
    print(wikitext)
    #return		## For debugging!

    ### Upload ###
    try:
	    wiki = wikitools.wiki.Wiki(WIKI_URL)
    except:
	    print "Can not connect to wiki. Check the URL"

    try:
	    wiki.login(username=wiki_username,password=wiki_password)
    except:
        # TODO: GUI
    	print "Invalid Username or Password"

    exit
    
    image=open(local_file_name,"r")
    picture=wikitools.wikifile.File(wiki=wiki, title=remote_file_name)
    print("Uploading…")
    #picture.upload(fileobj=image, comment=comment, ignorewarnings=True)
    time.sleep(6)
    print("Finished Uploading")
    
    page_name = "File:" + remote_file_name.replace(" ","_")
    page = wikitools.Page(wiki, page_name, followRedir=True, watch=True)
    #page.edit(text=wikitext)
    
    if use_tempfile:
      os.close(fd)
      os.remove(local_file_name)


### register Plugin ###
register(
        "python_fu_upload2commons",
        "Upload the Image to Wikimedia Commons.",
        "Upload the Image to Wikimedia Commons.",
        "Michael Schoenitzer",
        "Michael Schoenitzer",
        "2013",
        "Upload to Commons",
        "*",
        [
            (PF_IMAGE, "image", "Input image", None),
            (PF_DRAWABLE, "drawable", "Input drawable", None),
        ],
        [],
        python_upload2commons,
        menu = "<Image>/File/Save/"
)

main()

