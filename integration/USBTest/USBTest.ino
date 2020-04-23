#include <FastLED.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_TSL2591.h"

#define STEPPER_FRONT_IN1 9
#define STEPPER_FRONT_IN2 10
#define STEPPER_FRONT_IN3 11
#define STEPPER_FRONT_IN4 12

#define BACK_LED_PIN 3
#define FRONT_LED_PIN 2
#define NUM_LEDS 2


int gateNum = 0;
long currLux = 0;
int PERF_THRESHOLD = 14;
int lenPack = 2000;
bool foundPerf = false;

CRGB backLED[NUM_LEDS];
CRGB frontLED[NUM_LEDS];

Adafruit_TSL2591 tsl = Adafruit_TSL2591(2591);






void setup() {
  configureSensor();

  pinMode(STEPPER_FRONT_IN1, OUTPUT);
  pinMode(STEPPER_FRONT_IN2, OUTPUT);
  pinMode(STEPPER_FRONT_IN3, OUTPUT);
  pinMode(STEPPER_FRONT_IN4, OUTPUT);

  FastLED.addLeds<APA104, BACK_LED_PIN, GRB>(backLED, NUM_LEDS);
  FastLED.addLeds<APA104, FRONT_LED_PIN, GRB>(frontLED, NUM_LEDS);
  turnOffBackLight();
  turnOffFrontLight();
 
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    String line = Serial.readStringUntil('\n');
    
    if (line == "new") {
      getFirstPack();
    }
    
    if (line == "on") {
      nextPack(lenPack);
      foundPerf = findPerf();
      
      if (foundPerf) {
        nextPack(600)
        turnOnBackLight();
        Serial.println("backlight on");
      } 
      
      while (line != "took contour") {
        line = Serial.readStringUntil('\n');
      }
      
      turnOffBackLight();
      turnOnFrontLight();
      Serial.println("front light on");
      
      while (line != "took front photo") {
        line = Serial.readStringUntil('\n');
      }
      
      turnOffFrontLight();
    }
  }
}


void configureSensor(void) {
   tsl.setGain(TSL2591_GAIN_MED);      // 25x gain

   tsl.setTiming(TSL2591_INTEGRATIONTIME_100MS);  // shortest integration time (bright light)
}

void getFirstPack(void) {
  nextPack(3250); // moves first pill pack edge to the beginning of LED
  findPerf();
  nextPack(lenPack);
}

bool findPerf(void) {
  int numRotations = 0;
  
  while (currLux < PERF_THRESHOLD) {
    currLux = lightSensorRead();
    oneStep(true);
    numRotations++;
  }
  
  return true;
}

void nextPack(int stepLen) {
  for(int i = 0; i < stepLen;i++){
    oneStep(true);
  }
}

long lightSensorRead(void) {
  uint32_t lum = tsl.getFullLuminosity();
  uint16_t ir, full;
  ir = lum >> 16;
  full = lum & 0xFFFF;
  return tsl.calculateLux(full, ir);
}


void turnOnBackLight(void) {
  backLED[0] = CRGB (255, 255, 255);
  backLED[1] = CRGB (255, 255, 255);
  FastLED.show();
}

void turnOffBackLight(void) {
  backLED[0] = CRGB (0, 0, 0);
  backLED[1] = CRGB (0, 0, 0);
  FastLED.show();
}

void turnOnFrontLight(void) {
  frontLED[0] = CRGB (255, 255, 255);
  frontLED[1] = CRGB (255, 255, 255);
  FastLED.show();
}

void turnOffFrontLight(void) {
  frontLED[0] = CRGB (0, 0, 0);
  frontLED[1] = CRGB (0, 0, 0);
  FastLED.show();
}

void oneStep(bool dir){
  delay(2);
  if(dir){
    switch(gateNum){
        case 0:
          digitalWrite(STEPPER_FRONT_IN1, HIGH);
          digitalWrite(STEPPER_FRONT_IN2, LOW);
          digitalWrite(STEPPER_FRONT_IN3, LOW);
          digitalWrite(STEPPER_FRONT_IN4, LOW);

          break;
        case 1:
          digitalWrite(STEPPER_FRONT_IN1, LOW);
          digitalWrite(STEPPER_FRONT_IN2, HIGH);
          digitalWrite(STEPPER_FRONT_IN3, LOW);
          digitalWrite(STEPPER_FRONT_IN4, LOW);

          break;
        case 2:
          digitalWrite(STEPPER_FRONT_IN1, LOW);
          digitalWrite(STEPPER_FRONT_IN2, LOW);
          digitalWrite(STEPPER_FRONT_IN3, HIGH);
          digitalWrite(STEPPER_FRONT_IN4, LOW);

          break;
        case 3:
          digitalWrite(STEPPER_FRONT_IN1, LOW);
          digitalWrite(STEPPER_FRONT_IN2, LOW);
          digitalWrite(STEPPER_FRONT_IN3, LOW);
          digitalWrite(STEPPER_FRONT_IN4, HIGH);

          break;
      } 
  } else {
      switch(gateNum){
        case 0:
          digitalWrite(STEPPER_FRONT_IN1, LOW);
          digitalWrite(STEPPER_FRONT_IN2, LOW);
          digitalWrite(STEPPER_FRONT_IN3, LOW);
          digitalWrite(STEPPER_FRONT_IN4, HIGH);

          break;
        case 1:
          digitalWrite(STEPPER_FRONT_IN1, LOW);
          digitalWrite(STEPPER_FRONT_IN2, LOW);
          digitalWrite(STEPPER_FRONT_IN3, HIGH);
          digitalWrite(STEPPER_FRONT_IN4, LOW);

          break;
        case 2:
          digitalWrite(STEPPER_FRONT_IN1, LOW);
          digitalWrite(STEPPER_FRONT_IN2, HIGH);
          digitalWrite(STEPPER_FRONT_IN3, LOW);
          digitalWrite(STEPPER_FRONT_IN4, LOW);

          break;
        case 3:
          digitalWrite(STEPPER_FRONT_IN1, HIGH);
          digitalWrite(STEPPER_FRONT_IN2, LOW);
          digitalWrite(STEPPER_FRONT_IN3, LOW);
          digitalWrite(STEPPER_FRONT_IN4, LOW);

          break;
      } 
  }
  gateNum++;
  if(gateNum > 3) {
    gateNum = 0;
  }
}
