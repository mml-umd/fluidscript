# FluidScript Class Documentation

## **blob module**

#### Blob class

Represents a single droplet. Stores position, width, length, color, coordinates, OpenCV contour, angle, and velocity.

	Blob(pos, color, angle)

Constructor. Creates a blob of the given  **pos**,  **color**, and  **angle**.

	advanceTo(newblob)

Copies the properties of this blob to a new blob object  **newblob**. Uses the preexisting position property of the new blob to calculate the current velocity.

	pos()

Getter function. Returns the current position of this blob.

	highlight(frames)

Updates an internal counter to mark the blob to be highlighted for the next  **frames**  number of frames (default 15). The internal counter is decremented for each frame that it is drawn on-screen.

	draw(img)

Draws the blob on the image frame  **img**  provided.

## **blobgroup module**

**BlobGroup class**

Represents a collection of blobs; or all the blobs on-screen in a given frame.

	BlobGroup(blobs)

Constructor. Create a blob group from a list of  **blobs** (optional).

	get(index)

Returns a specific blob at the  **index** provided.

	drawBlobs(img)

Draw all the blobs in this group on the image frame **img** provided.

	byLength()

Returns a new Blobgroup where the blobs in the list are sorted by length.

	byRectArea()

Returns a new Blobgroup where the blobs in the list are sorted by area (length times width).

	byProximity(elem)

Returns a new Blobgroup where all the blobs in the list are sorted by distance to an element  **elem**  provided.

	byWithin(boundObj)

Returns a new Blobgroup containing only the blobs with center points that are within the element  **boundObj**provided. This method allows for Rect elements to be used as ROIs to select blobs in a specific region on-screen.

	waitForAnyWithin(objBound, timeout, wait)

Blocks the current thread until a blob enters the bounding element  **objBound**  specified. The default  **timeout**  until an exception is raised is config.BLOBUTIL_TIMEOUT, specified in the config module. The default busy-waiting period  **wait**  is config.BLOBUTIL_WAIT_PERIOD.

	waitForNoneWithin(objBound, timeout, wait)

Blocks the current thread until there are no blobs bounded by the element objBound specified.

	waitForAnyApproach(objStatic, timeout, wait)

Blocks the current thread until a blob horizontally transits the element  **objStatic**  specified. This method functions by waiting until the absolute x-distance between a point and a blob changes from positive to negative, or vise-versa.

	lazyOffsetApproach(objStatic, timeout, wait, offset, absOffset)

Functions the same as waitForAnyApproach, but moves the trigger point upstream by a set number of pixels,  **offset.** If absOffset is True (default False), then the shift is absolute, regardless of the direction the blob is traveling. This technique is useful for fine-tuning droplet capture operations on-the-fly where reliability is crucial and is more practical than manually moving the capture point element on-screen.

## **blobutil module**

A collection of utility functions mainly used internally for blob operations.

	dist(a, b)

Returns the distance between two coordinate pair tuples  **a** and  **b,**  in the form (x, y).

	xDist(a, b)

Returns the x-distance between two coordinate pairs.

	yDist(a, b)

Returns the y-distance between two coordinate pairs.

	xAbsDist(a, b)

Returns the absolute value of the x-distance between two coordinate pairs.

	yAbsDist(a, b)

Returns the absolute value of the y-distance between two coordinate pairs.

	withinObj(tObj, boundObj)

Returns True or False indicating if  **tObj**  is bounded by  **boundObj**, where the latter is a Rect element.

## **camera module**

**Camera class**

Wrapper class for an OpenCV capture device. Sub-classes the ThreadedClass class.

	Camera(fluidscript, source, width, height)

Constructor. Creates a Camera object with the given  **width** and  **height**. References the  **fluidscript** object provided. The video  **source**  can either be a number (camera device), an image filename, or a video filename.

	open()

Opens the OpenCV videoCapture object if it is a camera device or video file (if it is an image file, do nothing).

	reOpen()

Re-open the OpenCV videoCapture object again, on the same source. This can be called to reset video playback or fix issues with camera devices.

	setProperties()

