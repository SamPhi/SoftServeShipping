#include <WiFi.h>
#include <ArduinoJson.h>


const char* ssid = "SoftServeShipping";
const char* password = "SoftServeShipping";

const uint16_t port = 12345;
const char * host = "192.168.43.1";
WiFiClient client;


    

void setup(){
  Serial.begin(115200);
  phone_connect();
  client = start_client();

}

void loop(){
  send_data("test",client);
}  

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

WiFiClient start_client(){
  WiFiClient client;

  while (!client.connect(host,port)){
    Serial.println("Connection to host failed, trying again");
    delay(1000);
  }
  Serial.println("Successfully connected to server");
  return client;
}

void send_data(String data, WiFiClient client){
  client.print(data);
}

void recieve_data(){

}
