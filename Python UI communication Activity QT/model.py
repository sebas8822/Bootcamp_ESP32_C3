import paho.mqtt.client as mqtt
import logging
import json
import time
from PyQt5.QtCore import QObject, pyqtSignal


class MQTTModel(QObject):
    message_received = pyqtSignal(str, str)
    connection_status_changed = pyqtSignal(str)

    def __init__(self, view):
        super().__init__()
        self.view = view  # Assign the view to an instance variable
        # Local MQTT broker configuration
        self.local_server = None
        self.local_port = None
        self.local_client = mqtt.Client()
        self.publish_topic = "127.0.0.1"
        self.subscribe_topic = "1883"
        self.current_subscribe_topic = None  # Initialize the current subscribe topic
        self.local_client.on_connect = self.on_local_connect
        self.local_client.on_message = self.on_local_message
        self.controller = None
        self.devices = {
            f"ESP32-{i+1}": {"status": "Disconnected", "last_seen": 0, "state": "OFF"}
            for i in range(6)
        }

    def set_controller(self, controller):
        self.controller = controller

    def connect_local(self, server, port):
        self.local_server = server
        self.local_port = port
        if not self.local_server or not self.local_port:
            self.connection_status_changed.emit("Disconnected")
            self.controller.log_message(
                "MQTT server IP or port is required to establish the connection"
            )
            return

        try:
            self.local_client.connect(self.local_server, int(self.local_port), 60)
            self.local_client.loop_start()
        except Exception as e:
            logging.error(f"Failed to connect: {e}")
            self.connection_status_changed.emit("Disconnected")
            self.controller.log_message(
                f"Failed to connect to the MQTT server: {e}. Please check inputs!"
            )

    def disconnect_local(self):
        try:
            self.local_client.loop_stop()
            self.local_client.disconnect()
            self.connection_status_changed.emit("Disconnected")
        except Exception as e:
            logging.error(f"Failed to disconnect: {e}")
            self.controller.log_message(
                f"Failed to disconnect from the MQTT server: {e}"
            )

    def on_local_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connection_status_changed.emit("Connected")
            self.controller.log_message(
                f"Connected to MQTT server at {self.local_server}:{self.local_port}"
            )
        else:
            self.connection_status_changed.emit("Disconnected")
            self.controller.log_message(
                f"Failed to connect to MQTT server, return code {rc}"
            )

    def set_publish_topic_local(self, topic):
        self.publish_topic = topic

    def set_subscribe_topic_local(self, topic):
        if self.current_subscribe_topic:
            self.local_client.unsubscribe(self.current_subscribe_topic)
        self.subscribe_topic = topic
        self.local_client.subscribe(topic)
        self.current_subscribe_topic = topic

    def on_local_message(self, local_client, userdata, msg):
        print("I am here model")
        message = msg.payload.decode()
        self.message_received.emit(msg.topic, message)
        self.update_device_status(msg.topic, message)

    def update_device_status(self, topic, message):
        try:
            # Parse JSON message
            payload = json.loads(message)
            device = payload.get("device")
            status = payload.get("status")
            state = payload.get("state")

            if device and status and state:
                if device not in self.devices:
                    self.devices[device] = {
                        "status": None,
                        "last_seen": None,
                        "state": "OFF",
                    }
                self.devices[device]["status"] = status
                self.devices[device]["last_seen"] = time.time()
                self.devices[device]["state"] = state
                self.controller.update_device_status(device, status, state)

            else:
                raise ValueError(
                    f"Missing device, status, or state in payload: {payload}"
                )
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON from message: {message}. Error: {e}")
        except ValueError as e:
            logging.error(f"Error: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

    def publish_message_local(self, message):
        try:
            self.local_client.publish(self.publish_topic, message)
            self.controller.update_topic_log(message, "publish")
        except Exception as e:
            logging.error(f"Failed to publish message: {e}")

    def control_master(self, action):
        # Create JSON object
        status_request = {
            "type": "control",
            "controller": "MQTT_master",
            "device": "ALL",
            "status": "connected",  # assuming 'connected' is the intended status
            "message": action,
        }

        # Serialize JSON object to a string
        json_message = json.dumps(status_request)

        # Publish JSON string to the control topic
        self.publish_message_local(json_message)

    def control_device(self, device, action):
        # Create JSON object
        status_request = {
            "type": "control",
            "controller": "MQTT_master",
            "device": device,
            "status": "connected",  # assuming 'connected' is the intended status
            "message": action,
        }

        # Serialize JSON object to a string
        json_message = json.dumps(status_request)

        # Publish JSON string to the control topic
        self.publish_message_local(json_message)

    def check_device_timeouts(self):
        current_time = time.time()
        timeout_threshold = 10  # seconds

        for device, info in self.devices.items():
            if current_time - info["last_seen"] > timeout_threshold:
                if info["status"] != "Disconnected":
                    info["status"] = "Disconnected"
                    self.controller.update_device_status(device, "Disconnected", "OFF")