Set all the video properties necessary to capture video from the OpenCV videoCapture source. The properties defined are cv2.CAP_PROP_FOURCC, cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, and cv2.CAP_PROP_FPS, in the config module.

	getFrame()

Gets an image frame from the capture device, or tries to re-open the capture device if in error occurs.

	threadFunction()

Gets the latest frame from the capture device, increments the frame-rate counter, and sets a ready flag, to indicate to other threads that a new frame is available. This method overrides the threadFunction method provided by the ThreadedClass class.

	threadExitFunction()

Releases the video capture device. This method overrides the threadExitFunction method provided by the ThreadedClass class, and is called automatically when the thread exits.

## **colorchannel module**

**ColorChannel class**

Represents a set of hue, saturation and value (HSV) thresholds. Contains a BlobGroup object listing all blobs bounded by this color channel, as well as a list of tracer coordinates, used to draw tails behind each blob. Each threshold control is handled by a Trackbar object, which automatically populates a window with sliders that the user can drag to change the values.

	ColorChannel(name)

Constructor. Creates a color channel with the label  **name.**

	getMask(hsvImage)

Returns the mask (black and white image) for the blobs in the current blob group, given an image frame  **hsvImage** in HSV format. Performs erosion followed by dilation of the mask, which removes small erroneous detections. Gets OpenCV contours and determines center points.

## **config module**

Module containing various constants and configuration parameters for Fluidscript.

	CAMERA_WIDTH
	CAMERA_HEIGHT

The width and height of the camera frame. The camera must support this resolution.

	CAMERA_SOURCE

The OpenCV video device index to use. It is 0 if there is only one camera connected to the system.

	DATA_DIRECTORY

The directory to save data files, images, and video recordings.

	EPR_1_PORT
	EPR_2_PORT

The COM ports where the EPR regulators are connected.

	MANIFOLD_1_PORT
	MANIFOLD_2_PORT

The COM ports where the USB-to-serial manifold adapters are connected.

	FILE_TRACKBAR

The JSON file to cache trackbar positions.

	FILE_ELEMENT

The JSON file to cache user-drawn elements.

	FILE_EPR

The JSON file to cache EPR pressure setpoints.

	MAX_BLOBS

Only create contours for this many blobs. If there are more than MAX_BLOBS blobs onscreen, they are ignored.

	BLOB_VELOCITY_AVERAGE_SIZE

Average blob velocity over this many frames.

	BLOBUTIL_WAIT_PERIOD

While waiting for a condition to be met (a blob passing a point, or all blobs exiting an ROI, etc.), busy-wait this many seconds. Should be a small value.

	BLOBUTIL_TIMEOUT

Give up waiting after this many seconds, and raise an exception.

	BLOBUTIL_ANY_APPROACH_MAX_Y_DEVIATION

Don’t consider blobs that are above or below the reference point by more than this many pixels.

	BLOBUTIL_ANY_APPROACH_MAX_DIST

Don’t consider blobs that are further away (in all directions) than this many pixels from the reference point.

	HOVER_DISTANCE

Highlight on-screen elements when the mouse is within this distance.

	FOURCC_CAM
	FOURCC_OUTPUT

The four-character code (fourcc) used to select a video format for camera input, and video file output, respectively.

	OUTPUT_EXTENSION

The file extension given to video files.

	TARGET_CAM_FPS

The maximum frame-rate the camera will be polled at.

	OUTPUT_FPS

The frame-rate that the video file will receive. This only affects playback, and is not dependent on the actual rate that frames are written to the file.

	FONT

The OpenCV font to use for printing text on-screen.

	FONT_HEIGHT
	FONT_WIDTH

Reference size, in pixels, of the font at size “1”. This is used to calculate the actual size of text at different font sizes.

	FONT_HUD_SIZE

Size of the status text at the top of the video feed.

	FONT_SIZE

Size of text printed on the video feed.

	FONT_THICKNESS

Line thickness of text.

	FONT_LINETYPE

