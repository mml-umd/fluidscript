import cv2
import numpy as np
import util
import blob
import blobutil
import config
import time

def nonNegativeSign(x):
	if x < 0:
		return -1

	return 1

class BlobGroup:	#Chainable-selection-of-blobs class.
	def __init__(self, blobs = None):
		self.blobs = blobs if not (blobs is None) else []	#This list must be a UNIQUE list. Bug found when trying to simply use a default parameter in __init__.
		pass

	def get(self, index):
		if len(self.blobs) <= index:
			return None
	
		return self.blobs[index]

	def drawBlobs(self, img):
		for b in self.blobs:
			b.draw(img)
			b.highlighted = max(0, b.highlighted-1)

	def byLength(self):
		blobs = sorted(self.blobs, key = lambda x: x.length, reverse=True) or []
		return BlobGroup(blobs)

	def byRectArea(self):	#NOT pixel area
		blobs = sorted(self.blobs, key = lambda x: x.length*x.width, reverse=True) or []
		return BlobGroup(blobs)

	def byProximity(self, elem):
		def prox(elem2):
			return blobutil.dist(elem2.pos(), elem.pos())

		blobs = sorted(self.blobs, key = prox)

		return BlobGroup(blobs)

	def byWithin(self, boundObj):
		blobs = []
		for b in self.blobs:
			if blobutil.withinObj(b, boundObj):
				blobs += [b]
			else:
				pass

		return BlobGroup(blobs)




	def waitForAnyWithin(self, objBound, timeout=config.BLOBUTIL_TIMEOUT, wait=config.BLOBUTIL_WAIT_PERIOD):
		if objBound is None:
			print('Cannot get bounding object: None')
			return None

		now = time.time()

		startTime = now

		while True:
			if now - startTime > timeout:
				print('Wait for within timed out')
				raise Exception()
				return None

			obj = self.byWithin(objBound).get(0)

			if not obj is None:
				print('Within detected')
				obj.highlight()
				return obj

			#print('Waiting for within...')
			time.sleep(wait)	#TODO: Use frame event here instead of busy waiting?

			now = time.time()

	def waitForNoneWithin(self, objBound, timeout=config.BLOBUTIL_TIMEOUT, wait=config.BLOBUTIL_WAIT_PERIOD):
		if objBound is None:
			print('Cannot get bounding object: None')
			raise Exception()
			return False

		now = time.time()

		startTime = now

		while True:
			if now - startTime > timeout:
				print(f'Wait for none-within timed out: ID {objBound.id}')
				raise Exception()
				return False

			if len(self.byWithin(objBound).blobs) == 0:
				print('None-within detected')
				return True

			#print('Waiting for none within...')
			time.sleep(wait)

			now = time.time()

	def waitForAnyApproach(self, objStatic, timeout=config.BLOBUTIL_TIMEOUT, wait=config.BLOBUTIL_WAIT_PERIOD):
		if objStatic is None:
			print('Cannot get static object: None')
			raise Exception()
			return None

		lastXDistance = None
		distance = None

		now = time.time()

		startTime = now

		while True:
			if now - startTime > timeout:
				print(f'Wait for approach timed out: ID {objStatic.id}')
				raise Exception()
				return None

			obj = self.byProximity(objStatic).get(0)

			if not obj is None:
				xDistance = blobutil.xDist(objStatic.pos(), obj.pos())
				distance = blobutil.dist(objStatic.pos(), obj.pos())	#To make sure the blob isn't just very far away

				if not lastXDistance:
					lastXDistance = xDistance

				if distance < config.BLOBUTIL_ANY_APPROACH_MAX_DIST and np.sign(xDistance) != np.sign(lastXDistance): 	#if the candidate has started to pass the measurement point
					print('Approach detected')
					obj.highlight()
					return obj

				else:
					lastXDistance = xDistance

			time.sleep(wait)

			now = time.time()

	def lazyOffsetApproach(self, objStatic, timeout=config.BLOBUTIL_TIMEOUT, wait=config.BLOBUTIL_WAIT_PERIOD, offset=5, absOffset=None):	#Wait for an approach at a specific offset to the point given. Useful for tuning capture in-situ
		if objStatic is None:
			print('Cannot get static object: None')
			raise Exception()
			return None

		lastXDistance = None
		distance = None

		now = time.time()

		startTime = now

		while True:
			if now - startTime > timeout:
				print(f'Wait for approach timed out: ID {objStatic}')
				raise Exception()
				return None

			obj = self.byProximity(objStatic).get(0)

			if not obj is None:
				rawXDistance = blobutil.xDist(objStatic.pos(), obj.pos())

				if absOffset is None:
					xDistance = rawXDistance - offset*np.sign(rawXDistance)	#Adjust where zero is. Note: np.sign returns 0 on 0.
				else:
					xDistance = rawXDistance - absOffset
					print(f'Warn: absolute offet active.')

				#print(f'raw {rawXDistance} comp {xDistance}')

				distance = blobutil.dist(objStatic.pos(), obj.pos())	#Use to make sure the blob isn't just very far away

				if not lastXDistance:
					lastXDistance = xDistance



				yWithinBounds = True	#TODO: change to allow vertical approaches?
				if blobutil.yAbsDist(objStatic.pos(), obj.pos()) > config.BLOBUTIL_ANY_APPROACH_MAX_Y_DEVIATION:
					yWithinBounds = False

				if yWithinBounds and distance < config.BLOBUTIL_ANY_APPROACH_MAX_DIST and np.sign(xDistance) != np.sign(lastXDistance): 	#if the candidate has started to pass the measurement point
					print('Approach detected')
					obj.highlight()
					return obj

				else:
					lastXDistance = xDistance

			time.sleep(wait)

			now = time.time()


			