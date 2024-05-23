import paho.mqtt.client as mqtt
import time
import json
import logging


class MQTTModel:
    def __init__(
        self,
        local_server,
        local_port,
        aws_server,
        aws_port,
        aws_client_id,
        aws_username,
        aws_password,
    ):
        # Local MQTT broker configuration
        self.local_server = local_server
        self.local_port = local_port
        self.local_client = mqtt.Client()
        self.local_client.on_connect = self.on_local_connect
        self.local_client.on_message = self.on_local_message

        # AWS IoT Core configuration
        self.aws_server = aws_server
        self.aws_port = aws_port
        self.aws_client = mqtt.Client(client_id=aws_client_id)
        self.aws_client.username_pw_set(aws_username, aws_password)
        self.aws_client.on_connect = self.on_aws_connect
        self.aws_client.on_message = self.on_aws_message

        self.publish_topic = ""
        self.subscribe_topic = "ESP32bootcamp_com"
        self.devices = {
            f"ESP32-{i+1}": {"status": "Disconnected", "last_seen": 0, "state": "OFF"}
            for i in range(6)
        }
        self.controller = None

    def connect(self):
        try:
            self.local_client.connect(self.local_server, self.local_port, 60)
            self.local_client.loop_start()

            self.aws_client.connect(self.aws_server, self.aws_port, 60)
            self.aws_client.loop_start()
        except Exception as e:
            logging.error(f"Failed to connect: {e}")

    def disconnect(self):
        try:
            self.local_client.loop_stop()
            self.local_client.disconnect()
            self.aws_client.loop_stop()
            self.aws_client.disconnect()
        except Exception as e:
            logging.error(f"Failed to disconnect: {e}")

    def on_local_connect(self, client, userdata, flags, rc):
        self._on_connect(client, userdata, flags, rc, "Local MQTT Broker")

    def on_aws_connect(self, client, userdata, flags, rc):
        self._on_connect(client, userdata, flags, rc, "AWS IoT Core")

    def _on_connect(self, client, userdata, flags, rc, broker_name):
        try:
            if rc == 0:
                self.controller.log_message(f"Connected to {broker_name}")
                self.controller.update_status("Connected")
                client.subscribe(self.subscribe_topic)
            else:
                self.controller.log_message(
                    f"Failed to connect to {broker_name}, return code {rc}"
                )
                self.controller.update_status("Disconnected")
        except Exception as e:
            logging.error(f"Failed on_connect: {e}")

    def on_local_message(self, client, userdata, msg):
        self._on_message(client, userdata, msg, "Local MQTT Broker")

    def on_aws_message(self, client, userdata, msg):
        self._on_message(client, userdata, msg, "AWS IoT Core")

    def _on_message(self, client, userdata, msg, broker_name):
        message = msg.payload.decode()
        self.controller.log_message(
            f"Received message: {message} on topic {msg.topic} from {broker_name}"
        )
        self.update_device_status(msg.topic, message)

    def set_publish_topic(self, topic):
        self.publish_topic = topic

    def set_subscribe_topic(self, topic):
        self.subscribe_topic = topic
        self.local_client.subscribe(topic)
        self.aws_client.subscribe(topic)

    def publish_message(self, message):
        try:
            self.local_client.publish(self.publish_topic, message)
            self.aws_client.publish(self.publish_topic, message)
        except Exception as e:
            logging.error(f"Failed to publish message: {e}")

    def publish_message_input_field(self, message):
        try:
            json_message = self.package_message(message)
            self.local_client.publish(self.publish_topic, json_message)
            self.aws_client.publish(self.publish_topic, json_message)
        except Exception as e:
            logging.error(f"Failed to publish message: {e}")

    def package_message(self, custom_message):
        packaged_message = {
            "type": "control",
            "device": "MQTT_master",
            "status": "connected",
            "message": custom_message,
        }
        return json.dumps(packaged_message)

    def set_controller(self, controller):
        self.controller = controller

    def update_device_status(self, topic, message):
        try:
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

    def control_device(self, device, action):
        status_request = {
            "type": "control",
            "controller": "MQTT_master",
            "device": device,
            "status": "connected",
            "message": action,
        }

        json_message = json.dumps(status_request)
        self.publish_message(json_message)

    def request_status(self):
        status_request = {
            "type": "control",
            "controller": "MQTT_master",
            "device": "ALL",
            "status": "connected",
            "message": "status",
        }

        json_message = json.dumps(status_request)
        self.publish_message(json_message)

    def check_device_timeouts(self):
        current_time = time.time()
        timeout_threshold = 20

        for device, info in self.devices.items():
            if current_time - info["last_seen"] > timeout_threshold:
                if info["status"] != "Disconnected":
                    info["status"] = "Disconnected"
                    self.controller.update_device_status(device, "Disconnected", "OFF")
