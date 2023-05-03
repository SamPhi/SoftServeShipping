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
  if ((digitalRead(endSensor) == LOW) && (debounceCounter > debounceTime)) {
    debounceCounter = 0;
    return true;
  }
  else if ((digitalRead(endSensor) == LOW) && (debounceCounter <= debounceTime)) {
    debounceCounter += 1;
    return false;
  }
  else {
    debounceCounter = 0;
    return false;
  }
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
  if ((!leftHomed) && (!rightHomed) && (!resetZero) && (!moveToStart)) { ////////Add bool move to start
    writeMotors(-homingSpeed);
    leftHomed = checkLimLeft();
    if (leftHomed) {
      zeroPos = x_pos;
      resetZero = true;
    }
    return false;
  }

  else if ((leftHomed) && (!rightHomed) && (resetZero) && (!moveToStart)) {
    writeMotors(homingSpeed);
    rightHomed = checkLimRight();
    farRight = x_pos;
    return false;
  }

  else if ((rightHomed) && (leftHomed) && (resetZero) && (!moveToStart)) {
    int startingPoint = farRight-int((abs(farRight) + abs(zeroPos))/11);
    moveToStart = moveToPosition(startingPoint);
    return false;
  }
  else if ((rightHomed)&&(leftHomed)&& (resetZero) && (moveToStart)){
    writeMotors(0);
    rightHomed = false;
    resetZero = false;
    leftHomed = false;
    moveToStart = false;
    return true;
  }
  //else {
  //  writeMotors(0);
  //  return false;
  //}
}

bool actuator::moveToPosition(int xcoord){
  if(x_pos > (xcoord+tol)){
    writeMotors(-homingSpeed);
    return false;
  }
  else if (x_pos<(xcoord-tol)){
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

void actuator::callibratePot() {
  float total;
  for (int i = 0; i < 10000; i++) {
    total += analogRead(angleSensor);
  }
  center = total / 10000;
  return;
}

void actuator::shiftArray(float array[], float newValue){
  if(n>=ARRAY_SIZE){
    n = 0;
  }
  array[n] =  newValue;
  n+=1;
  return;
}

float actuator::medianArray(float array[]) {
  // Copy array to a temporary array
  float tempArray[ARRAY_SIZE];
  std::copy(array, array + ARRAY_SIZE, tempArray);

  // Sort the temporary array
  std::sort(tempArray, tempArray + ARRAY_SIZE);

  // Compute the median of the array
  if (ARRAY_SIZE % 2 == 0) {
    // If the array size is even, compute the average of the middle two elements
    return (tempArray[ARRAY_SIZE / 2] + tempArray[ARRAY_SIZE / 2 - 1]) / 2.0;
  } else {
    // If the array size is odd, return the middle element
    return tempArray[ARRAY_SIZE / 2];
  }
}

void actuator::autoMove(float x_des) {
    x = -x_pos; //CHANGE TO ENC_CORE_N
    float th = (getTheta())*M_PI/180;
    x = totalLength * x/totalEncoder;
    //take last 5 average values for theta
    shiftArray(th_hist, th);
    th = -1*medianArray(th_hist);

    float dth = (th-th_past)/dt;
    float dx =  (x - x_past)/dt;
    dth = dth/10000000;
    dx = dx/10000000;

    //Error in X
    float e = x_des-x;
    //Theta des
    float th_des = -kpx*(e) - kdx*(dx);
    //Error in theta
    float eth = th*180/M_PI - th_des;
    //Calculate PWM value
    float u = kpt*eth + kdt*dth; //ANGLE STABILIZNG
    if(abs(e) < 0.02 && abs(eth) < 0.6){
        u= 0;
    }

    PWM = u*scalePWM;
    shiftArray(PWM_hist, PWM);
    PWM = medianArray(PWM_hist);
    writeMotors(PWM);
    //Update past values for next run
    th_past = th;
    x_past = x;
    return;

}


