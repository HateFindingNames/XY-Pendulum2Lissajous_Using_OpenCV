import cv2
import numpy as np 
import imutils
import argparse
import time 
import csv
from collections import deque

# kamera objekt erstellen und einstellungen setzen
video = cv2.VideoCapture(1) # 1 im argument ist die hintere kamera
# Auflösung X, Y
video.set(3, 1440)
video.set(4, 900)

start = time.time()

num_frames = 120

for i in range(0, num_frames):
    ret, frame = video.read()

end = time.time()

seconds = end - start

fps = num_frames / seconds
ftime = seconds / num_frames

print("Ungefaehre fps    : {0}".format(fps))
print("Ungefähre Frametime  : {0}".format(ftime))

video.release()