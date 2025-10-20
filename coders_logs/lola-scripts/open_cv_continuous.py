import cv2
import time

# Open the device at the ID 0
# Use the camera ID based on
# /dev/videoID needed
cap = cv2.VideoCapture(0)

#Check if camera was opened correctly
if not (cap.isOpened()):
    print("Could not open video device")

# wait a bit until the camera is initialized
time.sleep(3)

#Set the resolution
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)


# Capture frame-by-frame
frameNr = 0
timestamp_old = 0
while frameNr < 100:
    ret, frame = cap.read()

    timestamp = 0
    if ret:
        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)
        
    # save
    #cv2.imwrite("outputImage.jpg", frame)

    print(frameNr, ret, timestamp-timestamp_old)
    frameNr += 1
    timestamp_old = timestamp

# When everything done, release the capture
cap.release()