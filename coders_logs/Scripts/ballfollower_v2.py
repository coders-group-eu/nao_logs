import cv2
import time
import numpy as np
import math
from Nao import Nao
import time
import shutil
import os


def detect_ball(image):
    # This function outputs the position of the center of the ball,
    # as estimated by the centroid of the closed edges it finds,
    # which usually corresponds to the black pentagons on the ball.
    
    src = cv2.imread(image, cv2.IMREAD_COLOR)

    #Transform source image to gray if it is not already
    if len(src.shape) != 2:
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    else:
        gray = src

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    blurred = cv2.bilateralFilter(gray, 5, 175, 175)

    edges = cv2.Canny(blurred, 50, 150)
    contours, hierarchy = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Separate closed and open contours
    closed_contours = []
    open_contours = []

    for i, contour in enumerate(contours):
        # Check if contour has a parent
        if hierarchy[0][i][3] == -1:
            closed_contours.append(contour)
        else:
            area = cv2.contourArea(contour)
            if area > 350:
                open_contours.append(contour)
    
    median = [0,0]
    M = {"m00": 0}

    for contour in open_contours:
        M = cv2.moments(contour)
        
        # Calculate centroid
        if M["m00"] != 0:  # Ensure that the contour has area
            centroid_x = int(M["m10"] / M["m00"])
            centroid_y = int(M["m01"] / M["m00"])
            median[0] += centroid_x
            median[1] += centroid_y
        else:
            centroid_x, centroid_y = 0, 0  # Default to (0, 0) if the contour has no area
            print("No Ball Detected")
        
    if len(open_contours) != 0:
        # median of the centroids
        median = [x / len(open_contours) for x in median]

    return median

def corrupted(image):
    # This function checks for corrupted images: sometimes the camera
    # start only producing green images, and needs to be reset.
    # We detect it using variance among pixel values
    src = cv2.imread(image, cv2.IMREAD_COLOR)

    #Transform source image to gray if it is not already
    if len(src.shape) != 2:
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    else:
        gray = src

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    if np.var(blurred) < 100:
        return True
    
    return False

    

# Open the device at the ID 0
# Use the camera ID based on
# /dev/videoID needed
cap = cv2.VideoCapture(0)

#Check if camera was opened correctly
if not (cap.isOpened()):
    print("Could not open video device")

# wait a bit until the camera is initialized
time.sleep(3)


# Destroy the previous temp directory and create a new, empty one
current_directory = os.getcwd()
final_directory = os.path.join(current_directory, r"temp")
shutil.rmtree(final_directory)
if not os.path.exists(final_directory):
    os.makedirs(final_directory)


nao = Nao()
stiffness = 0.0

for name in nao.joint_names:
    nao.jointStiffnessData[name] = 0.0

nao.jointStiffnessData["HeadYaw"] = 0.5
nao.jointStiffnessData["HeadPitch"] = 0.5


# variables to influence movement
current_pitch = 0
current_yaw = 0
movement_speed = 0.01

while nao.update():

    # frame is the image
    ret, frame = cap.read()
    
    filename = "temp/output.jpg" #+ str(i) + ".jpg"

    # save the image in temp
    cv2.imwrite(filename, frame)
    img = cv2.imread(filename)

    # if the images are corrupted (too low variance among pixels)
    if corrupted(filename):
        print("Resetting the Camera...")
        cap.release()
        time.sleep(2)
        cap = cv2.VideoCapture(0)
        time.sleep(3)
        ret, frame = cap.read()

    # detect the ball position
    ball_position = detect_ball(filename)
    print(ball_position)



    if ball_position != [0,0]:

        # compare the center of the ball with the center of the image, with a 5 pixel margin
        if (ball_position[0]) < ((img.shape[1] / 2) - 5):
            current_yaw += movement_speed
            if current_yaw > 0.99:
                current_yaw = 0.99
            nao.jointMotorData["HeadYaw"] = current_yaw
            print("Ball to the left")
        
        
        elif (ball_position[0]) > ((img.shape[1] / 2) + 5):
            current_yaw -= movement_speed
            if current_yaw < -0.99:
                current_yaw = -0.99
            nao.jointMotorData["HeadYaw"] = current_yaw
            print("Ball to the right")


        if (ball_position[1]) > ((img.shape[0] / 2) + 5):
            current_pitch += movement_speed
            if current_pitch > 0.99:
                current_pitch = 0.99
            nao.jointMotorData["HeadPitch"] = current_pitch
            print("Ball down")

        elif (ball_position[1]) < ((img.shape[0] / 2) - 5):
            current_pitch -= movement_speed
            if current_pitch < -0.99:
                current_pitch = -0.99
            nao.jointMotorData["HeadPitch"] = current_pitch
            print("Ball up")



# When everything done, release the capture
cap.release()