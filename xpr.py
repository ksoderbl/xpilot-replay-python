
import gzip
import sys
import io
import math

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
#from OpenGL.GLUT import *

RC_NEWFRAME=0x0b        #11
RC_DRAWARC=0x0c         #12
RC_DRAWLINES=0x0d       #13
RC_DRAWLINE=0x0e        #14
RC_DRAWRECTANGLE=0x0f   #15
RC_DRAWSTRING=0x10      #16
RC_FILLARC=0x11         #17
RC_FILLPOLYGON=0x12     #18
RC_PAINTITEMSYMBOL=0x13 #19
RC_FILLRECTANGLE=0x14   #20
RC_ENDFRAME=0x15        #21
RC_FILLRECTANGLES=0x16  #22
RC_DRAWARCS=0x17        #23
RC_DRAWSEGMENTS=0x18    #24
RC_GC=0x19              #25
RC_NOGC=0x1a            #26
RC_DAMAGED=0x1b         #27
RC_TILE=0x1c            #28
RC_NEW_TILE=0x1d        #29

RC_GC_FG = (1 << 0)
RC_GC_BG = (1 << 1)
RC_GC_LW = (1 << 2)
RC_GC_LS = (1 << 3)
RC_GC_DO = (1 << 4)
RC_GC_FU = (1 << 5)
RC_GC_DA = (1 << 6)
RC_GC_B2 = (1 << 7)
RC_GC_FS = (1 << 8)
RC_GC_XO = (1 << 9)
RC_GC_YO = (1 << 10)
RC_GC_TI = (1 << 11)

def ShapeName(shapeId):
	if shapeId == RC_NEWFRAME: return 'RC_NEWFRAME'
	elif shapeId == RC_DRAWARC: return 'RC_DRAWARC'
	elif shapeId == RC_DRAWLINES: return 'RC_DRAWLINES'
	elif shapeId == RC_DRAWLINE: return 'RC_DRAWLINE'
	elif shapeId == RC_DRAWRECTANGLE: return 'RC_DRAWRECTANGLE'
	elif shapeId == RC_DRAWSTRING: return 'RC_DRAWSTRING'
	elif shapeId == RC_FILLARC: return 'RC_FILLARC'
	elif shapeId == RC_FILLPOLYGON: return 'RC_FILLPOLYGON'
	elif shapeId == RC_PAINTITEMSYMBOL: return 'RC_PAINTITEMSYMBOL'
	elif shapeId == RC_FILLRECTANGLE: return 'RC_FILLRECTANGLE'
	elif shapeId == RC_ENDFRAME: return 'RC_EMDFRAME'
	elif shapeId == RC_FILLRECTANGLES: return 'RC_FILLRECTANGLES'
	elif shapeId == RC_DRAWARCS: return 'RC_DRAWARCS'
	elif shapeId == RC_DRAWSEGMENTS: return 'RC_DRAWSEGMENTS'
	elif shapeId == RC_GC: return 'RC_GC'
	elif shapeId == RC_NOGC: return 'RC_NOGC'
	elif shapeId == RC_DAMAGED: return 'RC_DAMAGED'
	elif shapeId == RC_TILE: return 'RC_TILE'
	elif shapeId == RC_NEW_TILE: return 'RC_NEW_TILE'
	else: return 'UNKNOWN SHAPE'



def RReadString(f):
	w = f.read(2)
	#print('w[0] =', hex(w[0]))
	#print('w[1] =', hex(w[1]))
	length = w[0] + (w[1]<<8)
	#print('length', length)
	s = f.read(length)
	##print('read string ' + str(s))
	#s is bytes, return string
	return s.decode('utf-8')

def RReadUShort(f):
	w = f.read(2)
	us = w[0] + (w[1]<<8)
	##print('read ushort ' + hex(us))
	return us

def RReadShort(f):
	h = RReadUShort(f)
	if h & 0x8000:
		h = -(-h & 0xffff)
	return h

	
def RReadULong(f):
	w = f.read(4)
	ul = w[0] + (w[1]<<8) + (w[2]<<16) + (w[3]<<24)
	##print('read ulong ' + hex(ul))
	return ul

def RReadLong(f):
	l = RReadULong(f)
	if l & 0x80000000:
		l = -(-l & 0xffffffff)
	return l

