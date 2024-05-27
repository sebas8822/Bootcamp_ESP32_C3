from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QMainWindow
from datetime import datetime
import json
import logging
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal


class MQTTView(QMainWindow):
    log_message_signal = pyqtSignal(str)
    update_topic_log_signal = pyqtSignal(str, str)
    update_device_status_signal = pyqtSignal(str, str, str)

    def __init__(self, controller):
        super().__init__()
        uic.loadUi("qtUiMqttBootcamProjectDesign.ui", self)

        self.controller = controller

        # Initialize button states
        self.button_states = {"mqtt_connection": "OFF", "task_schedule": "OFF"}

        # Find and assign widgets
        self.mqtt_server_input = self.findChild(
            QtWidgets.QLineEdit, "MQTT_server_input"
        )
        self.mqtt_port_input = self.findChild(QtWidgets.QLineEdit, "MQTT_port_input")
        self.publish_topic_input = self.findChild(
            QtWidgets.QLineEdit, "publish_topic_input"
        )
        self.subscribe_topic_input = self.findChild(
            QtWidgets.QLineEdit, "subscribe_topic_input"
        )
        self.user_input = self.findChild(QtWidgets.QLineEdit, "user_input")
        self.password_input = self.findChild(QtWidgets.QLineEdit, "password_input")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.client_id_input = self.findChild(QtWidgets.QLineEdit, "client_id_input")
        self.message_payload_textEdit = self.findChild(
            QtWidgets.QTextEdit, "message_payload_textEdit"
        )
        self.activity_log_textBrowser = self.findChild(
            QtWidgets.QTextBrowser, "activity_log_textBrowser"
        )
        self.published_log_textBrowser = self.findChild(
            QtWidgets.QTextBrowser, "published_log_textBrowser"
        )
        self.subscribed_log_textBrowser = self.findChild(
            QtWidgets.QTextBrowser, "subscribed_log_textBrowser"
        )

        # Find and assign buttons
        self.mqtt_connection_pushButton = self.findChild(
            QtWidgets.QPushButton, "mqtt_connection_pushButton"
        )
        self.task_schedule_pushButton = self.findChild(
            QtWidgets.QPushButton, "task_schedule_pushButton"
        )
        self.publish_pushButton = self.findChild(
            QtWidgets.QPushButton, "publish_pushButton"
        )
        self.master_control_pushButton_ON = self.findChild(
            QtWidgets.QPushButton, "master_control_pushButton_ON"
        )
        self.master_control_pushButton_OFF = self.findChild(
            QtWidgets.QPushButton, "master_control_pushButton_OFF"
        )
        self.master_control_pushButton_request_status = self.findChild(
            QtWidgets.QPushButton, "master_control_pushButton_request_status"
        )
        self.update_pub_pushButton = self.findChild(
            QtWidgets.QPushButton, "update_pub_pushButton"
        )
        self.update_sub_pushButton = self.findChild(
            QtWidgets.QPushButton, "update_sub_pushButton"
        )

        # Find and assign radio buttons
        self.aws_radioButton = self.findChild(QtWidgets.QRadioButton, "aws_radioButton")
        self.local_radioButton = self.findChild(
            QtWidgets.QRadioButton, "local_radioButton"
        )

        # Assign device buttons dynamically
        self.device_buttons = {}
        self.device_status_labels = {}
        for i in range(1, 7):
            self.device_buttons[f"esp32_{i}_pushButton"] = self.findChild(
                QtWidgets.QPushButton, f"esp32_{i}_pushButton"
            )
            self.device_status_labels[f"esp32_{i}_id_status_label"] = self.findChild(
                QtWidgets.QLabel, f"esp32_{i}_id_status_label"
            )

            # Initialize button state
            self.button_states[f"ESP32-{i}"] = "OFF"

        # Connect signals to slots
        self.mqtt_connection_pushButton.clicked.connect(self.toggle_mqtt_connection)
        self.task_schedule_pushButton.clicked.connect(self.toggle_task_schedule)
        self.publish_pushButton.clicked.connect(self.publish_message)
        self.master_control_pushButton_ON.clicked.connect(
            lambda: self.control_master("ON")
        )
        self.master_control_pushButton_OFF.clicked.connect(
            lambda: self.control_master("OFF")
        )
        self.master_control_pushButton_request_status.clicked.connect(
            lambda: self.control_master("status")
        )
        self.update_pub_pushButton.clicked.connect(self.update_publish_topic)
        self.update_sub_pushButton.clicked.connect(self.update_subscribe_topic)

        for i in range(1, 7):
            self.device_buttons[f"esp32_{i}_pushButton"].clicked.connect(
                lambda _, d=i: self.toggle_device(f"ESP32-{d}")
            )

        # Preload task schedule message
        self.message_payload_textEdit.setPlainText(
            json.dumps(
                {
                    "type": "control",
                    "controller": "MQTT_master",
                    "device": "ALL",
                    "status": "connected",
                    "message": "status",
                },
                indent=4,
            )
        )

        # Initial styles
        # self.update_button_style(self.mqtt_connection_pushButton)
        # self.update_button_style(self.task_schedule_pushButton)
        # for i in range(1, 7):
        #     self.update_button_style(self.device_buttons[f"esp32_{i}_pushButton"])

        # self.test_buttons()

    def toggle_mqtt_connection(self):
        current_state = self.button_states["mqtt_connection"]
        new_state = "OFF" if current_state == "ON" else "ON"
        self.controller.control_mqtt(new_state)

    def toggle_task_schedule(self):
        current_state = self.button_states["task_schedule"]
        new_state = "OFF" if current_state == "ON" else "ON"
        self.controller.control_schedule(new_state)
        self.button_states["task_schedule"] = new_state

    def toggle_device(self, device):
        current_state = self.button_states[device]
        new_state = "OFF" if current_state == "ON" else "ON"
        self.controller.control_device(device, new_state)

    def publish_message(self):
        message = self.message_payload_textEdit.toPlainText()
        self.controller.send_message(message)

    def control_master(self, action):
        self.controller.control_master(action)

    def update_button_state(self, button, state):
        if state == "OFF":
            button.setStyleSheet(
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
        else:
            button.setStyleSheet(
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

    def log_message(self, message):
        print(" I am log message")
        self.activity_log_textBrowser.append(message)

    def update_topic_log(self, message, topic_type):
        now = datetime.now()
        formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
        if topic_type == "publish":
            self.published_log_textBrowser.append(f"{formatted_now}\n{message}\n")
            self.published_log_textBrowser.moveCursor(QtGui.QTextCursor.End)
        else:
            self.subscribed_log_textBrowser.append(f"{formatted_now}\n{message}\n")
            self.subscribed_log_textBrowser.moveCursor(QtGui.QTextCursor.End)

    def update_publish_topic(self):
        topic = self.publish_topic_input.text()
        if not topic:
            self.log_message("Error: Topic cannot be empty.")
        else:
            self.controller.update_publish_topic(topic)

    def update_subscribe_topic(self):
        topic = self.subscribe_topic_input.text()
        if not topic:
            self.log_message("Error: Topic cannot be empty.")
        else:
            self.controller.update_subscribe_topic(topic)

    def update_device_status(self, device, status, state):
        device_key = device.lower().replace("-", "_")
        label = self.device_status_labels.get(f"{device_key}_id_status_label")
        if label:
            color = "green" if status == "Connected" else "red"
            label.setText(status)
            label.setStyleSheet(f"color: {color};")
            self.button_states[device] = state
            self.update_device_button(device, state)

    def update_device_button(self, device, state):
        try:
            print("update_device_button_start")
            device_key = device.lower().replace("-", "_")
            button = self.device_buttons.get(f"{device_key}_pushButton")
            print("update_device_button_processed button")

            if button:
                self.update_button_state(button, state)
                print("update_device_button_end")
        except Exception as e:
            logging.error(f"Failed to change the button color: {e}")
            logging.exception("Exception occurred")  # This will print the stack trace

    # def test_buttons(self):
    #     for i in range(6):
    #         QTimer.singleShot(
    #             i * 1000,
    #             lambda idx=i: self.update_device_status(
    #                 f"ESP32-{idx + 1}", "Connected", "ON"
    #             ),
    #         )
    #         QTimer.singleShot(
    #             (i * 1000) + 500,
    #             lambda idx=i: self.update_device_status(
    #                 f"ESP32-{idx + 1}", "Disconnected", "OFF"
    #             ),
    #         )
