import numpy
import cv2

def value(img, x):
	img = img.copy()
	v = img[..., 2]
	v = cv2.add(v, x)
	numpy.clip(v, 0, 255)

	img[..., 2] = v

	return img

def saturation(img, x):
	img = img.copy()
	s = img[..., 1]
	s = cv2.add(s, x)
	numpy.clip(s, 0, 255)

	img[..., 1] = s

	return img

def blurDeltaNormal(img, level):

	pixelradius = (level*2+1,)*2 #This formula creates a two-element tupple (same values). Smallest radius 1.


	img = img.astype("float32")
	if level > 0:
		blurred = cv2.blur(img, pixelradius)
		img = numpy.subtract(
			numpy.add(img, 255),
			blurred
		) * 0.5

	return img.astype("uint8")

def brightnessAndContrast(frame, b, c):	#Apply brightness and contrast to an image
	if b != 0:
		if b > 0:
			shadow = b
			highlight = 255
		else:
			shadow = 0
			highlight = 255 + b
		alpha_b = (highlight - shadow) / 255
		gamma_b = shadow

		buf = cv2.addWeighted(frame, alpha_b, frame, 0, gamma_b)
	else:
		buf = frame.copy()

	if c != 0:
		f = 131*(c + 127)/(127*(131 - c))
		alpha_c = f
		gamma_c = 127*(1-f)

		buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

	return buf



	
