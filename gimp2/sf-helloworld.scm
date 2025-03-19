; "Hello, World" Test
;
; Creates an image with the text "Hello, World!"

; Copyright 2010, Akkana Peck
; This program is free software; you can redistribute it and/or modify
; it under the terms of the GNU General Public License as published by
; the Free Software Foundation; either version 2 of the License, or
; (at your option) any later version.
;
; This program is distributed in the hope that it will be useful,
; but WITHOUT ANY WARRANTY; without even the implied warranty of
; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
; GNU General Public License for more details.
;
; You should have received a copy of the GNU General Public License
; along with this program; if not, write to the Free Software
; Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

(define (script-fu-helloworld text font size colour)
  (gimp-context-push)
  (gimp-context-set-foreground colour)
  (let* (
        ; initial image size is 10x10 -- we'll resize it later
        (img (car (gimp-image-new 1 1 RGB)))
        (dummy (gimp-image-undo-disable img))
        (text-layer (car (gimp-text-fontname img -1 0 0 text 10
                                             TRUE size PIXELS font)))
        (width (car (gimp-drawable-width text-layer)))
        (height (car (gimp-drawable-height text-layer)))
        )
    (gimp-image-resize img width height 0 0)

    (gimp-image-undo-enable img)
    (gimp-display-new img)
    (gimp-context-pop)
))

(script-fu-register "script-fu-helloworld"
    "_Hello World (SF)..."
    "Creates an image with a user specified text string."
    "Akkana Peck <akkana@shallowsky.com>"
    "Akkana Peck"
    "May, 2010"
    ""
    SF-STRING     "Text string"         "Hello, World!"
    SF-FONT       "Font"                "Sans"
    SF-ADJUSTMENT "Font size (pixels)"  '(100 2 1000 1 10 0 1)
    SF-COLOR      "Color"               '(255 0 0)
)

(script-fu-menu-register "script-fu-helloworld"
                         "<Image>/File/Create")
