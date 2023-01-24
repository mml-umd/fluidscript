import cv2
import jsonutil
import config

class Trackbar: #Element that represents a trackbar in the controls window
	def __init__(self, max, val, name, list=None):
		self.max = max
		self.val = val
		self.lastVal = val	#Used to see if writing to file is necessary when checked
		self.name = name

		try:
			json = jsonutil.readJSON(config.FILE_TRACKBAR)
			track = json[self.name]
			v = track["value"]
			self.val = v
		except Exception as e:
			print("Resetting trackbar " + self.name)
			self.writeOut()

		if not list is None:
			list.append(self)

	def on(self, val):	#Called by OpenCV when the value changes
		self.val = val

		self.writeOut()

	def getVal(self):
		return self.val

	def addTo(self, winName):
		cv2.createTrackbar(self.name, winName, self.val, self.max, self.on)

	def writeOut(self):
		json = jsonutil.readJSON(config.FILE_TRACKBAR)
		json[self.name] = {
			"value": self.val
		}
		jsonutil.writeJSON(json, config.FILE_TRACKBAR)
