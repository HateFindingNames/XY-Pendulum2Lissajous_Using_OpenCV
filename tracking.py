import cv2
import numpy as np 
import imutils
import time 
import csv
import array as ar
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from collections import deque

# plotting schalter
plots_enable = 0


# kamera objekt erstellen und einstellungen setzen
video = cv2.VideoCapture(0) # 1 im argument ist die hintere kamera
# Auflösung X, Y
video.set(3, 1440)
video.set(4, 900)

# Erzeugt das deque, buffer ist dann die länge der linie. None gibts eine "unendliche" linie, alles andere die maximale Länge
# buffer = int(128)
buffer = None
pts = deque(maxlen=buffer)
data = deque(maxlen=buffer)

#Zeitbuffer
time_stamp = deque(maxlen=buffer)

# Output Video erzeugen
frame_width = int(video.get(3))
frame_width_str = str(int(video.get(3)))
frame_height = int(video.get(4))
frame_height_str = str(int(video.get(4)))
framesize_str = str(frame_width_str + " x " + frame_height_str)
frame_center_x = frame_width / 2
frame_center_y = frame_height / 2
out = cv2.VideoWriter('laser_track.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 20, (frame_width,frame_height))

timestart = time.time()

x_array = ar.array('I', [])
y_array = ar.array('I', [])
t_array = ar.array('f', [])

# Beginn der Hauptschleife
while True:
    timeframe = time.time()
    timenow = timeframe - timestart
    timenow = round(timenow, 3)
    print(timenow)
    ret, frame = video.read()
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

	# Farbrange im HSV-Raum definieren
    lo_range = np.array([0,0,199]) #unteres limit für farbe
    hi_range = np.array([186,255,255]) #oberes limit

    mask = cv2.inRange(hsv, lo_range, hi_range) #kontrast erzeugen - weiß: in range; schwarz: nicht in range

    #gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    #ret, thresh = cv2.threshold(gray, 127, 255, 0)
    ret, thresh = cv2.threshold(mask, 127, 255, 0)

    M = cv2.moments(thresh)

    if M["m00"] != 0:
       cX = int(M["m10"] / M["m00"])
       cY = int(M["m01"] / M["m00"])
    else:
       #cX, cY = 0, 0
       cX = int(M["m10"] / (M["m00"] + 1))
       cY = int(M["m01"] / (M["m00"] + 1))
    
    center = (cX, cY) #liste der koordinaten
    center_shifted = (cX - frame_width / 2, cY - frame_height / 2)
    time_stamp = (round(cX / 5, 1), round(cY / 5, 1), timenow)
    
    pts.appendleft(center) #fuegt den aktellen koordinatensatz in das deque ein (laenge der liste = buffer)
    data.append(time_stamp)

    x_array.append(int(cX))
    y_array.append(int(cY))
    t_array.append(timenow)

    x_pltarr = x_array
    y_pltarr = y_array
    t_pltarr = t_array

    #Linien malen
    for i in range(1, len(pts)):
        if pts[i - 1] is None or pts[i] is None:
            continue
        
        thickness = int(1)
        cv2.line(frame, (pts[i - 1]), (pts[i]), (0, 0, 255), thickness)
    
    # Overlay auf die verschiedenen Fenster
    cv2.line(frame, (int(frame_center_x - 5), int(frame_center_y)), (int(frame_center_x + 5), int(frame_center_y)), (255, 0, 0), 1)
    cv2.line(frame, (int(frame_center_x), int(frame_center_y - 5)), (int(frame_center_x), int(frame_center_y + 5)), (255, 0, 0), 1)
    cv2.rectangle(frame, (280, 0), (1000, 720), (0, 255, 0), 2)
    cv2.circle(frame, (frame_width - 7, frame_height - 7), 7, (255, 0, 0), 1)    # kreis unten rechts
    cv2.putText(frame, "Laser", (cX - 25, cY - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.putText(frame, str(center_shifted), (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(frame, str(framesize_str), (0, (frame_height - 25)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)


    resized = cv2.resize(frame, (1280, 720), interpolation = cv2.INTER_AREA)
    cv2.imshow("Resized frame", resized) #öffnet fenster mit bild
    #cv2.imshow("Gray", gray)
    # cv2.imshow("Mask", mask)

    out.write(frame)

    
    if cv2.waitKey(1) == 27 or timenow >= 20.0: #ESC taste um aus schleife zu kommen (endet auch automatisch nach ende des videos)
        csvname = input("Enter .csv Name: ")
        with open("coords.csv", newline='', mode="w") as coords_csv:
            for i in range(0, len(pts)):
                csv_writer = csv.writer(coords_csv, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(pts[i])
        with open("{}.csv".format(csvname), newline='', mode="w") as timestamp_csv:
            for i in range(0, len(data)):   
                csv_writer = csv.writer(timestamp_csv, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(data[i])
            break
        print(data)

        # video aus
        video.release()
        cv2.destroyAllWindows()
        
if plots_enable is 1:

        fig_xyt = plt.figure()
        ax1 = fig_xyt.add_subplot(3, 1, 1)
        ax2 = fig_xyt.add_subplot(3, 1, 2)

        ax1.plot(t_pltarr, x_pltarr)
        ax2.plot(t_pltarr, y_pltarr)

        ax1.set_title("X-Auslenkung ueber Zeit")
        ax1.set_xlabel("Sekunden")
        ax1.set_ylabel("Pixel")
        ax2.set_title("Y-Auslenkung ueber Zeit")
        ax2.set_xlabel("Sekunden")
        ax2.set_ylabel("Pixel")

        # Achsenrange definieren
        trange_min = timenow - 30
        if trange_min < 0:
            trange_min = 0

        ax1.axis([trange_min, timenow, min(x_pltarr) - 10, max(x_pltarr) +10])
        ax2.axis([trange_min, timenow, min(y_pltarr) - 10, max(y_pltarr) +10])

        plt.subplots_adjust(hspace=2)

        plt.show()