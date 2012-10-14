#!/usr/bin/env python
# -*- coding: utf-8 -*-

# GIMP plugin to improve on the text-along-path button in the Text tool.
# (c) Ofnuts 2012
#
#   History:
#
#   v0.0: 	2012-04-08	first published version
#   v0.1: 	2012-04-09	remove trace (can cause Windows failure)
#				check for missing text and font
#				force workimage size args to int
#   v0.2: 	2012-04-11	register to work from a Text layer
#   v0.2.1      2012-10-13      add option to fill or stroke the new path
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
import math, random, os, sys
from gimpfu import *

debug=False
def trace(s):
	if debug:
		print s

# To set the text on the target path, each character is given a "pivot point".
# This point is the point to be moved to the target path, as well as the center
# of rotation to adjust the character tilt. The X coordinate of the pivot point
# is always the middle of the character box (single-character text layer). 
# The Y coordinate is  the combination of an adjustment value, and one of the 
# following heights:
BASELINE=0 	# The baseline
TOP=1		# The top of the character box	
BOTTOM=2	# The bottom of the character box
MIDDLEBOX=3	# The middle of the character box
TOPCAPS=4	# The top of uppercase characters
MIDDLECAPS=5	# The middle of uppercase characters

# Characters that won't produce a path (space, etc...)
blankCharacters=' '

# Text formatting over the path. 
# TEXT_JUSTIFY_CENTER/TEXT_JUSTIFY_LEFT/TEXT_JUSTIFY_RIGHT will use the defined extra spacing
# TEXT_JUSTIFY_FILL computes an extra spacing to fit the stroke width
TEXT_JUSTIFY_LEFT=0
TEXT_JUSTIFY_RIGHT=1
TEXT_JUSTIFY_CENTER=2
TEXT_JUSTIFY_FILL=3

#----------------------------------------------------
# Enhanced path Stroke
#----------------------------------------------------
class DirectionStroke:
			
	def __init__(self,stroke):
		self.stroke=stroke
		points,closed=self.stroke.points
		bezierCurves=(len(points)/3)-1
		
		# Number of curves seems to have an influence on global
		# precision, so adapt precision to number of curves for
		# best results
		self.precision=.05/bezierCurves

		# The stroke length, computed once for all. 
		# It appears that due to precision errors
		# self.stroke.get_point_at_dist(self.length) 
		# may not return a valid point.
		self.length=stroke.get_length(self.precision)

	# Obtain the oriented angle of the tangent at point. The Gimp API gives
	# an actual slope value without orientation, so we disambiguate using
	# an auxiliary point a bit farther in the stroke. This could lead to problems
	# if used too close to the end point (auxiliary point outside the stroke)
	# but we will only use this at least half a character away from the end.
	def computeThetaWithSlope(self,fromPoint,toPoint,slope):
		dX=toPoint[0]-fromPoint[0]
		dY=toPoint[1]-fromPoint[1]
		
		if math.fabs(dX) < .001:
			theta=math.copysign(math.pi/2,dY)
		else:
			theta=math.atan(slope)
			if dX<0:
				theta=theta+math.pi
		return theta % (math.pi*2)
		
	
	# Facade method, returns only if point is OK
	def getRawPointAtDist(self,dist):
		x,y,slope,valid=self.stroke.get_point_at_dist(dist,self.precision)
		if not valid: # Normally quite unlikely, since we avoid the cases where this could happen
			raise Exception('No point found at %6.4f in stroke %s with length %6.4f' % (dist,self.stroke.ID,self.length))
		return x,y,slope
	
	# Enhanced version of stroke.get_point_at_dist(...) that returns
	# information about the path direction. A full version should be able to 
	# handle special cases (extremities or past extremities) but this one is 
	# user at half a caharcter width frol the stroke extremities.
	# 
	def getPointAtDist(self,dist):
		# Now process regular case
		x,y,slope=self.getRawPointAtDist(dist)
		
		# Find the direction of the curve at given point, by comparing 
		# coordinates with nearby point further along the path at an 
		# arbitrary distance delta. We assume that dist+delta is still 
		# on the curve (ie, dist no too close to end)
		delta=.5
		toX,toY,s=self.getRawPointAtDist(dist+delta) 
		theta=self.computeThetaWithSlope([x,y],[toX,toY],slope)

		return (x,y,theta)


