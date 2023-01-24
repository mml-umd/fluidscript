import cProfile, pstats, io
from pstats import SortKey
import threading

class ThreadedClass:	#Will be subclassed by camera, gui, and processor 
			#(any class that will have a function in it meant to be run in a separate thread)
			#kill(), threadExitFunction(), threadInitFunction(), threadFunction() can be overloaded to add functionality

	def __init__(self):
		self._killFlag = False
		self.threadedClassName = 'n/a'
		self.doProfile = False
		self.thread = None

	def threadLoop(self):
		if self.doProfile:
			pr = cProfile.Profile()
			pr.enable()

		

		self.threadInitFunction()	#Do the initial stuff


		while True:
			self.threadFunction()	#Do the looping stuff
			if self._killFlag:
				self.threadExitFunction()	#Do stuff at the end
				break

		print('ThreadedClass stopped: ' + self.threadedClassName)

		if self.doProfile:
			pr.disable()

			print('Profile for thread ' + self.threadedClassName)

			s = io.StringIO()
			sortby = SortKey.CUMULATIVE
			ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
			ps.print_stats()
			print(s.getvalue())

	def start(self):
		self._killFlag = False
		
		if self.thread == None or not self.thread.is_alive():
			self.thread = threading.Thread(target=self.threadLoop)
			self.thread.daemon = True
			self.thread.start()
			return True

		else:
			return False

	def kill(self):	#If this function is subclassed, keep in mind that when called from a different thread,
					#that code will be running in a different thread, not this thread.
					#Use threadExitFunction() to keep exit code in the same thread.
		self._killFlag = True

	def threadInitFunction(self):	#To be subclassed
		pass

	def threadFunction(self):	#To be subclassed
		pass

	def threadExitFunction(self):	#To be subclassed
		pass



		