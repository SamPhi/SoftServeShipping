#include <ESP32Encoder.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <math.h>
#include <Arduino.h>
#include <WiFi.h>
#include <ArduinoJson.h> //NEEDS TO BE VERSION 5 NOT 6
#include <actuator.h>
#include <esp32.h>

//Actuator setup
actuator myActuator;
//Actuator setup over

//state machine setup
esp32 myESP32;
//stae nmachine setup over

//Multi core setup
TaskHandle_t Task1;
TaskHandle_t Task2;
SemaphoreHandle_t xMutex = NULL;  // Create a mutex object
volatile int enc_shared; //Encoder value shared between two cores. Try making not volatile if issue?
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
volatile int enc_core0 = 0; // encoder count on core 0
volatile int enc_core1 = 0; // encoder count on core 1
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
    enc_core0 = encoder1.getCount();
    Serial.println("Encoder polled");
    if (xSemaphoreTake(xMutex,0)){
      Serial.println("Mutex acquired core0!");
      enc_shared = enc_core0;
      xSemaphoreGive (xMutex); 
    }
    //Serial.print("Task1 running on core ");
    //Serial.println(xPortGetCoreID());
  }
}


void loop() {
  
  //Send/recieve data
  send_data(myESP32,client);
  recieve_data(client);  

  //Update encoder value
  if (xSemaphoreTake (xMutex, portMAX_DELAY)){
    //Serial.println("Mutex acquired core 1");
    enc_core1 = enc_shared;
    xSemaphoreGive (xMutex);
    myActuator.x_pos = enc_core1;
  }

  //ESP32 commands
  myESP32.updatePhysicalVals();
  myESP32.getstate();
  myESP32.actions();
  Serial.println(myESP32.state);
  Serial.println(myESP32.phone_state);
  Serial.println(myESP32.cancel);
  Serial.println(myESP32.checkFinished());
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
void send_data(esp32 myESP32, WiFiClient client){
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

  int x_des = root["x_des"];
  int y_des = root["y_des"];
  const char* state = root["state"]; //NO WAY THIS WORKS
  bool cancel = root["cancel"];

  myESP32.x_des = x_des;
  myESP32.phone_state = String(state);
  myESP32.cancel = cancel;
}