#----------------------------------------------------
# Character in text
#----------------------------------------------------
class Character(object):
	def __init__(self,character,width,height):
		self.character=character
		self.width=width
		self.height=height
		self.path=None
		self.kerning=0
		self.position=0
		self.first=False
		self.last=False
		
	def __str__(self):
		if self.path:
			return "<'%s' (%d,%d) @%3.2f, %d stroke(s)>" % (self.character,self.width,self.height,self.position,len(self.path.strokes))
		else:
			return "<'%s' (%d,%d) @%3.2f, (no path)>" % (self.character,self.width,self.height,self.position)
			
#----------------------------------------------------
# Text to work on
#----------------------------------------------------
class Text(object):
	
	def __init__(self,text,fontName,fontSize,
			layout=TEXT_JUSTIFY_CENTER, pivotYChoice=BASELINE, 
			useKerning=True, extraSpacing=0, verticalAdjust=0,
			keepPaths=False, keepUpright=False,
			wiggleXPercent=0, wiggleYPercent=0, wiggleTheta=0):
		self.text=text
		self.fontName=fontName
		self.fontSize=fontSize
		self.pivotYChoice=pivotYChoice
		self.useKerning=useKerning
		self.extraSpacing=extraSpacing
		self.verticalAdjust=verticalAdjust
		self.keepUpright=keepUpright
		self.layout=layout
		self.keepPaths=keepPaths
		self.wiggleXPercent=wiggleXPercent
		self.wiggleYPercent=wiggleYPercent
		self.wiggleTheta=wiggleTheta
		
		self.pivotY=None
		self.characters=[]
		self.workImage=gimp.Image(int(fontSize*4),int(fontSize*4), RGB)
		self.workImage.disable_undo()
		
	def __del__(self):
		gimp.delete(self.workImage)

	def extents(self,text):
		return pdb.gimp_text_get_extents_fontname(text, self.fontSize, PIXELS, self.fontName)
		
	def textPath(self,text):
		if len(text) == 1 and text in blankCharacters:
			path=None
		else:
			l=pdb.gimp_text_fontname(self.workImage, None, 0, 0, text, 0, True, self.fontSize, PIXELS, self.fontName)
			path=pdb.gimp_vectors_new_from_text_layer(self.workImage,l)
			self.workImage.remove_layer(l)
		return path
		
	def initializeCharacter(self,c):
		width,height,ascent,descent=self.extents(c)
		addedChar=Character(c,width,height)
		addedChar.path=self.textPath(c)
		# compute kerning unless first character
		if self.useKerning and len(self.characters) > 0:
			rightChar=self.characters[-1]
			kw,kh,ka,kd=self.extents(rightChar.character+addedChar.character)
			# Kerning is the difference between width with kerning (kw) 
			# and sum of individual character widths (negative for "AV")
			addedChar.kerning=kw-(addedChar.width+rightChar.width)
			if addedChar.kerning !=0:
				trace('Kerning %c -> %c: %3.2f' % (rightChar.character,addedChar.character,addedChar.kerning))

		self.characters.append(addedChar)
	
	def initializeCharacters(self):
		trace('Text: %s' % self.text)
		for c in self.text:
			self.initializeCharacter(c)
			
		self.characters[0].first=True
		self.characters[-1].last=True
		lastChar=self.characters[-1]
			
	# Compute offsets for pivot point Y. Since there is no API to obtain geometry information
	# for the font, some guesswork is required. We will assume that 'X' is fairly symmetrical
	# and that its topmost point is as much above the line of uppercase tops than its lowest point
	# is below the baseline (except for very round fonts this will be 0)
	def computePivotY(self):
		sampleText='X'
		# obtain path for sample text
		path=self.textPath(sampleText)
		
		width,height,ascent,descent=self.extents(sampleText)
		
		minY=height
		maxY=0
		for stroke in path.strokes:
			points,closed=stroke.points
			yValues=[points[i] for i in range(3,len(points),6)]
			minYStroke=min(yValues)
			maxYStroke=max(yValues)
			minY=min(minY,minYStroke)
			maxY=max(maxY,maxYStroke)

		self.wiggleYMax=height
		topCaps=minY+(maxY-ascent)
		# compute all possible pivotY and keep the good one (easier to debug)
		pivot=[0,0,0,0,0,0]
		pivot[BASELINE]=ascent
		pivot[TOP]=0
		pivot[BOTTOM]=height
		pivot[MIDDLEBOX]=height/2.
		pivot[MIDDLECAPS]=(topCaps+ascent)/2.
		pivot[TOPCAPS]=topCaps
		#trace(pivot)
		self.pivotY=pivot[self.pivotYChoice]+self.verticalAdjust
		
	# Lay out the characters on the stroke, by computing their.position coordinate
	def layoutOnStroke(self,stroke):
		# Plain text width
		plainTextWidth=0
		for c in self.characters:
			plainTextWidth=plainTextWidth+c.width+c.kerning
		
		# Check fit on stroke
		if self.layout != TEXT_JUSTIFY_FILL:
			# Check with requested extra spacing if not justified
			textWidth=plainTextWidth+self.extraSpacing*(len(self.characters)-1)
			if textWidth > stroke.length:
				raise Exception('Text width (%3.2f) larger than path stroke length (%3.2f)' % (textWidth,stroke.length))
			extraSpacing=self.extraSpacing
		else: # TEXT_JUSTIFY_FILL
			# Compute required extra spacing. 
			# Can be negative if stroke is too small. 
			# Can get nasty if stroke smaller than one chararacter width
			extraSpacing=(stroke.length-plainTextWidth)/(len(self.characters)-1)
			textWidth=stroke.length
		self.wiggleXMax=textWidth/len(self.characters)
		# Compute offset of left character
		if self.layout==TEXT_JUSTIFY_LEFT:
			offset=0
		elif self.layout==TEXT_JUSTIFY_RIGHT:
			offset=stroke.length-textWidth
		elif self.layout==TEXT_JUSTIFY_CENTER:
			offset=(stroke.length-textWidth)/2.
		else: #TEXT_JUSTIFY_FILL, normally
			offset=0
		
		trace('Plain text width: %3.2f, stroke length: %3.2f, start offset: %3.2f, extraSpacing: %3.2f, actual text width: %3.2f ' % (plainTextWidth,stroke.length,offset, extraSpacing, textWidth))
		
		# set.position for each character
		for c in self.characters:
			offset=offset+c.width/2.+c.kerning
			c.position=offset
			offset=offset+c.width/2.+extraSpacing
			
	# compute final pos for character
	def computeFinalPos(self,c,stroke):
		x,y,slope=stroke.getPointAtDist(c.position)
		if self.keepUpright:
			tilt=0
		else:
			tilt=slope*180/math.pi
		
		wiggleXRange=self.wiggleXMax*self.wiggleXPercent/100.
		wiggleYRange=self.wiggleYMax*self.wiggleYPercent/100.

		wx=random.uniform(-wiggleXRange,wiggleXRange)
		wy=random.uniform(-wiggleYRange,wiggleYRange)
		wtilt=random.uniform(-self.wiggleTheta,self.wiggleTheta)

		return x+wx*math.cos(slope)-wy*math.sin(slope),y+wy*math.cos(slope)+wx*math.sin(slope),tilt+wtilt
		
	# copy path (possibly to different image)
	def copyPath(self,sourcePath,name,img):
		newPath=pdb.gimp_vectors_new(img,name)
		pdb.gimp_image_add_vectors(img,newPath,0)
		self.copyStrokes(sourcePath,newPath)
		return newPath
		
	def copyStrokes(self,sourcePath,targetPath):
		for s in sourcePath.strokes:
			points,closed=s.points
			sid = pdb.gimp_vectors_stroke_new_from_points(targetPath,0, len(points),points, closed)
		
		
	def moveCharacterToStroke(self,c,stroke,img):
		if not c.path:
			return # nothing to do on blank characters
		# copy character path (defined on work image) to final image
		path=self.copyPath(c.path,"'"+c.character+"'",img)
		path.visible=False;
		x,y,tilt=self.computeFinalPos(c,stroke)
		trace('"%s": actual: %3.2f' % (c,x))
		for s in path.strokes:
			 s.rotate(c.width/2.,self.pivotY,tilt)
			 s.translate(x-c.width/2.,y-self.pivotY)
		self.copyStrokes(path,self.finalPath)
		if not self.keepPaths:
			pdb.gimp_image_remove_vectors(img,path)
			 
	def moveCharactersToStroke(self,stroke,img,pathName):
		self.finalPath=pdb.gimp_vectors_new(img,"'%s' over <%s>" % (self.text,pathName))
		self.finalPath.visible=True
		pdb.gimp_image_add_vectors(img,self.finalPath,0)

		trace("Max wiggle X,Y: %3.2f,%3.2f" % (self.wiggleXMax,self.wiggleYMax))
		for c in self.characters:
			self.moveCharacterToStroke(c,stroke,img)
			
	def run(self,path,image):
		if not len(path.strokes):
			raise Exception('No strokes in path "%s"' % path.name)
		pdb.gimp_image_undo_group_start(image)
		self.computePivotY()
		self.initializeCharacters()
		stroke=DirectionStroke(path.strokes[0])
		self.layoutOnStroke(stroke)
		self.moveCharactersToStroke(stroke,image,path.name)
		pdb.gimp_displays_flush()	
		pdb.gimp_image_undo_group_end(image)

