import RPi.GPIO as GPIO
import time
import picamera
import sendgrid
from sendgrid import SendGridAPIClient
import os
import board
import time
from adafruit_seesaw.seesaw import Seesaw
from sendgrid import SendGridAPIClient
# Import for SendGrid Email that will be sent when pump is on
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName,
    FileType, Disposition, ContentId)
import base64  # Used for the file attachment
from send_grid_api import SENDGRID_API_KEY
import RPi.GPIO as GPIO
import time
import pyttsx3

engine = pyttsx3.init()

engine.say("DigitalSpiffy.com GreenHouse Automation version 6 is beginning")
engine.runAndWait()

# Soil moisture sensore setup
i2c_bus = board.I2C()
ss = Seesaw(i2c_bus, addr=0x36)

GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

camera = picamera.PiCamera()
camera.rotation = 180

# Relay 1
GPIO.setup(6, GPIO.OUT)

# Relay 2
GPIO.setup(13, GPIO.OUT)

try:
    while True:
        # Current date & time variables for filenames used in photos/vids
        current_date = time.strftime("%m:%d:%Y")
        current_time = time.strftime("%H:%M:%S")
        # Read moisture level through capacitive touch pad
        touch = ss.moisture_read()
        # Read temperature from the temperature sensor
        temp = ss.get_temp()
        print("temp: " + str(temp) + "  moisture: " + str(touch))
        print("Temperature: {}".format(temp))
        # Setup for SendGrid API email
        message = Mail(
        from_email='dillan.craig@digitalspiffy.com',
        to_emails='dillan.k.craig@gmail.com',
        subject='Pump 1 has been activated @ ' + current_time,
        html_content='<strong>Photo taken on ' + current_date + ' at ' + current_time + '</strong>')
        time.sleep(5)
        if touch < 860:
            # Turn on the pump
            GPIO.output(6, GPIO.HIGH)
            print('Relay 1 ON')
            engine.say("Pump 1 is on")
            engine.runAndWait()
            camera.capture('pump1.jpg')
            camera.start_recording('pump1.h264')
            time.sleep(3)
            GPIO.output(6, GPIO.LOW)
            engine.say("Pump 1 is off")
            engine.runAndWait()
            print('Relay 1 OFF')
            camera.stop_recording()
            time.sleep(1)
            # Current date & time variables for filenames used in photos/vids
            current_date = time.strftime("%m:%d:%Y")
            current_time = time.strftime("%H:%M:%S")
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            #response = sg.send(message)
            # Email attachment of photo taken
            file_path = 'pump1.jpg'
            with open(file_path, 'rb') as f:
                data = f.read()
                f.close()
                encoded = base64.b64encode(data).decode()
                attachment = Attachment()
                attachment.file_content = FileContent(encoded)
                attachment.file_type = FileType('application/jpg')
                attachment.file_name = FileName('pump1.jpg')
                attachment.disposition = Disposition('attachment')
                attachment.content_id = ContentId('Example Content ID')
                message.attachment = attachment
            time.sleep(2)
            response = sg.send(message)
            GPIO.output(13, GPIO.HIGH)
            print('Relay 2 ON')
            engine.say("Pump 2 is on")
            engine.runAndWait()
            time.sleep(1)
            GPIO.output(13, GPIO.LOW)
            print('Relay 2 OFF')
            engine.say("Pump 2 is off")
            engine.runAndWait()
            time.sleep(1)
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            # time.sleep(43200) # 12 hours
            time.sleep(120)

finally:
    print('error')
    camera.close()
