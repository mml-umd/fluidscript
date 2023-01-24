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
vBase=0 
vAcid=1

vH1=2	#H bridge controls
vH2=3
vP1=22	#Pressure valves
vP2=23

vT = [12, 13, 14, 15, 16, 17, 18, 19, 20]	#Traps



flu = fluidscript.FluidScript()


base = flu.gui.createColorChannel('Base')
acid = flu.gui.createColorChannel('Acid')
product = flu.gui.createColorChannel('Product')


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
	print('...Flow stopped (on)')

def bothOff():
	manifold.off(vH1)
	manifold.off(vH2)
	print('...Flow stopped (off)')


def eject(i, channel):
	rect = element.getElementByID(element.Rect, i)

	loPres()

	time.sleep(.5)

	manifold.on(vT[i])

	while len(channel.blobgroup.byWithin(rect).blobs) > 0:	#While there is some droplet still within the trap
		time.sleep(.1)	#Wait for the blob to completely exit the trap (lo-pressure eject is slow)

	hiPres()


def capture(i, channel):
	point = element.getElementByID(element.Point, i)

	hiPres()

	try:
		channel.blobgroup.lazyOffsetApproach(point, timeout=20, offset=15)	#offset in px

	except:
		raise Exception('Failed waiting for approach')


	manifold.off(vT[i])


def merge(i, channel):
	point = element.getElementByID(element.Point, i)

	loPres()

	try:
		channel.blobgroup.lazyOffsetApproach(point, timeout=20, offset=flu.gui.offsetBar.getVal())

	except:
		raise Exception('Failed waiting for merge')

	manifold.on(vT[i])
	time.sleep(.05)
	manifold.off(vT[i])
	


def dispense(valve, flowTime):
	manifold.off(valve)
	time.sleep(flowTime)
	manifold.on(valve)


def runnerInit():	#We must reset the logger and the run number each time we restart the user script

	print('Initializing')

	loPres()

	time.sleep(1)

	for i in vT:
		manifold.on(i)

	time.sleep(1)

	hiPres()

	manifold.on(vAcid)
	manifold.on(vBase)

	fwd()

	time.sleep(.5)

	print('Done initializing')


def runnerLoop():
	print('======== Begin program!')

	acidTraps = [8, 7, 6]
	baseTraps = [5, 4, 3]

	for v in [vAcid, vBase]:	#Do this for base, then acid

		if v==vAcid:	#Select traps and color channel
			traps = acidTraps
			channel = acid
			flowTime = flu.gui.flowBarA.getVal() / 1000
		else:
			traps = baseTraps
			channel = base
			flowTime = flu.gui.flowBarB.getVal() / 1000

		for trap in traps:	#Dispense acid/base into traps
			
			print(f'{channel.name} @ {flowTime} sec to {trap}')
			dispense(v, flowTime)
			capture(trap, channel)
			time.sleep(.5)

	rev()

	for i in range(0, 3):
		acidTrap = acidTraps[i]
		baseTrap = baseTraps[2-i]
		targetTrap = i

		print(f'Acid {acidTrap}, base {baseTrap} to {targetTrap}')

		eject(acidTrap, acid)
		capture(targetTrap, acid)
		time.sleep(.5)
		eject(baseTrap, base)
		merge(targetTrap, base)
		time.sleep(1)

	flu.stop()


flu.init = runnerInit	#Run every time we restart the program
flu.onFrame = runnerLoop

flu.begin()


