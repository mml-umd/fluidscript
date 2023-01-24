import cv2



#See3Cam CU30 Res table

# 3.4MP	(2304 x 1536)	48 fps
# 3MP	(2304 x 1296)	60 fps
# 3MP	(2048 x 1536)	50 fps
# 1280P	(1920 x 1280)	50 fps
# FHD	(1920 x 1080)	60 fps
# 960P	(1280 x 960)	58 fps
# HD	(1280 x 720)	60 fps
# XGA+	(1152 x 768)	60 fps
# VGA	(640 x 480)	60 fps


CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
#CAMERA_WIDTH = 1280
#CAMERA_HEIGHT = 720

#CAMERA_SOURCE = 'sample.png'
#CAMERA_SOURCE = 'sample.mp4'
CAMERA_SOURCE = 0 	#First camera source (the only camera connected to the system)
#CAMERA_SOURCE = "a.png"

DATA_DIRECTORY = 'D:/fluidscript_data'

EPR_1_PORT = 'COM1'
EPR_2_PORT = 'COM10'
MANIFOLD_1_PORT ='COM4'
MANIFOLD_2_PORT = 'COM7'

FILE_TRACKBAR = "cache/trackbar.json"
FILE_ELEMENT = "cache/element.json"
FILE_EPR = 'cache/epr.json'

MAX_BLOBS = 20 	#Maximum number of blobs per channel to track (extra are ignored)
BLOB_VELOCITY_AVERAGE_SIZE = 5 	#Average blob velocity over this many frames (consider how much preamble blobs will have for this to stabilize before a measurement is made)

BLOBUTIL_WAIT_PERIOD = 1/80 	#Period for blobutil functions to wait.
BLOBUTIL_TIMEOUT = 20 	#Default timeout for blob waiting functions

BLOBUTIL_ANY_APPROACH_MAX_Y_DEVIATION = 15	#Vertical deviation for a valid transit
BLOBUTIL_ANY_APPROACH_MAX_DIST = 30

HOVER_DISTANCE = 30



FOURCC_CAM = cv2.VideoWriter_fourcc(*"MJPG")	#Codec used to retreive video from the camera



#FOURCC_OUTPUT = cv2.VideoWriter_fourcc(*"MPEG")
#OUTPUT_EXTENSION = ".avi"

FOURCC_OUTPUT = cv2.VideoWriter_fourcc(*"avc1")
OUTPUT_EXTENSION = ".mp4"

#FOURCC_OUTPUT = cv2.VideoWriter_fourcc(*"mp4v")
#OUTPUT_EXTENSION = ".mp4"

#FOURCC_OUTPUT = cv2.VideoWriter_fourcc(*"X264")
#OUTPUT_EXTENSION = ".mkv"




TARGET_CAM_FPS = 50
OUTPUT_FPS = 50	#For writing files





FONT = cv2.FONT_HERSHEY_PLAIN
FONT_HEIGHT = 15	#Font height in px at size 1
FONT_WIDTH = 10	#Font width in px at size 1

FONT_ELEMENT_SIZE = 1	#Font size multiplier (size)
FONT_HUD_SIZE = 1
FONT_SIZE = 1

FONT_HUD_COLOR = (0, 0, 255)

FONT_THICKNESS = 1
FONT_LINETYPE = cv2.LINE_AA	#4, 8, or cv2.LINE_AA (antialias)

LINE_THICKNESS = 1 	#Thickness for drawn elements and bodies

COLOR_HOVER = (0, 0, 255)	#Common colors for Element states
COLOR_ACTIVE = (0, 255, 0)
COLOR_INACTIVE = (0, 0, 0)

VALVE_KEYS = [		#Keys to use to control valves, ordered 0-23
	'`',
	'1',
	'2',
	'3',
	'4',
	'5',
	'6',
	'7',
	'8',
	'9',
	'0',
	'-',
	'f1',
	'f2',
	'f3',
	'f4',
	'f5',
	'f6',
	'f7',
	'f8',
	'f9',
	'f10',
	'f11',
	'f12'
]

KEYMAP = {
	8:'backspace',
	
	96:'`',
	49:'1',
	50:'2',
	51:'3',
	52:'4',
	53:'5',
	54:'6',
	55:'7',
	56:'8',
	57:'9',
	48:'0',
	45:'-',
	61:'=',

	7340032:'f1',
	7405568:'f2',
	7471104:'f3',
	7536640:'f4',
	7602176:'f5',
	7667712:'f6',
	7733248:'f7',
	7798784:'f8',
	7864320:'f9',
	7929856:'f10',
	7995392:'f11',
	8060928:'f12',

	113:'q',
	119:'w',
	101:'e',
	114:'r',
	116:'t',
	121:'y',
	117:'u',
	105:'i',
	111:'o',
	112:'p',
	91:'[',
	93:']',
	92:'\\',
	97:'a',
	115:'s',
	100:'d',
	102:'f',
	103:'g',
	104:'h',
	106:'j',
	107:'k',
	108:'l',
	59:';',
	39:'\'',
	122:'z',
	120:'x',
	99:'c',
	118:'v',
	98:'b',
	110:'n',
	109:'m',
	44:',',
	46:'.',
	47:'/',
	32:' ',

	2490368:'up',
	2621440:'down',
	2424832:'left',
	2555904:'right'

}