def text_along_path(image,layer,path,text,fontName,fontSize,
			layout,pivotYChoice,
			useKerning,extraSpacing,verticalAdjust,
			keepPaths, keepUpright,
			wiggleXPercent,wiggleYPercent,wiggleTheta):
				
	try:
		# extract data from text layer if provided
		if layer:
			if not pdb.gimp_drawable_is_text_layer(layer):
				raise Exception('Drawable "%s" is not a text layer' % layer.name)
			text = pdb.gimp_text_layer_get_text(layer)
			if not text:
				raise Exception('No text in layer "%s"' % layer.name)
			fontName = pdb.gimp_text_layer_get_font(layer)
			fontSize, unit = pdb.gimp_text_layer_get_font_size(layer)
			layout = pdb.gimp_text_layer_get_justification(layer)
			useKerning = pdb.gimp_text_layer_get_kerning(layer)
			extraSpacing = pdb.gimp_text_layer_get_letter_spacing(layer)
		
		if not fontName:
			fontName = pdb.gimp_context_get_font()
		if not text:
			raise Exception('No text provided')
		text=Text(text,fontName,fontSize,
				layout,pivotYChoice,
				useKerning, extraSpacing, verticalAdjust,
				keepPaths, keepUpright,
				wiggleXPercent,wiggleYPercent,wiggleTheta)
		text.run(path,image)
	except Exception as e:
		trace(e.args[0])
		pdb.gimp_message(e.args[0])


