import requests
import ujson
import network
import time
from machine import Pin, UART
from tflite_runtime.interpreter import Interpreter

# Initialize UART for motor control or similar output
uart = UART(1, baudrate=9600, tx=17, rx=16)  # Adjust pins as needed

# Wi-Fi connection details
WIFI_SSID = 'DELIOMEMY'
WIFI_PASS = '05432239'
CAMERA_URL = 'http://192.168.1.15/capture'  # ESP32-CAM endpoint for images

# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    while not wlan.isconnected():
        time.sleep(1)
    print("Connected to Wi-Fi")

# Load and initialize TFLite model
interpreter = Interpreter(model_path="your_tflite_model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Function to capture and process image
def process_image():
    # Capture image
    try:
        response = requests.get(CAMERA_URL)
        if response.status_code == 200:
            img_data = response.content
            # TODO: Preprocess image as needed for TFLite model input
            interpreter.set_tensor(input_details[0]['index'], img_data)
            interpreter.invoke()
            output_data = interpreter.get_tensor(output_details[0]['index'])
            
            # Interpret model output
            detected_object = classify_object(output_data)
            take_action(detected_object)
        else:
            print("Failed to retrieve image")
    except Exception as e:
        print("Error capturing or processing image:", e)

# Interpret the model output and determine the object
def classify_object(output_data):
    # Example threshold-based classification; adapt as needed for your model
    if output_data[0] > 0.5:
        return "bird"
    elif output_data[1] > 0.5:
        return "book"
    # Add more classifications based on model output
    return "unknown"

# Define actions based on object detection
def take_action(object_name):
    if object_name == "bird":
        send_movement_command("move_1")
    elif object_name == "book":
        send_movement_command("move_2")
    else:
        print("Object not in known list")

# Send movement commands via UART
def send_movement_command(command):
    uart.write(command.encode())
    print(f"Sent command: {command}")

# Main loop
connect_wifi()
while True:
    process_image()
    time.sleep(2)  # Delay between captures
