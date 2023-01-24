import util
from datetime import datetime

class Logger:	#Class for appending text to a file (csv, etc)
	def __init__(self, names):
		self.filename = util.getDatedFile("{}_data.csv")
		self.names = names
		#self.writeString(','.join(self.names + [datetime.now().isoformat()[0:19].replace(":", "-")]))
		
		self.writeString(','.join(self.names))


		print(f'==== Logger initialized: {self.filename} ====')

	def writeString(self, s):
		f = open(self.filename, 'a')
		f.write(s + '\n')
		f.close()

	def log(self, inDict):
		outStr = ''
		for name in self.names:
			if name in inDict:
				outStr += str(inDict[name]).replace(',', '","').replace('"', '""')
			else:
				outStr += 'n/a'

			outStr += ','

		self.writeString(outStr)
		