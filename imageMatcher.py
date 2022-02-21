import wrapper.wrapper as wrapper
import numpy as np
import pyautogui
import cv2 as cv
 

def matchImages(screen, subscreen):
    imageScreen = cv.imread(screen);
    imageSubscreen = cv.imread(subscreen);

    gray1 = cv.cvtColor(imageScreen, cv.COLOR_BGR2GRAY);
    gray2 = cv.cvtColor(imageSubscreen, cv.COLOR_BGR2GRAY);

    return wrapper.comparator(gray1, gray2);

