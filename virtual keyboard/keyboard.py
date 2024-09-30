import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import os
import pyautogui
import time
from pynput.keyboard import Controller

# Suppress TensorFlow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8, maxHands=1)

# Define the virtual keyboard layout
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]

def draw_keyboard(img, button_list):
    for button in button_list:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, button.text, (x + 20, y + 65),
                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
    return img

class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text

button_list = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        button_list.append(Button([100 * j + 50, 100 * i + 50], key))

last_click_time = 0
click_delay = 0.5  # Delay between clicks in seconds

keyboard = Controller()
text = ""
max_text_length = 20  # Maximum number of characters to display

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, draw=True)
    img = draw_keyboard(img, button_list)

    if hands:
        hand = hands[0]
        lmList = hand["lmList"]
        index_finger_tip = lmList[8]  # Index finger tip

        for button in button_list:
            x, y = button.pos
            w, h = button.size

            if x < index_finger_tip[0] < x + w and y < index_finger_tip[1] < y + h:
                cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                cv2.putText(img, button.text, (x + 20, y + 65),
                            cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                
                # Check if the index finger is lowered (button press)
                if lmList[8][1] > lmList[5][1]:  # Compare y-coordinates of tip and base of index finger
                    current_time = time.time()
                    if current_time - last_click_time > click_delay:
                        cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                        cv2.putText(img, button.text, (x + 20, y + 65),
                                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                        print(f"Clicked: {button.text}")
                        pyautogui.press(button.text.lower())
                        # Update the text variable
                        text += button.text
                        if len(text) > max_text_length:
                            text = text[-max_text_length:]
                        last_click_time = current_time

    # Display the text below the keyboard
    cv2.rectangle(img, (50, 350), (1230, 450), (255, 255, 255), cv2.FILLED)
    cv2.putText(img, text, (60, 425),
                cv2.FONT_HERSHEY_PLAIN, 5, (0, 0, 0), 5)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
