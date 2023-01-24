from datetime import datetime
import cv2
import config
import numpy as np
import os

def getDatedFile(name):
	#name will be something like 'my-video-{}.avi'

	stamp = datetime.now().isoformat()[0:19].replace(":", "-")
	ymd = stamp[0:10]

	if not os.path.exists(f'{config.DATA_DIRECTORY}/{ymd}'):
		os.makedirs(f'{config.DATA_DIRECTORY}/{ymd}')

	return f'{config.DATA_DIRECTORY}/{ymd}/{name.format(stamp)}'

def drawHudText(image, pos, text, color = None, pixelPos = False):
	if pixelPos is False:
		xPos = pos[0] * config.FONT_WIDTH * config.FONT_HUD_SIZE
		yPos = (pos[1] + 1) * config.FONT_HEIGHT * config.FONT_HUD_SIZE
	else:
		xPos = pos[0]
		yPos = pos[1]

	cv2.putText(image, text, (int(xPos), int(yPos)), config.FONT, config.FONT_HUD_SIZE, (0, 0, 0), config.FONT_THICKNESS + 1, config.FONT_LINETYPE)
	topColor = (255, 255, 255)
	if not color is None:
		topColor = color
	cv2.putText(image, text, (int(xPos), int(yPos)), config.FONT, config.FONT_HUD_SIZE, topColor, config.FONT_THICKNESS, config.FONT_LINETYPE)


def drawText(image, pos, text, color=None):
	if color is None:
		cv2.putText(image, text, pos, config.FONT, config.FONT_SIZE, (0, 0, 0), config.FONT_THICKNESS+1, config.FONT_LINETYPE)
		cv2.putText(image, text, pos, config.FONT, config.FONT_SIZE, (255, 255, 255), config.FONT_THICKNESS, config.FONT_LINETYPE)
	else:
		cv2.putText(image, text, pos, config.FONT, config.FONT_SIZE, color, config.FONT_THICKNESS, config.FONT_LINETYPE)


def colorHSV2BGR(c):
	color = np.uint8([c[0], c[1], c[2]]).reshape(1, 1, 3)
	bgrColor = cv2.cvtColor(color, cv2.COLOR_HSV2BGR).reshape(3)
	bgrColor = (int(bgrColor[0]), int(bgrColor[1]), int(bgrColor[2]))

	return bgrColor



