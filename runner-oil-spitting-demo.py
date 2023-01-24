import element
import manifold
import time
import fluidscript
import time
import manifold


#This program splits droplets by spitting oil from a trap.
#Four droplets are metered and split into eight traps.


#Valve ports. Each number is the index of a pneumatic manifold port:
vS1=0	#Sample 1
vS2=1	#Sample 2

vH1=2	#H bridge controls
vH2=3

vT = [12, 13, 14, 15, 16, 17, 18, 19, 20]	#Trap ports

#Pressure valve pins for trap pressure. These are not pneumatic ports on the manifold itself.
#Instead, we use the electronic connections on the manifold to drive
#two 2-way valves:
vP1=22
vP2=23	

flu = fluidscript.FluidScript()	#Main fluidscript object

colorChannel = flu.gui.createColorChannel('Red')	#Create the color channel we are going to threshold. We only need one.

flowTime = 0.15


def hiPres():	#Define some simple macros for high & low pressure, and forwards and reverse flow.
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


#Ejection macro. Takes an index, which identifies both the detection rectangle and the trap to target.
def eject(i):

	rect = element.getElementByID(element.Rect, i)

	loPres()
	time.sleep(.5)

	manifold.on(vT[i])

	while len(colorChannel.blobgroup.byWithin(rect).blobs) > 0:	#While there is some droplet still within the trap
		time.sleep(.1)	#Wait for the blob to completely exit the trap (lo-pressure eject is slow)

	hiPres()



#Capture macro. Same principle as ejection macro.
def capture(i, channel):
	point = element.getElementByID(element.Point, i)

	hiPres()

	try:
		channel.blobgroup.lazyOffsetApproach(point, timeout=15, offset=15)	#Wait for the blob to transit the capture point with an offset of 15 pixels.

	except:
		raise Exception('Failed waiting for approach')

	manifold.off(vT[i])	#Capture the blob.




#Globals to keep track of where we have placed droplets.
trapIndex = 0
trapOrder = [7, 8, 5, 6, 3, 4, 1, 2]	#This is the order in which we will capture droplets. (Traps indexed 0 thru 8)



#User script initialization function
def myInit():
	global rapIndex

	print('Initializing valves')

	for i in vT:	#Turn off all the traps
		manifold.off(i)

	hiPres()

	manifold.on(vS1)	#Close the sample valves
	manifold.on(vS2)

	fwd()

	trapIndex = 0 #Restart the trap index counter

	print('Done initializing')




#Main user script loop
def myLoop():
	global trapIndex

	print('======== Begin program!')
	print(f'Flow time: {flowTime}')

	splitP = element.getElementByID(element.Point, 0)	#Get the point element which we will use to trigger splitting

	trapFirst = trapOrder[trapIndex]	#We will place the first satellite in this trap.
	trapSecond = trapOrder[trapIndex+1]	#We will place the second satellite in this trap (the one after)

	pFirst = element.getElementByID(element.Point, trapFirst)	#Get the corresponding capture points
	pSecond = element.getElementByID(element.Point, trapSecond)

	manifold.on(vT[trapFirst])	#Prime these traps for capture
	manifold.on(vT[trapSecond])

	manifold.off(vT[0])	#Prime the splitting trap for splititng
	hiPres()

	time.sleep(2)

	manifold.off(vS1)	#Inject a droplet
	time.sleep(flowTime)
	manifold.on(vS1)

	time.sleep(1)

	

	colorChannel.blobgroup.lazyOffsetApproach(splitP, offset=5, timeout=15)	#Wait for a droplet to transit the trap.
																			#The offset here can be tweaked, e.g. if we want to achieve equal satellite size.
	manifold.on(vT[0])	#Split droplet
	colorChannel.blobgroup.lazyOffsetApproach(pFirst, timeout=30)	#Wait for first droplet to pass first trap, and do nothing

	time.sleep(.5)

	print(f'Capturing {trapFirst}')
	colorChannel.blobgroup.lazyOffsetApproach(pFirst, offset=15, timeout=30)	#Wait for the second droplet at the first trap, and this time, capture it.
	manifold.off(vT[trapFirst])

	print(f'Capturing {trapSecond}')
	colorChannel.blobgroup.lazyOffsetApproach(pSecond, offset=15, timeout=30)	#Wait for the first droplet at the second trap, and capture it.
																				#This ordering 
	manifold.off(vT[trapSecond])

	
	trapIndex += 2 	#Advance the trap index counter. The next two droplets will fill the next two traps.


	if trapIndex >= len(trapOrder):	#Once we reach the end...
		print(f'Captured all droplets.')

		time.sleep(5)



		loPres()	#Eject all the droplets. Start at low pressure.
		time.sleep(1)

		for i in [8, 7, 6, 5, 4, 3, 2, 1]:
			manifold.on(vT[i])	#Perform two-stage partial ejection at low pressure first.
			time.sleep(.8)		#Wait for the droplet to begin to exit the trap (dumb-ejection only, no droplet detection)
			hiPres()	#eject the droplet fully.

			time.sleep(1)
			loPres()	#Return to low pressure.

			time.sleep(4)


		flu.stop()	#Tell Fluidscript to stop the user script loop
		return	#Return immediately.

	time.sleep(2)



flu.init = myInit	#This is what we want to run every time we start the routine
flu.onFrame = myLoop	#This will run at maximum once per frame, unless it includes delays like we have used in this script.

flu.begin()	#Launch Fluidscript


