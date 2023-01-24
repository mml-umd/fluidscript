import cv2
import numpy as np
import util
import math
import time
import config
import blobutil

class Blob: #Wrapper for a blob
	def __init__(self, pos, color, angle = None):
		self._pos = (int(pos[0]), int(pos[1]))
		self.width = 0
		self.length = 0
		self.highlighted = 0
		self.color = color
		self.boxPoints = None
		self.contour = None

		self.angle = angle

		self.trail = [(pos, time.time())]	#Trails starts with one entry
		self.velocity = 0

		
	def advanceTo(self, newBlob):	#Forwards the blob properties from the blob of the previous frame. Not a cloning function. Also does velocity queue shift.
		now = time.time()
		self.trail.append((newBlob._pos, now))

		if len(self.trail) > config.BLOB_VELOCITY_AVERAGE_SIZE:
			self.trail.pop(0)	#Remove oldest position

		dx = blobutil.dist(self.trail[0][0], self.trail[-1][0])
		dt = self.trail[-1][1] - self.trail[0][1]

		self.velocity = dx/dt


		self._pos = newBlob._pos	#Clone the rest of the properties
		self.width = newBlob.width
		self.length = newBlob.length
		#self.highlighted = newBlob.highlighted 	#Do NOT copy highlighted property from new blob
		self.color = newBlob.color
		self.boxPoints = newBlob.boxPoints
		self.contour = newBlob.contour





	def pos(self):
		return self._pos

	def highlight(self, frames = 15):
		self.highlighted = frames

	def draw(self, img):
		thickness = 5 if self.highlighted > 0 else 1

		cv2.circle(img, self.pos(), 2, self.color, -1)	#point

		cv2.drawContours(img, [np.int0(self.boxPoints)], 0, self.color, thickness)



		