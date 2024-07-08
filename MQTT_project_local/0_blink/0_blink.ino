#include <Arduino.h>
// the setup function runs once when you press reset or power the board
void setup()
{
    Serial.begin(96200);
    // initialize digital pin LED_BUILTIN as an output.
    pinMode(8, OUTPUT);
}

// the loop function runs over and over again forever
void loop()
{
    digitalWrite(8, HIGH); // turn the LED on (HIGH is the voltage level)
    Serial.println("led HIGH");
    delay(300);          // wait for a second
    digitalWrite(8, LOW); // turn the LED off by making the voltage LOW
    Serial.println("led LOW");
    delay(300); // wait for a second
}
