import time


class FrameCounter:
	def __init__(self, limit = 100):	#Limit: Number of frames to average each time
		self.times = []
		self.limit = limit
		self.last = -1

	def count(self):
		now = time.time()
		self.times.append(now)
		if len(self.times) > self.limit:
			self.times = self.times[1:]	#Remove first element

	def calc(self):
		deltas = []
		for i in range(len(self.times)-1):
			deltas.append(self.times[i+1] - self.times[i])
			
		dSum = sum(deltas)
		self.last = (len(deltas)/dSum) if dSum > 0 else -1
		return self.last