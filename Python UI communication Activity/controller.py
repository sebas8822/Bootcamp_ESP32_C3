class MQTTController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Bind the controller to the model
        self.model.set_controller(self)

    def update_publish_topic(self, topic):
        self.model.set_publish_topic(topic)
        self.view.log_message(f"Publish topic updated to: {topic}")

    def update_subscribe_topic(self, topic):
        self.model.set_subscribe_topic(topic)
        self.view.log_message(f"Subscribed to topic: {topic}")

    def send_message(self, message):
        self.model.publish_message(message)
        self.view.log_message(
            f"Published message: {message} to topic: {self.model.publish_topic}"
        )

    def send_message_input_field(self, message):
        self.model.publish_message_input_field(message)
        self.view.log_message(
            f"Published message: {message} to topic: {self.model.publish_topic}"
        )

    def log_message(self, message):
        self.view.log_message(message)

    def topic_log_message(self, message):
        self.view.topic_log_message(message)

    def update_status(self, status):
        self.view.update_status(status)

    def update_device_status(self, device, status):
        self.view.update_device_status(device, status)

    def control_device(self, device, action):
        self.model.control_device(device, action)
        self.view.log_message(f"Sent {action} to {device}")

    def schedule_status_request(self):
        self.model.request_status()
        self.view.root.after(
            10000, self.schedule_status_request
        )  # Schedule next status request after 10 seconds
        self.model.check_device_timeouts()  # Check for device timeouts
