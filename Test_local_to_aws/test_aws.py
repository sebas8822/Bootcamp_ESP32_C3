from awscrt import mqtt, http, io, auth, exceptions
from awsiot import mqtt_connection_builder
import sys
import threading
import time
import json

# Configuration variables
endpoint = "a2hb1w86de6tcr-ats.iot.ap-southeast-2.amazonaws.com"
port = 8883
cert_filepath = r"connect_device_package\master_pc_seb.cert.pem"
pri_key_filepath = r"connect_device_package\master_pc_seb.private.key"
ca_filepath = r"connect_device_package\root-CA.crt"
client_id = "basicPubSub"

# Separate topics for publishing and subscribing
publish_topic = "ESP32bootcamp_control"
subscribe_topic = "ESP32bootcamp_com"

# Message to be published
message_string = "Hello, World!"
message_count = 10  # Set to 0 for infinite loop

received_count = 0
received_all_event = threading.Event()


# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print(f"Connection interrupted. error: {error}")


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(
        f"Connection resumed. return_code: {return_code} session_present: {session_present}"
    )
    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print(f"Resubscribe results: {resubscribe_results}")
    for topic, qos in resubscribe_results["topics"]:
        if qos is None:
            sys.exit(f"Server rejected resubscribe to topic: {topic}")


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print(f"Received message from topic '{topic}': {payload}")
    global received_count
    received_count += 1
    if received_count == message_count:
        received_all_event.set()


# Callback when the connection successfully connects
def on_connection_success(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
    print(
        f"Connection Successful with return code: {callback_data.return_code} session present: {callback_data.session_present}"
    )


# Callback when a connection attempt fails
def on_connection_failure(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionFailureData)
    print(f"Connection failed with error code: {callback_data.error}")


# Callback when a connection has been disconnected or shutdown successfully
def on_connection_closed(connection, callback_data):
    print("Connection closed")


def main():
    # Initialize the MQTT connection with mutual TLS authentication
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=endpoint,
        port=port,
        cert_filepath=cert_filepath,
        pri_key_filepath=pri_key_filepath,
        ca_filepath=ca_filepath,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=client_id,
        clean_session=False,
        keep_alive_secs=30,
        on_connection_success=on_connection_success,
        on_connection_failure=on_connection_failure,
        on_connection_closed=on_connection_closed,
    )

    # Connect to the AWS IoT Core
    print(f"Connecting to {endpoint} with client ID '{client_id}'...")
    connect_future = mqtt_connection.connect()
    try:
        connect_future.result()
        print("Connected!")
    except exceptions.AwsCrtError as e:
        print(f"Connection failed with error: {e}")
        return

    # Subscribe to the subscribe_topic
    print(f"Subscribing to topic '{subscribe_topic}'...")
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=subscribe_topic, qos=mqtt.QoS.AT_LEAST_ONCE, callback=on_message_received
    )
    subscribe_result = subscribe_future.result()
    print(f"Subscribed with {str(subscribe_result['qos'])}")

    # Publish messages to the publish_topic
    if message_string:
        if message_count == 0:
            print("Sending messages until program killed")
        else:
            print(f"Sending {message_count} message(s)")

        publish_count = 1
        while (publish_count <= message_count) or (message_count == 0):
            message = f"{message_string} [{publish_count}]"
            print(f"Publishing message to topic '{publish_topic}': {message}")
            message_json = json.dumps(message)
            mqtt_connection.publish(
                topic=publish_topic, payload=message_json, qos=mqtt.QoS.AT_LEAST_ONCE
            )
            time.sleep(1)
            publish_count += 1

    # Wait for all messages to be received
    if message_count != 0 and not received_all_event.is_set():
        print("Waiting for all messages to be received...")
        received_all_event.wait()
        print(f"{received_count} message(s) received.")

    # Disconnect from AWS IoT Core
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")


if __name__ == "__main__":
    main()
