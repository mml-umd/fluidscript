import time

class Interval:	#Simple timer class
	def __init__(self, dur):
		self.dur = dur
		self.lastTime = time.time()

	def reset(self):
		now = time.time()
		self.lastTime = now

	def check(self):
		now = time.time()
		if now-self.lastTime >= self.dur:
			self.lastTime = now
			return True
		return False

	def advance(self):	#Advance() is useful for video writing because it keeps perfect time over a long time.
				#Just using check() will drift, but will also act nicely if the interval is suddenly checked after a long pause.
				#Advance() will not drift, but will fire continuously to catch up if it is checked after a long pause.
		now = time.time()
		if now-self.lastTime >= self.dur:
			self.lastTime += self.dur	#Advance exactly
			return True
		return False

	def getLag(self):	#Check how far behind schedule the interval currently is
		return time.time() - self.lastTime