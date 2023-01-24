import threading
import framecounter
import config
import cv2
import time
import util
import threadedclass
import interval

class Camera(threadedclass.ThreadedClass):
	def __init__(self, fluidscript, source, width, height):
		super().__init__()

		self.fluidscript = fluidscript

		self.threadedClassName = 'Camera'

		self.source = source
		self.sourceIsVideoFile = False
		self.sourceIsPictureFile = False

		if isinstance(source, int):
			print('Source is camera device.')

		elif source.endswith('.jpg') or source.endswith('.png'):
			print('Source is picture file.')
			self.sourceIsPictureFile = True

		elif isinstance(source, str):
			print('Source is video file.')
			self.sourceIsVideoFile = True

		else:
			print('Could not determine input type!')

		self.videoCapture = None

		self.height = height
		self.width = width

		self.fpsCounter = framecounter.FrameCounter()	#For camera input
		self.fpsDisplayCounter = framecounter.FrameCounter()	#For GUI video output

		self.open()

		if not self.sourceIsPictureFile:
			self.setProperties()	#Request stuff from the camera

		print(f'Specified {self.width}x{self.height}')

		f = self.getFrame()
		self.width = f.shape[1]
		self.height = f.shape[0]

		print(f'Received {self.width}x{self.height}')

		self.latestFrame = None
		self.latestFrameReadyEvent = threading.Event()

		self.frameInterval = interval.Interval(1/config.OUTPUT_FPS)


	def open(self):
		if self.sourceIsVideoFile:
			self.videoCapture = cv2.VideoCapture(self.source)
		elif self.sourceIsPictureFile:
			self.videoCapture = None
		else:
			self.videoCapture = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)

	def reOpen(self):
		print('Re-opening ' + str(self.source) + '...')

		if self.sourceIsVideoFile:
			self.videoCapture.open(self.source)
		elif self.sourceIsPictureFile:
			self.videoCapture = None	#picture...
		else:
			self.videoCapture.open(self.source, cv2.CAP_DSHOW)

		print('Re-opened ' + str(self.source) + '...')

	def setProperties(self):
		sucFourCC = self.videoCapture.set(cv2.CAP_PROP_FOURCC, config.FOURCC_CAM)
		sucWidth = self.videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
		sucHeight = self.videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
		sucFPS = self.videoCapture.set(cv2.CAP_PROP_FPS, config.TARGET_CAM_FPS)

		print(f'Set FourCC:\t{sucFourCC}')
		print(f'Set Width:\t{sucWidth}')
		print(f'Set Height:\t{sucHeight}')
		print(f'Set FPS:\t{sucFPS}')

	def getFrame(self):
		ret = None
		frame = None
		while not ret:
			if not self.sourceIsPictureFile:
				ret, frame = self.videoCapture.read()

				if not ret:
					if self.sourceIsVideoFile:
						self.reOpen()
					else:
						print('Camera is broken')
						time.sleep(1)

			else:
				frame = cv2.imread(self.source, cv2.IMREAD_COLOR)
				ret = True
		return frame

	def threadFunction(self):
		if self.frameInterval.advance():	#Limit getting new frames to what the set framerate should be
			self.latestFrame = self.getFrame()
			self.fpsCounter.count()
			self.latestFrameReadyEvent.set()

		time.sleep((1/config.OUTPUT_FPS) / 2)	#Limit freewheeling
	def threadExitFunction(self):
		if self.videoCapture:
			self.videoCapture.release()
			print('Camera closed.')
		else:
			print('Camera was not closed.')