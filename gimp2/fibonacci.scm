;; fibonacci.scm: Make a Fibonacci grid and spiral,
;;                optionally with an animated spiral image too.
;; Copyright (C) 2006 by Akkana Peck, akkana@shallowsky.com.
;; 
;; This program is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License.

(define (script-fu-fibonacci-grid width box-color spiral-color
                                  font font-size text-color animatedp)
  (let* ((old-fg-color (car (gimp-context-get-foreground)))
         (grid-spacing (/ width 21))
         (height (* grid-spacing 13))
         ;; Make the new image
         (newimg (car (gimp-image-new width height RGB)))
         ;; and a background layer
         (bg-l (car (gimp-layer-new newimg width height
                                    RGBA-IMAGE "background"
                                  100 NORMAL-MODE)))
         (grid-l (car (gimp-layer-new newimg width height
                                      RGBA-IMAGE "grid"
                                      100 NORMAL-MODE)))
         (spiral-l (car (gimp-layer-new newimg width height
                                        RGBA-IMAGE "spiral"
                                        100 NORMAL-MODE)))
         (text-l (car (gimp-layer-new newimg width height
                                        RGBA-IMAGE "labels"
                                        100 NORMAL-MODE)))
         (floating-l nil)
         ;; If we're making an animated version, we need another image:
         (animated-im (if (= animatedp TRUE)
                          (car (gimp-image-new width height RGB))
                          nil))
         ;; Initial parameters for the golden spiral:
         (theta 0)
         (lastx 5.5)
         (lasty 3.5)
         (firstx (+ lastx .5 ))
         (firsty lasty)
        )

      (gimp-image-undo-disable newimg)
      (if (= animatedp TRUE) (gimp-image-undo-disable animated-im))
      (gimp-image-add-layer newimg bg-l -1)
      (gimp-image-add-layer newimg grid-l -1)
      (gimp-image-add-layer newimg spiral-l -1)
      (gimp-layer-set-opacity spiral-l 65)
      (gimp-image-add-layer newimg text-l -1)

      (gimp-drawable-fill bg-l BACKGROUND-FILL)
      (gimp-edit-clear grid-l)
      (gimp-edit-clear spiral-l)
      (gimp-edit-clear text-l)

      ; Horizontal lines
      (gimp-context-set-foreground box-color)
      (fibonacci-draw-line grid-l 0 0 21 0)
      (fibonacci-draw-line grid-l 5 3 8 3)
      (fibonacci-draw-line grid-l 5 4 6 4)
      (fibonacci-draw-line grid-l 0 5 8 5)
      (fibonacci-draw-line grid-l 0 13 21 13)
      ; Vertical lines
      (fibonacci-draw-line grid-l 0 0 0 13)
      (fibonacci-draw-line grid-l 5 0 5 5)
      (fibonacci-draw-line grid-l 6 3 6 5)
      (fibonacci-draw-line grid-l 8 0 8 13)
      (fibonacci-draw-line grid-l 21 0 21 13)
      ; Number the squares
      (gimp-context-set-foreground text-color)
      (fibonacci-label newimg text-l 2.5 2.5 "5" font font-size)
      (fibonacci-label newimg text-l 6.5 1.5 "3" font font-size)
      (fibonacci-label newimg text-l 5.5 3.5 "1" font font-size)
      (fibonacci-label newimg text-l 5.5 4.5 "1" font font-size)
      (fibonacci-label newimg text-l 7 4 "2" font font-size)
      (fibonacci-label newimg text-l 4 9 "8" font font-size)
      (fibonacci-label newimg text-l 14.5 6.5 "13" font font-size)

      ; Finally, draw a Golden Spiral. r = a*b^theta
      ; where b = phi^(1/90) ~= 1.35846 for radians (1.00536 for deg).
      ; and a is a scaling factor, grid-spacing.
      ; But since this is a Fibonacci spiral, not a real Golden spiral,
      ; we have to adjust it a little.
      (gimp-context-set-foreground spiral-color)
      (while (< theta 10)
             (let* ((b 1.378)
                    (r (pow b theta))
                    (pi2 6.283184)
                    (x (- firstx (/ (* r (cos theta)) 2)))
                    (y (+ firsty (/ (* r (sin theta)) 2)))
                    )
               (fibonacci-draw-line spiral-l lastx lasty x y)
               ; This list->vector approach works in tiny-fu,
               ; but not in GIMP 2.2 or earlier:
               ;(gimp-paintbrush spiral-l 0 4 (list->vector
               ;                               (list lastx lasty x y)) 0 0)
               (set! theta (+ theta 0.1))
               (set! lastx x)
               (set! lasty y)

               ;; Copy it to the animated image, if appropriate
               (if (= animatedp TRUE)
                   (let ((anim-l (car (gimp-layer-new animated-im width height
                                                      RGBA-IMAGE "100ms"
                                                      100 NORMAL-MODE)))
                         )
                     (gimp-image-add-layer animated-im anim-l -1)
                     (gimp-edit-copy-visible newimg)
                     (set! floating-l (car (gimp-edit-paste anim-l TRUE)))
                     (gimp-floating-sel-anchor floating-l)
                   ))
               ))

      ;; Clean up
      (gimp-context-set-foreground old-fg-color)
      (gimp-image-undo-enable newimg)
      (if (= animatedp TRUE) (gimp-image-undo-enable animated-im))
      (gimp-display-new newimg)
      (if (= animatedp TRUE) (gimp-display-new animated-im))

      ;; Something about this script, maybe all the cons-arrays,
      ;; allocates way too much memory, and script-fu doesn't
      ;; clean up when it's done, which can make the rest of GIMP
      ;; nonfunctional. So force a garbage collect before returning:
      (gc)
    ))

