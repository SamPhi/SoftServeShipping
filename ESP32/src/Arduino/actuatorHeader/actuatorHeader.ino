#ifndef actuator_h //Protects code from error if class is included more than once in a sketch
#define actuator_h //Defines class with name actuator
#include "Arduino.h" 

class actuator {
public: //Defines variables/functions that a sketch can use 
  actuator();
  //HALL EFFECT SENSOR 
  bool checkStart(); //Checks if left hall effect sensor triggered, returns true if so
  bool checkEnd(); //Checks if right hall effect sensor triggered, returns true if so
  //JOYSTICK 


private: //Defines variables/functions only accessbile to actuator class
  //LIMIT SWITCH 
  int LS1=4; //Lim switch left pin
  int LS2=16; // Lim switch right pin
  bool checkLimLeft(); //Internal function to check if Left Lim siwtch hit, returns true if so
  bool checkLimRight(); //Internal function to check if right lim switch hit, returns true if so
  //HALL EFFECT SENSOR 
  int startSensor=17; //Switch for start sensor
  int endSensor=21; //Switch for end sensor
  //MOTOR SETUP
  const int BIN_1 = 25; //Motor pin 1
  const int BIN_2 = 26; //Motor pin 2
  const int freq = 25000; //PWM frequency
  const int ledChannel_1 = 1; //PWM channel 1
  const int ledChannel_2 = 2; //PWM channel 2
  const int resolution = 8; //PWM resolution
  void writeMotors(int PWM); //Sets PWM value to motor, checking lim switches
  //JOYSTICK



};

#endif