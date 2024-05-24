import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QTextCursor
from model import MQTTModel
from view import MQTTView
from controller import MQTTController

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Initialize the model, view, and controller
    model = MQTTModel()
    view = MQTTView(None)  # Create the view without controller initially
    controller = MQTTController(model, view)

    # Bind the view to the controller
    view.controller = controller

    view.show()
    sys.exit(app.exec_())
