# Bootcamp Session

## Bootcamp Structure

### Objective

This bootcamp is designed to introduce participants to the fundamentals of IoT development using the ESP32 microcontroller. By the end of this workshop, attendees will have hands-on experience in setting up and programming the ESP32 to control an LED both physically and via the cloud using AWS IoT Core. Participants will learn to:

1. **Understand the Basics of IoT:** Gain a foundational understanding of IoT and explore its practical applications.
2. **Hardware and Software Setup:** Learn to set up the ESP32 development environment and connect hardware components such as LEDs.
3. **Program ESP32:** Write programs using the Arduino IDE to manipulate hardware (e.g., turning on an LED with a button).
4. **Integrate with AWS IoT Core:** Configure and connect the ESP32 to AWS IoT Core to control devices remotely and securely.
5. **Develop Practical IoT Skills:** Through building a small IoT project, develop the skills needed for larger-scale IoT development.


## Requirements

- Arduino IDE
- AWS CLI

### Part 1: Introduction to IoT and ESP32 (30 minutes)

- **Overview of IoT:** Explanation of IoT and its applications.
- **Introduction to ESP32:** Discuss capabilities and suitability for IoT projects.
- **Setup:** Guide through setting up the ESP32 development environment.

### Part 2: Physical LED Control with ESP32 (1 hour)

![LED Circuit](https://github.com/sebas8822/Bootcamp_ESP32_C3/blob/main/Breadboard_ESP32_C3.png)

- **Circuit Setup:** Connecting an LED to the ESP32.
- **Programming:** Writing a simple program to control the LED physically using a button.
- **Testing and Troubleshooting:** Ensuring setups work and troubleshooting issues.

### Part 3: Connecting ESP32 to AWS IoT Core (1 hour 15 minutes)


- **Introduction to AWS IoT Core:** Explanation of AWS IoT Core and its role in IoT.
- **Configuration:** Setting up ESP32 to connect to AWS IoT Core.
- **Virtual Control:** Creating a virtual button using AWS IoT Core to control the LED.
- **Security:** Discussing security practices for IoT.

### Part 4: Final Integration and Q&A (15 minutes)

- **Integration Check:** Ensuring setups work as intended, with LED controllable both physically and virtually.
- **Q&A Session:** Answering participants' questions and providing clarifications.

## Dictionary Concepts

### General Concepts

- **SDK (Software Development Kit):** Tools and libraries for creating applications for a specific platform.
- **ESP RainMaker:** Platform by Espressif for IoT device management and cloud integration.
- **REST API (Representational State Transfer Application Programming Interface):** Rules for building and interacting with web services.
- **CLI (Command Line Interface):** Interface for typing commands to perform tasks.
- **TLS (Transport Layer Security):** Cryptographic protocol for secure communication.
- **OTA (Over-The-Air) Technology:** Methods for distributing software updates to devices wirelessly.
- **MQTT (Message Queuing Telemetry Transport):** Lightweight messaging protocol for devices with limited processing power and low bandwidth.
- **Encryption:** Process of converting information into a code to prevent unauthorized access.
- **Secure Boot:** Standard ensuring that a device boots using only trusted software.

### Cloud Concepts

- **Private Cloud:** Cloud computing environment dedicated exclusively to a single organization.
- **Public Cloud:** Cloud computing model where a service provider makes resources available to the public over the internet.
- **AIoT Platform:** Platform combining AI technologies with IoT infrastructure.
- **Serverless Application Repository (SAR):** Repository for building and publishing serverless applications.

### Communication Technologies

- **Ethernet:** Networking technology commonly used in LANs, MANs, and WANs.
- **Serial Communication:** Sending data one bit at a time over a communication channel.
- **USB (Universal Serial Bus):** Standard for cables, connectors, and protocols for connection and communication between computers and devices.
- **Short-range wireless communication:** Technologies like ZigBee, Bluetooth, Wi-Fi, NFC, and RFID.
- **Long-range wireless communication:** Technologies like eMTC, LoRa, NB-IoT, and cellular networks (2G, 3G, 4G, 5G).

### Device and Firmware Concepts

- **Espressif:** Company designing and manufacturing chipsets for the IoT industry.
- **Firmware:** Software providing control, monitoring, and data manipulation of engineered products and systems.
- **Operations and Maintenance (O&M):** Ongoing processes ensuring proper functioning of information systems and software applications.
- **RF test (Radio Frequency test):** Testing radio frequency emissions from a device.
- **ESP-IDF (Espressif IoT Development Framework):** Espressif’s development framework for ESP32 and ESP32-S Series SoCs.
- **Device-side SDK:** SDK running on the device, providing libraries and tools for application development.
- **PWM control (Pulse Width Modulation control):** Method for achieving variable voltage supply by switching power on and off rapidly.
- **Flash:** Non-volatile storage technology that can be electrically erased and reprogrammed.
- **CoAP (Constrained Application Protocol):** Web transfer protocol for constrained nodes and networks in IoT.
- **WebSocket:** Protocol providing full-duplex communication channels over a single TCP connection.
