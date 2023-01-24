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








p0 = None
p1 = None
pC = None
r = None
colorChannel = None



direction = 'fwd'
runNumber = 0
frameNumber = 0

startFrames = 1*50

def myInit():
	global logger, p0, p1, pC, r, colorChannel

	logger = logger.Logger([
		'frame',
		'run',
		'timestamp',
		'direction',
		'pressure',
		'x',
		'velocity',
		'length',
		'width'
	])

	r = element.getElementByID(element.Rect, 0)

	p0 = element.getElementByID(element.Point, 0)
	p1 = element.getElementByID(element.Point, 1)
	pC = element.getElementByID(element.Point, 2)

	colorChannel = red

	loPres()

	manifold.on(vS1)
	manifold.on(vS2)

	for v in vT:
		manifold.on(v)




amplitude = 150

numRuns = 500


def myLoop():
	global direction, frameNumber, runNumber

	b = colorChannel.blobgroup.byWithin(r).get(0)

	if b is None:
		print('No blob')
		flu.stop()
		return

	distC = blobutil.xDist(pC.pos(), b.pos())

	logger.log({
		'frame':frameNumber,
		'run':runNumber,
		'timestamp':time.time(),
		'direction':direction,
		'pressure':flu.epr2.setPoint,
		'x':distC,
		'velocity':b.velocity,
		'length':b.length,
		'width':b.width
		})






	if direction == 'rev' and distC > amplitude:
		fwd()
		direction = 'fwd'
		runNumber += 1

	if direction == 'fwd' and distC < -amplitude:
		rev()
		direction = 'rev'
		runNumber += 1

	if runNumber > numRuns:
		print(f'Reached {runNumber} runs! ({frameNumber} frames)')
		flu.stop()
		return

	

	frameNumber += 1




flu.init = myInit
flu.onFrame = myLoop

flu.begin()


