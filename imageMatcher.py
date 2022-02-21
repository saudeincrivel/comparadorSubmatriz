from turtle import onscreenclick
from wrapper.wrapper import *
import numpy as np
import pyautogui
import cv2 as cv
 


def printscreen():
    image = pyautogui.screenshot()
    image = cv.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    image.save("./iamges/screnshot.png");
    return None;


def matchImages(screen, subscreen):
    imageScreen = cv.imread(screen);
    imageSubscreen = cv.imread(subscreen);

    gray1 = cv.cvtColor(imageScreen, cv.COLOR_BGR2GRAY);
    gray2 = cv.cvtColor(imageSubscreen, cv.COLOR_BGR2GRAY);

    return comparator(gray1, gray2);


def main():
    # EXAMPLE:
    x = matchImages("BIG_IMAGE_PATH", "SMALL_IMAGE_PATH");
    print("Occurrences :");
    print ( x);
    return None;
 

# main();