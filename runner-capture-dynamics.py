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

vS = vS1	#Red
#vS = vS2	#Green

vH1=2	#H bridge controls
vH2=3
vP1=22	#Pressure valves
vP2=23

vT = [12, 13, 14, 15, 16, 17, 18, 19, 20]

vTSplit = vT[1]	#Trap to use for splitting

flu = fluidscript.FluidScript()

green = flu.gui.createColorChannel('Green')
red = flu.gui.createColorChannel('Red')

colorChannel = red


dataLogger = None	#This will be a new logger on each run
runNumber = 0




minOffset = -100
maxOffset = 40

#minFlow = .05
minFlow = .2
maxFlow = .8

def hiPres():
	manifold.off(vP1)
	manifold.on(vP2)
	print('...High pressure')

def loPres():
	manifold.off(vP2)
	manifold.on(vP1)
	print('...Low pressure')

def cleanRoutine(): 	#Attempt to get stuff out of the channel
	hiPres()

	manifold.on(vTSplit)

	manifold.off(vS)
	time.sleep(.6)
	manifold.on(vS)
	time.sleep(3)

	manifold.off(vS)
	time.sleep(.6)
	manifold.on(vS)
	time.sleep(7)

	for i in range(0, 20, 1):
		manifold.off(vTSplit)
		time.sleep(.1)
		manifold.on(vTSplit)
		time.sleep(.1)

	time.sleep(20)

	


def myInit():	#We must reset the logger and the run number each time we restart the user script
	global dataLogger, runNumber

	dataLogger = logger.Logger([	#Provide the logger with the headings of the CSV file
		'runNumber',
		'timestamp',
		'flowTime',
		'capturePositionOffset',

		'velocityInitial',
		'lengthInitial',
		'widthInitial',

		'velocitySatellite',
		'lengthSatellite',
		'widthSatellite',

		'velocityCapture',
		'lengthCapture',
		'widthCapture'
	])

	runNumber = 0

def myLoop():
	global runNumber

	print(f'======== # {runNumber}')

	flu.statusText = f'Run no. {runNumber}'	#Set some on-screen status text for reference



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



	######## Section 1: Wait for a blob to approach the pre-trap measurement point

	plug = colorChannel.blobgroup.waitForAnyApproach(preMeasureP, timeout=15)
	velocityInitial = plug.velocity
	lengthInitial = plug.length
	widthInitial = plug.width

	print(f'Plug length: {lengthInitial}')




	######## Section 2: Wait for the blob to approach the split point, and split it

	plugBeforeSplit = colorChannel.blobgroup.waitForAnyApproach(splitP, timeout=6)
	actualCapturePositionOffset = blobutil.xDist(channelCenterP.pos(), plugBeforeSplit.pos())	#Take the actual position
	#splitPositionOvershoot = blobutil.xDist(channelCenterP.pos(), plugBeforeSplit.pos())	#Log the overshoot just for fun

	manifold.off(vTSplit)	#Split the droplet

	time.sleep(.1)


	######## Section 3: Wait for the first satellite to approach the post-trap measurement point
	try:
		satellite = colorChannel.blobgroup.waitForAnyApproach(postMeasureP, timeout=15)	#Large droplets just barely haning out of the trap may take some extra time to fall out. Best wait.

		velocitySatellite = satellite.velocity
		lengthSatellite = satellite.length
		widthSatellite = satellite.width

	except:
		velocitySatellite = 0
		lengthSatellite = 0
		widthSatellite = 0

	print(f'Sat1 length: {lengthSatellite}')

	time.sleep(2)


	loPres()
	time.sleep(1)
	manifold.on(vTSplit)
	time.sleep(.8)
	hiPres()


	######## Section 4: Wait for the second satellite to approach the post-trap measurement point
	try:
		colorChannel.blobgroup.waitForAnyWithin(validR, timeout=1)	#Throw error (no satellite) if there is nothing in the rect

		capture = colorChannel.blobgroup.waitForAnyApproach(postMeasureP, timeout=10)

		velocityCapture = capture.velocity
		lengthCapture = capture.length
		widthCapture = capture.width

	except:
		velocityCapture = 0
		lengthCapture = 0
		widthCapture = 0

	print(f'Sat2 length: {lengthCapture}')




	######## End section: Log the data



	dataLogger.log({	#Build the log file entry
		'runNumber':runNumber,
		'timestamp':time.time(),
		'flowTime':flowTime,
		
		'capturePositionOffset':actualCapturePositionOffset,

		'velocityInitial':velocityInitial,
		'lengthInitial':lengthInitial,
		'widthInitial':widthInitial,

		'velocitySatellite':velocitySatellite,
		'lengthSatellite':lengthSatellite,
		'widthSatellite':widthSatellite,

		'velocityCapture':velocityCapture,
		'lengthCapture':lengthCapture,
		'widthCapture':widthCapture
	})


	print(f'Completed run {runNumber}')

	time.sleep(6)

		
	runNumber += 1
	
	

flu.init = myInit
flu.onFrame = myLoop

flu.begin()