def RReadByte(f):
	b = f.read(1)
	return ord(b)
	
def RReadTile(f):
	ch = RReadByte(f)
	tileId = RReadByte(f)
	
	if ch == RC_TILE:
		if tileId == 0:
			return None
		#TODO: find tile from tile list
		return None
	
	if ch != RC_NEW_TILE:
		#print('ch=', ch, 'Expected RC_NEW_TILE', RC_NEW_TILE)
		sys.exit()
		
	w = RReadUShort(f)
	h = RReadUShort(f)
	n = w * h
	#print('tile w =', w)
	#print('tile h =', h)
	#print('tile n =', n)
	data = f.read(n)
	tile = [tileId, w, h, data]
	return tile

def drawText(x, y, text):
	position = (x, y, 0)
	font = pygame.font.Font(None, 16)
	textSurface = font.render(text, True, (255,255,0,255), (0,0,0,255))
	textData = pygame.image.tostring(textSurface, "RGBA", True)
	glRasterPos3d(*position)
	glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData) 	


class XPR:
	def __init__ (self):
		pass
		
class XPRHeader:
	def __init__ (self):
		pass

	def RReadHeader(self, f):
		self.magic = str(f.read(4))
		self.major = str(f.read(1))
		self.dot = str(f.read(1))
		self.minor = str(f.read(1))
		self.nl = str(f.read(1))
				
		#TODO: check magic, dot, nl, major and minor
		
		self.nick = RReadString(f)
		self.user = RReadString(f)
		self.host = RReadString(f)
		self.server = RReadString(f)
		self.fps = RReadByte(f)
		self.recDate = RReadString(f)
		self.maxColors = RReadByte(f)
				
		self.colors = []
		for i in range(0, self.maxColors):
			#print('reading color ' + str(i))
			pixel = RReadULong(f)
			red = RReadUShort(f)
			green = RReadUShort(f)
			blue = RReadUShort(f)
			self.colors.append((pixel, red, green, blue))
		
	
		self.gameFontName = RReadString(f)
		self.msgFontName = RReadString(f)
		self.viewWidth = RReadUShort(f)
		self.viewHeight = RReadUShort(f)
		#print('w, h = %d, %d' % (self.viewWidth, self.viewHeight) )
	
		
class XPRGCValues:
	def __init__(self):
		self.inputMask = 0
		self.foreground = 0
		self.background = 0
		pass
		
	def __repr__(self):
		return "inputmask = " + hex(self.inputMask) +\
			"fg="+str(self.foreground)+\
			"bg="+str(self.background)
		
	def RReadGCValues(self, f):
		gc = RReadByte(f)
		#TODO handle RC_NOGC etc.
		if gc == RC_GC:
			inputMask = RReadByte(f)
						
			if inputMask & RC_GC_B2:
				inputMask2 = RReadByte(f)
				inputMask |= (inputMask2 << 8)
			
			self.inputMask = inputMask
			if inputMask & RC_GC_FG:
				self.foreground = RReadByte(f)
			if inputMask & RC_GC_BG:
				self.background = RReadByte(f)
			if inputMask & RC_GC_LW:
				self.lineWidth = RReadByte(f)
			if inputMask & RC_GC_LS:
				self.lineStyle = RReadByte(f)
			if inputMask & RC_GC_DO:
				self.dashOffset = RReadByte(f)
			if inputMask & RC_GC_FU:
				self.function = RReadByte(f)
			if inputMask & RC_GC_DA:
				self.numDashes = RReadByte(f)
				self.dashes = []
				for i in range(self.numDashes):
					dash = RReadByte(f)
					self.dashes.append(dash)
			if inputMask & RC_GC_FS:
				self.fillStyle = RReadByte(f)
			if inputMask & RC_GC_XO:
				self.tsXOrigin = RReadLong(f)
			if inputMask & RC_GC_YO:
				self.tsYOrigin = RReadLong(f)
			if inputMask & RC_GC_TI:
				self.tile = RReadTile(f)	
		else:
			# should be an assertion ???
			printf("NO GC VALUES")

#
# Shape classes
#
class XPRShape:
	def __init__(self):
		self.GCValues = None
		self.fill = False;
		self.shapeId = 0
	def shapeName(self):
		return ShapeName(self.shapeId)
	def draw(self, palette):
		print("tried to draw", self.shapeName())
		#sys.exit()
		


