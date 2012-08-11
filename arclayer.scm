; arclayer.scm: a very simple version of arclayer
;   that just calls Polar Coordinates.
; See http://shallowsky.com/software/arclayer/
; Copyright (C) 2009 by Akkana Peck, akkana@shallowsky.com.
; 
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

; pass a box 200x100 to polar coordinates
; get a circle of diameter 106 (at least, that's the layer height)


(define (script-fu-arclayer img layer radius top)
  (gimp-image-undo-group-start img)

  (if (= top FALSE) (plug-in-rotate RUN-NONINTERACTIVE img layer 2 FALSE))
  (let* ((oldwidth (car (gimp-drawable-width layer)))
         (oldheight (car (gimp-drawable-height layer)))
         (newwidth (* 6.28318 radius))
         ;(newwidth (* 3.14 radius))
         (xoff (/ (- newwidth oldwidth) 2))
        )
    (gimp-layer-resize layer newwidth radius xoff 0)
  )

  (plug-in-polar-coords RUN-NONINTERACTIVE img layer
                        100 180 FALSE FALSE TRUE)
  (if (= top FALSE) (plug-in-rotate RUN-NONINTERACTIVE img layer 2 FALSE))

  (plug-in-autocrop-layer RUN-NONINTERACTIVE img layer)

  (gimp-image-undo-group-end img)
  (gimp-displays-flush)
  )

(script-fu-register "script-fu-arclayer"
		    _"<Image>/Filters/Distorts/Arclayer (SF)..."
		    "Bend the current layer in an arc."
		    "Akkana Peck"
		    "Akkana Peck"
		    "March 2009"
		    "*"
		    SF-IMAGE      "Image"        0
		    SF-DRAWABLE   "Drawable"     0
                    SF-ADJUSTMENT "Radius"      '(600 1 2000 10 50 0 1)
		    SF-TOGGLE     "Top"         TRUE)


