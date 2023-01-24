import camera
import element
import util
import manifold
import time
import cv2
import traceback
import random
import numpy as np
import logger
import fluidscript
import threading
import time
import framecounter
import interval
import manifold
import blobutil



#Valve ports
vS1=0	#Sample
vS2=1

#vS = vS1	#Red
vS = vS1	#Green

vT = [12, 13, 14, 15, 16, 17, 18, 19, 20]

vTSplit = vT[1]	#Trap to use for splitting

flu = fluidscript.FluidScript()

green = flu.gui.createColorChannel('Green')
red = flu.gui.createColorChannel('Red')

colorChannel = red


dataLogger = None	#This will be a new logger on each run
runNumber = 0

minOffset = -80
maxOffset = 80

#minFlow = .05
minFlow = .2
maxFlow = .8

def cleanRoutine(): 	#Tries to get stuff out of the channel
	manifold.on(vTSplit)

	manifold.off(vS)
	time.sleep(.6)
	manifold.on(vS)
	time.sleep(3)

	manifold.off(vS)
	time.sleep(.6)
	manifold.on(vS)
	time.sleep(6)

	for i in range(0, 20, 1):
		manifold.off(vTSplit)
		time.sleep(.1)
		manifold.on(vTSplit)
		time.sleep(.1)

	time.sleep(1)

	


def myInit():	#We must reset the logger and the run number each time we restart the user script
	global dataLogger, runNumber

	dataLogger = logger.Logger([
		'runNumber',
		'timestamp',
		'flowTime',
		'splitPositionOffset',

		'velocityInitial',
		'lengthInitial',
		'widthInitial',

		'velocityFirst',
		'lengthFirst',
		'widthFirst',

		'velocitySecond',
		'lengthSecond',
		'widthSecond'
	])

	runNumber = 0

def myLoop():
	global runNumber

	print(f'======== # {runNumber}')

	flu.statusText = f'Run no. {runNumber}'



	######## Pre-section: get all the required rects and points
	preMeasureP = element.getElementByID(element.Point, 1)
	channelCenterP = element.getElementByID(element.Point, 2)
	postMeasureP = element.getElementByID(element.Point, 3)

	splitP = element.getElementByID(element.Point, 9)

	validR = element.getElementByID(element.Rect, 0)




	#Create and move the split point if it does not already exist
	if splitP is None:
		splitP = element.Point((0, 0), 9)

	splitPositionOffset = random.random()*(maxOffset-minOffset) + minOffset
	thisSplitPos = (channelCenterP.pos()[0] + splitPositionOffset, channelCenterP.pos()[1])
	splitP.moveTo(thisSplitPos)


	print(f'Offset {splitPositionOffset}px')






	##### end setup

	##### begin experiment run



	manifold.off(vTSplit)

	time.sleep(3)

	#Cleaning check
	try:
		colorChannel.blobgroup.waitForNoneWithin(validR, timeout=1)	#If there are any blobs left

	except:
		cleanRoutine()	#If there are blobs stuck somewhere
		return


	#Select a wait time, and actuate the valve
	flowTime = random.random()*(maxFlow - minFlow) + minFlow
	manifold.off(vS)
	time.sleep(flowTime)
	manifold.on(vS)

	print(f'Flow time: {flowTime}')

	time.sleep(.5)



	######## Section 1: Wait for a blob to approach the pre-trap measurement point

	plug = colorChannel.blobgroup.waitForAnyApproach(preMeasureP, timeout=20)
	velocityInitial = plug.velocity
	lengthInitial = plug.length
	widthInitial = plug.width

	print(f'Plug length: {lengthInitial}')




	######## Section 2: Wait for the blob to approach the split point, and split it

	plugBeforeSplit = colorChannel.blobgroup.waitForAnyApproach(splitP, timeout=5)
	actualSplitPositionOffset = blobutil.xDist(channelCenterP.pos(), plugBeforeSplit.pos())	#Take the actual position
	splitPositionOvershoot = blobutil.xDist(channelCenterP.pos(), plugBeforeSplit.pos())	#Log the overshoot just for fun

	manifold.on(vTSplit)	#Split the droplet

	time.sleep(.1)


	######## Section 3: Wait for the first satellite to approach the post-trap measurement point
	try:
		first = colorChannel.blobgroup.waitForAnyApproach(postMeasureP, timeout=5)

		velocityFirst = first.velocity
		lengthFirst = first.length
		widthFirst = first.width

	except:
		velocityFirst = 0
		lengthFirst = 0
		widthFirst = 0

	print(f'Sat1 length: {lengthFirst}')

	time.sleep(.1)	#May double-detect the first satellite here?


	######## Section 4: Wait for the second satellite to approach the post-trap measurement point
	try:
		#second = blobutil.waitForAnyApproach(colorChannel.byWithin(validR), postMeasureP, timeout=5)	#Even though we know which blob this is (nearest to channelP), it might get messy during eject and be killed. Use anyApproach for safety.
		second = colorChannel.blobgroup.waitForAnyApproach(postMeasureP, timeout=4)

		velocitySecond = second.velocity
		lengthSecond = second.length
		widthSecond = second.width

	except:
		velocitySecond = 0
		lengthSecond = 0
		widthSecond = 0

	print(f'Sat2 length: {lengthSecond}')




	######## End section: Log the data



	dataLogger.log({	#Build the log file entry
		'runNumber':runNumber,
		'timestamp':time.time(),
		'flowTime':flowTime,
		
		'splitPositionOffset':actualSplitPositionOffset,

		'velocityInitial':velocityInitial,
		'lengthInitial':lengthInitial,
		'widthInitial':widthInitial,

		'velocityFirst':velocityFirst,
		'lengthFirst':lengthFirst,
		'widthFirst':widthFirst,

		'velocitySecond':velocitySecond,
		'lengthSecond':lengthSecond,
		'widthSecond':widthSecond
	})


	print(f'Completed run {runNumber}')

		
	runNumber += 1
	
	

flu.init = myInit
flu.onFrame = myLoop

flu.begin()


