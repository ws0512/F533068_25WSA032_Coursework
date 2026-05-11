src code: [%PROJECT_ROOT%/Task4/src/main.cpp](./src/main.cpp)

# Plot 1: Temperature vs Time
## Picture

![Plot1](./PLOT1_TemperatureVSTime.png)

this picture shows the graph produced by matplotlib using python

## What does this graph show?
- This graph shows that the temperature over time has not been stable, it increases rapidly after ~50 seconds and continues changing for the rest of the duration of the test.
- A significantly large spike in the temperature appears at ~160 seconds quickly rising from 25.5oC to just below 28oC before dropping down to 26oC. 
- There appears to be a very faint amount of noise within the stable part of the temperature (0-50 seconds) where the temperature changes to a step higher twice and once lower for a single sample. 
- When the sensor is cooling at 100 seconds it creates a shape that resembles a staircase.


---
# Plot 2: Magnitude vs Frequency

![Plot2](./PLOT2_MagnitudeVSFrequency.png)

this picture shows the graph produced by matplotlib using python for the task requiring to graph magnitude vs frequency.

## What does this graph show?
This graph shows that the sample used is very low-frequency dominated, and that there are lots of low-frequency oscillations. The lackthereof high-frequency magnitude in the graph, shows visually that there is no high-frequency noise in this sample. The dominant frequency for this sample is around 0.055Hz.

---
# Plot 3: Smoothed Temperature vs Time

![Plot3](./PLOT3_SmoothedTemperatureVSTime.png)

this picture shows the graph produced by matplotlib using python for the task requiring to graph both the raw and smoothed temperature vs time samples.

## What does this graph show?
The smoothing of the grapth makes the change in temperature appear a little later but it shows that any large spikes in the temperature curve out the peak into a more stable looking temperature. the trend still shows an increase in temperature over the duration of the sampling time. 

---
# Plot 4: Histogram of Temperature Readings

![Plot4](./PLOT4_HistogramOfTemperatureReadings.png)

this picture shows the graph produced by matplotlib using python for the task requiring to graph a histogram of the temperature values.

## What does this graph show?
- the most common temperature value was 23oC which was throughout the range 0-50 seconds
- A large cluster of temperature values fell withing 24oC and 26oC.

---
# Discussion of Findings
## Time-domain behaviour
- The temperature was stable at the beginning of the 3 minutes. Then it risen as expected. 
- The initial rise in temperature occured at around 50 seconds. 
- The signal did not appear to be significantly noisy  only appearing to change around +-0.2 degrees 3 times in the beginnning. 

## Frequency-domain behaviour
- The component with the highest frequency component appears to be component 1 ~ 0.056Hz.
- The graph shows that it was low-frequency dominant.
- The dft shows that there is only low frequency patters that it recognised. 
- As the magnitude for higher-frequency was almost 0, this indicates that there was almost no high-frequency noise in the sample used.

## System Behaviour 
- I wasnt aware that you needed to use the code from task 2 to sample the data, but that you needed a simple code to measure the temperature and send it to the PC. :(

## Data quality
- the recording duration could have been extended to ensure that the data is more accurate, but also there would be no issue with storing the data. 
- I believe that that rate of sampling was appropriate, to ensure that it wasnt too frequent that it would flood the UART with too much data and not too infrequent that there wouldnt be anouth data to analyze.

