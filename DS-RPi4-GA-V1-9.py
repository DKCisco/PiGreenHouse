import RPi.GPIO as GPIO
import time
import picamera
import sendgrid
from sendgrid import SendGridAPIClient
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

# Initialize time variable
initial = time.monotonic()

# Variables for light timer
light_on_time = datetime.datetime.utcnow()
needed_light_time = 30

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
engine.say("DigitalSpiffy.com GreenHouse Automation version 8 is beginning")
engine.runAndWait()

# Soil moisture sensore setup
i2c_bus = board.I2C()
ss = Seesaw(i2c_bus, addr=0x36)

# PiCamera setup
camera = picamera.PiCamera()
camera.rotation = 180

# Loop based on light time
try:
    while True:
        # Timer for light & amount of time needed for light to be on
        light_current_time = datetime.datetime.utcnow()
        light_timer = ((light_current_time - light_on_time).total_seconds())
        # Formatting light timer for print and bot speech
        format_timer_1 = "{:.2f}".format(float(light_timer))
        print(format_timer_1)
        # Where the timer is compared to the light needed in seconds
        if light_timer <= needed_light_time:
            # Bot states how long the light has been on for
            engine.say("The light has been on for " + format_timer_1 + "seconds")
            engine.runAndWait()
            GPIO.output(13, GPIO.LOW)
            # Current date & time variables for filenames used in photos/vids
            current_date = time.strftime("%m:%d:%Y")
            current_time = time.strftime("%H:%M:%S")
            # Read moisture level through capacitive touch pad
            touch = ss.moisture_read()
            # Read temperature from the temperature sensor
            temp = ss.get_temp()
            # Convert Celsius to Farenheit
            celsius_1 = float(temp)
            fahrenheit_1 = float((celsius_1 * 1.8) + 32  )
            format_farhenheit_1 = "{:.2f}".format(float(fahrenheit_1))
            # Printing and Bot saying temp and moisture level
            engine.say("Checking the sensor for moisture level")
            engine.say("The moisture level is " + str(touch))
            print('The moisture level is: ' + str(touch))
            engine.say("The tempature is " + format_farhenheit_1 + " degrees farhenheit")
            print("Temperature: " + format_farhenheit_1 + " degrees farhenheit")
            engine.runAndWait()
            # Setup for SendGrid API email
            message = Mail(
            from_email='dillan.craig@digitalspiffy.com',
            to_emails='dillan.k.craig@gmail.com',
            subject='Pump 1 has been activated @ ' + current_time,
            html_content='<strong>Photo taken on ' + current_date + ' at ' + current_time + '</strong>')
            time.sleep(5) # How often you check the moisture sensor (this needs to change to if else for prod)
            if touch < 860:
                # Bot says action
                engine.say("The plants need water. Pump 1 is on")
                engine.runAndWait()
                # Turn on pump power source
                GPIO.output(13, GPIO.HIGH)
                # Turn on the pump
                GPIO.output(5, GPIO.HIGH)
                print('Pump 1 ON')
                # Capture photo and video
                camera.capture('pump1.jpg')
                camera.start_recording('pump1.h264')
                # Wait while pump is on and recording video
                time.sleep(7)
                # Turn off pump 1
                GPIO.output(5, GPIO.LOW)
                # Turn off pump power source & light back on
                GPIO.output(13, GPIO.LOW)
                # Bot says action
                engine.say("Pump 1 is off")
                engine.runAndWait()
                print('Relay 1 OFF')
                camera.stop_recording()
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
                # Turn on pump power supply & turn light off
                GPIO.output(13, GPIO.HIGH)
                # Turn on pump 2
                GPIO.output(6, GPIO.HIGH)
                print('Pump 2 ON')
                engine.say("The plants needs water. Pump 2 is on")
                engine.runAndWait()
                time.sleep(5)
                GPIO.output(6, GPIO.LOW)
                # Turn off pump power supply & turn light on
                GPIO.output(13, GPIO.LOW)
                print('Pump 2 OFF')
                engine.say("Pump 2 is off")
                engine.runAndWait()
                time.sleep(1)
                sg = SendGridAPIClient(SENDGRID_API_KEY)
                # time.sleep(43200) # 12 hours
                time.sleep(10)
        else:
            GPIO.output(13, GPIO.HIGH)
            light_off_time = datetime.datetime.utcnow()
            engine.say("The light is off!")
            engine.runAndWait()
            time_needed_until_light_on = 60
            # Current date & time variables for filenames used in photos/vids
            current_date = time.strftime("%m:%d:%Y")
            current_time = time.strftime("%H:%M:%S")
            # Read moisture level through capacitive touch pad
            touch = ss.moisture_read()
            # Read temperature from the temperature sensor
            temp = ss.get_temp()
            # Convert Celsius to Farenheit
            celsius_1 = float(temp)
            fahrenheit_1 = float((celsius_1 * 1.8) + 32  )
            format_farhenheit_1 = "{:.2f}".format(float(fahrenheit_1))
            # Printing and Bot saying temp and moisture level
            engine.say("Checking the sensor for moisture level")
            engine.say("The moisture level is " + str(touch))
            print('The moisture level is: ' + str(touch))
            engine.say("The tempature is " + format_farhenheit_1 + " degrees farhenheit")
            print("Temperature: " + format_farhenheit_1 + " degrees farhenheit")
            engine.runAndWait()
            # Setup for SendGrid API email
            message = Mail(
            from_email='dillan.craig@digitalspiffy.com',
            to_emails='dillan.k.craig@gmail.com',
            subject='Pump 1 has been activated @ ' + current_time,
            html_content='<strong>Photo taken on ' + current_date + ' at ' + current_time + '</strong>')
            # How often you check the moisture sensor (this needs to change to if else for prod)
            time.sleep(5)
            light_timer_2 = ((light_off_time - light_on_time)).total_seconds()
            print(light_off_time)
            print(light_on_time)
            print(light_timer_2)
            if light_timer_2 >= time_needed_until_light_on:
                # Run a new iteration of the current script, providing any command line args from the current iteration.
                camera.close()
                GPIO.cleanup() 
                os.execv(sys.executable, ['python'] + sys.argv)
            if touch < 860:
                # Bot says action
                engine.say("The plants need water. Pump 1 is on")
                engine.runAndWait()
                # Turn on pump power source
                GPIO.output(13, GPIO.HIGH)
                # Turn on the pump
                GPIO.output(5, GPIO.HIGH)
                print('Pump 1 ON')
                # Capture photo and video
                camera.capture('pump1.jpg')
                camera.start_recording('pump1.h264')
                # Wait while pump is on and recording video
                time.sleep(7)
                # Turn off pump 1
                GPIO.output(5, GPIO.LOW)
                # Turn off pump power source & light back on
                GPIO.output(13, GPIO.LOW)
                # Bot says action
                engine.say("Pump 1 is off")
                engine.runAndWait()
                print('Relay 1 OFF')
                camera.stop_recording()
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
                # Turn on pump power supply & turn light off
                GPIO.output(13, GPIO.HIGH)
                # Turn on pump 2
                GPIO.output(6, GPIO.HIGH)
                print('Pump 2 ON')
                engine.say("The plants needs water. Pump 2 is on")
                engine.runAndWait()
                time.sleep(5)
                GPIO.output(6, GPIO.LOW)
                # Turn off pump power supply & turn light on
                GPIO.output(13, GPIO.LOW)
                print('Pump 2 OFF')
                engine.say("Pump 2 is off")
                engine.runAndWait()
                time.sleep(1)
                sg = SendGridAPIClient(SENDGRID_API_KEY)
                time.sleep(10)

finally:
    print('error')
    camera.close()
