import time
import serial
from serial.tools import list_ports
import traceback
import interval
import jsonutil
import config


#Control module for EPR pressure regulators. Requires USB to serial adapter.


class EPR:
	def __init__(self, id, comport):
		self.id = id
		self.setPoint = 0
		self.setPointStr = '0.00PSI'
		self.interval = interval.Interval(.05)
		self.baudrate = 19200
		self.increment = .02
		self.maxPSI = 8

		try:
			json = jsonutil.readJSON(config.FILE_EPR)
			track = json[self.id]
			s = track["setpoint"]
			self.setPoint = s
			self.updateSetPointStr()
		except Exception as e:
			print("Resetting EPR " + self.id)
			self.writeOut()




		try:
			self.ser = serial.Serial(port = comport, baudrate = self.baudrate, write_timeout=.5)

			print("Opened EPR on " + str(comport))
		except:
			#traceback.print_exc()
			print(">>>>>>>> Couldn't initialize " + str(comport) + ". Does it exist?")

	def writeOut(self):
		json = jsonutil.readJSON(config.FILE_EPR)
		json[self.id] = {
			"setpoint": self.setPoint
		}
		jsonutil.writeJSON(json, config.FILE_EPR)

	def updateSetPointStr(self):
		self.setPointStr = '{:2.2f}PSI'.format(self.setPoint)

	def _inc(self, x):
		if not self.interval.check():
			return

		self.setPoint += x
		self.setPoint = min(max(round(self.setPoint, 2), 0), self.maxPSI)

		self.updateSetPointStr()
		self.send()
		self.writeOut()

	def inc(self):
		self._inc(self.increment)

	def dec(self):
		self._inc(-self.increment)

	def send(self):
		msg = f'{self.id}S{self.setPoint}\r'
		self.ser.write(bytes(msg, 'ASCII'))


		