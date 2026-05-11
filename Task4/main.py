import matplotlib.pyplot as plt;
import numpy as np
import pandas as pd;
import os;
import math;
import tkinter as tk;

if os.path.exists("out.txt"):
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
