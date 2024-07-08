#include <Arduino.h>

// Define the PWM pin numbers for the RGB channels
const int pinR = 4; // Red LED control pin
const int pinG = 3; // Green LED control pin
const int pinB = 2; // Blue LED control pin

// Define the button pin
const int buttonPin = 10;

// Variable to store the LED state
bool ledsOn = false;
bool lastButtonState = HIGH; // Assume button starts unpressed

void setup()
{
  // Set the baud of serial comunication
  Serial.begin(115200);

  // Set RGB LED control pins as outputs
  pinMode(pinR, OUTPUT);
  pinMode(pinG, OUTPUT);
  pinMode(pinB, OUTPUT);

  // Set button pin as input with internal pull-up resistor
  pinMode(buttonPin, INPUT_PULLUP);

  // Initialize all LEDs to off
  digitalWrite(pinR, LOW);
  digitalWrite(pinG, LOW);
  digitalWrite(pinB, LOW);
}

// Function to fade an LED on a specified pin (Common Anode)
void fadeLED_On(int pin)
{
  Serial.print("\nfadeLED_On PIN - ");
  Serial.println(pin);

  // Gradually decrease the brightness (0 to 255 turns the LED off)
  for (int i = 255; i >= 0; i--)
  {
    analogWrite(pin, i);
    Serial.print(i);
    Serial.print(" ");
    delay(5); // Adjust this delay to control the speed of the fade
  }
}

// Function to fade an LED off on a specified pin (Common Anode)
void fadeLED_Off(int pin)
{
  Serial.print("\nfadeLED_Off PIN - ");
  Serial.println(pin);

  // Gradually increase the brightness (0 to 255 turns the LED on)
  for (int i = 0; i <= 255; i++)
  {
    analogWrite(pin, i);
    Serial.print(i);
    Serial.print(" ");
    delay(5); // Adjust this delay to control the speed of the fade
  }
}

void loop()
{
  // Read the current state of the button
  bool currentButtonState = digitalRead(buttonPin);

  // Check if the button has been pressed
  if (currentButtonState == LOW && lastButtonState == HIGH)
  {
    // Debounce by waiting a short period and checking again
    delay(50);
    currentButtonState = digitalRead(buttonPin);
    if (currentButtonState == LOW)
    {
      // Toggle the state of the LEDs
      ledsOn = !ledsOn;

      // Change the LEDs depending on the state
      if (ledsOn)
      {
        fadeLED_On(pinR);
        fadeLED_On(pinG);
        fadeLED_On(pinB);
      }
      else
      {
        fadeLED_Off(pinR);
        fadeLED_Off(pinG);
        fadeLED_Off(pinB);
      }

      // Wait for the button to be released to avoid multiple toggles
      while (digitalRead(buttonPin) == LOW)
      {
        // Do nothing until button is released
      }
    }
  }

  // Update the lastButtonState to the current state
  lastButtonState = currentButtonState;
}
