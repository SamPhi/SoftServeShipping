#include "Arduino.h"
#include "actuator.h"

actuator::actuator() {
  //Limit switch setup
  pinMode(LS1, INPUT_PULLUP);
  pinMode(LS2, INPUT_PULLUP);
  //Hall effect sensor setup
  pinMode(startSensor, INPUT_PULLUP);
  pinMode(endSensor, INPUT_PULLUP);
  //Motor setup
  ledcSetup(ledChannel_1, freq, resolution); //Configure LED PWM functionalities
  ledcSetup(ledChannel_2, freq, resolution);
  ledcAttachPin(BIN_1, ledChannel_1); // attach the channels to the GPIOs to be controlled
  ledcAttachPin(BIN_2, ledChannel_2);
  //JOYSTICK
  pinMode(x_key, INPUT);
  pinMode(y_key, INPUT);
  //Potentiometer
  pinMode(angleSensor, INPUT);
}

//Checks left limit switch, returns true if pressed
bool actuator::checkLimLeft() {
  if (digitalRead(LS1) == LOW) {
    return true;}
  else {
    return false;
  }
}

//Checks right limit switch, returns true if pressed
bool actuator::checkLimRight() {
  if (digitalRead(LS2) == LOW) {
    return true;}
  else {return false;}
}

//Returns true if left hall effect sensor triggered, otherwise false
bool actuator::checkStart() {
  if (digitalRead(startSensor) == LOW) {
    return true;}
  else {return false;}
}

//Returns true if right hall effect sensor triggered, otherwise false
bool actuator::checkEnd() {
  if (digitalRead(endSensor) == LOW) {
    return true;}
  else {return false;}
}

//Drives motors - checks PWM in operating range and for limit switch hits
void actuator::writeMotors(int PWM){
  //Check PWM Limits
  if (PWM>1023) {
    PWM = 1023;
  }
  if (PWM<-1023) {
    PWM = -1023;
  }

  //Set motor PWM based on sign, and check not hitting relevant limit switch for given direction
  if ((PWM >= 0) && !checkLimRight()) {
    ledcWrite(ledChannel_1, LOW);
    ledcWrite(ledChannel_2, PWM);
  }
  else if ((PWM < 0) && !checkLimLeft()){
    ledcWrite(ledChannel_1, -PWM);
    ledcWrite(ledChannel_2, LOW);
  }
  else {
    ledcWrite(ledChannel_1, LOW);
    ledcWrite(ledChannel_2, LOW);
  }
}

void actuator::manualMovement(){
  //Get joystick val
  int input = -(map((analogRead(x_key)),0,3600,-1023,1023));
  //Check if joystick val in deadband, actuate if not
  if (abs(input) > deadBand){
  writeMotors(input);
  }
  else{
    writeMotors(0);
  }
}

bool actuator::homingFunction(){
  if((!leftHomed) && (!resetZero)&&(!moveToStart)){ ////////Add bool move to start
    writeMotors(-homingSpeed);
    leftHomed = checkLimLeft();
    if(leftHomed){
      zeroPos = x_pos;
      resetZero = true;
    }
    return false;
  }
  else if((!rightHomed) && (leftHomed) && (!moveToStart)){
    writeMotors(homingSpeed);
    rightHomed = checkLimRight();
    return false;
  }
  else if ((rightHomed) && (leftHomed) && (!moveToStart)) {
    farRight = x_pos;
    int startingPoint = int((farRight + abs(zeroPos))/8 + zeroPos);
    moveToStart = moveToPosition(startingPoint);
    return false;
  }
  else if ((rightHomed)&&(leftHomed) && (moveToStart){
    writeMotors(0);
    rightHomed = false;
    resetZero = false;
    leftHomed = false;
    moveToStart = false;
    return true;
  }
}




bool actuator::moveToPosition(int xcoord){
  if((x_pos > (xcoord+tol)) && (!checkLimLeft())){
    writeMotors(-homingSpeed);
    return false;
  }
  else if ((x_pos<(xcoord-tol) && (!checkLimRight()))){
    writeMotors(homingSpeed);
    return false;
  }
  else{
    return true;
  }
}

//Returns theta in degrees - CCW positive, CW negative
float actuator::getTheta(){
  return (analogRead(angleSensor)-center)/oneDegInCounts;
}

bool actuator::autoMove(){
    return false;
}


