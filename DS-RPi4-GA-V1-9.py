import RPi.GPIO as GPIO
import time
import picamera
import sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *
import sys
import os
import board
from adafruit_seesaw.seesaw import Seesaw
from sendgrid import SendGridAPIClient
# Import for SendGrid Email that will be sent when pump is on
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName,
    FileType, Disposition, ContentId)
import base64  # Used for the file attachment
from send_grid_api import SENDGRID_API_KEY
import pyttsx3
import datetime

#Current version modified 3/23/23

# Initialize time variable
initial = time.monotonic()

# Variables for light timer
light_on_time = datetime.datetime.utcnow()
needed_light_time = 43200 # 12 hours in seconds

# Pi4 GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

# Relay 1
GPIO.setup(5, GPIO.OUT)

# Relay 2
GPIO.setup(6, GPIO.OUT)

# Power Strip Relay
GPIO.setup(13, GPIO.OUT)

# Turning the light on & the pump power source off (should be the default at startup)
GPIO.output(13, GPIO.LOW)

# Text to speech bot
engine = pyttsx3.init()
engine.say("DigitalSpiffy.com GreenHouse Automation version 1.9 is beginning")
engine.runAndWait()
print("DigitalSpiffy.com GreenHouse Automation version 1.9 is beginning")

# Sleep setup for light timer to be accurate
time.sleep(120)

# Soil moisture sensore setup
i2c_bus = board.I2C()
#sensor_1 = Seesaw(i2c_bus, addr=0x36)
sensor_2 = Seesaw(i2c_bus, addr=0x37)
#sensor_3 = Seesaw(i2c_bus, addr=0x38)
sensor_4 = Seesaw(i2c_bus, addr=0x39)

# PiCamera setup
camera = picamera.PiCamera()
camera.rotation = 180

# Convert Celsius to Farenheit, adjusted -2 for chip temp
celsius_2 = float(sensor_2.get_temp())
celsius_4 = float(sensor_4.get_temp())
fahrenheit_2 = float((celsius_2 * 1.8) + 30  )
fahrenheit_4 = float((celsius_4* 1.8) + 30  )
format_farhenheit_2 = "{:.2f}".format(float(fahrenheit_2))
format_farhenheit_4 = "{:.2f}".format(float(fahrenheit_4))

