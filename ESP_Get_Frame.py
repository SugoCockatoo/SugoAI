import cv2
import requests
import numpy as np

# URL of the ESP32-CAM video stream (replace with your actual IP and endpoint)
url = 'http://192.168.1.15/capture'  # Use your ESP32-CAM IP and endpoint

while True:
    try:
        # Get the image from the ESP32-CAM
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Convert the image to a NumPy array
            img_array = np.array(bytearray(response.content), dtype=np.uint8)
            # Decode the image from the array
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            # Check if frame is valid
            if frame is not None:
                # Display the frame
                cv2.imshow('ESP32-CAM Video Stream', frame)
            else:
                print("Frame is None, skipping...")
        else:
            print(f"Failed to get image, status code: {response.status_code}")

        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except Exception as e:
        print(f"Error: {e}")

# Release resources
cv2.destroyAllWindows()
