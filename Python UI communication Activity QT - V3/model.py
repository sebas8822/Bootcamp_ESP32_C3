import paho.mqtt.client as mqtt
import logging
import json
import time
from PyQt5.QtCore import QObject, pyqtSignal
from awscrt import mqtt as aws_mqtt
from awscrt import exceptions
from awsiot import mqtt_connection_builder
import threading
import sys


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
        self.publish_topic = ""
        self.subscribe_topic = ""
        self.current_subscribe_topic = None  # Initialize the current subscribe topic
        self.local_client.on_connect = self.on_local_connect
        self.local_client.on_message = self.on_local_message

        # AWS IoT Core configuration
        self.aws_endpoint = ""
        self.aws_port = 0
        self.aws_cert_filepath = r"connect_device_package/master_pc_seb.cert.pem"
        self.aws_pri_key_filepath = r"connect_device_package/master_pc_seb.private.key"
        self.aws_ca_filepath = r"connect_device_package/root-CA.crt"
        self.aws_client_id = "master_device"
        self.aws_publish_topic = ""
        self.aws_subscribe_topic = ""
        self.aws_connection = None
        self.aws_current_subscribe_topic = None

        # AWS connection state
        self.aws_connected = False

        self.controller = None
        self.devices = {
            f"ESP32-{i+1}": {"status": "Disconnected", "last_seen": 0, "state": "OFF"}
            for i in range(6)
        }

    def set_controller(self, controller):
        self.controller = controller

    # Local MQTT connection methods...

    def connect_local(self, server, port):
        self.local_server = server
        self.local_port = port
        try:
            self.local_client.connect(self.local_server, int(self.local_port), 60)
            self.local_client.loop_start()
            # self.controller.log_message(
            #     f"Connected to local server: {self.local_server}:{self.local_port}"
            # )
            return 100  # Success code
        except Exception as e:
            logging.error(f"Failed to connect: {e}")
            self.controller.log_message(
                f"Failed to connect to the MQTT server: {e}. Please check inputs!"
            )
            return 50  # Error code

    def disconnect_local(self):
        try:
            self.local_client.loop_stop()
            self.local_client.disconnect()
            self.controller.log_message(
                f"MQTT server Disconnected at {self.local_server}:{self.local_port}"
            )
        except Exception as e:
            logging.error(f"Failed to disconnect: {e}")
            self.controller.log_message(
                f"Failed to disconnect from the MQTT server: {e}"
            )

    def on_local_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.controller.log_message(
                f"Connected to MQTT server at {self.local_server}:{self.local_port}"
            )
        else:
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
        message = msg.payload.decode()
        self.controller.log_message("Message received on topic: " + msg.topic)
        self.controller.update_topic_log(message, "subscribed")
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

        return json_message

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

        return json_message

    def check_device_timeouts(self):
        current_time = time.time()
        timeout_threshold = 10  # seconds

        for device, info in self.devices.items():
            if current_time - info["last_seen"] > timeout_threshold:
                if info["status"] != "Disconnected":
                    info["status"] = "Disconnected"
                    self.controller.update_device_status(device, "Disconnected", "OFF")

    # AWS IoT Core methods...

    def connect_aws(self, server, port, client_id):
        self.aws_endpoint = server
        self.aws_port = int(port)
        self.aws_client_id = client_id

        if not self.aws_connection:
            self.aws_connection = mqtt_connection_builder.mtls_from_path(
                endpoint=self.aws_endpoint,
                port=self.aws_port,
                cert_filepath=self.aws_cert_filepath,
                pri_key_filepath=self.aws_pri_key_filepath,
                ca_filepath=self.aws_ca_filepath,
                client_id=self.aws_client_id,
                clean_session=False,
                keep_alive_secs=30,
                on_connection_interrupted=self.on_aws_connection_interrupted,
                on_connection_resumed=self.on_aws_connection_resumed,
                on_connection_success=self.on_aws_connection_success,
                on_connection_failure=self.on_aws_connection_failure,
                on_connection_closed=self.on_aws_connection_closed,
            )

        print(
            f"Connecting to AWS IoT Core at {self.aws_endpoint} with client ID '{self.aws_client_id}'..."
        )
        connect_future = self.aws_connection.connect()
        try:
            connect_future.result()
            self.aws_connected = True
            self.controller.log_message(
                f"Connected to AWS IoT Core at {self.aws_endpoint}"
            )
            return 100
        except exceptions.AwsCrtError as e:
            self.aws_connected = False
            logging.error(f"Failed to connect to AWS IoT Core: {e}")
            self.controller.log_message(f"Failed to connect to AWS IoT Core: {e}")
            return 50

    def disconnect_aws(self):
        if self.aws_connected:
            print("Disconnecting from AWS IoT Core...")
            disconnect_future = self.aws_connection.disconnect()
            try:
                disconnect_future.result()
                self.aws_connected = False
                self.controller.log_message("Disconnected from AWS IoT Core")
            except exceptions.AwsCrtError as e:
                logging.error(f"Failed to disconnect from AWS IoT Core: {e}")
                self.controller.log_message(
                    f"Failed to disconnect from AWS IoT Core: {e}"
                )

    def on_aws_connection_interrupted(self, connection, error, **kwargs):
        self.aws_connected = False
        print(f"AWS IoT Core connection interrupted. error: {error}")

    def on_aws_connection_resumed(
        self, connection, return_code, session_present, **kwargs
    ):
        print(
            f"Connection resumed. return_code: {return_code} session_present: {session_present}"
        )
        if return_code == aws_mqtt.ConnectReturnCode.ACCEPTED and not session_present:
            print("Session did not persist. Resubscribing to existing topics...")
            resubscribe_future, _ = connection.resubscribe_existing_topics()
            resubscribe_future.add_done_callback(self.on_resubscribe_complete)

    def on_resubscribe_complete(self, resubscribe_future):
        resubscribe_results = resubscribe_future.result()
        print(f"Resubscribe results: {resubscribe_results}")
        for topic, qos in resubscribe_results["topics"]:
            if qos is None:
                sys.exit(f"Server rejected resubscribe to topic: {topic}")

    def on_aws_message_received(self, topic, payload, dup, qos, retain, **kwargs):
        message = payload.decode()
        print(f"Received message from topic '{topic}': {message}")
        self.controller.log_message(f"Message received on topic: {topic}")
        self.controller.update_topic_log(message, "subscribed")
        self.update_device_status(topic, message)

    def on_aws_connection_success(self, connection, callback_data):
        assert isinstance(callback_data, aws_mqtt.OnConnectionSuccessData)
        print(
            f"Connection Successful with return code: {callback_data.return_code} session present: {callback_data.session_present}"
        )

    def on_aws_connection_failure(self, connection, callback_data):
        assert isinstance(callback_data, aws_mqtt.OnConnectionFailureData)
        print(f"Connection failed with error code: {callback_data.error}")

    def on_aws_connection_closed(self, connection, callback_data):
        print("Connection closed")

    def set_publish_topic_aws(self, topic):
        self.aws_publish_topic = topic

    def set_subscribe_topic_aws(self, topic):
        if self.aws_subscribe_topic:
            self.aws_connection.unsubscribe(self.aws_subscribe_topic)
        self.aws_subscribe_topic = topic
        self.aws_connection.subscribe(
            topic=topic,
            qos=aws_mqtt.QoS.AT_LEAST_ONCE,
            callback=self.on_aws_message_received,
        )

    def publish_message_aws(self, message):
        if self.aws_connected:
            try:
                self.aws_connection.publish(
                    topic=self.aws_publish_topic,
                    payload=message,
                    qos=aws_mqtt.QoS.AT_LEAST_ONCE,
                )
                self.controller.update_topic_log(message, "publish")
            except Exception as e:
                logging.error(f"Failed to publish message to AWS IoT Core: {e}")

    def control_device_aws(self, device, action):
        status_request = {
            "type": "control",
            "controller": "MQTT_master",
            "device": device,
            "status": "connected",
            "message": action,
        }
        json_message = json.dumps(status_request)
        self.publish_message_aws(json_message)

    def control_master_aws(self, action):
        status_request = {
            "type": "control",
            "controller": "MQTT_master",
            "device": "ALL",
            "status": "connected",
            "message": action,
        }
        json_message = json.dumps(status_request)
        self.publish_message_aws(json_message)
