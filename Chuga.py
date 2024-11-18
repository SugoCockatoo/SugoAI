import cv2
import requests
import numpy as np
import torch
import time

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5l6', pretrained=True)  # Make sure you have the local version

# ESP32-CAM image URL
url = 'http://192.168.1.15/capture'  # Replace with your ESP32-CAM URL

while True:
    try:
        # Capture image from ESP32-CAM
        response = requests.get(url)
        img_array = np.array(bytearray(response.content), dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if frame is None:
            print("Frame is none, skipping...")
            continue
        
        #Rotate the frame
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        # Process frame with YOLOv5
        results = model(frame)

        # Render results on the frame
        results.render()  # This modifies the frame in-place

        # Show the frame with detections
        cv2.imshow('YOLOv5 Detection', frame)

        # Exit loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(1)  # Optional: Wait a moment before retrying

# Clean up
cv2.destroyAllWindows()
