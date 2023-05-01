#include <ESP32Encoder.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <math.h>
#include <Arduino.h>
#include <WiFi.h>
#include <ArduinoJson.h> //NEEDS TO BE VERSION 5 NOT 6
#include <actuator.h>
#include <esp32.h>

//state machine setup
esp32 myESP32;
//stae nmachine setup over

//Multi core setup
TaskHandle_t Task1;
TaskHandle_t Task2;
SemaphoreHandle_t xMutex = NULL;  // Create a mutex object


volatile int x_pos_core1 = 0;
volatile bool homed_core1 = false;
volatile bool finished_core1 = false;
volatile int theta_core1 = 0;
int x_des_core1;
int y_des_core1;
const char* state_core1; 
bool cancel_core1;


volatile int x_pos_core0 = 0;
volatile bool homed_core0 = false;
volatile bool finished_core0 = false;
volatile int theta_core0 = 0;
int x_des_core0;
int y_des_core0;
const char* state_core0; 
bool cancel_core0;

volatile int x_pos_shared = 0;
volatile bool homed_shared = false;
volatile bool finished_shared = false;
volatile int theta_shared = 0;
int x_des_shared;
int y_des_shared;
const char* state_shared; 
bool cancel_shared;

#define INCLUDE_vTaskDelete 1 //For delay variable in xSemaphoreTake(Mutex, delay) function
//Multi core setup over

//Wifi setup
const char* ssid = "SoftServeShipping";
const char* password = "SoftServeShipping";

const uint16_t port = 12345;
const char * host = "192.168.43.1";
WiFiClient client;
//WIFI setup over

//Encoder setup
ESP32Encoder encoder1;
//Encoder setup over

void setup() {
  //Phone comms setup
  phone_connect();
  client = start_client();

  //Inter core comms setup
  xMutex = xSemaphoreCreateMutex();  // crete a mutex object

  Serial.begin(115200); 

//Encoder setup  
  ESP32Encoder::useInternalWeakPullResistors = UP; // Enable the weak pull up resistors
  encoder1.attachHalfQuad(39, 36); // Attache pins for use as encoder pins  M1(36,39)   M2(4,16)   M3(17,21)
  encoder1.setCount(0);  // set starting count value after attaching

  // Callibrate potentiometer
  myESP32.myActuator.callibratePot();

  //create a task that will be executed in the Task1code() function, with priority 1 and executed on core 0
  xTaskCreatePinnedToCore(
                    Task1code,   /* Task function. */
                    "Task1",     /* name of task. */
                    4000,       /* Stack size of task */
                    NULL,        /* parameter of the task */
                    1,           /* priority of the task */
                    &Task1,      /* Task handle to keep track of created task */
                    0);          /* pin task to core 0 */                  
  delay(500); 

  //create a task that will be executed in the Task2code() function, with priority 1 and executed on core 1

}

//Task1code: reads encoder and sends to main loop() if possible using mutex
void Task1code( void * pvParameters ){
  for(;;){
    //ESP32 commands
    myESP32.x_pos = encoder1.getCount(); //Update encoder
    //MAYBE ADD myESP32.myActuator.x_pos here??
    myESP32.updatePhysicalVals(); //Update other vals
    myESP32.getstate(); //Update state
    myESP32.actions(); //Act
  
    if (xSemaphoreTake(xMutex,0)){
      Serial.println("Mutex acquired core0!");
      //Values to send
      x_pos_shared = myESP32.x_pos;
      homed_shared = myESP32.homed;
      finished_shared = myESP32.finished;
      theta_shared = myESP32.theta;

      //Recieve values
      myESP32.x_des = x_des_shared;
      myESP32.phone_state = state_shared;
      myESP32.cancel = cancel_shared;

      xSemaphoreGive (xMutex); 
    }
    //Serial.print("Task1 running on core ");
    //Serial.println(xPortGetCoreID());
  }
}


void loop() {
  
  //Update encoder value
  if (xSemaphoreTake (xMutex, portMAX_DELAY)){ //TRY DELAY 0
    //Serial.println("Mutex acquired core 1");
    //Get values to send
    x_pos_core1 = x_pos_shared; 
    homed_core1 = homed_shared;
    finished_core1 = finished_shared;
    theta_core1 = theta_shared;

    //Update values to share
    x_des_shared = x_des_core1;
    state_shared = state_core1;
    cancel_shared = cancel_core1;

    xSemaphoreGive (xMutex);
    
  }
  //Send/recieve data
  send_data(x_pos_core1,homed_core1,finished_core1,theta_core1,client);
  recieve_data(client);  
}

//Connect to wifi network
void phone_connect(){
    WiFi.begin(ssid, password);
    Serial.println("\nConnecting");

    while(WiFi.status() != WL_CONNECTED){
        Serial.print(".");
        delay(100);
    }

    Serial.println("\nConnected to the WiFi network");
    Serial.print("Local ESP32 IP: ");
    Serial.println(WiFi.localIP());
}

//Create client to communicate on server
WiFiClient start_client(){
  WiFiClient client;

  while (!client.connect(host,port)){
    Serial.println("Connection to host failed, trying again");
    delay(1000);
  }
  Serial.println("Successfully connected to server");
  return client;
}

//Send data over socket
void send_data(int x_pos,bool homed,bool finished,int theta, WiFiClient client){
  StaticJsonBuffer<200> jsonBuffer;
  JsonObject& arrToSend = jsonBuffer.createObject();

  arrToSend["x_pos"] = myESP32.x_pos;
  arrToSend["y_pos"] = 0;
  arrToSend["homed"] = myESP32.homed;
  arrToSend["finished"] = myESP32.finished;
  arrToSend["theta"] = myESP32.theta;

  char data[100];
  arrToSend.printTo(data);
  client.print(data); //client.write() may work better for json
}

//Recieve data over socket

void recieve_data(WiFiClient client){
  StaticJsonBuffer<200> jsonBuffer;
  char json[80];
  client.readBytesUntil('\n',json,80);
  //Serial.println(json);
  // if (json.length() == 0){
  //   return "No Data";
  // }
  
  JsonObject& root = jsonBuffer.parseObject(json);
  //Serial.println(json);
  //Check if JSON in valid format
  //if(!root.success()){
  //  return "FAIL";     
  //}

  x_des_core1 = root["x_des"];
  //y_des_core1 = root["y_des"];
  state_core1 = root["state"]; //NO WAY THIS WORKS
  cancel_core1 = root["cancel"];
}