# Loop based on light time
try:
    while True:
        # Timer for light & amount of time needed for light to be on
        light_current_time = datetime.datetime.utcnow()
        light_timer = ((light_current_time - light_on_time).total_seconds())
        minutes_timer = (int(light_timer//60))
        # Formatting light timer for print and bot speech
        format_timer_1 = "{:.2f}".format(float(minutes_timer))
        # Where the timer is compared to the light needed in seconds
        if light_timer <= needed_light_time:
            # Bot states how long the light has been on for
            engine.say("The light has been on for " + format_timer_1 + "minutes")
            engine.runAndWait()
            print("The light has been on for " + format_timer_1 + " minutes")
            GPIO.output(13, GPIO.LOW)
            # Current date & time variables for filenames used in photos/vids
            current_date = time.strftime("%m:%d:%Y")
            current_time = time.strftime("%H:%M:%S")
            # Read moisture level through capacitive touch pad
            sensor_2.moisture_read()
            # Read temperature from the temperature sensor
            sensor_2.get_temp()
            # Printing and Bot saying temp and moisture level for sensor 2
            engine.say("Checking sensor 2 for moisture level")
            engine.runAndWait()
            engine.say("The moisture level for sensor 2 is " + str(sensor_2.moisture_read()))
            engine.runAndWait()
            print('The moisture level  for sensor 2 is: ' + str(sensor_2.moisture_read()))
            engine.say("The tempature for sensor 2 is " + format_farhenheit_2 + " degrees farhenheit")
            engine.runAndWait()
            print("Temperature: " + format_farhenheit_2 + " degrees farhenheit")
            # Printing and Bot saying temp and moisture level for sensor 4
            engine.say("Checking sensor 4 for moisture level")
            engine.runAndWait()
            engine.say("The moisture level for sensor 4 is " + str(sensor_4.moisture_read()))
            engine.runAndWait()
            print('The moisture level for sensor 4 is: ' + str(sensor_4.moisture_read()))
            engine.say("The tempature for sensor 4 is " + format_farhenheit_4 + " degrees farhenheit")
            engine.runAndWait()
            print("Temperature: " + format_farhenheit_4 + " degrees farhenheit")
            # Setup for SendGrid API email
            message = Mail(
            from_email='dillan.craig@digitalspiffy.com',
            to_emails='dillan.k.craig@gmail.com',
            subject='Pump 1 has been activated @ ' + current_time,
            html_content='<strong>Photo taken on ' + current_date + ' at ' + current_time + '</strong>')
            # Boolean for moisture sensor
            if sensor_2.moisture_read() < 950:
                # Bot says action
                engine.say("The plants need water. Pump 1 is on")
                engine.runAndWait()
                # Turn on pump power source
                GPIO.output(13, GPIO.HIGH)
                # Turn on the pump
                GPIO.output(5, GPIO.HIGH)
                print('Pump 1 ON')
                # Capture photo
                camera.capture('pump1.jpg')
                # Turn off pump 1
                GPIO.output(5, GPIO.LOW)
                # Turn off pump power source & light back on
                GPIO.output(13, GPIO.LOW)
                # Bot says action
                engine.say("Pump 1 is off")
                engine.runAndWait()
                print('Relay 1 OFF')
                time.sleep(1)
                # Current date & time variables for filenames used in photos/vids
                current_date = time.strftime("%m:%d:%Y")
                current_time = time.strftime("%H:%M:%S")
                # SendGrid API Call
                sg = SendGridAPIClient(SENDGRID_API_KEY)
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
                time.sleep(1)
                response = sg.send(message)
                # Will add another sensor here
            if sensor_4.moisture_read() < 950:
                # Bot says action
                engine.say("The plants need water. Pump 2 is on")
                engine.runAndWait()
                # Turn on pump power supply & turn light off
                GPIO.output(13, GPIO.HIGH)
                # Turn on pump 2
                GPIO.output(6, GPIO.HIGH)
                print('Pump 2 ON')
                time.sleep(25)
                GPIO.output(6, GPIO.LOW)
                # Turn off pump power supply & turn light on
                GPIO.output(13, GPIO.LOW)
                print('Pump 2 OFF')
                engine.say("Pump 2 is off")
                engine.runAndWait()
                time.sleep(1)
                # Current date & time variables for filenames used in photos/vids
                current_date = time.strftime("%m:%d:%Y")
                current_time = time.strftime("%H:%M:%S")
                # Capture photo
                camera.capture('pump2.jpg')
                # SendGrid API Call
                sg = SendGridAPIClient(SENDGRID_API_KEY)
                # Email attachment of photo taken
                file_path = 'pump2.jpg'
                with open(file_path, 'rb') as f:
                    data = f.read()
                    f.close()
                    encoded = base64.b64encode(data).decode()
                    attachment = Attachment()
                    attachment.file_content = FileContent(encoded)
                    attachment.file_type = FileType('application/jpg')
                    attachment.file_name = FileName('pump2.jpg')
                    attachment.disposition = Disposition('attachment')
                    attachment.content_id = ContentId('Example Content ID')
                    message.attachment = attachment
                    response = sg.send(message)
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            # How often you check the moisture sensor
            time.sleep(3600)   
        else:
            GPIO.output(13, GPIO.HIGH)
            engine.say("The light has been turned off.")
            engine.runAndWait()
            print("The light has been turned off at " + current_time + "on " + current_date)
            # How long the light will be off
            time.sleep(43200)
            # Run a new iteration of the current script, providing any command line args from the current iteration.
            camera.close()
            GPIO.cleanup() 
            os.execv(sys.executable, ['python'] + sys.argv)

finally:
    print('error')
    camera.close()
