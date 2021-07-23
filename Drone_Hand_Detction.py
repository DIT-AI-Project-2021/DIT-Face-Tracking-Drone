##############################
# 작업 중인 소스(김종현 교수)
##############################

import cv2
import mediapipe as mp
from djitellopy import Tello
import time

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
gesture = ""
##################################
tipIds = [4, 8, 12, 16, 20]
state = None
Gesture = None
wCam, hCam = 720, 640
############################

tello = Tello()
tello.connect()
print(tello.get_battery())
# tello.streamoff()
tello.streamon()
# time.sleep(0.5)
tello.takeoff()
tello.move_up(40)

frame_read = tello.get_frame_read()

def fingerPosition(image, handNo=0):
    lmList = []
    if results.multi_hand_landmarks:
        myHand = results.multi_hand_landmarks[handNo]
        for id, lm in enumerate(myHand.landmark):
            # print(id,lm)
            h, w, c = image.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            lmList.append([id, cx, cy])
    return lmList

# For webcam input:
# cap = cv2.VideoCapture(0)
# cap.set(3, wCam)
# cap.set(4, hCam)
# frame_read.cap.set(3, wCam)
# frame_read.cap.set(4, hCam)

with mp_hands.Hands(
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8) as hands:

  while True:
    image = frame_read.frame
    image = cv2.resize(image, (640/2, 480/2))

    # if not success:
    #     print("Ignoring empty camera frame.")
    #   # If loading a video, use 'break' instead of 'continue'.
    #     continue
    # Flip the image horizontally for a later selfie-view display, and convert
    # the BGR image to RGB.
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    lmList = fingerPosition(image)
    #print(lmList)

    # if len(lmList) != 0:
    if lmList :
        fingers = []

        # Thumb
        if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
            fingers.append(0)
        else:
            fingers.append(1)

        # 4 Fingers
        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
            # if (lmList[tipIds[id]][2] > lmList[tipIds[id] - 2][2]):
            #     fingers.append(0)

        print(fingers)

        # totalFingers = fingers.count(1)
        # print(totalFingers)
        #print(lmList[9][2])

        if fingers == [1,1,1,1,1]:
            gesture = "STOP"  # Open
            print(gesture)
            # tello.send_rc_control(0, 0, 0)
        elif fingers == [0,1,0,0,0]:  # Index
            gesture = "UP"
            print(gesture)
            tello.move_up(20)
        elif fingers == [0,0,0,0,0]: # Fist
            gesture = "LAND"
            print(gesture)
            tello.move_forward(30)
        # elif fingers == [0,0,1,0,0]:
        #     gesture = "Middle"
        #     print(gesture)
        elif fingers == [1,1,0,0,1]: # Spider
            gesture = "FLIP"
            tello.flip_forward()
            print(gesture)
        elif fingers == [0,1,1,0,0]: # Victory
            gesture = "DOWN"
            tello.move_down(20)
            print(gesture)
        elif fingers == [0,0,0,0,1]: # Pinky
            gesture = "LEFT"
            tello.move_left(40)
            print(gesture)
        elif fingers == [1,0,0,0,0]: # Tumb
            gesture = "RIGHT"
            tello.move_right(40)
            print(gesture)

    cv2.putText(image, str("AI Drone Gesture"), (10,40), cv2.FONT_HERSHEY_SIMPLEX,
                  1, (255, 0, 0), 2)
    cv2.imshow("Media Controller", image)
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
  cv2.destroyAllWindows()
