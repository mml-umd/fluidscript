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


banana = flu.gui.createColorChannel('Color')	#The colorchannel for the acid, base, and their banana-colored mixture (wide hue range to cover every shade)


dataLogger = None	#This will be a new logger on each run

def hiPres():
	manifold.off(vP1)
	time.sleep(.2)
	manifold.on(vP2)
	print('...High pressure')

def loPres():
	manifold.off(vP2)
	time.sleep(.2)
	manifold.on(vP1)
	print('...Low pressure')

def fwd():
	manifold.off(vH1)
	time.sleep(.2)
	manifold.on(vH2)
	print('...Forward')

def rev():
	manifold.off(vH2)
	time.sleep(.2)
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

	time.sleep(1)

	for z in [.05, .05, .1, .1]:
		manifold.on(vT[i])
		time.sleep(z)
		manifold.off(vT[i])
		time.sleep(.3)

	manifold.on(vT[i])

	while len(channel.blobgroup.byWithin(rect).blobs) > 0:	#While there is some droplet still within the trap
		time.sleep(.1)	#Wait for the blob to completely exit the trap (lo-pressure eject is slow)

	time.sleep(.5)

	hiPres()

	print(f'Ejected {i}')


def capture(i, channel):
	point = element.getElementByID(element.Point, i)

	hiPres()

	try:
		channel.blobgroup.lazyOffsetApproach(point, timeout=25, offset=flu.gui.offsetBar.getVal())	#offset in px

	except:
		raise Exception('Failed waiting for approach')


	manifold.off(vT[i])

	print(f'Captured {i}')


def merge(i, channel):
	point = element.getElementByID(element.Point, i)

	loPres()

	try:
		channel.blobgroup.lazyOffsetApproach(point, timeout=25, offset=flu.gui.offsetBar.getVal())

	except:
		raise Exception('Failed waiting for merge')

	manifold.on(vT[i])
	time.sleep(.1)
	manifold.off(vT[i])

	print(f'Merged {i}')

def split(i, channel):
	point = element.getElementByID(element.Point, i)

	hiPres()

	try:
		channel.blobgroup.lazyOffsetApproach(point, timeout=25, offset=flu.gui.splitOffsetBar.getVal())
	
	except:
		raise Exception('Failed waiting for split')

	manifold.on(vT[i])

	print(f'Split {i}')

def acknowledge(i, channel):	#Waits for a droplet at a point, but does not do anything.
	point = element.getElementByID(element.Point, i)

	try:
		channel.blobgroup.lazyOffsetApproach(point, timeout=25)
	
	except:
		raise Exception('Failed waiting for acknowledge')

	print(f'Acknowledged {i}')

def dispense(valve, flowTime):
	manifold.off(valve)
	time.sleep(flowTime)
	manifold.on(valve)


def runnerInit():	#We must reset the logger and the run number each time we restart the user script

	print('Initializing')

	manifold.on(vAcid)
	manifold.on(vBase)

	fwd()

	loPres()

	time.sleep(1)

	for i in vT:
		manifold.on(i)
		time.sleep(.1)

	time.sleep(3)

	hiPres()

	time.sleep(1)

	print('Done initializing')


def runnerLoop():
	print('======== Begin program!')

	flowCoef = 3

	traps = [8, 7, 6, 5, 4, 3, 2]
	#traps = [3, 2]

	titrations = [
		['a'],
		['a', 'b', 'a', 'a'],
		['a', 'b', 'a'],
		['a', 'b'],
		['a', 'b', 'b'],
		['a', 'b', 'b', 'b'],
		['b']
	]

	splitTrap = 0
	splitPoint = element.getElementByID(element.Point, splitTrap)
	splitRect = element.getElementByID(element.Rect, splitTrap)

	holdingTrap = 2
	holdingPoint = element.getElementByID(element.Point, holdingTrap)
	holdingRect = element.getElementByID(element.Rect, holdingTrap)


	hiPres()
	fwd()

	for trapIndex, trap in enumerate(traps):	#Dispense acid/base into traps
		titration = titrations[trapIndex]

		for i, x in enumerate(titration):
			if x=='a':
				#channel = acid
				channel = banana
				valve = vAcid
				flowTime = flowCoef * flu.gui.flowBarA.getVal() / 1000
			else:
				#channel = base
				channel = banana
				valve = vBase
				flowTime = flowCoef * flu.gui.flowBarB.getVal() / 1000

			manifold.off(vT[splitTrap])
			time.sleep(.5)

			print(f'{x} @ {flowTime} s to {trap} (manifold {trapIndex}) titration: {titration}')
			dispense(valve, flowTime)

			if len(titration) > 1: 	#If there is more than one step, splitting is needed
				print('This step requires splitting.')
				split(splitTrap, channel)	#Split in half
				time.sleep(.1)
				capture(splitTrap, channel)	#Capture the upstream half immediately
				time.sleep(1)
				
			else:
				print('One step does not require splitting!')
				acknowledge(splitTrap, channel)
				break	#Skip to final capture

			if banana.blobgroup.byWithin(holdingRect).blobs:
				merge(holdingTrap, channel)	#Merge if there is something there already
				print('Waiting for mixing...')
				time.sleep(3)

			else:
				capture(holdingTrap, channel)	#Capture if it is empty
				time.sleep(1)

			if banana.blobgroup.byWithin(splitRect).blobs:	#If there is any junk
				print('Ejecting junk')
				rev()
				time.sleep(.2)

				eject(splitTrap, channel)	#Discard the junk
				time.sleep(5)	#Allow to go to waste

				manifold.off(vT[splitTrap])

				fwd()

			if not i == 0 and not i == len(titration)-1:	#Discard half of the retained droplet if this isn't the first droplet or last
				print('Reducing sample for next step...')

				fwd()
				time.sleep(.5)
				eject(holdingTrap, channel)
				time.sleep(.2)
				rev()

				split(splitTrap, channel)
				time.sleep(.1)
				capture(splitTrap, channel)	#Discard half of the sample
				time.sleep(5)
				fwd()
				time.sleep(1)
				eject(splitTrap, channel)
				capture(holdingTrap, channel)
				time.sleep(5)	#Let half of the sample go to waste


				fwd()
			
		if trap != holdingTrap:	#If the sample should not simply be left where it is (e.g. last sample)
			if banana.blobgroup.byWithin(holdingRect).blobs:
				print('The final product is in the holding trap, ejecting it.')
				eject(holdingTrap, channel)

		capture(trap, channel)	#Move the droplet to the final trap

		print('Droplet done!')

		time.sleep(.5)



	flu.stop()


flu.init = runnerInit	#Run every time we restart the program
flu.onFrame = runnerLoop

flu.oneShot = True	#This loop shouldn't repeat once it ends.

flu.begin()