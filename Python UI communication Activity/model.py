import paho.mqtt.client as mqtt
import threading
import time
import json
import logging


class MQTTModel:
    def __init__(self, server, port):
        self.server = server
        self.port = port
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.publish_topic = ""
        self.subscribe_topic = ""
        self.devices = {
            f"ESP32-{i+1}": {"status": "Disconnected", "last_seen": 0} for i in range(6)
        }
        self.controller = None

    def connect(self):
        self.client.connect(self.server, self.port, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        try:
            if rc == 0:
                self.controller.log_message("Connected to MQTT Broker")
                self.controller.update_status("Connected")
                # Subscribe to status topics of all devices
                self.client.subscribe(self.subscribe_topic)
            else:
                self.controller.log_message(f"Failed to connect, return code {rc}")
                self.controller.update_status("Disconnected")
        except Exception as e:
            logging.error(f"Failed on_connect: {e}")

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode()
        self.controller.topic_log_message(
            f"Received message: {message} on topic {msg.topic}"
        )
        self.update_device_status(msg.topic, message)

    def set_publish_topic(self, topic):
        self.publish_topic = topic

    def set_subscribe_topic(self, topic):
        self.subscribe_topic = topic
        self.client.subscribe(topic)

    def publish_message(self, message):
        try:
            self.client.publish(self.publish_topic, message)
        except Exception as e:
            logging.error(f"Failed to publish message: {e}")

    def publish_message_input_field(self, message):
        try:
            json_message = self.package_message(message)
            self.client.publish(self.publish_topic, json_message)
        except Exception as e:
            logging.error(f"Failed to publish message: {e}")

    def package_message(self, custom_message):
        packaged_message = {
            "type": "control",
            "device": "MQTT_master",
            "status": "connected",  # assuming 'connected' is the intended status
            "message": custom_message,
        }
        return json.dumps(packaged_message)

    def set_controller(self, controller):
        self.controller = controller

    def update_device_status(self, topic, message):
        try:
            # Parse JSON message
            payload = json.loads(message)
            device = payload.get("device")
            status = payload.get("status")

            if device and status:
                if device not in self.devices:
                    self.devices[device] = {"status": None, "last_seen": None}
                self.devices[device]["status"] = status
                self.devices[device]["last_seen"] = time.time()
                self.controller.update_device_status(device, status)
            else:
                raise ValueError(f"Missing device or status in payload: {payload}")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON from message: {message}. Error: {e}")
        except ValueError as e:
            logging.error(f"Error: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

    def control_device(self, device, action):
        topic = f"{device}/control"
        self.client.publish(topic, action)
        self.controller.log_message(f"Sent {action} to {device}")

    def request_status(self):
        # Create JSON object
        status_request = {
            "type": "control",
            "device": "MQTT_master",
            "status": "connected",  # assuming 'connected' is the intended status
            "message": "status",
        }

        # Serialize JSON object to a string
        json_message = json.dumps(status_request)

        # Publish JSON string to the control topic
        self.publish_message(json_message)

    def check_device_timeouts(self):
        current_time = time.time()
        timeout_threshold = 20  # seconds

        for device, info in self.devices.items():
            if current_time - info["last_seen"] > timeout_threshold:
                if info["status"] != "Disconnected":
                    info["status"] = "Disconnected"
                    self.controller.update_device_status(device, "Disconnected")
