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




def observePattern():	#Detect droplets in traps from the video feed
	if isHiPres:	#Measurement only safe at low pressure
		loPres()
		time.sleep(1.5)

	ret = [' ']*9

	for i in range(0, 9):
		for c in ['R', 'G']:
			if c == 'R':
				colorChannel = red
			elif c=='G':
				colorChannel = green

			r = element.getElementByID(element.Rect, i)
			if not colorChannel.blobgroup.byWithin(r).get(0) is None:
				ret[i] = c

	return ret


def getPatternString(p):
	s = ''
	for i in [0, 1, 2, 5, 4, 3, 6, 7, 8]:	#Line by line to trap by trap numbering conversion
		s += p[i] if not p[i] == ' ' else '.'
		if i==2 or i==3 or i==8:
			s += '\n'

	return s






def eject(i, c, manualDelay=None):
	loPres()

	rect = element.getElementByID(element.Rect, i)

	time.sleep(.5)

	if c=='R':
		colorChannel = red
	elif c=='G':
		colorChannel = green

	manifold.on(vT[i])

	if manualDelay is None:	#If automatic gentle ejection
		try:
			colorChannel.blobgroup.waitForNoneWithin(rect)
		except:
			print(f'Gentle eject on {i} for {c} failed...')

		time.sleep(.4)	#Extra time

	else:	#Dumb gentle ejection
		time.sleep(manualDelay)


	hiPres()	#Droplet will come completely out at this stage

	time.sleep(.2)






def capture(i, c):
	point = element.getElementByID(element.Point, i)

	hiPres()

	try:
		if c=='R':
			colorChannel = red
		elif c=='G':
			colorChannel = green

		colorChannel.blobgroup.lazyOffsetApproach(point, timeout=15, offset=15)	#offset in px

	except:
		raise Exception('Failed waiting for approach')

	manifold.off(vT[i])

	time.sleep(.2)





def moveDroplet(i1, i2, c):
	print(f'{c} {i1} -> {i2}')
	if i1 < i2:
		fwd()
	else:
		rev()

	eject(i1, c)

	capture(i2, c)


def moveMergeDroplet(i1, i2, c):	#When i2 already contains something
	point = element.getElementByID(element.Point, i2)

	if c=='R':
		colorChannel = red
	elif c=='G':
		colorChannel = green

	print(f'{c} {i1} -m-> {i2}')
	if i1 < i2:
		fwd()
	else:
		rev()

	eject(i1, c)

	loPres()

	colorChannel.blobgroup.lazyOffsetApproach(point, timeout=15, offset=20)	#offset in px

	manifold.on(vT[i2])	#Eject partially, merge
	time.sleep(.1)
	manifold.off(vT[i2])	#Retain in trap

	time.sleep(.5)



def sortToPattern(target):	#Swapping version
	for d in range(0, 3):	#Move 3 reds
		print(f'[1/3] ({d}/3) Moving red')
		currentPattern = observePattern()

		#printPatternStatus()

		wrongRed = None
		empty = None

		for i in range(0, 9):	#Where red is obstructing green
			if target[i] == 'G' and currentPattern[i] == 'R':
				wrongRed = i;
				print(f'{i} should be green but is red')
				break

		for i in range(0, 9):	#Move to a designated empty spot or destination, just not a green destination.
			if target[i] != 'G' and currentPattern[i] == ' ':
				print(f'...moving red to {i}')
				empty = i;
				break
		
		if not wrongRed is None and not empty is None:
			
			moveDroplet(wrongRed, empty, 'R')	#Get red out of way


	for d in range(0, 3):	#Move 3 greens
		print(f'[2/3] ({d}/3) Moving green')
		currentPattern = observePattern()

		#printPatternStatus()

		wrongGreen = None
		destination = None

		for i in range(0, 9):	#Where green should not be
			if target[i] != 'G' and currentPattern[i] == 'G':
				print(f'{i} shouldnt be green')
				wrongGreen = i;
				break

		for i in range(0, 9):	#Find final destination
			if target[i] == 'G' and currentPattern[i] == ' ':
				print(f'...moving green destination {i}')
				destination = i;
				break
		
		if not wrongGreen is None and not destination is None:
			
			moveDroplet(wrongGreen, destination, 'G')	#Get green out of way


	for d in range(0, 3):	#Move 3 reds (again)
		print(f'[3/3] ({d}/3) Moving red')
		currentPattern = observePattern()

		wrongRed = None
		destination = None

		for i in range(0, 9):	#Where red should not be
			if target[i] != 'R' and currentPattern[i] == 'R':
				print(f'{i} shouldnt be red')
				wrongRed = i;
				break

		for i in range(0, 9):	#Find final destination
			if target[i] == 'R' and currentPattern[i] == ' ':
				print(f'...moving red to destination {i}')
				destination = i;
				break
		
		if not wrongRed is None and not destination is None:
			moveDroplet(wrongRed, destination, 'R')

	print('==== Droplets moved. ====')

		

def myInit():
	pass


def myLoop():
	loPres()
	fwd()

	manifold.on(vS1)
	manifold.on(vS2)

	time.sleep(2)

	currentPattern = observePattern()

	for i in range(0, 9):
		if currentPattern[i] == ' ':
			manifold.on(vT[i])	#Turn on empty traps

	sortToPattern('R GG RR G')	#vertical columns

	loPres()
	time.sleep(10)

	sortToPattern(' RRR GGG ')	#corners

	loPres()
	time.sleep(10)

	sortToPattern(' GGG RRR ')	#oposite corners

	loPres()
	time.sleep(10)

	sortToPattern('RRG  RG G')	#top left corner and single corners

	loPres()
	time.sleep(10)

	sortToPattern('RGRG  RG ')	#thing 1

	loPres()
	time.sleep(10)

	sortToPattern('RRR   GGG')	#Ending pattern

	loPres()
	time.sleep(10)


	moveMergeDroplet(0, 6, 'R')
	time.sleep(2)

	moveMergeDroplet(1, 7, 'R')
	time.sleep(2)
	
	moveMergeDroplet(2, 8, 'R')
	time.sleep(2)


	time.sleep(10)

	rev()

	time.sleep(1)



	eject(6, None, .8)
	time.sleep(1)

	eject(7, None, .8)
	time.sleep(1)

	eject(8, None, .8)
	time.sleep(1)

	loPres()
	print(f'==== Program done ====')
	flu.stop()

flu.init = myInit
flu.onFrame = myLoop

flu.begin()