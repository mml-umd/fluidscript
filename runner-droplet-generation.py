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



#Valve ports
vS1=0	#Sample1
vS2=1	#Sample2

vH1=2	#H bridge controls
vH2=3


vT = [12, 13, 14, 15, 16, 17, 18, 19, 20] #Traps

vP1=22	#Pressure valves
vP2=23

flu = fluidscript.FluidScript()

green = flu.gui.createColorChannel('Green')
red = flu.gui.createColorChannel('Red')




isHiPres = False



def hiPres():
	global isHiPres
	manifold.off(vP1)
	manifold.on(vP2)
	isHiPres = True
	#print('...High pressure')

def loPres():
	global isHiPres
	manifold.off(vP2)
	manifold.on(vP1)
	isHiPres = False
	#print('...Low pressure')

def fwd():
	manifold.off(vH1)
	manifold.on(vH2)
	#print('...Forward')

def rev():
	manifold.off(vH2)
	manifold.on(vH1)
	#print('...Reverse')





minFlow = 0
maxFlow = .5

dataLogger = None
runNumber = 0


def myInit():
	global dataLogger, runNumber

	runNumber = 0

	dataLogger = logger.Logger([
		'runNumber',
		'timestamp',
		'flowTime',
		'velocity',
		'length',
		'width'
	])

	loPres()

	fwd()



def cleanRoutine():
	print(f'Cleaning...')

	manifold.off(vS1)
	time.sleep(.8)
	manifold.on(vS1)

	time.sleep(10)
	print(f'Cleaning done')




def myLoop():
	global runNumber

	p = element.getElementByID(element.Point, 0)
	r = element.getElementByID(element.Rect, 0)

	flowTime = random.random()*(maxFlow - minFlow) + minFlow

	flu.statusText = f'Run {runNumber} {round(flowTime, 2)}s'
	print(f'Run {runNumber} {flowTime}s')

	manifold.off(vS1)
	time.sleep(flowTime)
	manifold.on(vS1)


	try:
		b = red.blobgroup.waitForAnyApproach(p, timeout=20)
	except:
		while True:
			try:
				red.blobgroup.waitForNoneWithin(r, timeout=5)
				break
			except:
				print(f'Stuck! Initiating cleaning')
				cleanroutine()

		return

	print(f'Length: {b.length}')


	dataLogger.log({
		'runNumber': runNumber,
		'timestamp': time.time(),
		'flowTime': flowTime,
		'velocity': b.velocity,
		'length': b.length,
		'width': b.width
	})



	time.sleep(15)

	runNumber += 1




flu.init = myInit
flu.onFrame = myLoop

flu.begin()



