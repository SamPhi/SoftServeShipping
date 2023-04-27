#include <actuator.h>

const int tol = 15;

void setup() {
  // put your setup code here, to run once:

}

void loop() {
  // put your main code here, to run repeatedly:

}

bool moveToPosition(int xcoord){
  if((x_pos > (xcoord+tol)) && (!checkLimLeft())){
    writeMotors(-homingspeed);
    return false;
  }
  else if ((x_pos<(xcoord-tol) && (!checkLimRight)){
    writeMotors(homingspeed);
    return false;
  }
  else{
    return true;
  }
}
