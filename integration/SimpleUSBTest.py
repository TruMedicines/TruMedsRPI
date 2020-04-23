import time
import serial
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from time import sleep # Import the sleep function from the time module

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(3, GPIO.OUT, initial=GPIO.LOW) # Set pin 8 to be an output pin and set initial value to low (off)

ser = serial.Serial('/dev/ttyACM0',9600)
ser.flush()

def sendByte(sentence, ser):
        sentence = sentence + "\n"
        ser.write(sentence.encode('ascii'))

def readByte(sentence, ser):
        line = ""
        while line != sentence:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').rstrip()

time.sleep(1) # Sleep for 1 second
sendByte("on", ser)
time.sleep(1)
sendByte("on", ser)

