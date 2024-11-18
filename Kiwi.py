#Comunication with Esp32
import serial

ser = serial.Serial("COM5", 9600, timeout=1)
def send_data(data):
    ser.write(data.encode())
    
print("Youre SUGO") #This was made by Sugo the cockatoo