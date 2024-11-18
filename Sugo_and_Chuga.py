#By Sugo and Chuga 
import cv2
import requests
import numpy as np
import torch
import time
import sqlite3
import serial
import random

#Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)  #Load the model
#ESP32-CAM image URL
url = 'http://192.168.1.15/capture'  #Replace with your ESP32-CAM URL

while True:
    try:
        #Capture image from ESP32-CAM
        response = requests.get(url)
        img_array = np.array(bytearray(response.content), dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if frame is None:
            print("Frame is none, skipping...")
            continue
        
        #Rotate the frame
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        #Process frame with YOLOv5
        results = model(frame)

        #Extract detected object names
        for detection in results.pred[0]:
            class_id = int(detection[5])  #Class ID is in the 6th position (index 5)
            object_name = results.names[class_id]  #Get the class name
            print(f"Detected: {object_name}")

        #Render results on the frame
        results.render()  #This modifies the frame in-place

        #Show the frame with detections
        cv2.imshow('YOLOv5 Detection', frame)

        #Exit loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
#Exeptions and errors 
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        time.sleep(1) 
    except requests.exceptions.RequestException as e:
        print(f"Network error occurred: {e}")
        time.sleep(2)
    except cv2.error as e:
        print(f"OpenCV error occurred: {e}")
        time.sleep(2)



#Clean up
cv2.destroyAllWindows()

#Connect to a database (or create it)
with sqlite3.connect('Quark.db') as conn:
    cursor = conn.cursor()

#Classification 
#First class: birb
#Second class: book, cellphone, ball
#Third class: laptop, person

second = ["book", "cell phone", "ball"]
third = ["laptop", "person"]

ser = serial.Serial('COM5', 9600, timeout=1) #Entable the connection 

#Allow some time for the connection to establish
time.sleep(2)

#Function to send data to Arduino and receive a response
def send_data(data):
    ser.write(data.encode())  #Send the data
    time.sleep(1)             #Wait for a response

rand = random.randint(1, 20)
#Functions
def Cockatoo():
    cursor.execute(f"""SELECT * FROM Cockatoo WHERE "MoveID" == {rand}""") #Selects random move 
    rows = cursor.fetchall() #Gets the info
    for row in rows:
        send_data(row)
        send_data("Cockatoo detected!") #Sends the data to Arduino 

def Ball():
    cursor.execute(f"""SELECT * FROM Ball WHERE "MoveID" == {rand}""") #Selects random move 
    rows = cursor.fetchall() #Gets the info
    for row in rows:
        send_data(row) 
        send_data("Person detected!")#Sends the data to Arduino 

def Book():
    cursor.execute(f"""SELECT * FROM Book WHERE "MoveID" == {rand}""") #Selects random move 
    rows = cursor.fetchall() #Gets the info
    for row in rows:
        send_data(row)
        send_data("Book detected!")#Sends the data to Arduino

if object_name == "bird": #If the object is a birb 
    Cockatoo()
    print("Cockatoo Detected!")
elif object_name in second: #If the object is a second class object
    Ball()
elif object_name in third: #If the object is a third class object
    Book()
else: #If the object is not in any of the lists
    print("Is not in the list!")

#Close the serial port when done
ser.close()