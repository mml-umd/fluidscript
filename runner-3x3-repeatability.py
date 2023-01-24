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
vS1=0	#Sample1
vS2=1	#Sample2

vH1=2	#H bridge controls
vH2=3


vT = [12, 13, 14, 15, 16, 17, 18, 19, 20]

flu = fluidscript.FluidScript()

red = flu.gui.createColorChannel('Red')

captures = 9*5


def hiPres():
	manifold.off(22)
	manifold.on(23)
	print('High pressure')

def loPres():
	manifold.off(23)
	manifold.on(22)
	print('Low pressure')

def fwd():
	manifold.off(2)
	manifold.on(3)
	print('Forward')

def rev():
	manifold.off(3)
	manifold.on(2)
	print('Reverse')

def myInit():
	pass





def myLoop():
	points = []
	for i in range(0, 9):
		points.append(element.getElementByID(element.Point, i))

	rect0 = element.getElementByID(element.Rect, 0)
	rect1 = element.getElementByID(element.Rect, 1)
	rect2 = element.getElementByID(element.Rect, 2)

	hiPres()
	fwd()

	i=0
	r=False

	lastI = None

	for capture in range(0, captures):
		print(f'======== [{capture+1}/{captures}] Capture @ {i}')


		try:	#Capture the droplet
			red.blobgroup.lazyOffsetApproach(points[i], timeout=7, offset=15)	#offset in px
		except:
			manifold.off(vT[i])

			return

		manifold.off(vT[i])


		time.sleep(.5)

		loPres()

		time.sleep(2)

		if not lastI is None:
			manifold.off(vT[lastI])	#Release the last used trap

		if i==8:
			r=True
			rev()

		elif i==0:
			r=False
			fwd()

		nextI = i + (1 if not r else -1)	#i of next run


		manifold.on(vT[nextI])	#prime next trap

		time.sleep(1)

		manifold.on(vT[i])	#gentle eject
		time.sleep(.5)	#dumb gentle eject (no sensing)
		hiPres()	#Fully eject


		lastI = i
		i = nextI



	time.sleep(1)

	flu.stop()
	
	

flu.init = myInit
flu.onFrame = myLoop

flu.begin()