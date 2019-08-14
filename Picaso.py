# Picaso V2.0 Work in progress.
# - Install OpenCV, pynput, and pillow (pip install opencv-python pynput pillow).
# - Do not touch or move the mouse while running.
# - To terminate, press ESC.

import cv2
import os
import time
import numpy as np
from PIL import ImageGrab
from itertools import combinations
from collections import Counter

from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController

from pynput.keyboard import Listener

mouse = MouseController()
keyboard = KeyboardController()

# Start ms paint maximized using cmd commands.
os.system("Start /max mspaint")
# Wait for ms paint to actually start before spamming left click.
time.sleep(1)
# Drawing top left starting point pixel coordinates.
# Tweak this based on monitor resolution
START_POS = (200, 200)
# Set mouse position.
mouse.position = START_POS


def on_press(key):
    # print("{} pressed".format(key))
    if key == Key.esc:
        os._exit(1)


def find_edit_button():
    edit_colors_button = cv2.imread("templates/edit_colors_button.png")
    h, w, c = edit_colors_button.shape

    # Grab an image of the application.
    img = ImageGrab.grab(bbox=None)
    img = np.array(img)
    # Convert to standard RGB.
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Match to template edit button image.
    res = cv2.matchTemplate(img, edit_colors_button, cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = min_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)

    # Calculate coordinates of button center.
    center = ((top_left[0] + bottom_right[0]) / 2, (top_left[1] + bottom_right[1]) / 2)
    return center


def find_fields():
    field = cv2.imread("templates/color_field.png")
    ok_button = cv2.imread("templates/ok_button.png")
    h, w, c = field.shape

    # Grab an image of the application.
    img = ImageGrab.grab(bbox=None)
    img = np.array(img)
    # Convert to standard RGB.
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Match to template field image.
    res = cv2.matchTemplate(img, field, cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = min_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)

    # Calculate coordinates of fields, assuming constant distance between boxes.
    red = ((top_left[0] + bottom_right[0]) / 2 + 25, (top_left[1] + bottom_right[1]) / 2)
    blue = (red[0], red[1] + 25)
    green = (red[0], red[1] + 50)

    # Match to template OK button.
    res = cv2.matchTemplate(img, ok_button, cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = min_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    button = ((top_left[0] + bottom_right[0]) / 2, (top_left[1] + bottom_right[1]) / 2)

    ret = {
        "red": red,
        "blue": blue,
        "green": green,
        "ok": button
    }
    # cv2.rectangle(img, top_left, bottom_right, 255, 2)
    return ret


def clear_field():
    for i in range(3):
        time.sleep(0.05)
        keyboard.press(Key.backspace)
        time.sleep(0.05)
        keyboard.press(Key.delete)


def update_RGB(r, g, b):
    time.sleep(1)
    # SELECT COLOR Button pixel coordinates
    mouse.position = find_edit_button()
    mouse.click(Button.left, 1)
    time.sleep(0.5)
    fields = find_fields()

    # SELECT COLOR\RED Button pixel coordinates
    mouse.position = fields["red"]
    mouse.click(Button.left, 1)
    clear_field()
    # Enter the max rgb value (grayThresh) in COLOR\RED
    keyboard.type(str(r))

    # SELECT COLOR\BLUE Button pixel coordinates
    mouse.position = fields["blue"]
    mouse.click(Button.left, 1)
    clear_field()
    # Enter the max rgb value (grayThresh) in COLOR\BLUE
    keyboard.type(str(g))

    # SELECT COLOR\GREEN Button pixel coordinates
    mouse.position = fields["green"]
    mouse.click(Button.left, 1)
    clear_field()
    # Enter the max rgb value (grayThresh) in COLOR\GREEN
    keyboard.type(str(b))

    time.sleep(0.1)
    # OK Button pixel coordinates
    mouse.position = fields["ok"]
    # Clicks it, returns to canvas
    mouse.click(Button.left, 1)
    # Reseting mouse position to starting position
    mouse.position = START_POS
    time.sleep(0.5)


def draw_image(imgPath):
    img = cv2.imread(imgPath)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    height, width, channels = img.shape

    # Ignore color if its less than X percent of image.
    pixel_tolerance = int((height * width) * .001)
    all_rgb_codes = img.reshape(-1, img.shape[-1])
    unique_rgbs, counts = np.unique(all_rgb_codes, axis=0, return_counts=True)

    # print("Total Number of RGB Iterations: {}".format(len(unique_rgbs)))
    # print("Pixel Tolerance: {}".format(pixel_tolerance))
    for ((r, g, b), c) in zip(unique_rgbs, counts):
        if c < pixel_tolerance:
            continue
        elif r == 255 and g == 255 and b == 255:
            continue

        print("R: {0}, G: {1}, B: {2}".format(r, g, b))
        # print("Number of Pixels: {}".format(num_pixels))
        update_RGB(r, g, b)

        for i in range(len(img)):
            mouse.position = (START_POS[0], mouse.position[1])
            mouse.move(0, 1)
            for j in range(len(img[i])):
                if list(img[i, j]) == [r, g, b]:
                    # Click (paint)
                    mouse.click(Button.left, 1)
                    # Speed, faster more errors
                    time.sleep(0.00001)
                mouse.move(1, 0)

# Keyboard termination, ESC
listener = Listener(on_press=on_press)
listener.start()
time.sleep(10)
draw_image("Images/mario.png")