class XPRArc(XPRShape):
	def __init__(self):
		XPRShape.__init__(self)
	def RReadArcShape(self, f):
		self.x = RReadShort(f)
		self.y = RReadShort(f)
		self.w = RReadByte(f)
		self.h = RReadByte(f)
		self.angle1 = RReadShort(f)
		self.angle2 = RReadShort(f)
	def draw(self, palette):
		#glColor3f(1.0, 0.5, 0.0)
		fg = self.GCValues.foreground
		color = palette[fg]
		glColor3f(color[0], color[1], color[2])
		
		x = self.x
		y = self.y
		w = self.w
		h = self.h
		a1 = self.angle1
		a2 = self.angle2
		#print("orange angles:", a1, a2)

		r1 = w // 2
		r2 = h // 2
		mx = x + r1
		my = y + r2
		deg1 = a1 // 64
		deg2 = a2 // 64
		degdiff = deg2 - deg1
		#print("r1", r1, "r2", r2, "mx", mx, "my", my, "deg1", deg1, "deg2", deg2, "degdiff", degdiff)
		parts = 12
		glBegin(GL_LINE_STRIP)
		for i in range(parts + 1):
			deg = deg1 + i * degdiff / parts
			#print("i,", i, "deg", deg)
			
			xi = mx + r1 * math.cos(deg * 2 * math.pi / 360)
			yi = my - r2 * math.sin(deg * 2 * math.pi / 360)
			glVertex2f(xi, yi)
		glEnd()
	



class XPRArcs(XPRShape):
	def __init__(self):
		XPRShape.__init__(self)
		self.arcs = []
	def RReadArcsShape(self, f):
		n = RReadUShort(f)
		for i in range(n):
			x = RReadShort(f)
			y = RReadShort(f)
			w = RReadByte(f)
			h = RReadByte(f)
			angle1 = RReadShort(f)
			angle2 = RReadShort(f)
			arc = [x, y, w, h, angle1, angle2]
			self.arcs.append(arc)
	def draw(self, palette):
		#glColor3f(0.0, 1.0, 1.0)
		fg = self.GCValues.foreground
		color = palette[fg]
		glColor3f(color[0], color[1], color[2])
		for arc in self.arcs:
			x = arc[0]
			y = arc[1]
			w = arc[2]
			h = arc[3]
			a1 = arc[4]
			a2 = arc[5]
						
			r1 = w // 2
			r2 = h // 2
			mx = x + r1
			my = y + r2
			deg1 = a1 // 64
			deg2 = a2 // 64
			degdiff = deg2 - deg1
			#print("r1", r1, "r2", r2, "mx", mx, "my", my, "deg1", deg1, "deg2", deg2, "degdiff", degdiff)
			parts = 12
			glBegin(GL_LINE_STRIP)
			for i in range(parts + 1):
				deg = deg1 + i * degdiff / parts
				#print("i,", i, "deg", deg)
				
				xi = mx + r1 * math.cos(deg * 2 * math.pi / 360)
				yi = my - r2 * math.sin(deg * 2 * math.pi / 360)
				glVertex2f(xi, yi)
			glEnd()


class XPRDamaged(XPRShape):
	def __init__(self):
		XPRShape.__init__(self)
	def RReadDamagedShape(self, f):
		self.damage = RReadByte(f)


class XPRItemSymbol(XPRShape):
	def __init__(self):
		XPRShape.__init__(self)
	def RReadItemSymbolShape(self, f):
		self.itemType = RReadByte(f)
		self.x = RReadShort(f)
		self.y = RReadShort(f)


class XPRLine(XPRShape):
	def __init__(self):
		XPRShape.__init__(self)
	def RReadLineShape(self, f):
		self.x1 = RReadShort(f)
		self.y1 = RReadShort(f)
		self.x2 = RReadShort(f)
		self.y2 = RReadShort(f)
	def draw(self, palette):
		fg = self.GCValues.foreground
		color = palette[fg]
		glColor3f(color[0], color[1], color[2])
		
		glBegin(GL_LINES)
		glVertex2i(self.x1, self.y1)
		glVertex2i(self.x2, self.y2)
		glEnd()

