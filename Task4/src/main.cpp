#include "pins_arduino.h"
#include <Arduino.h>

#define p Serial.print
#define P Serial.println


const long B = 4750; // B value of the thermistor
const long R0 = 100; // R0 = 100k
const int pinTempSensor = A0; // Temperature sensor pin 
const unsigned long CYCLE_TIME_MS = 60000UL;
const int HISTORY_SIZE = 10;
const float MIN_SAMPLE_RATE = 0.5f;
const float MAX_SAMPLE_RATE = 4.0f;
const float STABLE_THRESHOLD = 0.65f;

bool DEBUG_MODE = false;

enum POWER_MODE {
  ACTIVE_MODE,
  IDLE_MODE,
  POWER_DOWN_MODE
};

long N_tBuffer = 256;  // default size of the temp buffer; 
float* tempBuffer; 
long N_index = 0;
int samplescount = 0;
float sampleRate = 1; // active mode = 1Hz
float oldSampleRate = 1;
int mode = ACTIVE_MODE;
int stableCycles = 0;
float variationHistory[HISTORY_SIZE];
int historyCount = 0;

struct frequencyDomainSample {
  float real;
  float imaginary;
  float magnitude;
  float frequency;
  int k;
};
frequencyDomainSample* freqdomain;


// put function declarations here:
int myFunction(int, int);

void collect_temperature_data();
void send_data_to_pc(float* dft);
POWER_MODE decide_power_mode(float totalVariation, float predictedVariation);
void update_sample_rate(float dominantFreq);

void initTempBuffer() {
  tempBuffer = (float*) malloc(N_tBuffer * sizeof(float)); // allocate dynamic size of the buffer used for temperature
  N_index = 0;
  for (int i = 0; i< N_tBuffer; i++) {  // set all values in the buffer the a set value to ensure that there is no randum values
    tempBuffer[i] = 0.0f;
    delay(20);
    p(".");
  }
  return;
}

template<typename T>
void printBuffer(void *buffer, int index, int max_size) {
  int NLafterX = 10;
  T* typedbuffer = (T*) buffer;
  for(int i = 0; i < max_size; i++) {
    (i == index) ? [i, typedbuffer](){p("\033[32m"); p(typedbuffer[i]); p("\033[0m");}() : [i, typedbuffer](){p(typedbuffer[i]);}(); // adding green text colour for the latest added value
    ((i+1) % NLafterX == 0 ) ? Serial.print("\n"): Serial.print("\t");
  }
}

