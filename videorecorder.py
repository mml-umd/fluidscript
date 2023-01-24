import threadedclass
import interval
import numpy as np 
import cv2
import util
import config
import time
import framecounter

class VideoRecorder(threadedclass.ThreadedClass):

	def __init__(self, fluidscript):
		super().__init__()

		self.threadedClassName = 'VideoRecorder'

		self.fluidscript = fluidscript
		self.isRecording = False

		self.videoWriter = None
		self.rawVideoWriter = None

		self.frameInterval = interval.Interval(1/config.OUTPUT_FPS)

		self.fpsCounter = framecounter.FrameCounter()
		
		
	def threadInitFunction(self):
		if self.isRecording:
			return

		shapeTestFrame = self.fluidscript.processor.latestFrame
		rawShapeTestFrame = self.fluidscript.camera.latestFrame

		if (not shapeTestFrame is None) and (not rawShapeTestFrame is None):
			shape = (shapeTestFrame.shape[1], shapeTestFrame.shape[0])
			rawShape = (rawShapeTestFrame.shape[1], rawShapeTestFrame.shape[0])
			
			filename = util.getDatedFile("{}_video" + config.OUTPUT_EXTENSION)
			rawFilename = util.getDatedFile("{}_videoraw" + config.OUTPUT_EXTENSION)

			self.videoWriter = cv2.VideoWriter(filename, config.FOURCC_OUTPUT, config.OUTPUT_FPS, shape)
			self.rawVideoWriter = cv2.VideoWriter(rawFilename, config.FOURCC_OUTPUT, config.OUTPUT_FPS, rawShape)
			self.isRecording = True

			self.frameInterval.reset()

			

			print("Started recording: " + filename)

		else:
			print('Couldn\'t start recording')



	def threadFunction(self):
		if self.frameInterval.advance():	#Write at exactly 60fps or whatever set to
			self.videoWriter.write(self.fluidscript.processor.latestFrame)
			self.rawVideoWriter.write(self.fluidscript.camera.latestFrame)
			self.fpsCounter.count()

		time.sleep((1/config.OUTPUT_FPS) / 2)	#Since this thread freewheels, check at least twice per frame

	def threadExitFunction(self):
		self.isRecording = False		
		self.videoWriter.release()
		self.rawVideoWriter.release()


