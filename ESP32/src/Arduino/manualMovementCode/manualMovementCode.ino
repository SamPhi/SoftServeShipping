#include <ESP32Encoder.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <math.h>
#include <Arduino.h>
#include <Bounce2.h>
#include <WiFi.h>
#include <ArduinoJson.h>

// JOYSTICK CONTROLLER
const int x_key = 34;
const int y_key = 33;

int y_pos = 0;
int x_pos = 0;

const int deadBand = 15;


void setup() {
  Serial.begin(9600);
  pinMode(x_key, INPUT);
  pinMode(y_key, INPUT);
}

void loop() {
  Serial.println("test");
}

void manualMovement(){
  //Get joystick val
  int input = map((analogRead(x_key)),0,3600,-1023,1023);
  //Check if joystick val in deadband, actuate if not
  if (input > deadBand){
  writeMotors(input);
  }
  else{
    writeMotors(0);
  }
}
