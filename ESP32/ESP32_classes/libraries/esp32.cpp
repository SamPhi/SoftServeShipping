#include "Arduino.h"
#include "esp32.h"
#include <string>
#include <iostream>
using namespace std;

esp32::esp32() {
    phone_state = "select";
    x_des = 0; //y_des = 0
    cancel = false;

    x_pos = 0; //y_pos = 0
    theta = 0;

    state = "idle";
    finished = false;
    homed = false;
    partHomed = false;

    actuator myActuator();//?????????????
}

//Checks left limit switch, returns true if pressed
void esp32::updatePhysicalVals() {
    theta = myActuator.getTheta();
    x_pos = myActuator.x_pos;
}

//esp32 state machine
void esp32::getstate() {
    if((phone_state == "select" || state =="finished") && checkHomed()==true){
        state = "idle";
    }
    else if ((phone_state == "automatic" && cancel == false) && checkFinished()==false){
        state = "auto";
    }

    else if ((phone_state == "manual" && cancel == false) && checkFinished()==false){
        state = "manual";
    }
    else if ((phone_state == "thankyou")||(phone_state=="automatic"&&(cancel==true||checkFinished()== true))){
        state = "finished";
    }
    else if ((phone_state == "thankyou")||(phone_state=="manual"&&(cancel==true||checkFinished()== true))){
        state = "finished";
    }
    else if (phone_state == "select" && checkHomed() ==false){
        cout << "error not homed";
    }
    else{
      cout << "No corresponding esp32 state";
    }


}

void esp32::actions() {
  if (state == "idle") {
    myActuator.writeMotors(0);
    finished = false;
  }
  else if (state == "manual") {
    if (homed == true) {
      homed = false;
    }
    myActuator.manualMovement();
  }

  else if (state == "auto") {
    if (homed == true) {
      homed = false;
    }
    myActuator.autoMove();
  }

  else if (state == "finished") {
    if (cancel == true) {
      cancel = false;
    }
    if (homed == false) {
      homed = myActuator.homingFunction();
     // if (partHomed = true) {
    //    partHomed = true;////Questionable!!!!!!!
     // }
    }
  }
 }
 

  bool esp32::checkFinished(){
    if (finished == true) {
      return true;
    }
    else {
      finished = myActuator.checkEnd();
      return finished;
    }
  }

  bool esp32::checkHomed() {
    return homed;
   }

  int esp32::getStartPos() {
    int rightPos = myActuator.farRight;
    int leftPos = myActuator.zeroPos;
    float diff = abs(leftPos) + abs(rightPos);
    float startPos = float(leftPos) + float(diff)/8;

    return int(startPos);
  }

  //int esp32::unWrap(num){
  //  if (num > 500000) {
  //    num = num - 999999;
  //  }
  //  return num;
  //}

  //int esp32::wrap(num) {
  //  if (num < 0) {
  //    num = 999999 + num;
  //  }
  //  return num;
  //}