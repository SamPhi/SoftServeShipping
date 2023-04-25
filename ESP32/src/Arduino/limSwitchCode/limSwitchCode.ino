#include <ESP32Encoder.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <math.h>
#include <Arduino.h>
#include <Bounce2.h>

int LS1=4;
int LS2=16;
 
void setup() {
  Serial.begin(9600);
  pinMode(LS1, INPUT_PULLUP);
  pinMode(LS2, INPUT_PULLUP);
}
 
void loop() {
  Serial.println(checkLimLeft());
  Serial.println(checkLimRight());  
}


bool checkLimLeft() {
  if (digitalRead(LS1) == LOW) {
    return true;}
  else {return false;}
}

bool checkLimRight() {
  if (digitalRead(LS2) == LOW) {
    return true;}
  else {return false;}
}
