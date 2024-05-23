import sys
from PyQt5 import QtWidgets
from model import MQTTModel
from view import MQTTView
from controller import MQTTController

# MQTT settings
local_mqtt_server = "127.0.0.1"
local_mqtt_port = 1883

aws_mqtt_server = "your-aws-endpoint"  # Replace with your AWS IoT Core endpoint
aws_mqtt_port = 8883
aws_client_id = "your-aws-client-id"
aws_username = "your-aws-username"
aws_password = "your-aws-password"

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Initialize the model, view, and controller
    model = MQTTModel(
        local_mqtt_server,
        local_mqtt_port,
        aws_mqtt_server,
        aws_mqtt_port,
        aws_client_id,
        aws_username,
        aws_password,
    )
    view = MQTTView(None)  # Create the view without controller initially
    controller = MQTTController(model, view)

    # Bind the view to the controller
    view.controller = controller

    view.show()
    sys.exit(app.exec_())
