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
vRed=1	#Sample1
vGreen=0	#Sample2

vH1=2	#H bridge controls
vH2=3
vP1=22	#Pressure valves
vP2=23

vT = [12, 13, 14, 15, 16, 17, 18, 19, 20]	#Traps



flu = fluidscript.FluidScript()

green = flu.gui.createColorChannel('Green')
red = flu.gui.createColorChannel('Red')
brown = flu.gui.createColorChannel('Brown')




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

def bothOn():
	manifold.on(vH1)
	manifold.on(vH2)
	print('...Flow stopped')



def myInit():	#We must reset the logger and the run number each time we restart the user script
	global dataLogger

	print('Initializing valves')

	loPres()

	time.sleep(1)

	for i in vT:
		manifold.on(i)

	time.sleep(1)

	hiPres()

	manifold.on(vRed)
	manifold.on(vGreen)

	fwd()

	print('Done initializing')



def myLoop():
	print('======== Begin program!')

	for trapIndex in [8, 7, 6, 5, 4, 3, 2, 1, 0]:
		channelRectIndex = int(trapIndex/3)
		trapValve = vT[trapIndex]

		d = flu.gui.flowBar.getVal() / 1000

		print(f'======== Destination trap: {trapIndex} d={d}s')

		

		for sampleIndex in [0, 1]:	#For valve and color chanel
			sampleValve = [vRed, vRed][sampleIndex]
			colorChannel = [red, red][sampleIndex]

			channelR = element.getElementByID(element.Rect, channelRectIndex)	#ID = 0, 1, or 2. Rects over the channels to test if a dropet has arrived.

			print(f'Sample: "{colorChannel.name}"')

		
			red.blobgroup.waitForNoneWithin(channelR)	#Wait for everything to clear
			green.blobgroup.waitForNoneWithin(channelR)	#green, too.
		

			manifold.off(sampleValve)
			time.sleep(d)
			manifold.on(sampleValve)

			

			candidate = colorChannel.blobgroup.waitForAnyWithin(channelR, timeout=30)

			if candidate is None:
				print(f'Failed to generate a droplet for {colorChannel.name}')
				time.sleep(10)
				return

			trapCenterP = element.getElementByID(element.Point, trapIndex)

			if sampleIndex == 0:
				colorChannel.blobgroup.lazyOffsetApproach(trapCenterP, timeout=20, offset=15)
				manifold.off(trapValve)

				time.sleep(1)

				loPres()	#Set this here for the NEXT run. This run is high pressure.

			else:
				colorChannel.blobgroup.lazyOffsetApproach(trapCenterP, timeout=20, offset=15)
				manifold.on(trapValve)	#partially eject
				time.sleep(.1)
				manifold.off(trapValve)	#Keep it in the trap

				time.sleep(1)

				hiPres()	#Set this here for the NEXT run. This run is low pressure.

			time.sleep(1)
	flu.stop()


flu.init = myInit	#Run every time we restart the program
flu.onFrame = myLoop

flu.begin()


