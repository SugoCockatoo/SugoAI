import time
import random
import numpy as np
from machine import Pin, PWM
import tensorflow as tf
import requests
import cv2

# ESP32 Camera capture URL
url = 'http://192.168.1.15/capture'  

# Initialize TFLite model
interpreter = tf.lite.Interpreter(model_path="converted_model.tflite")
interpreter.allocate_tensors()

# Get input and output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Servo GPIO setup
pitch_servo_pin = PWM(Pin(19), freq=50)  # Pin for pitch servo 
roll_servo_pin = PWM(Pin(21), freq=50)   # Pin for roll servo
yaw_servo_pin = PWM(Pin(22), freq=50)    # Pin for yaw servo 

# Moves 
cockatoo_moves = [30, 60, 90]  # For "bird" category
ball_moves = [90, 120, 150]    # For "ball" category objects
book_moves = [150, 90, 60]     # For "book" category objects

# Object categories for specific actions
second_class_moves = ["book", "cellphone", "ball"]
third_class_moves = ["laptop", "person"]

# Servo control function
def set_servo_angle(servo_pin, angle):
    duty = int((angle / 180) * 1023)  # Convert angle to duty cycle
    servo_pin.duty(duty)
    time.sleep(0.01)

# Function to map object position to servo angle
def map_position_to_angle(position, frame_dim, min_angle=30, max_angle=150):
    return min_angle + (max_angle - min_angle) * (position / frame_dim)

# Execute sequence of moves
def execute_moves(moves):
    for angle in moves:
        set_servo_angle(yaw_servo_pin, angle)  # Yaw control

# Actions for specific detected objects
def cockatoo_action():
    print("Executing Cockatoo Moves")
    execute_moves(cockatoo_moves)

def ball_action():
    print("Executing Ball Moves")
    execute_moves(ball_moves)

def book_action():
    print("Executing Book Moves")
    execute_moves(book_moves)

# Initialize tracker variables
trackers = cv2.MultiTracker_create()
tracked_objects = {}

# Image Procesing
while True:
    try:
        # Capture image from ESP32-CAM
        response = requests.get(url)
        img_array = np.array(bytearray(response.content), dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if frame is None:
            print("Frame is none, skipping...")
            continue

        # Rotate frame if necessary
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        # Preprocess image for TFLite model (assuming model input size is 224x224)
        input_shape = input_details[0]['shape']
        img_resized = cv2.resize(frame, (input_shape[1], input_shape[2]))
        input_data = np.expand_dims(img_resized, axis=0).astype(np.float32)

        # Set input tensor and invoke model
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        # Get and interpret the output
        output_data = interpreter.get_tensor(output_details[0]['index'])
        detected_class_id = np.argmax(output_data)
        object_name = output_details[0]['name'][detected_class_id]  # Get object name from class id
        print(f"Detected: {object_name}")

        # Initialize new trackers for detected objects
        if object_name not in tracked_objects:
            # If new object, initialize a tracker for it
            tracker = cv2.TrackerKCF_create()  # Or use any other tracker (e.g., MIL, CSRT)
            bbox = (100, 100, 50, 50)  # Placeholder bounding box; update based on detection results
            ok = tracker.init(frame, bbox)
            if ok:
                trackers.add(tracker, frame, bbox)
                tracked_objects[object_name] = tracker
                print(f"Initialized tracker for: {object_name}")

                # Perform action based on object detected
                if object_name == "bird":
                    cockatoo_action()
                elif object_name in second_class_moves:
                    ball_action()
                elif object_name in third_class_moves:
                    book_action()
                else:
                    print("Object not recognized in predefined list.")

        # Update all trackers
        ok, boxes = trackers.update(frame)
        if ok:
            for i, box in enumerate(boxes):
                (x, y, w, h) = [int(v) for v in box]
                object_center_x = x + w // 2
                object_center_y = y + h // 2

                # Map object position to servo angles
                yaw_angle = map_position_to_angle(object_center_x, frame.shape[1])
                pitch_angle = map_position_to_angle(object_center_y, frame.shape[0])

                # Adjust servos for tracking
                set_servo_angle(yaw_servo_pin, yaw_angle)
                set_servo_angle(pitch_servo_pin, pitch_angle)

                # Optional: Roll movement based on some criteria (e.g., object size or specific detection)
                if object_name in ["bird", "ball", "book"]:
                    roll_angle = random.choice([60, 90, 120])  # Example: Random roll
                    set_servo_angle(roll_servo_pin, roll_angle)

        # Display and exit handling
        cv2.imshow('Object Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(1)

# Cleanup
cv2.destroyAllWindows()
pitch_servo_pin.deinit()
roll_servo_pin.deinit()
yaw_servo_pin.deinit()
