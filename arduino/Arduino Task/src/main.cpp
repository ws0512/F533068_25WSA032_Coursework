#include "pins_arduino.h"
#include <Arduino.h>

const int B = 4275000; // B value of the thermistor
const int R0 = 100000; // R0 = 100k
const int pinTempSensor = A0; // Temperature sensor pin 

int N_tBuffer = 32;  // default size of the temp buffer; 
float* tempBuffer; 
int N_index = 0;

// put function declarations here:
int myFunction(int, int);

void initTempBuffer() {
  tempBuffer = (float*) malloc(N_tBuffer * sizeof(float)); // allocate dynamic size of the buffer used for temperature
  
  for (int i = 0; i< N_tBuffer; i++) {  // set all values in the buffer the a set value to ensure that there is no randum values
    tempBuffer[i] = 0.0f;
  }
}

void changeSizeOfTempBuffer(int newIndexSize) {
  float* newBuffer = (float*) malloc(newIndexSize * sizeof(float)); //create and allocate memory space for the new buffer
  int copycunt = min(N_tBuffer, newIndexSize); // minimum count of idexes that will need to be copied
  
  for ( int i = 0; i < copycunt; i++) {
    int idx = (N_index +i + ((newIndexSize < N_tBuffer) ? -copycunt+N_tBuffer : 0) ) % N_tBuffer; // index of old buffer accounted for when the new buffer is smaller than the old buffer. 
    newBuffer[i] = tempBuffer[idx];
  }

   for (int i = copycunt; i < newIndexSize; i++) { // if the buffer is larger set all new values as teh default 0.0f
    newBuffer[i] = 0.0f;
  }

  N_index = copycunt % newIndexSize; // update variables
  free(tempBuffer); // free the memory used for the old buffer
  tempBuffer = newBuffer;
  N_tBuffer = newIndexSize;

  for(int i = 0; i < N_tBuffer; i++) { // print whole buffer (order independant)
    (i == N_index) ? [i](){Serial.print("\033[32m"); Serial.print(tempBuffer[i]); Serial.print("\033[0m");}() : [i](){Serial.print(tempBuffer[i]);}();
    ( (i+1) % 5  == 0 ) ? Serial.print("\n"): Serial.print("\t");
  }
}

void setup() {
  Serial.begin(9600);
  // put your setup code here, to run once:
  int result = myFunction(2, 3);
  Serial.println(result);

  initTempBuffer();
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println("Hi!");
  int a = analogRead(A0);

  float temperature = 1.0/(log(((1023.0/a-1.0)*R0)/R0)/B+1/298.15)-273.15;
  tempBuffer[N_index] = temperature;
  
  for(int i = 0; i < N_tBuffer; i++) { // print whole buffer (order independant)
    (i == N_index) ? [i](){Serial.print("\033[32m"); Serial.print(tempBuffer[i]); Serial.print("\033[0m");}() : [i](){Serial.print(tempBuffer[i]);}(); // adding green text colour for the latest added value
    ( (i+1) % 5  == 0 ) ? Serial.print("\n"): Serial.print("\t");
  }

  N_index = (N_index + 1) % N_tBuffer; // Number of the next index in the ring buffer
  
  Serial.print("\ntemperature = ");
  Serial.println(temperature);

  /*if (temperature > 25.70f) {
    changeSizeOfTempBuffer(16);
  }*/
  
  delay(2000);
}

// put function definitions here:
int myFunction(int x, int y) {
  return x + y;
}