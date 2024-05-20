import tkinter as tk
from tkinter import scrolledtext


class MQTTView:
    def __init__(self, root, controller):
        self.controller = controller
        self.root = root
        self.root.title("MQTT Client")

        main_frame = tk.Frame(root)
        main_frame.pack(padx=10, pady=10)

        # Left column frame for MQTT controls
        left_frame = tk.Frame(main_frame)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # Right column frame for device status and controls
        right_frame = tk.Frame(main_frame)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        # Publish section
        publish_frame = tk.Frame(left_frame)
        publish_frame.pack(pady=10)

        publish_label = tk.Label(publish_frame, text="Publish Topic:")
        publish_label.pack(side=tk.LEFT, padx=5)

        self.publish_topic_entry = tk.Entry(publish_frame)
        self.publish_topic_entry.pack(side=tk.LEFT, padx=5)

        publish_update_button = tk.Button(
            publish_frame, text="Update", command=self.update_publish_topic
        )
        publish_update_button.pack(side=tk.LEFT, padx=5)

        # Subscribe section
        subscribe_frame = tk.Frame(left_frame)
        subscribe_frame.pack(pady=10)

        subscribe_label = tk.Label(subscribe_frame, text="Subscribe Topic:")
        subscribe_label.pack(side=tk.LEFT, padx=5)

        self.subscribe_topic_entry = tk.Entry(subscribe_frame)
        self.subscribe_topic_entry.pack(side=tk.LEFT, padx=5)

        subscribe_update_button = tk.Button(
            subscribe_frame, text="Update", command=self.update_subscribe_topic
        )
        subscribe_update_button.pack(side=tk.LEFT, padx=5)

        # Message section
        message_frame = tk.Frame(left_frame)
        message_frame.pack(pady=10)

        message_label = tk.Label(message_frame, text="Message:")
        message_label.pack(side=tk.LEFT, padx=5)

        self.publish_message_entry = tk.Entry(message_frame)
        self.publish_message_entry.pack(side=tk.LEFT, padx=5)

        message_send_button = tk.Button(
            message_frame, text="Send", command=self.send_message
        )
        message_send_button.pack(side=tk.LEFT, padx=5)

        # Status indicator
        self.status_label = tk.Label(left_frame, text="Status: Disconnected", fg="red")
        self.status_label.pack(pady=10)

        # Log section
        log_label = tk.Label(left_frame, text="Activity Log:")
        log_label.pack(pady=5)

        self.log_text = scrolledtext.ScrolledText(
            left_frame, width=140, height=10, state=tk.DISABLED
        )
        self.log_text.pack(pady=5)

        # Topic log section
        topic_log_label = tk.Label(left_frame, text="Topic Log:")
        topic_log_label.pack(pady=5)

        self.topic_log_text = scrolledtext.ScrolledText(
            left_frame, width=140, height=10, state=tk.DISABLED
        )
        self.topic_log_text.pack(pady=5)

        # MQTT and Schedule toggles
        mqtt_frame = tk.Frame(right_frame)
        mqtt_frame.pack(pady=10)

        mqtt_label = tk.Label(mqtt_frame, text="MQTT:")
        mqtt_label.pack(side=tk.LEFT, padx=5)

        self.mqtt_toggle_button = tk.Button(
            mqtt_frame,
            text="Turn OFF",
            command=self.toggle_mqtt,
            bg="green",
        )
        self.mqtt_toggle_button.pack(side=tk.LEFT, padx=5)

        schedule_frame = tk.Frame(right_frame)
        schedule_frame.pack(pady=10)

        schedule_label = tk.Label(schedule_frame, text="Schedule:")
        schedule_label.pack(side=tk.LEFT, padx=5)

        self.schedule_toggle_button = tk.Button(
            schedule_frame,
            text="Turn OFF",
            command=self.toggle_schedule,
            bg="green",
        )
        self.schedule_toggle_button.pack(side=tk.LEFT, padx=5)

        # Device status section
        device_frame = tk.Frame(right_frame)
        device_frame.pack(pady=10)

        self.device_status_labels = {}
        self.device_buttons = {}
        for i in range(6):
            device = f"ESP32-{i+1}"
            device_label = tk.Label(
                device_frame, text=f"{device}: Disconnected", fg="red"
            )
            device_label.pack()

            control_frame = tk.Frame(device_frame)
            control_frame.pack()

            on_button = tk.Button(
                control_frame,
                text="Turn On",
                command=lambda d=device: self.toggle_device(d),
                bg="red",
            )
            on_button.pack(side=tk.LEFT)

            self.device_status_labels[device] = device_label
            self.device_buttons[device] = on_button

    def update_publish_topic(self):
        topic = self.publish_topic_entry.get()
        print("update_publish_topic", topic)
        print("type", type(topic))

        topic = topic.strip()  # Remove leading/trailing whitespaces

        if not topic:
            print("Error: Topic cannot be empty Publish to '.'")
            topic = "."

        self.controller.update_publish_topic(topic)

    def update_subscribe_topic(self):
        topic = self.subscribe_topic_entry.get()
        print("update_subscribe_topic", topic)
        print("type", type(topic))

        topic = topic.strip()  # Remove leading/trailing whitespaces

        if not topic:
            print("Error: Topic cannot be empty subscribed to '.'")
            topic = "."

        self.controller.update_subscribe_topic(topic)

    def send_message(self):
        message = self.publish_message_entry.get()
        self.controller.send_message_input_field(message)

    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.yview(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def topic_log_message(self, message):
        self.topic_log_text.config(state=tk.NORMAL)
        self.topic_log_text.insert(tk.END, message + "\n")
        self.topic_log_text.yview(tk.END)
        self.topic_log_text.config(state=tk.DISABLED)

    def update_status(self, status):
        self.status_label.config(
            text=f"Status: {status}", fg="green" if status == "Connected" else "red"
        )

    def update_device_status(self, device, status, state):
        color = "green" if status == "Connected" else "red"
        self.device_status_labels[device].config(text=f"{device}: {status}", fg=color)
        self.update_device_button(device, state)

    def control_device(self, device, action):
        self.controller.control_device(device, action)

    def toggle_device(self, device):
        current_text = self.device_buttons[device].cget("text")
        new_action = "ON" if current_text == "Turn On" else "OFF"
        self.control_device(device, new_action)

    def update_device_button(self, device, state):
        if state == "ON":
            self.device_buttons[device].config(text="Turn Off", bg="green")
        else:
            self.device_buttons[device].config(text="Turn On", bg="red")

    def toggle_mqtt(self):
        current_text = self.mqtt_toggle_button.cget("text")
        new_action = "ON" if current_text == "Turn On" else "OFF"
        self.controller.control_mqtt(new_action)
        self.mqtt_toggle_button.config(
            text="Turn Off" if new_action == "ON" else "Turn On",
            bg="green" if new_action == "ON" else "red",
        )

    def toggle_schedule(self):
        current_text = self.schedule_toggle_button.cget("text")
        new_action = "ON" if current_text == "Turn On" else "OFF"
        self.controller.control_schedule(new_action)
        self.schedule_toggle_button.config(
            text="Turn Off" if new_action == "ON" else "Turn On",
            bg="green" if new_action == "ON" else "red",
        )
