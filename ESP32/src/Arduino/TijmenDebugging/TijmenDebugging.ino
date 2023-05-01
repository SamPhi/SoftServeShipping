#include <Arduino.h>
#include <ESP32Encoder.h>
#include <actuator.h>
# define M_PI           3.14159265358979323846  /* pi */



//Create actuator
actuator myActuator;

//Code from other scripts:

ESP32Encoder encoder1;
int enc_core1;



//Physical parameters:
const float g = 9.81;
const float massGantry = 0.5; //Kg
const float massContainer = 0.1; //Kg
const float lengthCable = 0.25; //m
const float dt = 0.001;

int zeroPos = 0;
int last_x_pos = 0;
float lastTheta = 0;
int x=0;
int PWM= 0;




void setup() {
  //encoder
  
  Serial.begin(115200);
  ESP32Encoder::useInternalWeakPullResistors = UP; // Enable the weak pull up resistors
  encoder1.attachHalfQuad(39, 36); // Attache pins for use as encoder pins  M1(36,39)   M2(4,16)   M3(17,21)
  encoder1.setCount(0);  // set starting count value after attaching

}

int auto_u_container(float dth,float g,float l,float m1,float m2,float t,float th,int x,int x_des) {
    //AUTO_U_CONTAINER
    //    U = AUTO_U_CONTAINER(DTH,G,L,M1,M2,T,TH,X,X_DES)

    //    This function was generated by the Symbolic Math Toolbox version 9.2.
    //    25-Apr-2023 12:37:52

    float t2 = cos(th);
    float t3 = sin(th);
    float t4 = sq(t2);
    float u = -(l*(m1+m2-m2*t4)*(dth*(-1.0/2.0)-th*3.0e+1+x*(3.0/2.0)-x_des*(3.0/2.0)+((x/10-x_des/10+8.630374447253786*pow(10,-4))*3.0e+1)/(t-10)+(g*t3*(m1+m2))/(l*(m1+m2*sq(t3)))+(sq(dth)*m2*t2*t3*2.0)/(m1*2.0+m2-m2*(t4*2.0-1.0))))/t2;
    return int(u);
}

void autoMove(int x_des) {

    //define state vars
    float l = lengthCable;
    float mg = massGantry; //Kg
    float mc = massContainer; //Kg
    float t = dt;
    float th = myActuator.getTheta()*M_PI/180;
    float th_past = lastTheta;
    float dth = (th_past - th)/dt;
    
    
    //cout << "X pos " << x;

    PWM = auto_u_container(dth,g,l,mg,mc,t,th,x,x_des);
    
    //Actually write calculated PWMN vals to motor
    myActuator.writeMotors(PWM);

    //Update past values for next run
    last_x_pos = x;
    lastTheta = th;
    return;
}

bool homed = false;

void loop() {
  if (homed == false){
    homed = myActuator.homingFunction();
  }
  else{
    x = encoder1.getCount();
    autoMove(-400);
    Serial.println(x);
  }
}