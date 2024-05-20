import tkinter as tk
from model import MQTTModel
from view import MQTTView
from controller import MQTTController

# MQTT settings
mqtt_server = "127.0.0.1"
mqtt_port = 1883

if __name__ == "__main__":
    # Create the main application window
    root = tk.Tk()

    # Initialize the model, view, and controller
    model = MQTTModel(mqtt_server, mqtt_port)
    view = MQTTView(root, None)
    controller = MQTTController(model, view)

    # Bind the view to the controller
    view.controller = controller

    # Start the MQTT client after the GUI is fully initialized
    root.after(100, model.connect)
    root.after(1000, controller.schedule_status_request)  # Schedule status request

    # Run the GUI loop
    root.mainloop()
