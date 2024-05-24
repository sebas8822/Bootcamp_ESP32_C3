from PyQt5.QtCore import QTimer


class MQTTController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.timer = QTimer(self.view)

        # Bind the controller to the model
        self.model.set_controller(self)

        # Connect the timer to the schedule_status_request method
        self.timer.timeout.connect(self.schedule_status_request)

    def control_mqtt(self, action):
        print("Action on control mqtt", action)
        if action == "ON":
            if self.view.local_radioButton.isChecked():
                server = self.view.mqtt_server_input.text()
                port = self.view.mqtt_port_input.text()
                self.update_mqtt_connection_pushButton("Turn OFF")
                if server and port:
                    self.model.connect_local(server, port)
                else:
                    self.log_message(
                        "MQTT server IP or port is required to establish the connection"
                    )
                    self.update_mqtt_connection_pushButton("Turn ON")
        else:
            if self.view.local_radioButton.isChecked():
                self.model.disconnect_local()
                self.update_mqtt_connection_pushButton("Turn ON")

    def update_mqtt_connection_pushButton(self, state):
        if state == "Turn OFF":
            self.view.mqtt_connection_pushButton.setText("Turn OFF")
            self.view.mqtt_connection_pushButton.setStyleSheet(
                """
                QPushButton {
                    background-color: cyan;
                    color: black;
                    border: 1px solid darkcyan;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: darkcyan;
                }
                """
            )
        else:
            self.view.mqtt_connection_pushButton.setText("Turn ON")
            self.view.mqtt_connection_pushButton.setStyleSheet(
                """
                QPushButton {
                    background-color: red;
                    color: white;
                    border: 1px solid darkred;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: darkred;
                }
                """
            )

    def log_message(self, message):
        self.view.log_message(message)

    def update_topic_log(self, message, topic_type):
        self.view.update_topic_log(message, topic_type)

    def update_publish_topic(self, topic):
        self.model.set_publish_topic_local(topic)
        self.log_message(f"Publish topic updated to: {topic}")

    def update_subscribe_topic(self, topic):
        self.model.set_subscribe_topic_local(topic)
        self.log_message(f"Subscribed to topic: {topic}")

    def send_message(self, message):
        self.model.publish_message_local(message)

    def schedule_status_request(self):
        self.model.control_master("status")
        self.model.check_device_timeouts()  # Check for device timeouts

    def start_status_request(self):
        self.schedule_status_request()
        self.timer.start(5000)  # Schedule next status request after 5 seconds

    def stop_status_request(self):
        self.timer.stop()

    def control_schedule(self, action):
        if action == "ON":
            self.start_status_request()
        else:
            self.stop_status_request()
        self.view.log_message(f"Task Schedule {action}")

    def update_device_status(self, device, status, state):
        self.view.update_device_status(device, status, state)

    def control_master(self, action):
        self.model.control_master(action)
