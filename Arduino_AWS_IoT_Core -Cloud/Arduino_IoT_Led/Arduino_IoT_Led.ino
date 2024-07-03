#include "secrets.h"  // Your WiFi and AWS IoT credentials
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "WiFi.h"

// Define MQTT topics
#define AWS_IOT_SUBSCRIBE_TOPIC "ESP32bootcamp_control"
#define AWS_IOT_PUBLISH_TOPIC "ESP32bootcamp_com"

// Define GPIO pins for RGB LEDs and status indicators
#define pinR 4 // Red LED control pin
#define pinG 3 // Green LED control pin
#define pinB 2 // Blue LED control pin
#define statusPin 8 // GPIO pin used to indicate the status
#define buttonPin 10 // GPIO pin used for button input

// Device status and name
const char* deviceStatus = "Connected"; // Status message to be sent
const char* deviceName = THINGNAME; // Unique device name for each ESP32

WiFiClientSecure net;
PubSubClient mqttClient(net);

bool ledsOn = false;
bool lastButtonState = HIGH;

// Function to initialize LED pins and turn them off initially
void setupLEDs() {
    pinMode(pinR, OUTPUT);
    pinMode(pinG, OUTPUT);
    pinMode(pinB, OUTPUT);
    digitalWrite(pinR, LOW);
    digitalWrite(pinG, LOW);
    digitalWrite(pinB, LOW);
}

// Function to gradually turn off the LED
void fadeLED_Off(int pin) {
    for (int i = 0; i <= 255; i++) {
        analogWrite(pin, i);
        delay(5);
    }
}

// Function to gradually turn on the LED
void fadeLED_On(int pin) {
    for (int i = 255; i >= 0; i--) {
        analogWrite(pin, i);
        delay(5);
    }
}

// Function to handle incoming MQTT messages
void messageHandler(char* topic, byte* payload, unsigned int length) {
    Serial.print("Incoming message on topic: ");
    Serial.println(topic);

    char message[length + 1];
    strncpy(message, (char*)payload, length);
    message[length] = '\0';

    Serial.print("messageHandler(message): ");
    Serial.println(message);

    const size_t capacity = JSON_OBJECT_SIZE(5) + 60;
    DynamicJsonDocument doc(capacity);
    DeserializationError error = deserializeJson(doc, payload, length);
    if (error) {
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.f_str());
        return;
    }

    const char* type = doc["type"];
    const char* controller = doc["controller"];
    const char* device = doc["device"];
    const char* status = doc["status"];
    const char* messageContent = doc["message"];

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

    if (strcmp(type, "com") == 0) {
        Serial.println("com received from myself");
    } else if (strcmp(type, "control") == 0) {
        Serial.print("Controller: ");
        Serial.println(controller);
        Serial.print("Device: ");
        Serial.println(device);
        Serial.print("Status: ");
        Serial.println(status);
        Serial.print("Message: ");
        Serial.println(messageContent);

        if (strcmp(controller, "MQTT_master") == 0 && strcmp(messageContent, "status") == 0) {
            Serial.print("Sending message on topic: ");
            Serial.println(AWS_IOT_PUBLISH_TOPIC);

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

            mqttClient.publish(AWS_IOT_PUBLISH_TOPIC, responseBuffer);
        }

        if ((strcmp(device, "ALL") == 0 || strcmp(device, deviceName) == 0) &&
            strcmp(controller, "MQTT_master") == 0 &&
            strcmp(messageContent, "ON") == 0) {
            fadeLED_On(pinR);
            fadeLED_On(pinG);
            fadeLED_On(pinB);
            ledsOn = true;

            Serial.print("Sending message on topic: ");
            Serial.println(AWS_IOT_PUBLISH_TOPIC);

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

            mqttClient.publish(AWS_IOT_PUBLISH_TOPIC, jsonBuffer);
        }

        if ((strcmp(device, "ALL") == 0 || strcmp(device, deviceName) == 0) &&
            strcmp(controller, "MQTT_master") == 0 &&
            strcmp(messageContent, "OFF") == 0) {
            fadeLED_Off(pinR);
            fadeLED_Off(pinG);
            fadeLED_Off(pinB);
            ledsOn = false;

            Serial.print("Sending message on topic: ");
            Serial.println(AWS_IOT_PUBLISH_TOPIC);

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

            mqttClient.publish(AWS_IOT_PUBLISH_TOPIC, jsonBuffer);
        }
    }
}

// Function to connect to WiFi
void connectToWiFi() {
    Serial.println("Connecting to WiFi...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    digitalWrite(statusPin, HIGH);
}

// Function to set up the MQTT client
void setupMQTT() {
    net.setCACert(AWS_CERT_CA);
    net.setCertificate(AWS_CERT_CRT);
    net.setPrivateKey(AWS_CERT_PRIVATE);
    mqttClient.setServer(AWS_IOT_ENDPOINT, 8883);
    mqttClient.setCallback(messageHandler);
    reconnectMQTT();
}

// Function to reconnect to the MQTT server
void reconnectMQTT() {
    while (!mqttClient.connected()) {
        Serial.print("Attempting AWS IoT CORE MQTT connection...");
        if (mqttClient.connect(THINGNAME)) {
            Serial.println("connected");
            mqttClient.subscribe(AWS_IOT_SUBSCRIBE_TOPIC);
            digitalWrite(statusPin, HIGH);
        } else {
            Serial.print("failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
            digitalWrite(statusPin, LOW);
        }
    }
}

// Initial setup function
void setup() {
    Serial.begin(115200); // Initialize serial communication at 115200 baud
    pinMode(statusPin, OUTPUT); // Set the status pin as an output
    setupLEDs(); // Initialize LEDs
    pinMode(buttonPin, INPUT_PULLUP); // Set the button pin as input with internal pull-up resistor
    connectToWiFi(); // Connect to the WiFi network
    setupMQTT(); // Set up the MQTT client
}

// Main loop function
void loop() {
    // Check if the MQTT client is connected
    if (!mqttClient.connected()) {
        digitalWrite(statusPin, LOW); // Set status pin low when MQTT is not connected
        reconnectMQTT(); // Attempt to reconnect to the MQTT server
    }
    mqttClient.loop(); // Process incoming messages and maintain the connection

    // Read the current state of the button
    bool currentButtonState = digitalRead(buttonPin);

    // Check if the button has been pressed
    if (currentButtonState == LOW && lastButtonState == HIGH) {
        // Debounce by waiting a short period and checking again
        delay(50);
        currentButtonState = digitalRead(buttonPin);
        if (currentButtonState == LOW) {
            // Toggle the state of the LEDs
            ledsOn = !ledsOn;

            // Change the LEDs depending on the state
            if (ledsOn) {
                fadeLED_On(pinR);
                fadeLED_On(pinG);
                fadeLED_On(pinB);
            } else {
                fadeLED_Off(pinR);
                fadeLED_Off(pinG);
                fadeLED_Off(pinB);
            }

            Serial.print("Sending message on topic: ");
            Serial.println(AWS_IOT_PUBLISH_TOPIC);

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

            mqttClient.publish(AWS_IOT_PUBLISH_TOPIC, jsonBuffer);

            // Wait for the button to be released to avoid multiple toggles
            while (digitalRead(buttonPin) == LOW) {
                mqttClient.loop(); // Ensure MQTT loop is called during the wait
            }
        }
    }

    // Update the lastButtonState to the current state
    lastButtonState = currentButtonState;
}
