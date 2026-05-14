# READ ME

The point of this project is to use an arduino board and python code for measuring a the ambient temperature through the use of a seeed studio temperature sensor v1.3 (That doesnt exist anywhere online). This temperature data is stored in memory, discrete fourier transform is applied to the temperature data and sent off via the UART connection to the PC/Laptop. 
The python code from task 3 mainly focuses on optimising the ecosystem of the little robot's universe. Optimising the logic of the way they interact with the chargers and which pizza they take first to deliver. 

Task 4 mainly focuses on taking the data that was sent through the UART connection to the terminal of your device and analysing this into defferent graphs. 

# How to run and compile
## Task 2 
- in VSCode/VSCodium install the 'PlatformIO IDE' extension
- on the left _task bar(?)_ below extensions there is an ailien icon labeled PlatformIO, click on it. 
- where it says quick access click on *PIO Home* > *Open*
- this should show a GUI screen in the workspace
- click on *import Arduino project*
- Select the 'Arduino Uno' board and locate the folder **./arduino/Arduino\ Task/** select this location.
- on the bottom of the VSC window there will be a terminal button labeled *PlatformIO: New Terminal*, click it.
- with an arduino Uno board connected to your device; compile and upload the code with `pio run --target upload`
- monitor the output of the board with `pio device monitor --raw --baud 115200`

## Task 3
- enter the venv by running `source ./.venv/bin/activate` while inside the directory **F533068_25WSA032_Coursework**
- run the pytho code with `python -m robots.robot_optimisation`

## Task 4
- with platformIO import **./Task4** in the same way as it was done in task 2
- with an arduino Uno board connected to your device; compile and upload the code with `pio run --target upload`
- to create a file needed for task 4 later on collect temperature data with this command `pio device monitor --raw --baud 115200 > ./samples.txt` This will take the entire output of the terminal and put it into the file at **./Task4/samples.txt**
- run the python code with `python main.py`
- click on one of the five buttons to view the graph for that button.

# How To Contribute
![stupid](./stupid.png)

![](./chinese-panda.png)
![](./2.png)