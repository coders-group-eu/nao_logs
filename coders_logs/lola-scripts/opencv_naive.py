import cv2
import numpy as np
import time

# Open the device at the ID 0
# Use the camera ID based on
# /dev/videoID needed
cap = cv2.VideoCapture(0)

#Check if camera was opened correctly
if not (cap.isOpened()):
    print("Could not open video device")
    
# wait a bit before reading the first frame
time.sleep(2)

# read one frame
ret, frame = cap.read()

# (480, 640, 3)
# the frame is in RGB format
print(frame.shape)

# save the image to file
cv2.imwrite("outputImage.png", frame)

# close the capture
cap.release()