Line type of text, provided by OpenCV. This should be an anti-aliased type to get smooth-looking characters.

	LINE_THICKNESS

Line thickness of elements (Rects, Points, blobs).

	COLOR_HOVER

Color of elements when the mouse is hovering over them.

	COLOR_INACTIVE

Color of elements.

	VALVE_KEYS

A list of keys, in order, that correspond to pneumatic valves. By default, 24 keys are used.

	KEYMAP

A map of keycodes to a short name for the corresponding key. This makes referencing the OpenCV keycodes much easier.

## **element module**

This module contains both the Element class as well as its sub-classes (Point and Rect), and some non-class utility functions.

	getPoints()

Returns the Point elements currently stored in the list of all elements.

	getRects()

Returns the Rect elements currently stored in the list of all elements.

	getAllElements()

Returns a list containing both Rect elements and Point elements.

	getElementByID(elemClass, id)

Returns the element which has the type  **elemClass**  and the ID of  **id**. If no elements have the right id, None is returned.

	writeElements()

Save all elements (including position, etc.) to a file.

	loadElements()

Load elements from the file into the corresponding lists.

#### Element class

Represents a generic element. This class is sub-classed by Rect and Point.

	Element(id)

Constructor. The default  **id**  is 0 but should be changed with the GUI after a Point or Rect is created.

	nextID()

Increments the ID of this element.

	previousID()

Decrements the ID of this element.

	pos()

Getter method for the position of this element. For a point, the position is the center. For a rectangle, the position is the upper left corner.

	pos2()

Getter method for the secondary position of the element. The Rect class uses this property to locate the lower right corner.

	intPos()

Returns the position of the element, truncated to integer values.

	move(offset)

Moves the element by the distance specified in  **offset**, in the form (x-distance, y-distance).

	moveTo(pos)

Sets the position of the element to  **pos**.

	destroy()

Removes the element.

#### Point class

This class sub-classes Element. It represents a single point.

Point(pos, id)

Constructor. Creates a point element at  **pos**,  with the specified  **id.**

draw(img)

Draws cross-hairs and the element ID onto the image frame  **img**  provided.

#### Rect class

This class sub-classes Element. It represents a rectangle or ROI.

	Rect(pos, pos2, id)

Constructor. Creates a rectangle element with corner positions  **pos**  and  **pos2**, with the specified  **id.**

	draw(img)

Draws a rectangle and element ID onto the image frame  **img**  provided.

	move(offset)

This overrides the move method of the Element class. Moves both the primary position (top left corner) and secondary position (bottom right corner) by the amounts specified in  **offset**, in the form (x-distance, y-distance).

## **epr module**

**EPR class**

Manages serial connection to an EPR digital pressure regulator.

	EPR(id, comport)

Constructor. Supply an  **id**  and a serial port  **comport**. The ID is used to make pressure settings persistent across program restarts, and to identify each EPR regulator.

	writeOut()

Writes the current pressure set-point to file.

	updateSetPointStr()

Sets an internal string showing the set-point in the format “1.23PSI”. Used to show the pressure as text on the video output.

	_inc(x)

Internal method to change the set-point by  **x**  psi, either positive or negative.

	inc()

Increments the set-point by a small amount.

	dec()

Decrements the set-point by a small amount.

	send()

Sends the current set-point to the serial port. Includes the regulator-specific ID set in the constructor, which may be required for the regulator to accept the command.

## **filterutil module**

Provides various image manipulation functions used to process the video feed.

	saturation(img, x)

Adds a scalar  **x**  to the saturation component of an image  **img**  in HSV format.

	blurDeltaNormal(img, level)

Performs a normalization operation on the image, by taking the difference between the input image frame  **img**  in BGR format and a blurred copy of itself. The radius of the blur is proportional to  **level**. The normalization operation has the effect of leveling the bulk of the image to middle gray, while retaining small details and edges.

	brightnessAndContrast(frame, b, c)

Apply brightness  **b** and contrast **c** (values from 0-255) to the image  **frame**  in BGR format.

