#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// WiFi credentials and MQTT server details
const char *ssid = "androidSebPro";                       // SSID of your WiFi network
const char *password = "123456789";                       // Password for your WiFi network
const char *mqttServer = "192.168.64.183";                // IP Address of the MQTT server
const int mqttPort = 1883;                                // Port of the MQTT server
const char *controllerName = "MQTT_master";               // Unique device name for the controller
const char *deviceName = "ESP32-1";                       // Unique device name for each ESP32
const char *mqttPublishTopic = "ESP32bootcamp_com";       // Topic to publish messages
const char *mqttSubscribeTopic = "ESP32bootcamp_control"; // Topic to subscribe to control messages
const char *deviceStatus = "Connected";                   // Status message to be sent

// Define the PWM pin numbers for the RGB channels
const int pinR = 4; // Red LED control pin
const int pinG = 3; // Green LED control pin
const int pinB = 2; // Blue LED control pin

// Pin to show WiFi connection status
const int statusPin = 8; // GPIO pin used to indicate the status

// Define the button pin
const int buttonPin = 10; // GPIO pin used for button input

// MQTT client setup
WiFiClient espClient;               // Create a WiFi client
PubSubClient mqttClient(espClient); // Pass the WiFi client to the MQTT client

// LED state variables
bool ledsOn = false;         // Initial state of LEDs
bool lastButtonState = HIGH; // Assume button starts unpressed

// Function to initialize LED pins and turn them off initially
void setupLEDs()
{
    pinMode(pinR, OUTPUT);
    pinMode(pinG, OUTPUT);
    pinMode(pinB, OUTPUT);
    digitalWrite(pinR, LOW);
    digitalWrite(pinG, LOW);
    digitalWrite(pinB, LOW);
}

// Function to handle incoming MQTT messages
void messageHandler(char *topic, byte *payload, unsigned int length)
{
    Serial.print("Incoming message on topic: ");
    Serial.println(topic);

    // Convert payload to a null-terminated string
    char message[length + 1]; // +1 for the null terminator
    strncpy(message, (char *)payload, length);
    message[length] = '\0'; // Ensure null termination

    // Print the message
    Serial.print("messageHandler(message): ");
    Serial.println(message);

    // Allocate the JSON document
    const size_t capacity = JSON_OBJECT_SIZE(5) + 60; // Adjusted capacity for additional fields
    DynamicJsonDocument doc(capacity);

    // Deserialize the JSON document
    DeserializationError error = deserializeJson(doc, payload, length);
    if (error)
    {
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.f_str());
        return;
    }

    // Extract the type of message
    const char *type = doc["type"];
    const char *controller = doc["controller"];
    const char *device = doc["device"];
    const char *status = doc["status"];
    const char *messageContent = doc["message"];

    Serial.print("Type: ");
    Serial.println(type);
    Serial.print("Controller: ");
    Serial.println(controller);
    Serial.print("Device: ");
    Serial.println(device);
    Serial.print("Status: ");
    Serial.println(status);
    Serial.print("Message: ");
    Serial.println(messageContent);

    // If the message is from itself
    if (strcmp(type, "com") == 0)
    {
        Serial.println("com received from myself");
    }
    else if (strcmp(type, "control") == 0)
    {
        // Print values
        Serial.print("Controller: ");
        Serial.println(controller);
        Serial.print("Device: ");
        Serial.println(device);
        Serial.print("Status: ");
        Serial.println(status);
        Serial.print("Message: ");
        Serial.println(messageContent);

        // Respond with status if the controller requests it
        if (strcmp(controller, controllerName) == 0 && strcmp(messageContent, "status") == 0)
        {
            Serial.print("Sending message on topic: ");
            Serial.println(mqttPublishTopic);

            Serial.print("Device: ");
            Serial.println(deviceName);
            Serial.print("Status: ");
            Serial.println(deviceStatus);
            Serial.print("State: ");
            Serial.println(ledsOn ? "ON" : "OFF");
            Serial.print("Message: ");
            Serial.println("status_response");

            DynamicJsonDocument responseDoc(200);
            responseDoc["type"] = "control";
            responseDoc["device"] = deviceName;
            responseDoc["status"] = deviceStatus;
            responseDoc["state"] = ledsOn ? "ON" : "OFF";
            responseDoc["message"] = "status_response";

            char responseBuffer[512];
            serializeJson(responseDoc, responseBuffer);

            mqttClient.publish(mqttPublishTopic, responseBuffer);
        }

        // Control the strip light based on the status
        if ((strcmp(device, "ALL") == 0 || strcmp(device, deviceName) == 0) &&
            strcmp(controller, controllerName) == 0 &&
            strcmp(messageContent, "ON") == 0)
        {
            fadeLED_On(pinR);
            fadeLED_On(pinG);
            fadeLED_On(pinB);
            ledsOn = true;

            Serial.print("Sending message on topic: ");
            Serial.println(mqttPublishTopic);

            Serial.print("Device: ");
            Serial.println(deviceName);
            Serial.print("Status: ");
            Serial.println(deviceStatus);
            Serial.print("Status: ");
            Serial.println(ledsOn);
            Serial.print("Message: ");
            Serial.println("state has changed");

            DynamicJsonDocument doc(200);
            doc["type"] = "com";
            doc["device"] = deviceName;
            doc["status"] = deviceStatus;
            doc["state"] = ledsOn ? "ON" : "OFF";
            doc["message"] = "state has changed";

            char jsonBuffer[512];
            serializeJson(doc, jsonBuffer);

            mqttClient.publish(mqttPublishTopic, jsonBuffer);
        }

        if ((strcmp(device, "ALL") == 0 || strcmp(device, deviceName) == 0) &&
            strcmp(controller, controllerName) == 0 &&
            strcmp(messageContent, "OFF") == 0)
        {
            fadeLED_Off(pinR);
            fadeLED_Off(pinG);
            fadeLED_Off(pinB);
            ledsOn = false;

            Serial.print("Sending message on topic: ");
            Serial.println(mqttPublishTopic);

            Serial.print("Device: ");
            Serial.println(deviceName);
            Serial.print("Status: ");
            Serial.println(deviceStatus);
            Serial.print("Status: ");
            Serial.println(ledsOn);
            Serial.print("Message: ");
            Serial.println("state has changed");

            DynamicJsonDocument doc(200);
            doc["type"] = "com";
            doc["device"] = deviceName;
            doc["status"] = deviceStatus;
            doc["state"] = ledsOn ? "ON" : "OFF";
            doc["message"] = "state has changed";

            char jsonBuffer[512];
            serializeJson(doc, jsonBuffer);

            mqttClient.publish(mqttPublishTopic, jsonBuffer);
        }
    }
}

