
'''
#!/usr/bin/python             # This is server.py file
import socket                 # Import socket module
import time
import RPi.GPIO as GPIO       # Import GPIO library
GPIO.setmode(GPIO.BOARD)      # Use board pin numbering
GPIO.setup(11, GPIO.OUT)      # Setup GPIO Pin 11 to OUT
GPIO.output(11,False)         # Init Led off

def led_blink():
    while 1:
        print "got msg"         # Debug msg
        GPIO.output(11,True)    # Turn on Led
        time.sleep(1)           # Wait for one second
        GPIO.output(11,False)   # Turn off Led
        time.sleep(1)           # Wait for one second
    GPIO.cleanup()

s = socket.socket()           # Create a socket object
host = "localhost"        # Get local machine name
port = 1883                 # Port
s.bind((host, port))          # Bind to the port
s.listen(5)                   # Now wait for client connection.
while True:
    c, addr = s.accept()       # Establish connection with client.
    print 'Got connection from', addr
    msg = c.recv(1024)
    msg1 = '10'
    if msg == msg1:
        led_blink()
    print msg
    c.close()


import socket               # Import socket module
s = socket.socket()         # Create a socket object
host = "localhost" # Get local machine name
port = 1883                # port

s.connect((host, port))
s.send('10')
s.close  

'''

import paho.mqtt.publish as publish
import time
print("Sending 0...")
publish.single("esp8266/4", "1", hostname="localhost")
time.sleep(1)
print("Sending 1...")
publish.single("ledStatus", "1", hostname="localhost")