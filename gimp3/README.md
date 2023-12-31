These are the plug-ins I've ported to the GIMP 3 API
(currently represented by GIMP 2.99 or the default GIMP git master build).

This API is still changing (as I write this in December 2023) so it's
possible they can get behind, though I'll try to keep them working.

To use one of them, you'll need to make a subdirectory: you can't just copy
the plug-in file as with GIMP 2.x. So for example:

mkdir ~/.config/GIMP/2.99/plug-ins/saver
cp saver.py ~/.config/GIMP/2.99/plug-ins/saver/

As always with plug-ins, Linux, Unix and Mac users must make sure the file
is executable, e.g.
```chmod +x ~/.config/GIMP/2.99/plug-ins/saver/saver.py```
