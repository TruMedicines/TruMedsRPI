from datetime import datetime
import RPi.GPIO as GPIO
import time
import serial

ser = serial.Serial('/dev/ttyACM0',9600)

bool sentConfirmation = False 

def sendReminder(): # add from Zhongyi's code

def confirmTakePills(): # receive notice from web app that the user agrees to take pills.
        return takePills # bool

def takePhotos(): # takes photos of next day's pills
        # Raspi takes picture with backlight
        # Raspi sends a signal back saying that it took the picture
        # while loop reading from Arduino
                # Arduino sends signals that says the front light is lit
        
        # Raspi takes picture with front light
        

while True :
        now = datetime.now()
        currTime = int(now.strftime("%H%M%S")) # 24 hr clock
        schedTime = 9000 # filler for now. Will be an input time from user. 
        if (schedTime == currTime): # can also add an OR statement that adds receivedReminder
                sendReminder() 
                while not sentConfirmation:
                        sentConfirmation = confirmTakePills

                sentConfirmation = False # reset boolean for tomorrow's meds

                # send code to Arduino to send pills
                # while loop reading from Arduino
                        # Arduino sends signals that says the backlight is lit
                
                # at this point, the packet should have dispensed to the user right now
                takePhotos()
                
                # do other imaging stuff here. Add steve's code.
                # go to sleep until next scheduled time?
                
        
        
