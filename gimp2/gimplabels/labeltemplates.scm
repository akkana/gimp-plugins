; labeltemplates.scm: Templates for labels.scm.
; Copyright (C) 2005,2009 by Akkana Peck, akkana@shallowsky.com.
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

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; LABEL TEMPLATES
;; Eventually these should move to a separate, auto-generated file.
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; Rectangular labels: (name comment (w h) (nx ny x0 y0 dx dy))
(define label-templates-rectangular
  '(

;; File: /usr/share/glabels/templates/misc-us-templates.xml
    ( "OfficeMax OM99060" "Mailing Labels" ( 203.76 72.0 ) (3 10 0.0 36.0 203.76 72.0))
    ( "Kingdom L" "Cassette Labels" ( 252.0 117.0 ) (2 6 33.12 27.0 261.0 126.144))
    ( "Tough-Tags TTLW-2016" "Microtube labels" ( 92.16 36 ) (5 17 68 4.17 100.8 45.3))
    ( "Netc 749303-70001 " "DLT Labels" ( 162 59.4 ) (3 10 36 45 189 72))
    ( "Neato Slimline CD Case, spine" "Slimline CD Case (upside down)" ( 394.5 342.5 ) (1 2 96.5 41.9 0 363))
    ( "Neato Slimline CD Case" "Slimline CD Case (rightside up)" ( 394.5 342.5 ) (1 2 130 41.9 0 363))
    ( "Stomper PRO Spine" "PRO CD Labels 2-up (CD spine only)" ( 288 20 ) (2 1 18 385 288 0))
    ( "Stomper PRO Zip" "PRO CD Labels 2-up (Face only)" ( 168 142 ) (1 2 407 68 0 142))
    ( "Neato USCD2lbl Rectangles" "CD Template Rectangles" ( 77.04 234.36 ) (2 1 51.3 279.72 433.44 0))
    ( "Southworth BC" "Business Cards" ( 252 144 ) (2 5 36 36 288 144))

;; File: /usr/share/glabels/templates/avery-us-templates.xml
    ( "Avery LSK-3.5" "Divider Labels" ( 225.36 36.0 ) (1 20 36.0 36.0 315.36 36.0))
    ( "Avery LSK-3" "Divider Labels" ( 225.36 36.0 ) (2 20 36.0 36.0 315.36 36.0))
    ( "Avery LSK-5.5" "Divider Labels" ( 126.0 36.0 ) (2 20 36.0 21.6 147.6 36.0))
    ( "Avery LSK-5" "Divider Labels" ( 126.0 36.0 ) (4 20 36.0 21.6 147.6 36.0))
    ( "Avery LSK-8.5" "Divider Labels" ( 81.36 36.0 ) (2 20 36.0 36.0 153.36 36.0))
    ( "Avery LSK-8" "Divider Labels" ( 81.36 36.0 ) (4 20 36.0 36.0 153.36 36.0))
    ( "Avery 3274.1" "Square Labels" ( 180.0 180.0 ) (3 3 22.5 90.0 193.5 216.0))
    ( "Avery 8165" "Full Sheet Labels" ( 612.0 792.0 ) (1 1 0 0 0 0))
    ( "Avery 6570" "ID Labels" ( 126.0 90.0 ) (4 8 36.0 36.0 139.536 90.0))
    ( "Avery 5997-Spine" "Video Tape Spine Labels" ( 414 48 ) (1 15 99 36 0 48))
    ( "Avery 5997-Face" "Video Tape Face Labels" ( 220 133 ) (2 5 80 60.5 236 133))
    ( "Avery 5931-Spine" "CD/DVD Labels (Spine Labels)" ( 15.75 337.5 ) (2 2 36.0 52.875 33.75 348.75))
    ( "Avery 5395" "Name Badge Labels" ( 243.0 167.999999976 ) (2 4 49.5 41.999999976 270.0 180.0))
    ( "Avery 8373" "Business Cards" ( 252.0 144.0 ) (2 4 36.0 54.0 288.0 180.0))
    ( "Avery 5389" "Post cards" ( 432.0 288.0 ) (1 2 90.0 90.0 432.0 324.0))
    ( "Avery 5388" "Index Cards" ( 360.0 216.0 ) (1 3 126.0 72.0 360.0 216.0))
    ( "Avery 5371" "Business Cards" ( 252.0 144.0 ) (2 5 54.0 36.0 252.0 144.0))
    ( "Avery 5366" "Filing Labels" ( 247.5 48.000000024 ) (2 15 38.25 36.0 288.0 48.000000024))
    ( "Avery 6490" "Diskette Labels" ( 193.5 144.0 ) (3 5 9.0 36.0 200.25 144.0))
    ( "Avery 5663" "Address Labels" ( 306.0 144.0 ) (2 5 0.0 36.0 306.0 144.0))
    ( "Avery 5197" "Address Labels" ( 288.0 108.0 ) (2 6 13.5 72.0 297.0 108.0))
    ( "Avery 5196" "Diskette Labels" ( 198.0 198.0 ) (3 3 9.0 36.0 198.0 216.0))
    ( "Avery 5167" "Return Address Labels" ( 126.0 36.0 ) (4 20 20.25 36.0 148.5 36.0))
    ( "Avery 5168" "Shipping Labels" ( 252.0 360.0 ) (2 2 36.0 36.0 288.0 360.0))
    ( "Avery 5164" "Shipping Labels" ( 288.0 239.999999976 ) (2 3 11.25 36.0 301.5 239.999999976))
    ( "Avery 5163" "Shipping Labels" ( 288.0 144.0 ) (2 5 11.7 36.0 301.5 144.0))
    ( "Avery 5159" "Address Labels" ( 288.0 108.0 ) (2 7 11.25 18.0 301.5 108.0))
    ( "Avery 6879" "Address Labels" ( 270.0 90.0 ) (2 6 27.0 81.0 288.0 108.0))
    ( "Avery 5305" "Tent Cards" ( 612.0 180.0 ) (1 2 0.0 216.0 0.0 360.0))
    ( "Avery 5162" "Address Labels" ( 288.0 95.999999976 ) (2 7 11.25 59.999999976 301.5 95.999999976))
    ( "Avery 5161" "Address Labels" ( 288.0 72.0 ) (2 10 11.25 36.0 301.5 72.0))
    ( "Avery 5160" "Address Labels" ( 189.0 72.0 ) (3 10 13.5 36.0 198.0 72.0))
    ) )

;; CD Labels: (name comment (radius hole) (nx ny x0 y0 dx dy))
(define label-templates-cd
  '(
    ("Avery 5931" "CD Labels, 2 per sheet" (166.5 58.5) (1 2 139.5 49.5 0 360))
    ) )

;; Paper sizes we recognize:
;; Note, this is currently somewhat bogus because the label templates are
;; specific to a particular paper size.
(define page-sizes
  '(
    ("a4" 595.276 841.89)
    ("us-letter" 612 792)
    ))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; END LABEL TEMPLATES
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