class XPRLines(XPRShape):
	def __init__(self):
		XPRShape.__init__(self)
		self.points = []
	def RReadLinesShape(self, f):
		n = RReadUShort(f)
		for i in range(n):
			x = RReadShort(f)
			y = RReadShort(f)
			point = [x, y]
			self.points.append(point)
		self.mode = RReadByte(f)
	def draw(self, palette):
		fg = self.GCValues.foreground
		color = palette[fg]
		
		#glColor3f(color[0], color[1], color[2])
		
		glColor3f(0, 0, 0)
		
		glBegin(GL_LINE_STRIP)
		for point in self.points:
			x = point[0]
			y = point[1]
			glVertex2i(x, y)
		glEnd()


class XPRPolygon(XPRShape):
	def __init__(self):
		XPRShape.__init__(self)
		self.points = []
	def RReadPolygonShape(self, f):
		n = RReadUShort(f)
		for i in range(n):
			x = RReadShort(f)
			y = RReadShort(f)
			point = [x, y]
			self.points.append(point)
		self.polygonShape = RReadByte(f)
		self.mode = RReadByte(f)
	def draw(self, palette):
		
		fg = self.GCValues.foreground
		color = palette[fg]
		glColor3f(color[0], color[1], color[2])
		glColor3f(1.0, 0, 0)
		#TODO: make this use GL_POLYGON
		glBegin(GL_LINE_LOOP)
		pts = self.points[0:-1]
		for point in pts:
			x = point[0]
			y = point[1]
			glVertex2i(x, y)
		glEnd()				

class XPRRectangle(XPRShape):
	def __init__(self):
		XPRShape.__init__(self)
		self.rectangle = None
	def RReadRectangleShape(self, f):
		x = RReadShort(f)
		y = RReadShort(f)
		w = RReadByte(f)
		h = RReadByte(f)
		self.rectangle = [x, y, w, h]
	def draw(self, palette):
		#print(self.GCValues)
		fg = self.GCValues.foreground
		color = palette[fg]
		glColor3f(color[0], color[1], color[2])
				
		rect = self.rectangle
		x = rect[0]
		y = rect[1]
		w = rect[2]
		h = rect[3]
		glBegin(GL_QUADS)
		glVertex2i(x, y)
		glVertex2i(x+w, y)
		glVertex2i(x+w, y+h)
		glVertex2i(x, y+h)
		glEnd()

		

class XPRRectangles(XPRShape):
	def __init__(self):
		XPRShape.__init__(self)
		self.rectangles = []
	def RReadRectanglesShape(self, f):
		n = RReadUShort(f)
		for i in range(n):
			x = RReadShort(f)
			y = RReadShort(f)
			w = RReadByte(f)
			h = RReadByte(f)
			rect = [x, y, w, h]
			self.rectangles.append(rect)
	def draw(self, palette):
		fg = self.GCValues.foreground
		color = palette[fg]
		#glColor3f(color[0], color[1], color[2])
		glColor3f(0, 0, 0)
		
		for rect in self.rectangles:
			x = rect[0]
			y = rect[1]
			w = rect[2]
			h = rect[3]
			glBegin(GL_QUADS)
			glVertex2i(x, y)
			glVertex2i(x+w, y)
			glVertex2i(x+w, y+h)
			glVertex2i(x, y+h)
			glEnd()


class XPRSegments(XPRShape):
	def __init__(self):
		XPRShape.__init__(self)
		self.segments = []
	def RReadSegmentsShape(self, f):
		n = RReadUShort(f)
		for i in range(n):
			x1 = RReadShort(f)
			y1 = RReadShort(f)
			x2 = RReadShort(f)
			y2 = RReadShort(f)
			segment = [x1, y1, x2, y2]
			self.segments.append(segment)
	def draw(self, palette):
		fg = self.GCValues.foreground
		color = palette[fg]
		glColor3f(color[0], color[1], color[2])
		glBegin(GL_LINES)
		for segment in self.segments:
			x1 = segment[0]
			y1 = segment[1]
			x2 = segment[2]
			y2 = segment[3]
			glVertex2i(x1, y1)
			glVertex2i(x2, y2)
		glEnd()