# Call form path list: no text layer provided, use full options
def text_along_path_full(image,path,text,fontName,fontSize,
			layout,pivotYChoice,
			useKerning,extraSpacing,verticalAdjust,
			keepPaths, keepUpright,
			wiggleXPercent,wiggleYPercent,wiggleTheta):
	text_along_path(image,None,path,text,fontName,fontSize,
			layout,pivotYChoice,
			useKerning,extraSpacing,verticalAdjust,
			keepPaths, keepUpright,
			wiggleXPercent,wiggleYPercent,wiggleTheta)
	
# Call from Layers list: many options taken from text layer
def text_along_path_layer(image,layer,path,
			pivotYChoice,verticalAdjust,
			keepPaths, keepUpright,
			wiggleXPercent,wiggleYPercent,wiggleTheta):
	text_along_path(image,layer,path,None,None,None,
			None,pivotYChoice,
			None,None,verticalAdjust,
			keepPaths, keepUpright,
			wiggleXPercent,wiggleYPercent,wiggleTheta)
	
# Call from Images's Layer dialog, and fill or stroke the path:
def text_along_path_layer(image,layer,path,
			pivotYChoice,verticalAdjust,
			keepPaths, keepUpright,
			wiggleXPercent,wiggleYPercent,wiggleTheta,
                        fill):
	text_along_path(image,layer,path,None,None,None,
			None,pivotYChoice,
			None,None,verticalAdjust,
			keepPaths, keepUpright,
			wiggleXPercent,wiggleYPercent,wiggleTheta)

        # Now get the path we just made, convert it to a selection
        # and fill or stroke it in a new layer.
        wiggletext = pdb.gimp_image_get_active_vectors(image)
        newlayer = gimp.Layer(image, "path-" + wiggletext.name,
                              image.width, image.height,
                              RGBA_IMAGE, 100, NORMAL_MODE)
        image.add_layer(newlayer, 0)
        if fill :
                pdb.gimp_image_select_item(image, CHANNEL_OP_REPLACE,
                                           wiggletext)
                pdb.gimp_edit_fill(newlayer, FOREGROUND_FILL)
        else :
                pdb.gimp_edit_stroke_vectors(newlayer, wiggletext)
        pdb.gimp_selection_none(image)
        if not keepPaths:
                pdb.gimp_image_remove_vectors(image, wiggletext)

