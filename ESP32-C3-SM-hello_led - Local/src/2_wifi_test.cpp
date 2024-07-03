#include <Arduino.h>
#include <WiFi.h>

// WiFi credentials
const char *ssid = "androidSebPro"; // SSID of your WiFi network
const char *password = "123456789"; // WiFi password

// Pin to show WiFi connection status
const int statusPin = 8;

void connectToWiFi()
{
    Serial.println("Connecting to WiFi...");
    WiFi.begin(ssid, password); // Start the connection process

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }

    Serial.println("\nWiFi connected.");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
}

void reconnectToWiFi()
{
    if (WiFi.status() != WL_CONNECTED)
    {
        Serial.println("Reconnecting to WiFi...");
        WiFi.begin(ssid, password);
        unsigned long startTime = millis();
        while (WiFi.status() != WL_CONNECTED && millis() - startTime < 10000)
        {
            delay(500);
            Serial.print(".");
        }
        if (WiFi.status() == WL_CONNECTED)
        {
            Serial.println("\nWiFi reconnected.");
            Serial.print("IP address: ");
            Serial.println(WiFi.localIP());
        }
        else
        {
            Serial.println("\nFailed to reconnect.");
        }
    }
}

void setup()
{
    Serial.begin(115200);
    pinMode(statusPin, OUTPUT);

    connectToWiFi();
}

void loop()
{
    static unsigned long lastCheckTime = 0;
    const long checkInterval = 10000; // Check every 10 seconds

    if (millis() - lastCheckTime >= checkInterval)
    {
        lastCheckTime = millis();

        if (WiFi.status() == WL_CONNECTED)
        {
            Serial.println("WiFi connected.");
            digitalWrite(statusPin, 1);
        }
        else
        {
            digitalWrite(statusPin, 0);
            reconnectToWiFi();
        }
    }
}
