#include <Arduino.h>

///REQUIRED ADDITIONAL IMPORTS

/// END IMPORTS

int startSensor=17;
int endSensor=21;
 
void setup() {
  Serial.begin(9600);
  pinMode(startSensor, INPUT_PULLUP);
  pinMode(endSensor, INPUT_PULLUP);
}
 
void loop() {
  Serial.println(checkStart());
  Serial.println(checkEnd());  
}

//Returns true if left hall effect sensor triggered, otherwise false
bool checkStart() {
  if (digitalRead(startSensor) == LOW) {
    return true;}
  else {return false;}
}

//Returns true if right hall effect sensor triggered, otherwise false
bool checkEnd() {
  if (digitalRead(endSensor) == LOW) {
    return true;}
  else {return false;}
}
