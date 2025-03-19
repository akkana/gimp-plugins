;; stack.scm: Make an averaged image stack:
;; combine all the layers with opacity 1/num_images.
;; Copyright (C) 2007 by Akkana Peck, akkana@shallowsky.com.
;; 
;; This program is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License.

(define (script-fu-stack-average img drawable)
  (let* ((layers (gimp-image-get-layers img))
         (numlayers (car layers))
         (layer-array (cadr layers))
         (i 0)
         )
    (gimp-message "Stacking")
    (gimp-image-undo-group-start img)
    ;(gimp-context-push)

    ;; Loop over the layers.
    ;; Layers are numbered starting with 0 as the top layer in the stack.
    (while (< i numlayers)
           (gimp-message (number->string i))
           (let* ((thislayer (aref layer-array i)))
             (gimp-layer-set-opacity thislayer (* 100 (/ 1 (- numlayers i))))
           )
           (set! i (+ i 1))
    )

    ;(gimp-message "")
    ;(gimp-context-pop)
    (gimp-image-undo-group-end img)
    (gimp-displays-flush)
    ) ; close let
)

(if (symbol-bound? 'script-fu-menu-register (the-environment))
    (begin
     (script-fu-register "script-fu-stack-average"
                         _"Stack (Average)..."
                         _"Set all layers' opacity to 1/N"
                         "Akkana Peck"
                         "Akkana Peck"
                         "January 2008"
                         "*"
                         SF-IMAGE       "Image"              0
                         SF-DRAWABLE    "Drawable"           0
     )

     (script-fu-menu-register "script-fu-stack-average"
                              _"<Image>/Filters/Combine")
     ) ; end begin
     (script-fu-register "script-fu-stack-average"
                         _"<Image>/Filters/Combine/Stack (Average)..."
                         _"Line up layers as a panorama"
                         "Akkana Peck"
                         "Akkana Peck"
                         "January 2008"
                         "*"
                         SF-IMAGE       "Image"              0
                         SF-DRAWABLE    "Drawable"           0
     )
)

