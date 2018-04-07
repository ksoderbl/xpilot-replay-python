#ideas:

#-reuse gc to color objects correctly

#-resize recording linearly by resizing window

#-emit parsed recording

#-resize recording during viewing or in emit

#-attempt to detect map objects: treasure boxes, bases, walls etc.

#-filter out e.g. talk messages or private talk messages

#-attempt to find player position on map (e.g. on blood's music)

#-view where ship is fixed and map rotates




import gzip
import sys
import io
import random

import xpr
from xpr import XPRHeader
from xpr import XPRFrame

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
#from OpenGL.GLUT import *

import os
import random

#set from xpr header
WIDTH = 0
HEIGHT = 0
FPS = 0

# number of pixels in texture
TWIDTH = 4
THEIGHT = 64
TBPP = 3  # bytes per pixel
SMOOTH_PIXELS=True


def makeTexture(w, h, d, j):
	#r = [((i*43+j*32) & 0xff) for i in range(w * h * d)]
	
	#xmul = WIDTH // w
	#ymul = HEIGHT // h
	xmul = 1
	ymul = 1
	
	tex = []
	for y in range(h):
		for x in range(w):
			#r = (x + j) & 0xff;
			#g = (y + j) & 0xff;
			#b = (x + y + j) & 0xff;
			
			r = (x * xmul + j) & 0xff;
			g = (y * ymul + j) & 0xff;
			b = (2 * x * xmul + 3 * y * ymul + j) & 0xff;

			r = (r >> 2) + 1
			g = (g >> 2) + 1
			b = (b >> 1) + 1
			if r > 0xff:
				r = 0xff
			if g > 0xff:
				g = 0xff
			if b > 0xff:
				b = 0xff
											
			tex.append(r)
			tex.append(g)
			tex.append(b)
	
	return tex


def myquit():
	pygame.quit()
	quit()
	
	

