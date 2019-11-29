#include <Ultrasonic.h>

#define TRIGGER_PIN 7
#define ECHO_PIN 8

Ultrasonic ultrasonic(TRIGGER_PIN, ECHO_PIN);

int distance;

void setup() {
  Serial.begin(9600);
}

void loop() {
  distance = ultrasonic.read();
  Serial.println(distance);
  delay(1000);
}