## **fluidscript module**

**FluidScript class**

Main class for FluidScript components. Instantiates Camera, Processor, GUI, VideoRecorder, Manifold, and EPR objects.

	FluidScript()

Constructor.

	stop()

Stops the user-script loop.

	start()

Starts the user-script loop.

	kill()

Sets the kill flag to stop FluidScript and close the program.

	begin()

The method that the user-script must call to start the video capture, processing, and GUI operations. This method does not exit until the program stops (i.e. it runs in an infinite loop in the main thread). It handles calling the user-script “onFrame” function when a new video frame is available, and shutting down the other threads when program exits.

## **framecounter module**

**FrameCounter class**

A simple class that handles calculating frame-rates by calling a method once per frame.

	FrameCounter(limit)

Constructor. The default number of frames to average the frame-rate over, **limit**,  is 100.

	count()

Call this method once per frame. Updates the internal list of count times.

	calc()

Returns the calculated frame-rate using the stored times.

## **gui module**

**GUI class**

Sub-classes ThreadedClass. Manages color channels, video control track-bars, click-and-drag functionality, and keypresses.

	GUI(flu)

Constructor. Provide the FluidScript object  **flu**  that this class should reference.

	createColorChannel(name)

Returns a color channel with the specified  **name**. By calling this method, a window with thresholding track-bars will automatically be created.

	threadInitFunction()

Creates a window for video controls, and a main window for video playback. This method overrides the threadInitFunction method provided by the ThreadedClass class.

	threadFunction()

Handles keypresses received from the cv2 module with the handleKey method. Highlights the element that the mouse is currently hovering over. Concatenates the latest frame from the processor module and the camera module into a two-frame video feed, so both the raw and processed images can be displayed neatly onscreen. This method overrides the threadFunction method provided by the ThreadedClass class.

	threadExitFunction()

Closes all the open windows.  This method overrides the threadExitFunction method provided by the ThreadedClass class.

	saveFrame(annotation)

Saves the current image frame from both processed and raw feeds, with the optional  **annotation**  string included in the filename.

	handleKey(keycode)

Performs various actions according to the  **keycode**  received.

	handleMouse(event, x, y, flags, param)

Creates and removes elements on-screen when the mouse is clicked. Only the upper video panel (processed video) responds to the mouse. The element created upon a left-click is either Point or Rect, determined by the selectedElementClass variable.

## **interval module**

**Interval class**

Simple timer class.

	Interval(dur)

Constructor. Creates a timer of the specified duration  **dur**.

	reset()

Resets the timer’s counter to the current time.

	advance()

Returns True if the timer has expired. If so, it is reset.

## **jsonutil module**

This module contains some functions for handling JSON file reading and writing.

	readJSON(file)

Reads JSON data from the  **file**  specified. Returns a Python dictionary with the contents. If there is an error parsing the contents, an empty dictionary is returned.

	writeJSON(data, file)

Writes the  **data**  specified to  **file**. The data should be a Python dictionary.

## **logger module**

**Logger class**

Class to handle writing experiment data to a CSV file.

	Logger(names)

Constructor. Creates a new logger object with the specified column  **names**. The names are written to the first row of the CSV file.

	writeString(s)

Internal function to write a string of text,  **s**,  to the CSV file.

	log(inDict)

Logs experiment data to a new line of the CSV file. The input dictionary  **inDict**  should contain key/value pairs, with keys the same as the column names used when the logger was created. If the dictionary doesn’t contain a value for a certain column, “n/a” is written. If the dictionary contains a key that isn’t in the list of column names, that entry will be ignored.

## **manifold module**

**Manifold class**

Class for interfacing with pneumatic manifolds through a serial adapter.

	Manifold(comport)

Constructor. Creates a Manifold object representing one physical valve manifold and one serial port,  **comport**. The total number of available valves and manifold objects created are tracked when a new Manifold object is instantiated.

	send(index, state)

Sends a command to the manifold controller. The  **index**  specifies the valve to be actuated, and  **state**  is True or False to indicate an on or off state.

	on(index)

