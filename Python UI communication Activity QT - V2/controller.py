from PyQt5.QtCore import QTimer, QObject, pyqtSlot


class MQTTController(QObject):
    def __init__(self, model, view):
        super().__init__()
        self.model = model
        self.view = view
        self.timer = QTimer(self.view)

        # Bind the controller to the model
        self.model.set_controller(self)

        # Connect the timer to the schedule_status_request method
        self.timer.timeout.connect(self.schedule_status_request)

        # Connect model signals to slots
        self.model.message_received.connect(self.on_message_received)
        self.model.connection_status_changed.connect(self.on_connection_status_changed)

    def control_mqtt(self, action):
        print("Action on control mqtt", action)
        if action == "ON":
            if self.view.local_radioButton.isChecked():
                server = self.view.mqtt_server_input.text()
                port = self.view.mqtt_port_input.text()
                print("I am here control_mqtt 1")
                if server and port:
                    print("I am here control_mqtt")
                    result_connect = self.model.connect_local(server, port)
                    if result_connect == 100:
                        self.view.button_states["mqtt_connection"] = "ON"
                        self.update_mqtt_connection_button("ON")
                    else:  # Covers result_connect == 50 and any other return code
                        self.view.button_states["mqtt_connection"] = "OFF"
                        self.update_mqtt_connection_button("OFF")
                else:
                    print("I am here control_mqtt no inputs")
                    self.log_message(
                        "MQTT server IP or port is required to establish the connection"
                    )
                    self.view.button_states["mqtt_connection"] = "OFF"
                    self.update_mqtt_connection_button("OFF")
        else:
            if self.view.local_radioButton.isChecked():
                self.model.disconnect_local()
                self.view.button_states["mqtt_connection"] = "OFF"
                self.update_mqtt_connection_button("OFF")

    def update_mqtt_connection_button(self, state):
        self.view.update_button_state(self.view.mqtt_connection_pushButton, state)

    def log_message(self, message):
        print(" I am log message")
        self.view.log_message(message)

    def update_topic_log(self, message, topic_type):
        self.view.update_topic_log(message, topic_type)

    def update_publish_topic(self, topic):
        self.model.set_publish_topic_local(topic)
        self.log_message(f"Publish to topic: {topic}")

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
        self.view.update_button_state(self.view.task_schedule_pushButton, action)

    def on_message_received(self, topic, message):
        self.update_topic_log(message, "subscribed")
        self.model.update_device_status(topic, message)

    def on_connection_status_changed(self, status):
        if status == "Connected":
            self.update_mqtt_connection_button("ON")
        else:
            self.update_mqtt_connection_button("OFF")

    def update_device_status(self, device, status, state):
        self.view.update_device_status(device, status, state)

    def control_master(self, action):
        self.model.control_master(action)

    def control_device(self, device, action):
        self.model.control_device(device, action)
