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





def myInit():	#We must reset the logger and the run number each time we restart the user script
	global dataLogger

	print('Initializing valves')

	loPres()

	time.sleep(1)

	for i in vT:
		manifold.on(i)

	time.sleep(1)

	hiPres()

	manifold.on(vS1)
	manifold.on(vS2)

	fwd()

	print('Done initializing')



def myLoop():
	print('======== Begin program!')

	for trapIndex in range(0, 9):
		channelRectIndex = int(trapIndex/3)
		trapValve = vT[trapIndex]

		d = flu.gui.flowBar.getVal() / 1000

		print(f'======== Destination trap: {trapIndex} d={d}s')

		

		for sampleIndex in [0, 1]:	#For valve and color chanel
			sampleValve = [vS1, vS2][sampleIndex]
			colorChannel = [red, green][sampleIndex]
			

			channelR = element.getElementByID(element.Rect, channelRectIndex)	#ID = 0, 1, or 2. Rects over the channels to test if a dropet has arrived.

			print(f'Sample: "{colorChannel.name}"')

		
			red.blobgroup.waitForNoneWithin(channelR)	#Wait for everything to clear
			green.blobgroup.waitForNoneWithin(channelR)	#green, too.
		

			manifold.off(sampleValve)
			time.sleep(d)
			manifold.on(sampleValve)

			

			candidate = colorChannel.blobgroup.waitForAnyWithin(channelR, timeout=20)

			if candidate is None:
				print(f'Failed to generate a droplet for {red.name}')
				time.sleep(10)
				return

			#print(f'Found blob in rect ID {channelR.id}')

			trapCenterP = element.getElementByID(element.Point, trapIndex+1)

			if sampleIndex == 0:	#Red droplet
				colorChannel.blobgroup.lazyOffsetApproach(trapCenterP, timeout=7, offset=10)
				manifold.off(trapValve)

				time.sleep(1)

				loPres()	#Set this here for the NEXT run. This run is high pressure.

			else:	#Green droplet
				colorChannel.blobgroup.lazyOffsetApproach(trapCenterP, timeout=7, offset=20)
				manifold.on(trapValve)	#EJECT the red droplet
				time.sleep(.1)
				manifold.off(trapValve)	#Keep it in the trap

				time.sleep(1)

				hiPres()	#Set this here for the NEXT run. This run is low pressure.

	flu.stop()


flu.init = myInit	#Run every time we restart the program
flu.onFrame = myLoop

flu.begin()