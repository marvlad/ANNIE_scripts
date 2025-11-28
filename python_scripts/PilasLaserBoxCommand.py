#!/usr/bin/python

import serial
import sys 
import os

serial_port = '/dev/ttyUSB0'
if not os.path.exists(serial_port):
    print("ERROR: Serial port /dev/ttyUSB0 not detected. The laser box is not powered or the USB is not connected.")
    sys.exit(1)
print("*** Welcome to Picosecond Laser System ***")

# Open the serial port
ser = serial.Serial(serial_port, 19200, timeout=1)  # Adjust baud rate as needed

# Send the command
#ser.write(b"version?\n")

# Get the command from user input
#command = input("Enter the command to send: ")

# Check if a command was provided as an argument
if len(sys.argv) < 2:
   print("Use: PiLaserBoxCommand \"<command>\"")
   #print("Example: PiLaserBoxCommand \"help?\"")
   #sys.exit(1)
   command = "help?"
else:
   command = sys.argv[1]
  

# Get the command from the command-line argument
#command = sys.argv[1]

# Send the command
ser.write((command + "\n").encode('utf-8'))

# Read the response
while True:
  response = ser.readline().decode('utf-8').strip()
  if not response:  # Break the loop if no more data is received
    break
  #print("Controller Serial Number:", response)
  print(response)

# Close the serial port
ser.close()