### Registration

whoiam='\n'+os.path.abspath(sys.argv[0])

# Registration items

regImage=		(PF_IMAGE,   'image', 		'Input image:', 	None)
regPath=		(PF_VECTORS, 'path', 		'Guide path:', 		None)
regLayer=		(PF_DRAWABLE,'textLayer',       'Text layer:', 		None)
regText=		(PF_STRING,  'text', 		'Text:', 		'')
regFontName=		(PF_FONT,    'fontName',	'Font name:', 		0)
regFontSize=		(PF_SPINNER, 'fontSize',	'Font size:',		20,(1, 1000, 1))
regLayout=		(PF_OPTION,  'layout', 		'Layout:', 		0, ['Left-justified','Right-justified','Centered','Filled'])
regHeightReference=	(PF_OPTION,  'pivotYChoice', 	'Height reference:', 	0, ['Baseline','Top of box','Bottom of box','Middle of box','Top of caps','Middle of caps'])
regUseKerning=		(PF_TOGGLE,  'useKerning',	'Use kerning:', 	True)
regExtraSpacing=	(PF_FLOAT,   'extraSpacing',	'Extra spacing (px):',	0.)
regVerticalAdjust=	(PF_FLOAT,   'verticalAdjust',	'Vertical adjust (px):',0.)
regKeepPaths=		(PF_TOGGLE,  'keepPaths',	'Keep character paths:',False)
regKeepUpright=		(PF_TOGGLE,  'keepUpright',	'Keep upright:', 	False)
regWiggleXPercent=	(PF_SPINNER, 'wiggleXPercent', 	'Lateral wiggle (%):',	0,(0, 100, 1))
regWiggleYPercent=	(PF_SPINNER, 'wiggleYPercent', 	'Vertical wiggle (%):',	0,(0, 100, 1))
regWiggleTheta=		(PF_SPINNER, 'wiggleTheta', 	'Tilt wiggle (°):',	0,(0, 90, 1))
regFillOrStroke=        (PF_BOOL, "filled",  "Filled", True)



	
register(
	'text-along-path-full',
	'Text along path...'+whoiam,
	'Text along path...',
	'Ofnuts',
	'Ofnuts',
	'2012',
	'Text along path Py...',
	'*',
	[
		regImage,
		regPath,
		regText,
		regFontName,
		regFontSize,
		regLayout,
		regHeightReference,
		regUseKerning,
		regExtraSpacing,
		regVerticalAdjust,
		regKeepPaths,
		regKeepUpright,
		regWiggleXPercent,
		regWiggleYPercent,
		regWiggleTheta
	],
	[],
	text_along_path_full,
	menu='<Vectors>/Tools',
)

register(
	'text-along-path-layer',
	'Text along path...'+whoiam,
	'Text along path...',
	'Ofnuts',
	'Ofnuts',
	'2012',
	'Text along path Py...',
	'*',
	[
		regImage,
		regLayer,
		regPath,
		regHeightReference,
		regVerticalAdjust,
		regKeepPaths,
		regKeepUpright,
		regWiggleXPercent,
		regWiggleYPercent,
		regWiggleTheta
	],
	[],
	text_along_path_layer,
	menu='<Layers>',
)

register(
	'text-along-path-visible',
	'Text along path...'+whoiam,
	'Text along path...',
	'Ofnuts',
	'Ofnuts',
	'2012',
	'Text along path visible...',
	'*',
	[
		regImage,
		regLayer,
		regPath,
		regHeightReference,
		regVerticalAdjust,
		regKeepPaths,
		regKeepUpright,
		regWiggleXPercent,
		regWiggleYPercent,
		regWiggleTheta,
                regFillOrStroke
	],
	[],
	text_along_path_layer,
	menu='<Image>/Layer',
)


main()
