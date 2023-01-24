import cv2
import numpy
import imutils
import time
import config
import blobutil
import threading
from multiprocessing import Process
import numpy as np
import math
import traceback
import jsonutil
import util


_points = []	#...
_rects = []






def getPoints():
	return _points

def getRects():
	return _rects




def getAllElements():	#Return all Elements
	return _points + _rects



def getElementByID(elemClass, id):	#Get a specific element by calass and id
	for elem in elemClass._list:
		if elem.id == id:
			return elem

	return None



def writeElements():
	json = {}
	json["list"] = []
	for elem in getAllElements():
		params = {
			"xPos": int(elem.pos()[0]),	#Numbers from numpy, etc. are not "int" type. Convert for safety
			"yPos": int(elem.pos()[1]),
			"xPos2": int(elem.pos2()[0]),
			"yPos2": int(elem.pos2()[1]),
			"class": elem.__class__.__name__,
			"id": int(elem.id)
		}

		json["list"].append(params)
	jsonutil.writeJSON(json, config.FILE_ELEMENT)

def loadElements():
	print("Loading elements...")
	json = jsonutil.readJSON(config.FILE_ELEMENT)

	if json.get("list") == None:	#If the JSON file is empty
		json["list"] = []

	for elem in json["list"]:
		pos = (elem["xPos"], elem["yPos"])
		pos2 = (elem["xPos2"], elem["yPos2"])

		if elem['class'] == 'Point':
			e = Point(pos, elem['id'])
			print(f'Loaded Point {e.id}')

		elif elem['class'] == 'Rect':
			e = Rect(pos, pos2, elem['id'])
			print(f'Loaded Rect {e.id}')

		else:
			print(f"Failed to load element with class {element['class']}")


class Element:	#Base class for a screen Element
	def __init__(self, id=0):	#Generic constructor called by child classes
		self._pos = (0, 0)
		self._pos2 = (0, 0)

		self.lastChangedTime = time.time()

		self.hover = False

		self.__class__._list.append(self)

		self.id = id

	def nextID(self):
		self.id += 1
		writeElements()

	def previousID(self):
		self.id -= 1
		writeElements()

	def pos(self):
		return self._pos

	def pos2(self):
		return self._pos2

	def intPos(self):
		return (int(self.pos()[0]), int(self.pos()[1]))

	def move(self, offset):
		self._pos = (self.pos()[0] + offset[0], self.pos()[1] + offset[1])
		writeElements()

	def moveTo(self, pos):
		self._pos = pos
		writeElements()

	def move2To(self, pos2):
		self._pos2 = pos2
		writeElements()

	def destroy(self):
		self.__class__._list.remove(self)
		writeElements()

class Point(Element):
	_list = _points
	def __init__(self, pos, id=0):
		super().__init__(id)

		self._pos = pos
		self.color = config.COLOR_INACTIVE

	def draw(self, img):
		if(self.hover):
			color = config.COLOR_HOVER
		else:
			color = self.color

		util.drawHudText(
			img,
			(
				self.intPos()[0] + 5,
				self.intPos()[1] + 35
			),
			'P' + str(self.id),
			(255, 255, 255),
			pixelPos = True
		)

		#Points that make up the cross marker
		l11 = (self.intPos()[0] - 20, self.intPos()[1])
		l12 = (self.intPos()[0] + 20, self.intPos()[1])
		l21 = (self.intPos()[0], self.intPos()[1] - 20)
		l22 = (self.intPos()[0], self.intPos()[1] + 20)

		cv2.line(
			img,
			l11,
			l12,
			color,
			thickness=1)

		cv2.line(
			img,
			l21,
			l22,
			color,
			thickness=1)




class Rect(Element):
	_list = _rects
	def __init__(self, pos, pos2, id=0):

		super().__init__(id)

		self._pos = pos
		self._pos2 = pos2
		self.color = config.COLOR_INACTIVE
		self._lastState = False
		self.state = False

	def draw(self, img):
		if(self.hover):
			color = config.COLOR_HOVER
		else:
			color = self.color

		util.drawHudText(
			img,
			(
				self.intPos()[0],
				self.intPos()[1]
			),
			'R' + str(self.id),
			(255, 255, 255),
			pixelPos = True
		)

		cv2.rectangle(img, self.intPos(), (int(self._pos2[0]), int(self._pos2[1])), color, config.LINE_THICKNESS)

	def move(self, offset):
		self._pos = (self.pos()[0] + offset[0], self.pos()[1] + offset[1])
		self._pos2 = (self.pos2()[0] + offset[0], self.pos2()[1] + offset[1])
		writeElements()



		