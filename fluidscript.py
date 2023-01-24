import camera
import processor
import gui
import manifold
import sys
import threading
import threadedclass
import time
import signal
import cv2
import config
import traceback
import element
import epr
import videorecorder

class FluidScript:
	def __init__(self):
		print('MML FluidScript')
		print('CUDA Devices: ' + str(cv2.cuda.getCudaEnabledDeviceCount()))

		element.loadElements()



		#Launch separate threads:
		self.camera = camera.Camera(self, config.CAMERA_SOURCE, config.CAMERA_WIDTH, config.CAMERA_HEIGHT)
	
		self.processor = processor.Processor(self)
	
		self.gui = gui.GUI(self)

		self.videoRecorder = videorecorder.VideoRecorder(self)
		
		self.manifold1 = manifold.Manifold(config.MANIFOLD_1_PORT)	#1-12
		self.manifold2 = manifold.Manifold(config.MANIFOLD_2_PORT)	#13-24

		self.epr1 = epr.EPR('A', config.EPR_1_PORT)
		self.epr2 = epr.EPR('B', config.EPR_2_PORT)

		self.killFlag = False	#just a primative flag.
		self.onFrame = None	#User script function run on each frame
		self.init = None	#Init function run before each program start
		self.onFrameRunState = False


		self.statusText = None

		if not self.camera.start():	#Race condition unless we start them all at once quickly like this
			print('Error starting camera thread')
		if not self.processor.start():
			print('Error starting processor thread')
		if not self.gui.start():
			print('Error starting gui thread')

		self.oneShot = False
			

	def stop(self):	#User calls this to end the program
		print('==== Program will stop... ====')
		self.onFrameRunState = False

	def start(self):
		print('==== Program started! ====')
		self.onFrameRunState = True

	def kill(self):
		print('======== Quitting FluidScript... ========')
		self.killFlag = True

	def begin(self):	#Run in main thread
		firstRun = True
		while True:
			if not self.processor.latestFrameReadyEventOnFrame.wait(timeout=1):	#Wait for Processor to spit out a frame
				print('Processor isn\'t working')

			self.processor.latestFrameReadyEventOnFrame.clear()

			if self.onFrameRunState and not self.onFrame is None:
				try:
					if firstRun:
						self.init()	#Run the user's init function
						firstRun = False
					self.onFrame()
					
				except Exception as e:
					print('==== onFrame error ====')
					traceback.print_exc()
					print('Continuing...')
					time.sleep(2)

				if self.oneShot:
					print('==== onFrame one-shot finished. ====')
					self.onFrameRunState = False
					firstRun = True

			if self.killFlag:
				print('Stopping Camera...')
				self.camera.kill()

				#time.sleep(.5)

				print('Stopping GUI...')
				self.gui.kill()

				#time.sleep(.5)

				print('Stopping Processor...')
				self.processor.kill()

				#time.sleep(.5)

				print('Closing serial ports...')
				self.manifold1.destroy()
				self.manifold2.destroy()

				
				time.sleep(.5)	#Bug: This sleep is required, otherwise threads don't stop.

				print('Done.')


				break

				