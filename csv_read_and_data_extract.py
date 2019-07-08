import numpy as np
import csv
import matplotlib
import matplotlib.pyplot as plt
import array as ar
from scipy import optimize as opt
from collections import deque
from scipy.signal import find_peaks
from matplotlib.offsetbox import AnchoredText
from scipy.optimize import curve_fit

plots_enable = 0

# Initialisierung der Variablen, deques usw.
Ydek = 0
Xdek = 0
Ygamma = 0
Xgamma = 0
xval = deque(maxlen=None)
yval = deque(maxlen=None)
time = ar.array('f', [])
times = deque(maxlen=None)
Ypeak_val = deque(maxlen=None)
Xpeak_val = deque(maxlen=None)
Ydamp_func = deque(maxlen=None)
Xdamp_func = deque(maxlen=None)
Xtime_index = deque(maxlen=None)
Ytime_index = deque(maxlen=None)
i = 0

# Die Daten aus der .csv extrahieren und in jeweilige deques fuer X und Y schreiben
with open('data10_45deg.csv', newline='') as csvfile:
    data = csv.reader(csvfile, delimiter=',')
    for row in data:
        xval.append(float(row[0]) - 128)
        yval.append(float(row[1]) - 72)
        times.append(float(row[2]))
        # i += 1

# Wir suchen die Peaks in X und Y und schreiben die entsprechenden indices in jeweilige deques
Ypeak_index, _ = find_peaks(yval, distance=8, height=0)
Xpeak_index, _ = find_peaks(xval, distance=8, height=0)

for i, j in enumerate(Xpeak_index):
    Xtime_index.append(times[j])

for i, j in enumerate(Ypeak_index):
    Ytime_index.append(times[j])


# Ein neues deque erstellen mit den X-Y Peakwerten an den Zeit-Koordinaten
for i, j in enumerate(Ypeak_index):
    Ypeak_val.append(yval[j])

for i, j in enumerate(Xpeak_index):
    Xpeak_val.append(xval[j])

# Gemitteltes delta_t der Peaks in X und Y ermitteln (Periodendauer T)
n_dist = 10
dist_start = 5
Ydistances = 0
Xdistances = 0

print("X Peaks")
for i in range(len(Xpeak_index)):
    print(round(xval[Xpeak_index[i]], 3))

print("Y Peaks")
for i in range(len(Ypeak_index)):
    print(round(yval[Ypeak_index[i]], 3))

for i in range(dist_start, n_dist):
    Ydistances += times[Ypeak_index[i + 1]] - times[Ypeak_index[i]]
    Xdistances += times[Xpeak_index[i + 1]] - times[Xpeak_index[i]]

Yav_dist = Ydistances / (n_dist - dist_start)
Xav_dist = Xdistances / (n_dist - dist_start)

time = list()
for i in range(0, len(Ypeak_index)):
    time.append(yval[Ypeak_index[i]]) 

# Aus dem gemittelten delta_t die Frequenz fuer X und Y ermitteln
Yomega = (2 * np.pi) / Yav_dist
Xomega = (2 * np.pi) / Xav_dist
print("Omega in X ist: ", round(Xomega, 4), "\nOmega in Y ist: ", round(Yomega, 4))
print("Periodendauer in X ist: ", round(Xav_dist, 4), "\nPeriodendauer in Y ist: ", round(Yav_dist, 4))
print("Frequenz in X ist: ", 1 / round(Xav_dist, 4), "\nFrequenz in Y ist: ", 1 / round(Yav_dist, 4))
print("Anzahl Perioden in X ist: ", len(Xpeak_index))
print("Anzahl Perioden in Y ist: ", len(Ypeak_index))

# Die Graphen plotten
if plots_enable is 1:
    
    fig, ax = plt.subplots()
    ax.grid()
    ax.set(xlabel='Zeit / Sekunden', ylabel='Amplitude / mm')
    plt.plot(times, xval, 'b-', label='Amplitude')
    plt.plot(Xtime_index, Xpeak_val, 'yx', label='Peaks')
    plt.legend(bbox_to_anchor=(0.99, 0.99), loc='upper right', borderaxespad=0.)

    text_box = AnchoredText(str('T_x = ' + str(round(Xav_dist, 2)) + ' s\nw_x = ' + str(round(Xomega, 4))), frameon=True, loc=4, pad=0.5)
    plt.setp(text_box.patch, facecolor='white', alpha=0.5)
    ax.add_artist(text_box)

    plt.show()

    fig, ax = plt.subplots()
    ax.grid()
    ax.set(xlabel='Zeit / Sekunden', ylabel='Amplitude / mm')
    ## plt.plot(times, Ydamp_func, 'r--', label='Einhuellende')
    ## plt.plot(time, damp(time, popt[0], popt[1]), 'r-')
    plt.plot(times, yval, 'b-', label='Amplitude')
    plt.plot(Ytime_index, Ypeak_val, 'yx', label='Peaks')
    plt.legend(bbox_to_anchor=(0.99, 0.99), loc='upper right', borderaxespad=0.)
    ## plt.text(max(times) - 100, min(yval), str('f=' + str(round(freq, 4)) + ' Hz'), horizontalalignment='left', fontsize=10)
    ## plt.text(max(times) - 100, min(yval) + 20, str('gamma=' + str(round(gamma, 4)) + ' kg*m/s'), horizontalalignment='left', fontsize=10)

    text_box = AnchoredText(str('T_y = ' + str(round(Yav_dist, 2)) + ' s\nw_y = ' + str(round(Yomega, 4))), frameon=True, loc=4, pad=0.5)
    plt.setp(text_box.patch, facecolor='white', alpha=0.5)
    ax.add_artist(text_box)

    plt.show()