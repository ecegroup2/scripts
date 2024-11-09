#!/usr/bin/env python3
import serial
import requests as re
import time
from datetime import datetime
# Define constants for the device readiness and initialization messages
INITIALIZATION_SUCCESS = "Initializing pulse oximeter..SUCCESS"
INITIALIZATION_FAILED = "Initializing pulse oximeter..FAILED"
TIMEOUT_SECONDS = 10  # Time to wait for the device to be ready (in seconds)
INITIALIZATION_SERIAL=False
INITIALIZATION_POM=False
while True:
    # Try to open the serial port
    if not INITIALIZATION_SERIAL:
        try:
            ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
            ser.reset_input_buffer()
            INITIALIZATION_SERIAL=True
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            INITIALIZATION_SERIAL=False
        
    while INITIALIZATION_SERIAL:
        if ser.in_waiting > 0:
            time.sleep(1)
            line = ser.readline().decode('utf-8').rstrip()
            print(f"Received: {line}")
                
                # Check for successful initialization
            if line == INITIALIZATION_SUCCESS:
                print("Pulse oximeter initialized successfully.")
                  # Proceed with normal operation
                INITIALIZATION_POM=True
                break
                # Check for failed initialization
            elif line == INITIALIZATION_FAILED:
                print("Pulse oximeter initialization failed.")
                INITIALIZATION_POM=False

    COLLECT_DATA = False
    while INITIALIZATION_POM and INITIALIZATION_SERIAL:
        if ser.in_waiting > 0:
            # Read data from the serial buffer
            line = ser.readline().decode('utf-8').rstrip()
            
            # Handle data collection
            if COLLECT_DATA:
                try:
                    # Try to split the data correctly
                    a, b = line.split(' : ')
                    a = float(a)
                    b = float(b)
                    url = 'http://localhost:9080/api/data/add'
                    now = datetime.now()
                    # Format the date and time
                    formatted_datetime = now.strftime("%Y%m%d%H%M%S")
                    myobj = {"userId": formatted_datetime ,"heartrate": a, "spo2": b}

                    # Send data to the server
                    response = re.post(url, json=myobj)

                    # Check the response from the server
                    if response.status_code == 201:
                        print(f"Data sent successfully: {response.content}")
                    else:
                        print(f"Failed to send data. Status code: {response.status_code}")
                except ValueError:
                    # If the line cannot be split or converted to float, log the error and continue
                    print(f"Skipping invalid data: {line}")
                COLLECT_DATA = False
                break
            elif len(line) <= 2:
                # If line is just a small number, start collecting data when '60' is received
                if line == '60':
                    COLLECT_DATA = True
            else:
                # If 'FAILED' is detected in the line, break the loop
                if line.split('..')[-1] == 'FAILED':
                    print("Data collection failed. Exiting.")
                    INITIALIZATION_POM=False
                    break
            # Print the line for debugging or logging
            print(line)
        # Optional: Add a short sleep time to reduce CPU usage
        time.sleep(1)
        time.sleep(1)
    time.sleep(TIMEOUT_SECONDS)
    