def main():
	pygame.init()	
	clock = pygame.time.Clock()
	
	print(sys.argv)
	
	filename = sys.argv[1]
	mode = 'rb'
	
	print('opening ' + filename)
	
	if filename.endswith('.gz'):
		f1 = gzip.open(filename, mode)
	else:
		f1 = open(filename, mode)
		
	#f = io.BufferedReader(f1)
	f = f1
	
	hdr = XPRHeader()	
	hdr.RReadHeader(f)
	
	
	print('xpr magic = ' + hdr.magic)
	print('xpr major = ' + hdr.major)
	print('xpr dot = ' + hdr.dot)
	print('xpr minor = ' + hdr.minor)
	print('xpr nl = ' + hdr.nl)
	print('xpr nick = ' + hdr.nick)
	print('xpr user = ' + hdr.user)
	print('xpr host = ' + hdr.host)
	print('xpr server = ' + hdr.server)
	print('xpr fps = ' + str(hdr.fps))
	print('xpr maxColors = ' + str(hdr.maxColors))
	#print('xpr colors = ', hdr.colors)
	print('xpr gameFontName = ' + hdr.gameFontName)
	print('xpr msgFontName = ' + hdr.msgFontName)
		
	print('xpr width =' + str(hdr.viewWidth))
	print('xpr height =' + str(hdr.viewHeight))
	
	WIDTH = hdr.viewWidth
	HEIGHT = hdr.viewHeight
	
	print("RECORDING: " + str(WIDTH) + "x" + str(HEIGHT))
	
	FPS = hdr.fps
	PALETTE = []
	
	for color in hdr.colors:
		r = (color[1] / 65535)
		g = (color[2] / 65535)
		b = (color[3] / 65535)
		PALETTE.append([r, g, b])
		
	for i in range(len(PALETTE)):
		p = PALETTE[i]
		print(i, p[0], p[1], p[2])
	
	display = (WIDTH,HEIGHT)
	
	#http://www.pygame.org/docs/ref/display.html
	pygame.display.set_mode(display, DOUBLEBUF|OPENGL|RESIZABLE)

	# query aliased and smooth point size
	aps = glGetFloatv(GL_ALIASED_POINT_SIZE_RANGE)
	print('aliased point size range', aps)
	sps = glGetFloatv(GL_SMOOTH_POINT_SIZE_RANGE)
	print('smooth point size range', sps)
	spsg = glGetFloatv(GL_SMOOTH_POINT_SIZE_GRANULARITY)
	print('smooth point size granularity', spsg)
	glPointSize(5.0)
	
	texname = glGenTextures(1)
	glBindTexture(GL_TEXTURE_2D, texname)
	
	j = 0
	
	if SMOOTH_PIXELS:
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
		glShadeModel(GL_FLAT)
	else:
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)	
	
	glClearColor(0.0, 0.0, 0.5, 0.0)
	#glClearColor(1.0, 1.0, 1.0, 0.0)
	glColor3f(1.0, 1.0, 1.0)
	# y goes from HEIGHT to 0 to move origin to the top left
	glOrtho(0.0, WIDTH, HEIGHT, 0, -1.0, 1.0)
	
	# p. 53
	
	glLineWidth(2)
	alwr = glGetFloatv(GL_ALIASED_LINE_WIDTH_RANGE)
	print('GL_ALIASED_LINE_WIDTH_RANGE', alwr)
	alwr = glGetFloatv(GL_SMOOTH_LINE_WIDTH_RANGE)
	print('GL_SMOOTH_LINE_WIDTH_RANGE', alwr)
	slwg = glGetFloatv(GL_SMOOTH_LINE_WIDTH_GRANULARITY)
	print('GL_SMOOTH_LINE_WIDTH_GRANULARITY', slwg)
	
	
	i = 0
	
	frameCounter = 0;
	seconds = 0
	
	pause = False
	
	while True:
		#http://www.pygame.org/docs/ref/event.html
		"""
		QUIT             none
		ACTIVEEVENT      gain, state
		KEYDOWN          unicode, key, mod
		KEYUP            key, mod
		MOUSEMOTION      pos, rel, buttons
		MOUSEBUTTONUP    pos, button
		MOUSEBUTTONDOWN  pos, button
		JOYAXISMOTION    joy, axis, value
		JOYBALLMOTION    joy, ball, rel
		JOYHATMOTION     joy, hat, value
		JOYBUTTONUP      joy, button
		JOYBUTTONDOWN    joy, button
		VIDEORESIZE      size, w, h
		VIDEOEXPOSE      none
		USEREVENT        code
		"""
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				print("event: QUIT")
				print(event.dict)
				myquit()
			if event.type == pygame.ACTIVEEVENT:
				print("event: ACTIVEEVENT")
				print(event.dict)
			if event.type == pygame.KEYDOWN:
				changeTexture = False
				print("event: KEYDOWN")
				print(event.dict)
				pause = not pause
			if event.type == pygame.KEYUP:
				changeTexture = True
				print("event: KEYUP")
				print(event.dict)
				#pause = False
			if event.type == pygame.MOUSEMOTION:
				pass
				#print("event: MOUSEMOTION")
				#print(event.dict)
				
				#pos = event.dict['pos']
				#mousePos[0] = pos[0]
				#mousePos[1] = HEIGHT - pos[1]
				
			if event.type == pygame.MOUSEBUTTONUP:
				print("event: MOUSEBUTTONUP")
				print(event.dict)
				if event.dict['button'] == 4:
					FPS += 1
					print("FPS was increased to", FPS)
					
			if event.type == pygame.MOUSEBUTTONDOWN:
				print("event: MOUSEBUTTONDOWN")
				print(event.dict)
				if event.dict['button'] == 5:
					FPS -= 1
					if FPS < 1:
						FPS = 1
					else:
						print("FPS was decreased to", FPS)
				
			if event.type == pygame.JOYAXISMOTION:
				print("event: JOYAXISMOTION")
				print(event.dict)
			if event.type == pygame.JOYBALLMOTION:
				print("event: JOYBALLMOTION")
				print(event.dict)
			if event.type == pygame.JOYHATMOTION:
				print("event: JOYHATMOTION")
			if event.type == pygame.JOYBUTTONUP:
				print("event: JOYBUTTONUP")
				print(event.dict)
			if event.type == pygame.JOYBUTTONDOWN:
				print("event: JOYBUTTONDOWN")
				print(event.dict)
			if event.type == pygame.VIDEORESIZE:
				print("event: VIDEORESIZE")
				print(event.dict)
				WIDTH = event.dict['w']
				HEIGHT = event.dict['h']
				display = event.dict['size']
				print(display)
				screen=pygame.display.set_mode(event.dict['size'],DOUBLEBUF|OPENGL|RESIZABLE)

				
			if event.type == pygame.VIDEOEXPOSE:
				print("event: VIDEOEXPOSE")
				print(event.dict)
			if event.type == pygame.USEREVENT:
				print("event: USEREVENT")
				print(event.dict)


		if not pause:			
			# 3 because of GL_RGB
			if False:
				texture = os.urandom(TWIDTH * THEIGHT * TBPP)
			else:
				r = makeTexture(TWIDTH, THEIGHT, TBPP, j )
				#print(r)
				texture = bytearray(r)
				#j += random.randint(1, 10)
				
			j += 3
			
			
			if TBPP == 3:
				val = GL_RGB
			else:
				val = GL_RGBA
			glTexImage2D(GL_TEXTURE_2D, 0, val, TWIDTH, THEIGHT, 0, val, GL_UNSIGNED_BYTE, texture)			
			
		
			frame = XPRFrame()
			frame.RReadFrame(f)
	
			if frame.eof:
				print('endframe', frameCounter, 'recording seconds =', frameCounter/FPS)
				print('endframe', frameCounter, 'recording minutes =', frameCounter/(FPS*60))
				sys.exit()
				
			#print("=" * 10, "read frame", frameCounter, "=" * 10)
			#print("frame size: ", frame.w, "x", frame.h)
			
			#DRAW FRAME
			glClear(GL_COLOR_BUFFER_BIT)
			
			glEnable(GL_TEXTURE_2D)
			
			glBegin(GL_POLYGON)
			glTexCoord2f(0.0, 0.0)
			glVertex3f(0, 0, 0.0)
			glTexCoord2f(1.0, 0.0)
			glVertex3f(WIDTH, 0, 0.0)
			glTexCoord2f(1.0, 1.0)
			glVertex3f(WIDTH, HEIGHT, 0.0)
			glTexCoord2f(0.0, 1.0)
			glVertex3f(0, HEIGHT, 0.0)
			glEnd()
			
			glDisable(GL_TEXTURE_2D)
			
			#don't show texture background
			#glClear(GL_COLOR_BUFFER_BIT)
			
			#glColor3f(1.0, 1.0, 1.0)
			#drawText(500, 500, 'ja päivää')
	
		
			# set the colors to use in the frame
				
			#glLineStipple(1, random.randint(0xf000, 0xffff)) #0xaaaa
			#glEnable(GL_LINE_STIPPLE)
					
			for shape in frame.shapes:
				shape.draw(PALETTE)
	
			
			#if (frameCounter % fps) == (fps - 1):
			#	seconds += 1
			frameCounter += 1
			print("frameCounter", frameCounter)
		
			pygame.display.flip()
		
		clock.tick(FPS)
		
		#b = RReadByte(f)
		#h = hex(b)
		#h = h[2:]
		#while len(h) < 2:
		#	h = '0' + h
			
		#i = i + 1
		#print(h, end=' ')
		#if (i >= 32):
		#	print('')
		#	i = 0
	myquit()
	
if __name__ == '__main__':
        main()
