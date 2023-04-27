#include <Arduino.h>

const int angleSensor = 32;
const float center = 1863.5;
//const float fortyFiveDeg = 1371.6;
const float oneDegInCounts = 10.93;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(angleSensor, INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println(getTheta());
}

//Returns theta in degrees - CCW positive, CW negative
float getTheta(){
  return (analogRead(angleSensor)-center)/oneDegInCounts;
}
