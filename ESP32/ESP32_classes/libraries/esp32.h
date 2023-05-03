#ifndef esp32_h //Protects code from error if class is included more than once in a sketch
#define esp32_h //Defines class with name actuator

#include <Arduino.h>
#include <iostream>
#include <actuator.h>//>>>>>>>
using namespace std;


class esp32 {
public: //Defines variables/functions that a sketch can use
  esp32();

  //Instance af actuator class
  actuator myActuator; //??????????

  //Received from phone
  String phone_state;
  float x_des;
  bool cancel;
  //int y_des =0;

  //Physical vals from actuator
  volatile int x_pos;
  volatile int theta;
  //int y_pos = 0

  // self update state variables
  string state;
  bool finished ;
  bool homed;
  bool partHomed;

  void getstate(); // update esp32 state based on phone_state
  void updatePhysicalVals();   // get sensor reading and update theta + encoder
  void actions(); // actuator movement
  bool checkFinished(); //check ending sensor
  bool checkHomed();


private: //Defines variables/functions only accessbile to actuator class

  int getStartPos();
 // int unWrap(int num); //Create linear scale for measured encoder
 // int wrap(int num) // Return wrapped value in case startPos is negative

};

#endif