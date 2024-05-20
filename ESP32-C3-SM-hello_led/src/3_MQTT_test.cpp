
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// WiFi credentials and MQTT server details
const char *ssid = "androidSebPro";        // SSID of your WiFi network
const char *password = "123456789";        // Password for your WiFi network
const char *mqttServer = "192.168.64.183"; // IP Address MQTT server
const int mqttPort = 1883;
const char *controllerName = "MQTT_master"; // Unique device name for controller
const char *deviceName = "ESP32-1";         // Unique device name for each ESP32
const char *mqttPublishTopic = "ESP32bootcamp";
const char *mqttSubscribeTopic = "ESP32bootcamp_control"; // switch between "ESP32bootcamp" and "ESP32bootcamp_control"
const char *deviceStatus = "Connected";

// Pin to show WiFi connection status
const int statusPin = 8;

// MQTT client setup
WiFiClient espClient;
PubSubClient mqttClient(espClient);

// Function to handle incoming messages
// Function to handle incoming messages
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
    const size_t capacity = JSON_OBJECT_SIZE(4) + 60;
    DynamicJsonDocument doc(capacity);

    // Deserialize the JSON document
    DeserializationError error = deserializeJson(doc, payload, length);

    // Test if parsing succeeds
    if (error)
    {
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.f_str());
        return;
    }

    // Extract the type of message
    const char *type = doc["type"];
    const char *device = doc["device"];
    const char *status = doc["status"];
    const char *messageContent = doc["message"];

    if (strcmp(type, "com") == 0)
    {
        // Print communication received from the same device
        Serial.println("com received from myself");
    }
    else if (strcmp(type, "control") == 0)
    {
        // Print values
        Serial.print("Device: ");
        Serial.println(device);
        Serial.print("Status: ");
        Serial.println(status);
        Serial.print("Message: ");
        Serial.println(messageContent);

        // Respond with status if the controller requests it
        if (strcmp(device, controllerName) == 0 && strcmp(messageContent, "status") == 0)
        {
            // Create JSON object
            DynamicJsonDocument responseDoc(200);
            responseDoc["type"] = "control";
            responseDoc["device"] = deviceName;
            responseDoc["status"] = deviceStatus;
            responseDoc["message"] = "status_response";

            // Serialize JSON object to a string
            char responseBuffer[512];
            serializeJson(responseDoc, responseBuffer);

            // Publish JSON string
            mqttClient.publish(mqttSubscribeTopic, responseBuffer);
        }
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
    digitalWrite(statusPin, HIGH); // Set status pin high when WiFi is connected
}

void setupMQTT()
{
    mqttClient.setServer(mqttServer, mqttPort);
    mqttClient.setCallback(messageHandler);
    reconnectMQTT();
}

void reconnectMQTT()
{
    // Loop until we're reconnected
    while (!mqttClient.connected())
    {
        Serial.print("Attempting MQTT connection...");
        // Attempt to connect
        if (mqttClient.connect(deviceName))
        {
            Serial.println("connected");
            mqttClient.subscribe(mqttSubscribeTopic);
            digitalWrite(statusPin, HIGH); // Set status pin high when MQTT is connected
        }
        else
        {
            Serial.print("failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println(" try again in 5 seconds");
            // Wait 5 seconds before retrying
            delay(5000);
            digitalWrite(statusPin, LOW); // Set status pin low when MQTT is not connected
        }
    }
}

void setup()
{
    Serial.begin(115200);
    pinMode(statusPin, OUTPUT);
    connectToWiFi();
    setupMQTT();
}

void loop()
{
    if (!mqttClient.connected())
    {
        digitalWrite(statusPin, LOW); // Set status pin low when MQTT is not connected
        reconnectMQTT();
    }
    mqttClient.loop();

    static unsigned long lastMessageTime = 0;
    if (millis() - lastMessageTime > 10000)
    {
        lastMessageTime = millis();

        // Create JSON object
        DynamicJsonDocument doc(200);
        doc["type"] = "com";
        doc["device"] = deviceName;
        doc["status"] = deviceStatus;
        doc["message"] = "hello from team _#_";

        // Serialize JSON object to a string
        char jsonBuffer[512];
        serializeJson(doc, jsonBuffer);

        // Publish JSON string
        mqttClient.publish(mqttPublishTopic, jsonBuffer);
    }
}
