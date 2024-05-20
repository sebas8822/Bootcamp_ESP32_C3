#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>

// Define the PWM pin numbers for the RGB channels
const int pinR = 4; // Red LED control pin
const int pinG = 3; // Green LED control pin
const int pinB = 2; // Blue LED control pin

// Pin to show WiFi connection status
const int statusPin = 8;

// WiFi credentials and MQTT server details
const char *ssid = "androidSebPro"; // SSID of your WiFi network
const char *password = "123456789"; // Password for your WiFi network
const char *mqttServer = "192.168.111.183";
const int mqttPort = 1883;
const char *mqttPublishTopic = "IoT_project";
const char *mqttSubscribeTopic = "IoT_project";

// MQTT client setup
WiFiClient espClient;
PubSubClient mqttClient(espClient);

void setupLEDs()
{
    pinMode(pinR, OUTPUT);
    pinMode(pinG, OUTPUT);
    pinMode(pinB, OUTPUT);
    // Initialize all LEDs to off
    digitalWrite(pinR, LOW);
    digitalWrite(pinG, LOW);
    digitalWrite(pinB, LOW);
}

void messageHandler(char *topic, byte *payload, unsigned int length)
{
    Serial.print("Message arrived [");
    Serial.print(topic);
    Serial.print("] ");
    String message;
    for (int i = 0; i < length; i++)
    {
        message += (char)payload[i];
    }
    Serial.println(message);

    control_strip_light(message);
}

void control_strip_light(String message)
{
    if (message == "ON")
    {
        // Turn LEDs on
        fadeLED_On(pinR);
        fadeLED_On(pinG);
        fadeLED_On(pinB);
    }
    else if (message == "OFF")
    {
        // Turn LEDs off
        fadeLED_Off(pinR);
        fadeLED_Off(pinG);
        fadeLED_Off(pinB);
    }
}

void fadeLED_On(int pin)
{
    // Gradually increase the brightness
    for (int i = 0; i <= 255; i++)
    {
        analogWrite(pin, i);
        delay(5); // Adjust this delay to control the speed of the fade
    }
}

void fadeLED_Off(int pin)
{

    for (int i = 256; i >= 0; i--)
    {
        analogWrite(pin, i);
        delay(5); // Adjust this delay to control the speed of the fade
    }
}

void connectToWiFi()
{
    Serial.println("Connecting to WiFi...");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
}

void reconnectMQTT()
{
    // Loop until we're reconnected
    while (!mqttClient.connected())
    {
        Serial.print("Attempting MQTT connection...");
        if (mqttClient.connect("ESP32Client"))
        {
            Serial.println("connected");
            mqttClient.subscribe(mqttSubscribeTopic);
        }
        else
        {
            Serial.print("failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
        }
    }
}

void setup()
{
    Serial.begin(115200);
    pinMode(statusPin, OUTPUT);
    setupLEDs();
    connectToWiFi();
    mqttClient.setServer(mqttServer, mqttPort);
    mqttClient.setCallback(messageHandler);
    reconnectMQTT();
}

void loop()
{

    digitalWrite(statusPin, WiFi.status() == WL_CONNECTED);

    if (!mqttClient.connected())
    {
        reconnectMQTT();
    }
    mqttClient.loop();

    // Example of toggling a message every 5 seconds
    static unsigned long lastMessageTime = 0;
    static bool ledState = false; // Keeps track of the LED state to toggle between messages

    // Check if 5 seconds have passed
    if (millis() - lastMessageTime > 5000)
    {
        lastMessageTime = millis(); // Update the last message time

        // Toggle the LED state
        ledState = !ledState;

        // Publish "ON" or "OFF" based on the ledState
        if (ledState)
        {
            mqttClient.publish(mqttPublishTopic, "ON");
            Serial.println("Sent 'ON' message");
        }
        else
        {
            mqttClient.publish(mqttPublishTopic, "OFF");
            Serial.println("Sent 'OFF' message");
        }
    }
}
