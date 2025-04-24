#Developed by @Soumikcoder
#Purpose: To update data collected from arduino to database
#!/usr/bin/env python3
import serial
import requests as re
import time
from datetime import datetime
# Define constants for the device readiness and initialization messages
INITIALIZATION_SUCCESS = "Initializing"
INITIALIZATION_FAILED = "Initializing pulse oximeter..FAILED"
TIMEOUT_SECONDS = 10  # Time to wait for the device to be ready (in seconds)
INITIALIZATION_SERIAL=False
# Try to open the serial port
if not INITIALIZATION_SERIAL:
    try:
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=None)
        ser.reset_input_buffer()
        INITIALIZATION_SERIAL=True
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        INITIALIZATION_SERIAL=False
print('Initialized successfully') 

COLLECTED_ECG = False
COLLECTED_SPO2=False  

i=0
ecg=[]

while INITIALIZATION_SERIAL:
    if ser.in_waiting > 0:
        # Read data from the serial buffer
        line = ser.readline().decode('utf-8').rstrip()
        if not COLLECTED_SPO2:
            try:
                heartrate, spo2 = line.split(',')
                heartrate = float(heartrate)
                spo2 = float(spo2)
                COLLECTED_SPO2=True
            except ValueError:
                # If the line cannot be split or converted to float, log the error and continue
                print(f"Skipping invalid data: {line}")
        
        # Handle ecg data collection
        elif not COLLECTED_ECG:
            try:
                ecg.append(int(line))
                if i== 500:
                    COLLECTED_ECG=True
            except ValueError:
                # If the line cannot be split or converted to float, log the error and continue
                print(f"Skipping invalid data: {line}")
            i+=1

        #All ecg and heart rate datas are collected
        # and ready to upload
        if COLLECTED_ECG and COLLECTED_SPO2:
            # Try to split the data correctly
            url = 'http://localhost:9080/api/data/add'
            now = datetime.now()
            # Format the date and time
            formatted_datetime = now.strftime("%Y%m%d%H%M%S")
            myobj = {
                "userId": formatted_datetime ,
                "heartrate": heartrate,
                "spo2": spo2,
                "ecg":ecg
            }

            # Send data to the server
            response = re.post(url, json=myobj)

            # Check the response from the server
            if response.status_code == 201:
                print(f"Data sent successfully: {response.content}")
            else:
                print(f"Failed to send data. Status code: {response.status_code}")
            COLLECT_DATA = False
            break
        else:
            # If 'FAILED' is detected in the line, break the loop
            if line.split('..')[-1] == 'FAILED':
                print("Data collection failed. Exiting.")
                INITIALIZATION_POM=False
                break
        # Print the line for debugging or logging
        print(line)
    