Turns on the valve specified at the  **index**.

	off(index)

Turns off the valve specified at the  **index**.

	toggle(index)

Switches the state of the valve at the  **index**  specified.

	getState(index)

Returns the state (on or off) of the specified valve at  **index**.

	destroy()

Closes this serial port.

## **processor module**

**Processor class**

Sub-classes ThreadedClass. Handles video processing.

	Processor(flu)

Constructor. Creates a Processor object where  **flu**  is the FluidScript object it will reference.

	threadFunction()

Fetches the latest camera frame when it is available and prepares to run the doVision method.  This method overrides the threadFunction method provided by the ThreadedClass class.

	doVision(inputImg)

Applies blob detection and filters to the given video frame  **inputImg**. This includes blur/normalization, brightness and contrast, blob detection, and overlay information. The blobs for each color channel are detected individually. This method stores information about the detected blobs in their respective color channel blob groups, and stores the processed image frame in a variable where the GUI thread will fetch and display it.

## **threadedclass module**

**ThreadedClass class**

A base class for running tasks in separate threads.

	ThreadedClass()

Constructor.

	threadLoop()

This method runs within a new thread. It calls threadInitFunction once, when the thread is first started, then calls threadFunction in a loop until the kill method is called (either from this thread or another thread), and then finally threadExitFunction is called.

	start()

Launches a new thread, passing the threadLoop method as the target. Returns false if the thread is already running.

	kill()

Sets a flag which will stop the thread. However, threadFunction must yield (run completely through), otherwise threadLoop will never have a chance to check this flag, and stop the thread. If there are long delays or loops in threadFunction the thread will not stop until they finish.

	threadInitFunction()

This method should be overridden with custom functionality. Runs once when the thread is started.

	threadFunction()

This method should be overridden with custom functionality. Runs repeatedly.

	threadExitFunction()

This method should be overridden with custom functionality. Runs once when the thread exits.

## **trackbar module**

**Trackbar class**

Manages creation and persistence of OpenCV trackbars.

	Trackbar(max, val, name, list)

Constructor. The track-bar can select values between zero and the  **max**. The default value will be  **val**. The track bar label,  **name,** must be unique. The last value of a track-bar with the same name (if it exists) is recalled from the file.

	on(val)

OpenCV will call this function whenever the track-bar is modified (the slider is dragged), and passes it the new value.

	getVal()

Returns the current value.

	addTo(winName)

Creates the OpenCV track-bar on the given window name  **winName**.

	writeOut()

Updates the value of this track-bar in the JSON file and saves it to disk.

**util module**

Contains various macro functions and other utilities.

	getDatedFile(name)

When passed a filename,  **name**, with braces (“{}”), they are replaced by the current date in ISO format. Also checks to make sure that a daily folder (year-month-day) exists, and creates it if not. Returns the full path to the file with the modified filename.

	drawHudText(image, pos, text, color, pixelPos)

Prints  **text**  on the specified frame,  **image**, at the position  **pos**  given as a tuple (x, y). The color is either white, or  **color**  given as a tuple (B, G, R). This function puts a larger black copy of the text behind the white/colored text, so that it is easy to read no matter what the background image is. If pixelPos is True (default False), then the position is in terms of pixels, not whole characters.

	colorHSV2BGR(c)

Converts a color in (H, S, V) format to (B, G, R) format.

## **videorecorder module**

**VideoRecorder class**

Sub-classes ThreadedClass. Records image frames to a video file.

	VideoRecorder(fluidscript)

Constructor. Provide the  **fluidscript**  object to be referenced.

	threadInitFunction()

Creates an OpenCV videoWriter object for both raw and processed streams, pointed to unique files in the output directory. This method overrides the threadInitFunction method provided by the ThreadedClass class.

	threadFunction()

Sends the latest video frames to the videoWriter objects at the frame-rate specified in config.OUTPUT_FPS.  This method overrides the threadFunction method provided by the ThreadedClass class.

	threadExitFunction()

Releases the videoWriter objects.