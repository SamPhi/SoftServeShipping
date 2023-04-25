#include <ESP32Encoder.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <math.h>
#include <Arduino.h>
#include <Bounce2.h>

//This code now works and drives motors on core0 whilst printing encoder on core 1
//Issue: Interrupt that actually polls encoder is still running on core0, need to learn how to move timer + interrupt to second core.
//Next steps:
//1) Copy rest of ESP32 functions to Arduino
//2) 

//FoR MULTI CORE STUFF:
TaskHandle_t Task1;
TaskHandle_t Task2;
//MUTI CORE INIT OVER

#define BTN 15  // declare the button ED pin number
#define LED_PIN 13 // declare the builtin LED pin number

Bounce2::Button button = Bounce2::Button(); // declares the button library as an object

// MOTOR 1 (25 and 26)
#define BIN_1 25
#define BIN_2 26

// JOYSTICK CONTROLLER
int x_key = 34;
int y_key = 33;

int y_pos = 0;
int x_pos = 0;
bool zeroed = true;

volatile bool buttonIsPressed = false;
int state = 1; //initial state that is desered at start of code

// setting PWM properties ----------------------------
const int freq = 25000;
const int ledChannel_1 = 1;
const int ledChannel_2 = 2;
const int resolution = 8;
const int MAX_PWM_VOLTAGE = 255;
const int NOM_PWM_VOLTAGE = 150;


//Setup Speed Measurement variables ----------------------------
int speed1 = 0;
volatile int count1 = 0; // encoder count

//Setup interrupt variables ----------------------------
ESP32Encoder encoder1;
volatile bool interruptCounter = false;    // check timer interrupt 1
volatile bool deltaT = false;     // check timer interrupt 2
int totalInterrupts = 0;   // counts the number of triggering of the alarm
hw_timer_t * timer0 = NULL;
hw_timer_t * timer1 = NULL;
portMUX_TYPE timerMux0 = portMUX_INITIALIZER_UNLOCKED;
portMUX_TYPE timerMux1 = portMUX_INITIALIZER_UNLOCKED;


int speed1D = 0;
int D1 = 0;
int enc_count = 0;
int dummy = 5;

//Initialization ------------------------------------
void IRAM_ATTR isr() {  // the function to be called when interrupt is triggered
  buttonIsPressed = button.pressed();
}

void IRAM_ATTR onTime0() {
  portENTER_CRITICAL_ISR(&timerMux0);
  interruptCounter = true; // the function to be called when timer interrupt is triggered
  portEXIT_CRITICAL_ISR(&timerMux0);
}

void IRAM_ATTR onTime1() {
  portENTER_CRITICAL_ISR(&timerMux1);
  count1 = encoder1.getCount();
  //encoder1.clearCount ( );
  deltaT = true; // the function to be called when timer interrupt is triggered
  portEXIT_CRITICAL_ISR(&timerMux1);
}



void setup() {
  //button setup
  button.attach(BTN, INPUT);
  pinMode(BTN, INPUT_PULLUP);
  
  button.interval(50);
  button.setPressedState(HIGH);
  //allocation of pins to be used for LEDs and Modes
  pinMode(LED_PIN, OUTPUT);
  pinMode(x_key, INPUT);
  pinMode(y_key, INPUT);
  //pinMode(LED_mode3, OUTPUT);

  // configure LED PWM functionalitites
  ledcSetup(ledChannel_1, freq, resolution);
  ledcSetup(ledChannel_2, freq, resolution);

  // attach the channel to the GPIO to be controlled
  ledcAttachPin(BIN_1, ledChannel_1);
  ledcAttachPin(BIN_2, ledChannel_2);

  //attach button interrupt
  attachInterrupt(BTN, isr, CHANGE);

  Serial.begin(115200); 
  
  ESP32Encoder::useInternalWeakPullResistors = UP; // Enable the weak pull up resistors
  encoder1.attachHalfQuad(39, 36); // Attache pins for use as encoder pins  M1(36,39)   M2(4,16)   M3(17,21)
  encoder1.setCount(0);  // set starting count value after attaching

  // initilize timer
  timer0 = timerBegin(0, 80, true);  // timer 0, MWDT clock period = 12.5 ns * TIMGn_Tx_WDT_CLK_PRESCALE -> 12.5 ns * 80 -> 1000 ns = 1 us, countUp
  timerAttachInterrupt(timer0, &onTime0, true); // edge (not level) triggered
  timerAlarmWrite(timer0, 5000000, true); // 5000000 * 1 us = 5 s, autoreload true

  timer1 = timerBegin(1, 80, true);  // timer 1, MWDT clock period = 12.5 ns * TIMGn_Tx_WDT_CLK_PRESCALE -> 12.5 ns * 80 -> 1000 ns = 1 us, countUp
  timerAttachInterrupt(timer1, &onTime1, true); // edge (not level) triggered
  timerAlarmWrite(timer1, 10000, true); // 10000 * 1 us = 10 ms, autoreload true

  // at least enable the timer alarms
  timerAlarmEnable(timer0); // enable
  timerAlarmEnable(timer1); // enable

  //Serial.println("BGantry Mode 1 (not stabilized)");
  delay(100);



  //create a task that will be executed in the Task1code() function, with priority 1 and executed on core 0
  xTaskCreatePinnedToCore(
                    Task1code,   /* Task function. */
                    "Task1",     /* name of task. */
                    10000,       /* Stack size of task */
                    NULL,        /* parameter of the task */
                    1,           /* priority of the task */
                    &Task1,      /* Task handle to keep track of created task */
                    0);          /* pin task to core 0 */                  
  delay(500); 

  //create a task that will be executed in the Task2code() function, with priority 1 and executed on core 1

  //MULTI CORE SETUP OVER
}

//Task1code: blinks an LED every 1000 ms
void Task1code( void * pvParameters ){
  for(;;){
    enc_count = count1;
    Serial.println(enc_count);
  } 
}

void loop() {
  //Serial.print("Task2 running on core ");
  //Serial.println(xPortGetCoreID());
  //Serial.print("Task1 running on core ");
    //Serial.println(xPortGetCoreID());
    speed1D = map(analogRead(x_key),0,3600,-1000,1000);
    D1 = speed1D;
    if (D1>1000) {
      D1 = 1000;
    }
    if (D1<-1000) {
      D1 = -1000;
  }
  driveMotors();
  
}

void driveMotors() {
  // Move the DC motor forward at maximum speed
  if (D1 >= 0) {
    ledcWrite(ledChannel_1, LOW);
    ledcWrite(ledChannel_2, D1);
  }
  else if (D1 < 0) {
    ledcWrite(ledChannel_1, -D1);
    ledcWrite(ledChannel_2, LOW);
  }
  else {
    ledcWrite(ledChannel_1, LOW);
    ledcWrite(ledChannel_2, LOW);
  }
}