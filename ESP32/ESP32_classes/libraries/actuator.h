#ifndef actuator_h //Protects code from error if class is included more than once in a sketch
#define actuator_h //Defines class with name actuator

#include <Arduino.h>

class actuator {
public: //Defines variables/functions that a sketch can use
  //Initializer
  actuator();
  //HALL EFFECT SENSOR
  //HALL EFFECT SENSOR
  bool checkStart(); //Checks if left hall effect sensor triggered, returns true if so
  bool checkEnd(); //Checks if right hall effect sensor triggered, returns true if so
  void writeMotors(int PWM); //Sets PWM value to motor, checking lim switches
  //Manual movement
  void manualMovement(); //Moves gantry based on joystick input
  //x_pos
  volatile int x_pos = 0;
  //Homing
  int farRight; //Value of encoder at far right, to be updated during homing
  int zeroPos; //Value of encoder at far left, to be updated during homing
  bool homingFunction(); //Homing function
  bool moveToPosition(int xcoord); //Moves to xcoord
  //Potentiometer
  float getTheta(); //Returns angle in degrees, center = 0, CCW = positive, CW = negative
  bool autoMove();
  bool checkLimRight(); //Internal function to check if right lim switch hit, returns true if so
  void callibratePot();



private: //Defines variables/functions only accessbile to actuator class
  //LIMIT SWITCH
  int LS1=4; //Lim switch left pin
  int LS2=16; // Lim switch right pin
  bool checkLimLeft(); //Internal function to check if Left Lim siwtch hit, returns true if so
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
  //JOYSTICK
  const int x_key = 34; //Pin for joystick in X
  const int y_key = 33; //Pin for joystick in Y
  const int deadBand = 15; //Deadband for joysticks
  //Homing
  const int homingSpeed = 500; //PWM value for homing function
  bool leftHomed = false; //flag for homing function to check if homed left
  bool rightHomed = false; //Flag for homing function to check if homed right
  bool resetZero = false; //Flag to check if zero pos needs to be reset during homing
  bool moveToStart = false; //flag to check if moved to starting position <-----------------------------------------
  //MoveToPosition
  const int tol = 15;
  //Potentiometer
  const int angleSensor = 32;
  float center = 1863.5;
  const float oneDegInCounts = 10.93;

  //for debounce
  const int debounceTime = 10;
  volatile int debounceCounter=0;




};

#endif