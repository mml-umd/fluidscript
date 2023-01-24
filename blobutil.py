import numpy as np
import math
import cv2
import element
import time
import blob
import config

def dist(a, b):
	if(not a or not b):
		return None

	return math.sqrt(abs(a[0] - b[0]) ** 2 + abs(a[1] - b[1]) ** 2)

def xDist(a, b):
	if(not a or not b):
		return None
	return b[0] - a[0]

def yDist(a, b):
	if(not a or not b):
		return None
	return b[1] - a[1]

def xAbsDist(a, b):
	return abs(xDist(a, b))

def yAbsDist(a, b):
	return abs(yDist(a, b))

def withinObj(tObj, boundObj):
	if isinstance(boundObj, element.Rect):
		return tObj.pos()[0] > boundObj.pos()[0] and tObj.pos()[1] > boundObj.pos()[1] and tObj.pos()[0] < boundObj._pos2[0] and tObj.pos()[1] < boundObj._pos2[1]
	else:
		return dist(tObj.pos(), boundObj.pos()) <= boundObj.radius - tObj.radius
