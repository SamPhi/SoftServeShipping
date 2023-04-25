#include <actuator.h>


const int homingSpeed = 600; //PWM value for homing function
bool leftHomed = false; //flag for homing function to check if homed left
bool rightHomed = false; //Flag for homing function to check if homed right
bool resetZero = false; //Flag to check if zero pos needs to be reset during homing
int farRight = 0; //Value of encoder at far right, to be updated during homing
int zeroPos = 0; //Value of encoder at far left, to be updated during homing



void setup() {
  // put your setup code here, to run once:
  
}

void loop() {
  // put your main code here, to run repeatedly:

}

bool homingFunction(){
  if((!leftHomed) && (!resetZero)){
    writeMotors(-homingSpeed);
    leftHomed = checkLimLeft();
    if(leftHomed){
      zeroPos = x_pos;
      resetZero = true;
    }
    return false;
  }
  else if((!rightHomed) && (leftHomed)){
    writeMotors(homingSpeed);
    rightHomed = checkLimRight();
    return false;
  }
  else if ((rightHomed)&&(leftHomed)){
    writeMotors(0);
    farRight = x_pos;
    rightHomed = false;
    leftHomed = false;
    return true;
  }
}
