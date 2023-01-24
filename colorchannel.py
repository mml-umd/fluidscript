import trackbar
import cv2
import imutils
import math
import numpy as np
import blob
import util
import random
import blobgroup
import copy
import blobutil
import config
import time

class ColorChannel:
	def __init__(self, name):
		self.name = name

		self.trackbars = []


		#Create trackbars for color channel thresholding
		self.hueMinBar =	trackbar.Trackbar(179, 0, 	self.name + ' Hmin', list=self.trackbars)
		self.hueMaxBar =	trackbar.Trackbar(179, 30, 	self.name + ' Hmax', list=self.trackbars)

		self.satMinBar =	trackbar.Trackbar(63, 0, 	self.name + ' Smin', list=self.trackbars)
		self.satMaxBar =	trackbar.Trackbar(255, 10, 	self.name + ' Smax', list=self.trackbars)
		
		self.valMinBar =	trackbar.Trackbar(255, 100, self.name + ' Vmin', list=self.trackbars)
		self.valMaxBar =	trackbar.Trackbar(255, 255, self.name + ' Vmax', list=self.trackbars)

		self.eroBar =		trackbar.Trackbar(10, 3, 	self.name + ' Ero',  list=self.trackbars)
		self.dilBar =		trackbar.Trackbar(10, 3, 	self.name + ' Dil',  list=self.trackbars)

		self.minSizeBar =   trackbar.Trackbar(100, 0,   self.name + ' minA', list=self.trackbars)

		self.blobgroup = blobgroup.BlobGroup()

		self.tracers = []

	def getMask(self, hsvImage):
		hueMin = self.hueMinBar.getVal()
		hueMax = self.hueMaxBar.getVal()

		minSat = self.satMinBar.getVal()
		maxSat = self.satMaxBar.getVal()
		minVal = self.valMinBar.getVal()
		maxVal = self.valMaxBar.getVal()

		mask = None
		averageHue = None

		if hueMin < hueMax:	#If hue range is continous
			boundsMin = (hueMin, minSat, minVal)
			boundsMax = (hueMax, maxSat, maxVal)
			mask = cv2.inRange(hsvImage, boundsMin, boundsMax)
			averageHue = (hueMin + hueMax)/2

		else:
			lowerBoundsMin = (0,      minSat, minVal)
			lowerBoundsMax = (hueMax, maxSat, maxVal)

			upperBoundsMin = (hueMin, minSat, minVal)
			upperBoundsMax = (179,    maxSat, maxVal)
		
			lowerMask = cv2.inRange(hsvImage, lowerBoundsMin, lowerBoundsMax)
			upperMask = cv2.inRange(hsvImage, upperBoundsMin, upperBoundsMax)
			
			mask = cv2.bitwise_or(lowerMask, upperMask)	#Combine the two masks
			averageHue = ((hueMin + hueMax)/2 + 90)%180

		
		#Use erosion and dilation to remove small erroneous detections
		mask = cv2.erode(mask, None, iterations = self.eroBar.getVal())
		mask = cv2.dilate(mask, None, iterations = self.eroBar.getVal() + self.dilBar.getVal())	#Increase the edges to counter shadows
		
		contours = imutils.grab_contours(cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE))
		newBlobs = []

		for contour in contours:
			boxPoints = cv2.boxPoints(cv2.minAreaRect(contour))

			M = cv2.moments(contour)
			if(M["m00"] != 0):
					x = int(M["m10"] / M["m00"])  #Calculate center of the contour
					y = int(M["m01"] / M["m00"])
					contourCenter = (x, y)
			else:
					contourCenter = (0, 0)  #Catch divide by zero


			blobColor = util.colorHSV2BGR((averageHue, 255, 255))

			b = blob.Blob(contourCenter, blobColor)

			b.contour = contour

			b.boxPoints = boxPoints
			dx1 = boxPoints[0][0]-boxPoints[1][0]
			dy1 = boxPoints[0][1]-boxPoints[1][1]

			dx2 = boxPoints[0][0]-boxPoints[3][0]
			dy2 = boxPoints[0][1]-boxPoints[3][1]

			dist1 = math.sqrt(math.pow(dx1, 2) + math.pow(dy1, 2))
			dist2 = math.sqrt(math.pow(dx2, 2) + math.pow(dy2, 2))

			b.width = min(dist1, dist2)
			b.length = max(dist1, dist2)

			if b.length < self.minSizeBar.getVal():
				continue


			if len(newBlobs) < config.MAX_BLOBS:	#Prevent a huge lag spike if large area of grainy noise is detected as individual blobs
				newBlobs.append(b)


		self.tracers = []

		availableOldBlobs = copy.copy(self.blobgroup.blobs)

		for newBlob in blobgroup.BlobGroup(newBlobs).byRectArea().blobs:
			if availableOldBlobs:
				nearestDist = None
				nearestOldBlob = None

				for oldBlob in availableOldBlobs:
					thisDist = blobutil.dist(oldBlob.pos(), newBlob.pos())

					if nearestDist is None or thisDist < nearestDist:
						nearestDist = thisDist
						nearestOldBlob = oldBlob

				availableOldBlobs.remove(nearestOldBlob)

				nearestOldBlob.advanceTo(newBlob)

				for i in range(0, len(nearestOldBlob.trail) - 1):
					self.tracers.append((nearestOldBlob.trail[i][0], nearestOldBlob.trail[i+1][0]))

			else:
				self.blobgroup.blobs.append(newBlob)	#No old blobs left to forward from, add directly

		while availableOldBlobs:	#If there are no old blobs, check if there are new blobs
			self.blobgroup.blobs.remove(availableOldBlobs.pop(0))	#Remove only these old blobs from the group

		return mask




		