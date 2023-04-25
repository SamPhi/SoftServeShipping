#include <ESP32Encoder.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <math.h>
#include <Arduino.h>
#include <Bounce2.h>
#include <WiFi.h>
#include <ArduinoJson.h>

// JOYSTICK CONTROLLER
int x_key = 34;
int y_key = 33;

int y_pos = 0;
int x_pos = 0;

int speed;

void setup() {
  Serial.begin(9600);
  pinMode(x_key, INPUT);
  pinMode(y_key, INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  speed = map((analogRead(x_key)),0,3600,-1023,1023);
  //speed = analogRead(x_key);
  Serial.println(speed);

}
