import matplotlib.pyplot as plt;
import numpy as np
import pandas as pd;
import os;
import math;
import tkinter as tk;
import re

'''if os.path.exists("out.txt"):
    with open("out.txt","r") as f:
        if os.path.exists("out.csv"):
            os.remove("out.csv");
            print("meow");
        with open("out.csv","w") as nf:
            for line in f:
                if line.startswith("--- "):
                    continue;
                nf.write(line);
        TimeTempData = pd.read_csv("out.csv"); # for every line in f, yield the line if it doesnt start with "--- "
else :
    print("out.txt doesnt exist please connect the arduino board and run the main.cpp with `pio device monitor --baud 115200 > out.txt` to generate the file")
'''




## use the sample data taken from the dynamic arduino code and stitch together time stamps to continously increase rather than jump from 59 seconds to 0.0 seconds. 
## output that data to out2.csv and import it back into pandas

OUTPUT_CSV = "out2.csv"

continuous_data = []

if os.path.exists("samples.txt"):

    collecting = False

    global_offset = 0.0

    prev_local_time = None
    prev_dt = 0.0

    last_continuous_time = 0.0

    with open("samples.txt", "r") as f:

        for raw_line in f:

            line = raw_line.strip()

            # start of time-domain table
            if line.startswith("Time") and "Temperature" in line:

                collecting = True
                prev_local_time = None
                continue

            # end of table
            if line.startswith("Dominant Frequency"):

                collecting = False

                # next block starts after previous sample spacing
                global_offset = last_continuous_time + prev_dt

                continue

            if not collecting:
                continue

            match = re.match(
                r'^\s*([\d.]+),\s*([\d.]+)',
                line
            )

            if match:

                local_time = float(match.group(1))
                temp = float(match.group(2))

                if prev_local_time is not None:
                    prev_dt = local_time - prev_local_time

                continuous_time = global_offset + local_time

                if continuous_time > 180.0: # up to 3 min
                    break

                last_continuous_time = continuous_time

                continuous_data.append([
                    continuous_time,
                    temp
                ])

                prev_local_time = local_time

    df = pd.DataFrame(
        continuous_data,
        columns=["Time(s)", "Temperature(oC)"]
    )

    df.to_csv(OUTPUT_CSV, index=False)

    TimeTempData = pd.read_csv(OUTPUT_CSV)

    print(TimeTempData)

else:
    print("out.txt does not exist")

print(TimeTempData);










def dft(signal, fs):
    N = len(signal)

    X = np.zeros(N, dtype=complex)
    freqs = np.zeros(N)

    for k in range(N):
        for n in range(N):
            X[k] += signal[n] * np.exp(-2j * np.pi * k * n / N)

        freqs[k] = k * fs / N

    magnitude = np.abs(X)

    return np.column_stack((freqs[:N//2], magnitude[:N//2])) # N//2 to ignore the mirrored frequencies


def moving_average(data, window_size):
    result = [];

    for i in range(len(data)):
        start = max(0, i - window_size + 1);
        window = data[start:i+1];
        result.append(sum(window) / len(window));

    return result;

def time_temperatureplot1():
    
    plt.plot(TimeTempData["Time(s)"], TimeTempData["Temperature(oC)"]);
    plt.xlabel("Time (s)");
    plt.ylabel("Temperature (°C)");
    plt.title("Plot 1: Temperature vs Time");
    plt.show();

def Magn_FreqPlot2():
    
    dftarray = dft(TimeTempData["Temperature(oC)"], 1/(TimeTempData["Time(s)"][1]+TimeTempData["Time(s)"][0]) )
    dftarray = dftarray[1:] # exclude k=0
    print(dftarray);
    plt.stem(dftarray[:, 0], dftarray[:, 1], basefmt=" ");
    plt.xlabel("Frequency (Hz)");
    plt.ylabel("Magnitude");
    plt.title("Plot 2: Magnitude vs Frequency");
    plt.show()

def Smoothed_TimeTempPlot3():
    
    smoothed = moving_average(TimeTempData["Temperature(oC)"], 7); #smoothed at window size 7
    plt.plot(TimeTempData["Time(s)"], TimeTempData["Temperature(oC)"], label="RAW");
    plt.plot(TimeTempData["Time(s)"], smoothed, label="SMOOTHED");
    plt.xlabel("Time (s)");
    plt.ylabel("Temperature (°C)");
    plt.legend();
    plt.title("Plot 3: Smoothed Temperature vs Time");
    plt.show();

def Histogram_TempPlot4():
    
    plt.hist(TimeTempData["Temperature(oC)"], bins=20);
    plt.xlabel("Temperature (°C)");
    plt.ylabel("Count");
    plt.title("Plot 4: Histogram of Temperature Readings");
    plt.show();

def rate_Plot5():
    
    rate = []
    for i in range(1, len(TimeTempData["Temperature(oC)"])):
        dT = TimeTempData["Temperature(oC)"][i]- TimeTempData["Temperature(oC)"][i-1];
        dt = TimeTempData["Time(s)"][i] - TimeTempData["Time(s)"][i-1];
        rate.append(dT/dt);
    #print(rate);
    plt.plot(TimeTempData["Time(s)"][1:], rate);
    plt.xlabel("Time")
    plt.ylabel("Change (dy)")
    plt.title("Plot 5: Temperature Change Rate vs Time");
    plt.show();

print("tkinter")

## error note
'''Authorization required, but no authorization protocol specified

Authorization required, but no authorization protocol specified

Traceback (most recent call last):
  File "/home/CrackHead/Documents/F533068_25WSA032_Coursework/Task4/main.py", line 199, in <module>
    root = tk.Tk();
  File "/usr/lib/python3.14/tkinter/__init__.py", line 2484, in __init__
    self.tk = _tkinter.create(screenName, baseName, className, interactive, wantobjects, useTk, sync, use)
              ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_tkinter.TclError: couldn't connect to display ":0" '''



root = tk.Tk();
tk.Button(root, text="Plot 1: Temperature vs Time", command=lambda:[plt.close('all'),time_temperatureplot1()]).pack();
tk.Button(root, text="Plot 2: Magnitude vs Frequency", command=lambda:[plt.close('all'),Magn_FreqPlot2()]).pack();
tk.Button(root, text="Plot 3: Smoothed Temperature vs Time", command=lambda:[plt.close('all'),Smoothed_TimeTempPlot3()]).pack();
tk.Button(root, text="Plot 4: Histogram of Temperature Readings", command=lambda:[plt.close('all'),Histogram_TempPlot4()]).pack();
tk.Button(root, text="Plot 5: Temperature Change Rate vs Time", command=lambda:[plt.close('all'),rate_Plot5()]).pack();

root.mainloop();

#rate_Plot5();
#Smoothed_TimeTempPlot3()
#Magn_FreqPlot2()
#print(dft(TimeTempData["Temperature(oC)"], 1 ))
