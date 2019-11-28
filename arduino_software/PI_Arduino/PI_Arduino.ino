#include <Ultrasonic.h>

#define TRIGGER_PIN 7
#define ECHO_PIN 8

Ultrasonic ultrasonic(TRIGGER_PIN, ECHO_PIN);

int distance;
String inputString = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete

void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
}

void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    digitalWrite(LED_BUILTIN, HIGH);
    char inChar = (char)Serial.read();

    if (inChar == '\n') {
      stringComplete = true;
    } else {
      // add it to the inputString:
      inputString += inChar;
    }
  }
}

void loop() {
  if (stringComplete) {
    distance = ultrasonic.read();;
    Serial.println(distance);
    inputString = "";
    stringComplete = false;
    digitalWrite(LED_BUILTIN, LOW);
  }
}
