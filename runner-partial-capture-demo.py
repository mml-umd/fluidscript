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
import sys
import trackbar



#Valve ports
vS1=0	#Sample1
vS2=1	#Sample2

vS=vS1

vH1=2	#H bridge controls
vH2=3


vT = [12, 13, 14, 15, 16, 17, 18, 19, 20]	#Traps

vP1=22	#Pressure valves
vP2=23

flu = fluidscript.FluidScript()

green = flu.gui.createColorChannel('Green')
red = flu.gui.createColorChannel('Red')

colorChannel = red




dataLogger = None	#This will be a new logger on each run

def hiPres():
	manifold.off(vP1)
	manifold.on(vP2)
	print('...High pressure')

def loPres():
	manifold.off(vP2)
	manifold.on(vP1)
	print('...Low pressure')

def fwd():
	manifold.off(vH1)
	manifold.on(vH2)
	print('...Forward')

def rev():
	manifold.off(vH2)
	manifold.on(vH1)
	print('...Reverse')




def eject(i):
	loPres()

	rect = element.getElementByID(element.Rect, i)

	time.sleep(.5)

	manifold.on(vT[i])

	while len(red.blobgroup.byWithin(rect).blobs) > 0:	#While there is some droplet still within the trap
		time.sleep(.1)	#Wait for the blob to completely exit the trap (lo-pressure eject is slow)

	hiPres()




def capture(i, channel):
	point = element.getElementByID(element.Point, i)

	hiPres()

	try:
		channel.blobgroup.lazyOffsetApproach(point, timeout=15, offset=15)	#offset in px.blobgroup.lazyOffsetApproach(point, timeout=15, offset=15)

	except:
		raise Exception('Failed waiting for approach')

	manifold.off(vT[i])


trapIndex = 0
trapOrder = [8, 7, 6, 5, 4, 3, 2, 1]


def myInit():	#We must reset the logger and the run number each time we restart the user script
	global dataLogger, trapIndex

	print('Initializing valves')

	for i in vT:
		manifold.off(i)

	hiPres()

	manifold.on(vS)
	manifold.on(vS)

	fwd()

	trapIndex = 0

	print('Done initializing')








def myLoop():
	global trapIndex

	print(f'Begin run.')

	flowTime = flu.gui.flowBar.getVal()/1000
	splitP = element.getElementByID(element.Point, 0)

	trapFirst = trapOrder[trapIndex]
	pFirst = element.getElementByID(element.Point, trapFirst)

	trapSecond = trapOrder[trapIndex+1]
	pSecond = element.getElementByID(element.Point, trapSecond)


	print(f'Flow time: {flowTime}')

	manifold.on(vT[0])
	manifold.on(vT[trapFirst])
	manifold.on(vT[trapSecond])

	hiPres()

	time.sleep(2)

	manifold.off(vS)
	time.sleep(flowTime)
	manifold.on(vS)

	time.sleep(1)

	

	colorChannel.blobgroup.lazyOffsetApproach(splitP, absOffset=flu.gui.offsetBar.getVal(), timeout=15)	#offset shall be downstream for partial capture.
	manifold.off(vT[0])	#Partially capture droplet




	print(f'Capturing {trapFirst}')
	colorChannel.blobgroup.lazyOffsetApproach(pFirst, offset=15, timeout=30)
	manifold.off(vT[trapFirst])


	loPres()
	time.sleep(1)

	manifold.on(vT[0])
	time.sleep(.8)
	hiPres()	#Gentle eject

	print(f'Capturing {trapSecond}')
	colorChannel.blobgroup.lazyOffsetApproach(pSecond, offset=15, timeout=30)
	manifold.off(vT[trapSecond])

	
	trapIndex += 2 	#Advance


	if trapIndex >= len(trapOrder):
		manifold.off(vT[0])

		print(f'Captured all droplets.')


		time.sleep(5)


		loPres()

		time.sleep(1)

		for i in [8, 7, 6, 5, 4, 3, 2, 1]:
			manifold.on(vT[i])
			time.sleep(.8)
			hiPres()
			time.sleep(1)
			manifold.off(vT[i])
			loPres()
			time.sleep(4)




		flu.stop()
		return

	time.sleep(2)


flu.init = myInit	#Run every time we restart the program
flu.onFrame = myLoop

flu.begin()