void appendToBuffer(void *buffer, long *index, long max_size, void *value, int element_size) {
  if (*index < max_size) {
    char *byte_buffer = (char *)buffer;
    memcpy(byte_buffer + (*index * element_size), value, element_size);
    (*index)++;
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

void wipeTempBuffer() {
  for (int i = 0; i < N_tBuffer; i++) {
    tempBuffer[i] = 0.0f;
    N_index = 0;
    samplescount = 0;
    p(tempBuffer[i]);
  }
}

float calculate_variation(float data[], int N) {
  float total = 0.0f;
  
  for (int i = 1; i < N; i++) {
    total += fabs(data[i] - data[i - 1]);
  }
  p("VARIATION: "); P(total, 3);
  return total;
}

float moving_average(float newValue) {
  if (historyCount < HISTORY_SIZE) {
    variationHistory[historyCount++] = newValue;
  } else {
    for (int i = 1; i < HISTORY_SIZE; i++) {
      variationHistory[i-1] = variationHistory[i];
    }
    variationHistory[HISTORY_SIZE-1] = newValue;
  }

  float sum = 0.0f;

  for (int i = 0; i < historyCount; i++) {
    sum += variationHistory[i];
  }

  return sum / historyCount;
}

float* apply_dft(float data[], int N, float sample_Rate) {
  float maxMagnitude = 0.0f;
  float *dominantFrequency = (float*) malloc(sizeof(float));

  freqdomain = (frequencyDomainSample*) malloc(sizeof(frequencyDomainSample)*(N/2));


  /* loop through each frequency bin
   * k=1 skips DC component
   * N/2 is enough due to mirrored spectrum
   */ 
  for (int k = 1; k < N/2; k++) {
    float real = 0.0f;
    float imaginary = 0.0f;

    // sum all samples
    for (int n = 0; n < N; n++) {
      // 2PIkn/N is the power of e without j
      float angle = (2.0f * PI * k * n) / N;
      real += data[ (N_index - samplescount + n + N_tBuffer ) % N_tBuffer ] * cos(angle);
      imaginary -= data[ ( N_index - samplescount + n + N_tBuffer ) % N_tBuffer ] * sin(angle);
      //P(angle);
    }
    //p("real: ");
    //P(real);
    //p("imaginary: ");
    //P(imaginary);

    //measures and compares if it is the biggest peak
    float magnitude = sqrt((real * real) + (imaginary * imaginary));
    //p("\nk: ");p(k);p("\tmagnitude calculated: ");p(magnitude);p("\n");

    freqdomain[k-1] = {.real = real, .imaginary = imaginary, .magnitude = magnitude, .frequency = (k*sample_Rate)/N, .k = k}; // add frequency domain index into buffer. 
 
    if (magnitude > maxMagnitude && k!=0) {
      //p("Max found: k: ");p(k);p(" magnitude: ");p(magnitude);p(" sampleRate: ");p(sample_Rate);p(" N: ");p(N);//p(" Previous Dominant: ");P(*dominantFrequency);
      maxMagnitude = magnitude;
      *dominantFrequency = (k * sample_Rate) / N ;
    }

  }
  return dominantFrequency;
}

void setup() {
  Serial.begin(115200);
  delay(1500);

  p("int is x bytes: ");
  P(sizeof(int)); // 16 bit
  p("long is x bytes: ");
  P(sizeof(long)); // 32 bit
}

void loop() {
  // put your main code here, to run repeatedly:
  //Serial.println("Hi!");

  //p("millis: ");
  //P(millis());
  N_tBuffer = ceil( ((!DEBUG_MODE) ? 1.2 : 0.55) * 60*sampleRate) + 1; // 1.2 minutes of samples size of buffer or ~35 sec if running in debug mode
  //P(N_tBuffer);
  initTempBuffer();
  
  collect_temperature_data(); //collect one minute of sample data

  float variation = calculate_variation(tempBuffer, samplescount); //calcuaate the variation 

  float predicted = moving_average(variation); // get predicted value from variation

  float *dft = apply_dft(tempBuffer, samplescount, sampleRate ); // apply dft to the collected sample data
  
  if(DEBUG_MODE) {
    p("dft value");
    p(*dft);
    p("\tvariation: ");
    p(variation);
    p("\tpredicted: ");
    P(predicted);
  }

  mode = decide_power_mode(variation, predicted);

  update_sample_rate(*dft);

  send_data_to_pc(dft);

  free(tempBuffer);
  free(freqdomain);
  free(dft);
  oldSampleRate = sampleRate;
  delay(100); // delay the function a second after finnishing processing
}
  
// put function definitions here:
int myFunction(int x, int y) {
  return x + y;
}

void collect_temperature_data() {
  P("Collecting Temperature '_'");
  unsigned long temp_time_start = millis();
  samplescount = 0;
  //P("Time(ms),Temperature(oC)");
  for (int i = 0; i< ceil(((!DEBUG_MODE) ? 1 : 0.5)*60*sampleRate); i++) { // 1 minute of samples 
    long tempStart = millis();
    long a = analogRead(pinTempSensor);
    float temperature = 1.0 / (log((R0 * (1023.0 / a - 1.0) ) / R0) / B + 1.0 / 298.15) - 273.15;
    
    //p((millis()-temp_time_start));p(",");P(temperature);
    p("#");
    appendToBuffer(tempBuffer, &N_index, N_tBuffer, &temperature, sizeof(float));
    (samplescount < N_tBuffer) ? samplescount++ : samplescount;
    long time = ( 1000/sampleRate ) - millis() + tempStart;
    /*p("delay time: ");
    P(time);
    p("RAW TEMPERATURE: ");
    P(a);*/
    //p("#");
    delay(time); // delay set to the samplerate - time it took to calculate and append data.
  }
  P("--END OF COLLECTING TEMPERATURE--");
  //printBuffer<float>(tempBuffer, N_index-1, N_tBuffer);
  return;
}

void send_data_to_pc(float* dft) {
  P("Time\t\tTemperature\tfrequency\tmagnitude");
  for(int i = 0; i< samplescount; i++) {

    // --- Time and temperature data --
    p(i/oldSampleRate, 3); //TIME TO 3 DP
    p(",\t");
    p(tempBuffer[(N_index - samplescount + i + N_tBuffer) % N_tBuffer], 3);
    p(",\t\t");
     // --- frequency and magnitude 
    if (i < samplescount / 2 - 1) { 
      p(freqdomain[i].frequency, 4);
      p(",\t\t");
      p(freqdomain[i].magnitude, 4);
      P("");
    }
    else {
      P("");
    }
  }
  p("Dominant Frequency: "); P(*dft, 3);
  p("stablecount: "); P(stableCycles);
  p("variation History: ");
  for( float val : variationHistory) {
    p(val, 3);p("\t");
  }
  P();
  p("Mode: "); P(mode);
  p("SAMPLE_RATE: ");P(oldSampleRate);
  P("---END OF DATA TRANSMISSION---");
  return;
}

POWER_MODE decide_power_mode(float totalVariation, float predictedVariation) {
  // if sudden spike or higher then theshold then sswitch to active mode
  if (totalVariation > STABLE_THRESHOLD * 2.0f) {
    p("TATAL  TRIGGERRED total: ");p(totalVariation, 3);p("\tpredicted: ");P(predictedVariation);
    stableCycles = 0;
    return ACTIVE_MODE;
  }
  if (predictedVariation > STABLE_THRESHOLD) {
    P("PREDICTED TRIGGERED");
    stableCycles = 0;
    return ACTIVE_MODE;
  }

  stableCycles++;
  P("neither triggered");
  if (stableCycles >= 5) { // if the temperature has been stable for more than 5 cycles then switch to POWER_DOWN_MODE
    return POWER_DOWN_MODE;
  }

  return IDLE_MODE;
}

void update_sample_rate(float dominantFreq) {
  float target = dominantFreq * 2.0f;
  if (variationHistory[0] > 1) target += 0.5;

  if (target < MIN_SAMPLE_RATE) target = MIN_SAMPLE_RATE;
  if (target > MAX_SAMPLE_RATE) target = MAX_SAMPLE_RATE;

  // smooth decrease if the target is lower than the samplerate
  if (target < sampleRate) {
    sampleRate -= 0.25f;
    if (sampleRate < target) sampleRate = target;
  } else {
    sampleRate = target;
  }
}