(define (fibonacci-draw-line drawable x1 y1 x2 y2)
  (let (;(points (cons-array 4 'double))
        (spacing (/ (car (gimp-drawable-width drawable)) 21))
        )
    ;(aset points 0 (* x1 spacing))
    ;(aset points 1 (* y1 spacing))
    ;(aset points 2 (* x2 spacing))
    ;(aset points 3 (* y2 spacing))
    ;(gimp-pencil drawable 4 points)
    (gimp-paintbrush drawable 0 4 (list->vector (list (* x1 spacing)
                                                      (* y1 spacing)
                                                      (* x2 spacing)
                                                      (* y2 spacing))) 0 0)
  ))

(define (fibonacci-label img text-l x y text font font-size)
  (let* ((spacing (/ (car (gimp-drawable-width text-l)) 21))
         ;; Text extents are needed for centering:
         (text-extents (gimp-text-get-extents-fontname text
                                                       font-size PIXELS
                                                       font))
         ;; Create the text:
         (floating-l
          (car (gimp-text-fontname img text-l
                                   (- (* x spacing) (/ (car text-extents) 2))
                                   (- (* y spacing) (/ (cadr text-extents) 2))
                                   text 1 TRUE
                                   font-size PIXELS font)))
         )
    (gimp-floating-sel-anchor floating-l)
  ))

(script-fu-register "script-fu-fibonacci-grid"
                     _"<Image>/File/Create/Misc/Fibonacci Grid..."
                    "Make a Fibonacci grid and spirals"
                    "Akkana Peck"
                    "Akkana Peck"
                    "November 2006"
                    ""
                    SF-ADJUSTMENT _"Width (pixels)" '(1024 500 3200 1 10 0 1)
                    SF-COLOR      _"Box color"      '(0 0 0)
                    SF-COLOR      _"Spiral color"   '(0 0 255)
                    SF-FONT       _"Font"           "Arial Bold Italic"
                    SF-ADJUSTMENT _"Font size (pixels)" '(30 2 500 1 10 0 1)
                    SF-COLOR      _"Text color"     '(255 0 0)
                    SF-TOGGLE     _"Animated"        FALSE
)

