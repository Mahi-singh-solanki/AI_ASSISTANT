import time
import math
import cv2 as cv
import numpy as np
import mediapipe as mp
from pyautogui import size
from pynput.mouse import Controller, Button
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from rag.globals import gesture_event








def finger_up(hand, tip, pip):
    return hand[tip].y < hand[pip].y

def thumbs_up(hand,tip,pip):
    return hand[tip].x < hand[pip].x


def gesture_control():
    FRAME_REDUCTION = 100

    LEFT_CLICK_THRESHOLD = 0.04
    RIGHT_CLICK_THRESHOLD = 0.04

    CLICK_COOLDOWN = 0.4

    MAX_MISSING_FRAMES = 5


    screen_w, screen_h = size()


    mouse = Controller()


    base_options = python.BaseOptions(
    model_asset_path=rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\hand_landmarker.task"
    )

    options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1
    )

    landmarker = vision.HandLandmarker.create_from_options(
    options
    )


    cap = cv.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("Camera not available")



    current_x = 0
    current_y = 0

    last_left_click = 0
    last_right_click = 0

    prev_scroll_y = None

    missing_frames = 0
    while True:
        gesture_event.wait()
        ret, frame = cap.read()

        if not ret:
            break

        frame = cv.flip(frame, 1)

        h, w, _ = frame.shape

        rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
        )

        result = landmarker.detect(mp_image)

        if not result.hand_landmarks:

            missing_frames += 1

            if missing_frames > MAX_MISSING_FRAMES:
                prev_scroll_y = None

            if cv.waitKey(1) == ord("q"):
                break

            continue

        missing_frames = 0

        hand = result.hand_landmarks[0]

        thumb = hand[4]
        index_tip = hand[6]
        middle_tip = hand[12]
        ring_tip=hand[16]
        thumb_up=thumbs_up(hand,4,3)
        index_up = finger_up(hand, 8, 6)
        middle_up = finger_up(hand, 12, 10)
        ring_up = finger_up(hand, 16, 14)
        pinky_up = finger_up(hand, 20, 18)
        finger_x = int(index_tip.x * w)
        finger_y = int(index_tip.y * h)
        # cv.putText(rgb,f"{thumb_up},{index_up},{middle_up},{ring_up},{pinky_up}",(20,60), cv.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2,cv.LINE_AA)
        target_x = np.interp(
        finger_x,
        (FRAME_REDUCTION, w - FRAME_REDUCTION),
        (0, screen_w)
        )

        target_y = np.interp(
        finger_y,
        (FRAME_REDUCTION, h - FRAME_REDUCTION),
        (0, screen_h)
        )


        movement_distance = math.hypot(
        target_x - current_x,
        target_y - current_y
        )

        smooth = 3 if movement_distance > 300 else 7

        current_x += (target_x - current_x) / smooth
        current_y += (target_y - current_y) / smooth


        left_distance = math.hypot(
        thumb.x - index_tip.x,
        thumb.y - index_tip.y
        )

        right_distance = math.hypot(
        thumb.x - ring_tip.x,
        thumb.y - ring_tip.y
        )

        move_mode = (
        index_up  and
        not middle_up and
        not ring_up and
        not pinky_up
        )
        scroll_down=(
        not index_up and not middle_up and not ring_up and not pinky_up
        )
        scroll_up=(index_up and middle_up and ring_up and pinky_up)
        if scroll_down:
            cv.putText(rgb,"Scroll down",(20,60), cv.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2,cv.LINE_AA)
            mouse.  scroll(0,-0.5)
        if scroll_up:
            cv.putText(rgb,"Scroll up",(20,60), cv.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2,cv.LINE_AA)
            mouse.scroll(0,0.5)

        left_click_mode = (
        left_distance < LEFT_CLICK_THRESHOLD
        )

        right_click_mode = (
        right_distance < RIGHT_CLICK_THRESHOLD
        )


        if move_mode and not left_click_mode and not scroll_down and not scroll_up:
            mouse.position = (
            int(current_x),
            int(current_y)
            )

        now = time.time()

        if (
        left_click_mode and not scroll_down and not scroll_up and move_mode and 
        now - last_left_click > CLICK_COOLDOWN
        ):
            cv.putText(rgb,"left click",(20,60), cv.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2,cv.LINE_AA)
            mouse.click(Button.left)
            last_left_click = now

        if (
        right_click_mode and not scroll_down and not scroll_up and move_mode and
        now - last_right_click > CLICK_COOLDOWN
        ):
            cv.putText(rgb,"right click",(20,60), cv.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2,cv.LINE_AA)
            mouse.click(Button.right)
            last_right_click = now


        # cv.imshow('frame',frame)
        if cv.waitKey(1) == ord("q"):
            break

    cap.release()
    cv.destroyAllWindows()