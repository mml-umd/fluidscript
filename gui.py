import trackbar
import cv2
import manifold
import config
import element
import numpy as np
import sys
import threadedclass
import util
import blobutil
import colorchannel
import interval
import time

class GUI(threadedclass.ThreadedClass):
	def __init__(self, flu):
		super().__init__()

		self.threadedClassName = 'GUI'

		self.fluidscript = flu

		self.selectedElementClass = element.Point
		self.lastSelectedElementClass = None

		self.controlTrackbars = []

		#Brightness and contrast slider
		self.brightBar = trackbar.Trackbar(255, 128, "Brightness", list=self.controlTrackbars)
		self.contrastBar = trackbar.Trackbar(255, 128, "Contrast", list=self.controlTrackbars)
		
		#Delta blur denominator bar
		self.blurBar = trackbar.Trackbar(32, 0, "Norm", list=self.controlTrackbars)

		self.currentMousePos = (0, 0)
		self.currentHover = None

		self.latestFrame = None

		self.displaySideBySide = True
		
		self.colorChannels = []

	def createColorChannel(self, name):
		c = colorchannel.ColorChannel(name)
		self.colorChannels.append(c)
		print(f'Created color {name}')
		return c

	def threadInitFunction(self):
		cv2.namedWindow('Controls', cv2.WINDOW_NORMAL)

		for bar in self.controlTrackbars:
			bar.addTo('Controls')

		for c in self.colorChannels:
			cv2.namedWindow(c.name, cv2.WINDOW_NORMAL)
			for bar in c.trackbars:
				bar.addTo(c.name)		

		cv2.namedWindow('Main Window')
		cv2.setMouseCallback('Main Window', self.handleMouse)

	def threadFunction(self):
		keycode = cv2.waitKeyEx(1)
		self.handleKey(keycode)

		if not self.fluidscript.processor.latestFrameReadyEvent.wait(timeout=1):
			pass

		self.fluidscript.processor.latestFrameReadyEvent.clear()
		
		if(self.currentHover != None):
			self.currentHover.hover = False  #Un-highlight the current element
		self.currentHover = None

		nearestDist = None	#Find nearest element for highlighting
		nearestElem = None	#May be None if none hovered

		for elem in element.getAllElements():
			dist = blobutil.dist(self.currentMousePos, elem.pos())
			if dist <= config.HOVER_DISTANCE and (not nearestDist or dist < nearestDist):
				nearestDist = dist
				nearestElem = elem

		if nearestElem:
			if(self.currentHover != None):
				self.currentHover.hover = False  #Swap out the hover flag to the new closest element

			self.currentHover = nearestElem #Set the new hover element
			self.currentHover.hover = True #Highlight it


		if self.displaySideBySide:
			guiImage = np.concatenate((self.fluidscript.processor.latestFrame, self.fluidscript.camera.latestFrame), axis=0)
		else:
			guiImage = self.fluidscript.processor.latestFrame

		cv2.imshow('Main Window', guiImage)

	def threadExitFunction(self):
		cv2.destroyAllWindows()
		print('CV2 Destroyed.')

	def saveFrame(self, annotation=''):	#Saves a frame to disk
		if not self.fluidscript.processor.latestFrame is None:
			if not annotation == '':
				annotation += '_'
				
			filename = util.getDatedFile(f'{{}}_{annotation}frame.png')
			rawFilename = util.getDatedFile(f'{{}}_{annotation}frameraw.png')

			cv2.imwrite(filename, self.fluidscript.processor.latestFrame)
			cv2.imwrite(rawFilename, self.fluidscript.camera.latestFrame)
			print('Saved frame: ' + filename)
		else:
			print('No frame to save.')
			
	def handleKey(self, keycode):
		if keycode < 0:
			return

		try:
			key = config.KEYMAP[keycode]	#Keycode may not exist, keyerror

			if self.currentHover:
				if key == ']':
					self.currentHover.nextID()

				elif key == '[':
					self.currentHover.previousID()

				elif key == 'up':
					self.currentHover.move((0, -1))

				elif key == 'down':
					self.currentHover.move((0, 1))

				elif key == 'left':
					self.currentHover.move((-1, 0))

				elif key == 'right':
					self.currentHover.move((1, 0))

			if key == 'z':
				self.selectedElementClass = element.Point
				print('Switched to Point')

			elif key == 'x':
				self.selectedElementClass = element.Rect
				print("Switched to Rect")

			elif key == 'o':
				self.fluidscript.epr1.inc()
			elif key == 'k':
				self.fluidscript.epr1.dec()
			elif key == 'p':
				self.fluidscript.epr2.inc()
			elif key == 'l':
				self.fluidscript.epr2.dec()



			elif key == ',':
				self.fluidscript.processor.displayR ^= 1 	#Toggle

			elif key == '.':
				self.fluidscript.processor.displayG ^= 1

			elif key == '/':
				self.fluidscript.processor.displayB ^= 1

			elif key == 's':
				self.saveFrame()

			elif key == 'r':
				if not self.fluidscript.videoRecorder.isRecording:
					self.fluidscript.videoRecorder.start()
				else:
					self.fluidscript.videoRecorder.kill()

			elif key == 'd':
				self.displaySideBySide ^= 1

			elif key == 'q':
				self.fluidscript.kill()

			elif key == 'm':
				self.fluidscript.processor.displayMask ^= 1

			elif key == 'h':
				self.fluidscript.processor.displayOverlay ^= 1

			elif key == 'b':
				self.fluidscript.processor.displayBlobs ^= 1

			elif key == 't':
				self.fluidscript.processor.displayTracers ^= 1

			elif key == 'n':
				self.fluidscript.camera.reOpen()

			elif key == 'backspace':	#Start and stop the user script
				if self.fluidscript.oneShot:
					if not self.fluidscript.onFrameRunState:
						self.fluidscript.start()
					else:
						pass
				else:
					if self.fluidscript.onFrameRunState:
						self.fluidscript.stop()

					else:
						self.fluidscript.start()

			for k in range(len(config.VALVE_KEYS)):	#Operate the various valves
				if key == config.VALVE_KEYS[k]:
					manifold.toggle(k)

		except Exception as e:
			print("Error running keycommand: " + str(e))

	def handleMouse(self, event, x, y, flags, param):  #Handle creating Elements from clicks and drags
		if x < 0 or x > self.fluidscript.camera.width or y < 0 or y > self.fluidscript.camera.height:	#No out of bounds clicking!
			return

		if(event == cv2.EVENT_MOUSEMOVE):
			self.currentMousePos = (x, y)

		if(event == cv2.EVENT_LBUTTONDOWN):
			self.lastSelectedElementClass = self.selectedElementClass #Hold this until done in case of switching type during drag


			if self.selectedElementClass == element.Point:
				newElement = element.Point((x, y))
			elif self.selectedElementClass == element.Rect:
				newElement = element.Rect((x, y), (x+10, y+10))
			else:
				print('No element class selected')

		if(event == cv2.EVENT_LBUTTONUP):
			if self.selectedElementClass == element.Rect:
				obj = element.getRects()[-1]

				x1 = obj._pos[0]
				y1 = obj._pos[1]

				obj._pos2 = (max(x, x1), max(y, y1))
				obj._pos = (min(x, x1), min(y, y1))

			else:
				pass

			self.lastSelectedElementClass = None
			element.writeElements()

		if(event == cv2.EVENT_RBUTTONDOWN and self.currentHover != None):  #Right click removes elements
			self.currentHover.destroy()
			self.currentHover = None



			