import time
import serial
from serial.tools import list_ports
import traceback


#Valve control module

_baudrate = 115200
numValves = 12
numTotalValves = 0

_manifolds = []

def getManifoldValveOwner(valve):
	manifoldIndex = int(valve / numValves)
	return _manifolds[manifoldIndex]

def getState(valve):
	return getManifoldValveOwner(valve).getState(valve%12)

def toggle(valve):
	getManifoldValveOwner(valve).toggle(valve%12)

def on(valve):
	getManifoldValveOwner(valve).on(valve%12)

def off(valve):
	getManifoldValveOwner(valve).off(valve%12)

def demo():
	for i in range(numTotalValves):
		toggle(i)
		time.sleep(.2)

class Manifold:
	def __init__(self, comport):
		global _manifolds, numTotalValves

		self._comport = comport
		self._states = [False] * numValves	#Boolean array stores states of valves
		self._serial = None

		try:
			self._serial = serial.Serial(port = self._comport, baudrate = _baudrate)

			_manifolds += [self]

			numTotalValves += numValves

			print("Opened manifold on " + str(self._comport))
		except:
			traceback.print_exc()
			print(">>>>>>>> Couldn't initialize " + str(self._comport) + ". Does it exist?")



	def send(self, index, state):
		state = True if state else False

		if self._serial:
			command = "P" + str(index) + "S" + ("1" if state else "0") + "\n"
			#print(command)
			self._serial.write(bytes(command, "utf-8"))
		else:
			print(">>>>>>>> Couldn't set valve state " + str(index) + " for " + str(self._comport))
		self._states[index] = state

		time.sleep(.02)	#Bug. This seems to be necessary, but consecutive manifold calls fail. May be due to interference or serial implementation.

	def on(self, index):	#Turn on pin
		self.send(index, 1)

	def off(self, index):	#Turn off pin
		self.send(index, 0)

	def toggle(self, index):
		if self._states[index]:
			self.off(index)
		else:
			self.on(index)

	def demo(self):	#Just test all the pins
		for i in range(numValves):
			self.on(i)
			time.sleep(.2)

		for i in range(numValves):
			self.off(i)
			time.sleep(.2)

		for a in range(3):
			self.allOn()
			time.sleep(.2)
			self.allOff()
			time.sleep(.2)

	def allOn(self):	#Turn everything on
		for i in range(numValves):
			self.on(i)

	def allOff(self):	#Turn everything off
		for i in range(numValves):
			self.off(i)

	def getState(self, index):	#Fetch the state of an output for this specific manifold
		return self._states[index]

	def destroy(self):
		self._serial.close()
		print('Serial port closed.')




		