#include <Arduino.h>

///REQUIRED ADDITIONAL IMPORTS

/// END IMPORTS

//Code from other scripts:
int LS1=4;
int LS2=16;
//END

// MOTOR SETUP
const int BIN_1 = 25;
const int BIN_2 = 26;
// setting PWM properties ----------------------------
const int freq = 25000;
const int ledChannel_1 = 1;
const int ledChannel_2 = 2;
const int resolution = 8;
//END MOTOR SETUP

 
void setup() {
  //Lim switches from other script:
  pinMode(LS1, INPUT_PULLUP);
  pinMode(LS2, INPUT_PULLUP);
  //

  //MOTOR SETUP
  // configure LED PWM functionalitites
  ledcSetup(ledChannel_1, freq, resolution);
  ledcSetup(ledChannel_2, freq, resolution);
  // attach the channel to the GPIO to be controlled
  ledcAttachPin(BIN_1, ledChannel_1);
  ledcAttachPin(BIN_2, ledChannel_2);

  //END MOTOR SETUP

  Serial.begin(9600);
  //pinMode(startSensor, INPUT_PULLUP);
  //pinMode(endSensor, INPUT_PULLUP);
}
 
void loop() {
  writeMotors(-250);
}

void writeMotors(int PWM){ 
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


//Code from other scripts:
bool checkLimLeft() {
  if (digitalRead(LS1) == LOW) {
    return true;}
  else {return false;}
}

bool checkLimRight() {
  if (digitalRead(LS2) == LOW) {
    return true;}
  else {return false;}
}