// Function to gradually turn off the LED
void fadeLED_Off(int pin)
{
    for (int i = 0; i <= 255; i++)
    {
        analogWrite(pin, i);
        delay(5);
    }
}

// Function to gradually turn on the LED
void fadeLED_On(int pin)
{
    for (int i = 255; i >= 0; i--)
    {
        analogWrite(pin, i);
        delay(5);
    }
}

// Function to connect to WiFi
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
    digitalWrite(statusPin, HIGH); // Set status pin high when WiFi is connected
}

// Function to set up the MQTT client
void setupMQTT()
{
    mqttClient.setServer(mqttServer, mqttPort);
    mqttClient.setCallback(messageHandler);
    reconnectMQTT();
}

// Function to reconnect to the MQTT server
void reconnectMQTT()
{
    while (!mqttClient.connected())
    {
        Serial.print("Attempting MQTT connection...");
        if (mqttClient.connect(deviceName))
        {
            Serial.println("connected");
            mqttClient.subscribe(mqttSubscribeTopic); // Subscribe to the control topic
            digitalWrite(statusPin, HIGH);            // Set status pin high when MQTT is connected
        }
        else
        {
            Serial.print("failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
            digitalWrite(statusPin, LOW); // Set status pin low when MQTT is not connected
        }
    }
}

// Initial setup function
void setup()
{
    Serial.begin(115200);             // Initialize serial communication at 115200 baud
    pinMode(statusPin, OUTPUT);       // Set the status pin as an output
    setupLEDs();                      // Initialize LEDs
    pinMode(buttonPin, INPUT_PULLUP); // Set the button pin as input with internal pull-up resistor
    connectToWiFi();                  // Connect to the WiFi network
    setupMQTT();                      // Set up the MQTT client
}

// Main loop function
void loop()
{
    // Check if the MQTT client is connected
    if (!mqttClient.connected())
    {
        digitalWrite(statusPin, LOW); // Set status pin low when MQTT is not connected
        reconnectMQTT();              // Attempt to reconnect to the MQTT server
    }
    mqttClient.loop(); // Process incoming messages and maintain the connection

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

            Serial.print("Sending message on topic: ");
            Serial.println(mqttPublishTopic);

            Serial.print("Device: ");
            Serial.println(deviceName);
            Serial.print("Status: ");
            Serial.println(deviceStatus);
            Serial.print("Status: ");
            Serial.println(ledsOn);
            Serial.print("Message: ");
            Serial.println("state has changed");

            // Create JSON object to notify state change
            DynamicJsonDocument doc(200);
            doc["type"] = "com";
            doc["device"] = deviceName;
            doc["status"] = deviceStatus;
            doc["state"] = ledsOn ? "ON" : "OFF";
            doc["message"] = "state has changed";

            char jsonBuffer[512];
            serializeJson(doc, jsonBuffer);

            mqttClient.publish(mqttPublishTopic, jsonBuffer);

            // Wait for the button to be released to avoid multiple toggles
            while (digitalRead(buttonPin) == LOW)
            {
                mqttClient.loop(); // Ensure MQTT loop is called during the wait
            }
        }
    }

    // Update the lastButtonState to the current state
    lastButtonState = currentButtonState;
}