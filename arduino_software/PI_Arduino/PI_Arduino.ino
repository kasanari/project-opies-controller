#include <Ultrasonic.h>

#define TRIGGER_PIN 7
#define ECHO_PIN 8

Ultrasonic ultrasonic(TRIGGER_PIN, ECHO_PIN);

int distance;
int incomingByte;

void setup(){
Serial.begin(115200);
}

void loop(){
  if (Serial.available() > 0) {
    distance = ultrasonic.read();
    incomingByte = Serial.read(); 
    Serial.println(distance);
  }
}
