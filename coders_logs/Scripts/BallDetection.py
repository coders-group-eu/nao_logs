# parts of code from https://pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
# Issue with it is that it only works for green balls
# This script tries to avoid that

# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import matplotlib.pyplot as plt


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# initialize the list of tracked points
pts = deque(maxlen=args["buffer"])

# if a video path was not supplied, grab the reference to the webcam
if not args.get("video", False):
	vs = VideoStream(src=0).start()
	FPS = vs.stream.get(cv2.CAP_PROP_FPS)
# otherwise, grab a reference to the video file
else:
	vs = cv2.VideoCapture(args["video"])
	FPS = vs.get(cv2.CAP_PROP_FPS)
# allow the camera or video file to warm up
time.sleep(3.0)



def main():
	while True:
		# grab the current frame
		frame = vs.read()
		# handle the frame from VideoCapture or VideoStream
		frame = frame[1] if args.get("video", False) else frame
		
		# if we are viewing a video and we did not grab a frame,
		# then we have reached the end of the video
		if frame is None:
			break
		
		# resize the frame, blur it, and convert it to the HSV
		# color space
		frame = imutils.resize(frame, width=600)
		
		# convert the frame to grayscale
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		# detect circles in the image
		circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 100)
		# ensure at least some circles were found
		if circles is not None:
			# convert the (x, y) coordinates and radius of the circles to integers
			circles = np.round(circles[0, :]).astype("int")
			# loop over the (x, y) coordinates and radius of the circles
			for (x, y, r) in circles:
				center = (x,y)
				pts.appendleft(center)
				# draw the circle in the output image, then draw a rectangle
				# corresponding to the center of the circle
				cv2.circle(frame, (x, y), r, (0, 0, 255), 2)
				#cv2.rectangle(gray, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
		
		
		# loop over the set of tracked points
		for i in range(1, len(pts)):
			# if either of the tracked points are None, ignore
			# them
			if pts[i - 1] is None or pts[i] is None:
				continue
			# otherwise, compute the thickness of the line and
			# draw the connecting lines
			thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
			cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
		# show the frame to our screen
		cv2.imshow(f"FPS: {FPS}, (press 'q' to stop)", frame)
		key = cv2.waitKey(1) & 0xFF
		# if the 'q' key is pressed, stop the loop
		if key == ord("q"):
			break

def exit_gracefully():
	# if we are not using a video file then we tried to open the camera before so we must stop the camera video stream
	if not args.get("video", False):
		vs.stop()
	# otherwise, release the camera
	else:
		vs.release()
	# close all windows
	cv2.destroyAllWindows()


if __name__=="__main__":
	try:
		main()
	except Exception as E:
		print(f"An error occured:")
		print(E)
	finally:
		exit_gracefully()
		print("Program ended")