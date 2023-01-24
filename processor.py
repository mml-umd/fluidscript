import framecounter
import config
import threading
import filterutil
import cv2
import element
import imutils
import manifold
import blob
import math
import util
import blobutil
import threadedclass
import numpy as np
from datetime import datetime

#This class creates the full image to put on the GUI (everything)

class Processor(threadedclass.ThreadedClass):
	def __init__(self, flu):
		super().__init__()

		self.threadedClassName = 'Processor'

		self.fluidscript = flu
		self.fpsCounter = framecounter.FrameCounter()

		self.displayB = True
		self.displayG = True
		self.displayR = True
		self.displayElements = True
		self.displayOverlay = False
		self.displayMask = False
		self.displayTracers = False
		self.displayBlobs = True

		self.latestFrame = None
		self.latestFrameReadyEvent = threading.Event()
		self.latestFrameReadyEventOnFrame = threading.Event()

	def threadFunction(self):
		if self.fluidscript.camera.latestFrameReadyEvent.wait(timeout=1):	#Must use timeout, so that the thread can be killed.
			self.fluidscript.camera.latestFrameReadyEvent.clear()
			frame = self.fluidscript.camera.latestFrame

			self.doVision(frame)
			self.fpsCounter.count()

		else:
			#print('Processor Timeout')
			pass

	def doVision(self, inputImg):  #Processes a frame and retreives blob, processes elements
		
		pipelineImg = inputImg	#in BGR format

		pipelineImg = filterutil.blurDeltaNormal(pipelineImg, self.fluidscript.gui.blurBar.getVal() ** 2)
		pipelineImg = filterutil.brightnessAndContrast(pipelineImg, self.fluidscript.gui.brightBar.getVal() - 127, self.fluidscript.gui.contrastBar.getVal() - 127)  #Apply bright/contr

		hsvImage = cv2.cvtColor(pipelineImg, cv2.COLOR_BGR2HSV)

		sumMask = None

		for channel in self.fluidscript.gui.colorChannels:
			mask = channel.getMask(hsvImage)

			if sumMask is None:
				sumMask = mask
			else:
				sumMask = cv2.bitwise_or(sumMask, mask)

		if self.displayMask:
			pipelineImg = cv2.bitwise_and(pipelineImg, pipelineImg, mask = cv2.bitwise_not(sumMask))  #Masked image (includes color from original)




		for channel in self.fluidscript.gui.colorChannels:
			if self.displayBlobs:
				channel.blobgroup.drawBlobs(pipelineImg)

			if self.displayTracers and len(channel.tracers) > 0:
				for tracer in channel.tracers:
					cv2.line(pipelineImg, tracer[0], tracer[1], (255, 0, 0))
		

		if not self.displayB:
			pipelineImg[:, :, 0] = 0
		if not self.displayG:
			pipelineImg[:, :, 1] = 0
		if not self.displayR:
			pipelineImg[:, :, 2] = 0



		#Draw valve states
		for valve in range(manifold.numTotalValves):
			color = (0, 0, 255) if manifold.getState(valve) else None
			util.drawHudText(pipelineImg, (valve*2.5, 0), str(valve), color)



		if self.displayElements:
			for elem in element.getAllElements(): #Draw all drawable elements
					elem.draw(pipelineImg)

		if self.displayOverlay:
			text0 = "OUT:{:5.1f} REC:{:5.1f} CAM:{:5.1f}FPS [{}] Blobs:{} Mask:{} User:{}".format(
				self.fpsCounter.calc(),
				self.fluidscript.videoRecorder.fpsCounter.calc(),
				self.fluidscript.camera.fpsCounter.calc(),
				("R" if self.displayR else"_") + ("G" if self.displayG else "_") + ("B" if self.displayB else "_"),
				"SHOW" if self.displayBlobs else "HIDE",
				"MASK" if self.displayMask else "NORM",
				"RUN" if self.fluidscript.onFrameRunState else "STOP"
			)

			text1 = "{} {}".format(
				datetime.now().isoformat()[0:22],
				"[REC]" if self.fluidscript.videoRecorder.isRecording else ''
			)
			
			text2 = 'H20:{}  OIL:{}'.format(
				self.fluidscript.epr1.setPointStr,
				self.fluidscript.epr2.setPointStr
			)

			util.drawHudText(pipelineImg, (0, 1), text0)
			util.drawHudText(pipelineImg, (0, 2), text1)
			util.drawHudText(pipelineImg, (0, 3), text2)




		if not self.fluidscript.statusText is None:
			util.drawHudText(pipelineImg, (0, 4), self.fluidscript.statusText)





		self.latestFrame = pipelineImg
		self.latestFrameReadyEvent.set()
		self.latestFrameReadyEventOnFrame.set() 	#Separate event for fluidscript onFrame



