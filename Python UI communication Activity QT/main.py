import sys
from PyQt5 import QtWidgets
from model import MQTTModel
from view import MQTTView
from controller import MQTTController
import logging

if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)

        # Initialize the view
        view = MQTTView(None)  # Create the view without controller initially

        # Initialize the model, passing the view
        model = MQTTModel(view)

        # Initialize the controller
        controller = MQTTController(model, view)

        # Bind the view to the controller
        view.controller = controller

        view.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"Failed application: {e}")
