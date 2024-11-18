import cv2
import torch

# Load the YOLOv5 model (yolov5s is the small version, you can use 'yolov5m', 'yolov5l', etc.)
model = torch.hub.load('ultralytics/yolov5', 'yolov5l6')  # Or replace with your custom model

# Open the laptop's camera (0 for the default camera)
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open video stream from camera.")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Use YOLOv5 model to detect objects
    results = model(frame)

    # Draw bounding boxes and labels on the frame
    detections = results.pandas().xyxy[0]  # Extract detections as a Pandas DataFrame

    for index, row in detections.iterrows():
        x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
        label = row['name']
        confidence = row['confidence']

        # Draw the bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Display the label and confidence
        cv2.putText(frame, f'{label} {confidence:.2f}', (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

    # Display the resulting frame
    cv2.imshow('YOLOv5 Object Detection', frame)

    # Press 'q' to exit the video stream
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture and close windows
cap.release()
cv2.destroyAllWindows()