class XPRString(XPRShape):
	def __init__(self):
		XPRShape.__init__(self)
	def RReadStringShape(self, f):
		self.x = RReadShort(f)
		self.y = RReadShort(f)
		self.font = RReadByte(f)
		self.length = RReadUShort(f)   # redundant???
		self.s = f.read(self.length).decode('utf-8')
	def draw(self, palette):
		fg = self.GCValues.foreground
		color = palette[fg]
		glColor3f(color[0], color[1], color[2])
		drawText(self.x, self.y, self.s)
		#print(self.s)
		







class XPRFrame:
	def __init__ (self):
		self.shapes = []
		
	def CreateShape(self, shapeId, f):
		if shapeId in [RC_DRAWARC, RC_FILLARC]:
			shape = XPRArc()
			shape.fill = (shapeId == RC_FILLARC)
			shape.RReadArcShape(f)
			
		elif shapeId == RC_DRAWARCS:
			shape = XPRArcs()
			shape.RReadArcsShape(f)
			
		elif shapeId == RC_DRAWLINE:
			shape = XPRLine()
			shape.RReadLineShape(f)
			
		elif shapeId == RC_DRAWLINES:
			shape = XPRLines()
			shape.RReadLinesShape(f)
			
		elif shapeId in [RC_DRAWRECTANGLE, RC_FILLRECTANGLE]:
			shape = XPRRectangle()
			shape.fill = (shapeId == RC_FILLRECTANGLE)
			shape.RReadRectangleShape(f)
						
		elif shapeId == RC_DRAWSTRING:
			shape = XPRString()
			shape.RReadStringShape(f)
			
		elif shapeId == RC_FILLPOLYGON:
			shape = XPRPolygon()
			shape.fill = True
			shape.RReadPolygonShape(f)
			
		elif shapeId == RC_PAINTITEMSYMBOL:
			shape = XPRItemSymbol()
			shape.RReadItemSymbolShape(f)
			
		elif shapeId == RC_FILLRECTANGLES:
			shape = XPRRectangles()
			shape.fill = True
			shape.RReadRectanglesShape(f)
			
		elif shapeId == RC_DRAWSEGMENTS:
			shape = XPRSegments()
			shape.RReadSegmentsShape(f)
						
		elif shapeId == RC_DAMAGED:
			shape = XPRDamaged()
			shape.RReadDamagedShape(f)
			
		else:	
			self.todo(shapeId)

		shape.shapeId = shapeId
		return shape
		
	
	def todo(self, shapeId):
		print('TODO:', shapeId, ShapeName(shapeId))
		sys.exit()
	
	def RReadFrame(self, f):
		self.eof = False
		
		#
		# ASSUME FIRST BYTE IN FRAME MUST BE RC_NEWFRAME
		#
		
		c = f.read(1)
		if c == b'':
			print('got EOF, exiting...')
			self.eof = True
			return None
		
		b = ord(c)
				
		if b != RC_NEWFRAME:
			return None
			
		#
		# FRAME WIDTH AND HEIGHT
		#
			
		self.w = RReadUShort(f)
		self.h = RReadUShort(f)
		
		#
		#
		#
		
		#print("frame: " + str(self.w) + "x" + str(self.h))
		
		done = False
		
		#
		# READ SHAPES FROM FRAME
		#
		
		while not done:
			
			shapeId = RReadByte(f)
			#print('shape', shape, hex(shape), ShapeName(shape))
			
			if shapeId in [RC_DRAWARC, 
				RC_DRAWLINES, 
				RC_DRAWLINE, 
				RC_DRAWRECTANGLE,
				RC_DRAWSTRING, 
				RC_FILLARC, 
				RC_FILLPOLYGON, 
				RC_PAINTITEMSYMBOL,
				RC_FILLRECTANGLE, 
				RC_FILLRECTANGLES, 
				RC_DRAWARCS, 
				RC_DRAWSEGMENTS, 
				RC_DAMAGED]:
				
				#
				# GC VALUES PERTAIN TO THE SHAPE OBJECT
				#
				gcval = XPRGCValues()
				gcval.RReadGCValues(f)
				
				shape = self.CreateShape(shapeId, f)
				#if shapeId == RC_FILLRECTANGLE:
				#	print(gcval)
				
				shape.GCValues = gcval
				self.shapes.append(shape)

			elif shapeId == RC_ENDFRAME:
				#print("endframe: done")
				done = True
			else:
				self.todo(shapeId)
	
