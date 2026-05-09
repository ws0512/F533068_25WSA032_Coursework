#include <Arduino.h>

#define P Serial.println
#define p Serial.print


const long B = 4250; // B value of the thermistor
const long R0 = 100; // R0 = 100k
const int pinTempSensor = A0; // Temperature sensor pin 
const float sampleRate = 1; // 1Hz

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  delay(1000);
}

void loop() {
  // put your main code here, to run repeatedly:
  long timeStart = millis();
  P("Time(s),Temperature(oC)");
  do {
    long temperatureStart = millis();
    long a = analogRead(pinTempSensor);
    float temperature = 1.0 / (log((R0 * (1023.0 / a - 1.0) ) / R0) / B + 1.0 / 298.15) - 273.15;
    
    p((millis() - timeStart) / 1000.0, 3);p(",");P(temperature);

    delay(( 1000l/sampleRate ) - millis() + temperatureStart);
  }while (millis()-timeStart < 3l*60l*1000l );
  delay(-1);
};