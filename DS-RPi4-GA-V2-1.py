"""
Version 2.1 adds 3 more soil moisture sensor
and a 2nd IOT relay

"""

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
needed_light_time = 43200

# Pi4 GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

# Relay 1
GPIO.setup(5, GPIO.OUT)

# Relay 2
GPIO.setup(6, GPIO.OUT)

# Power Strip Relay IOT_Realy_1
GPIO.setup(13, GPIO.OUT)

# Power Strip Relay IOT_Realy_2
GPIO.setup(19, GPIO.OUT)

# Turning the light connect to IOT_Realy_1 on & the pump power source off (should be the default at startup)
GPIO.output(13, GPIO.LOW)

# Turning the 2nd light connect to IOT_Realy_2 on
GPIO.output(19, GPIO.LOW)

# Text to speech bot
engine = pyttsx3.init()
engine.say("DigitalSpiffy.com GreenHouse Automation version 9 is beginning")
engine.runAndWait()

# Soil moisture sensore setup
i2c_bus = board.I2C()
sensor_1 = Seesaw(i2c_bus, addr=0x36)
sensor_2 = Seesaw(i2c_bus, addr=0x37)
sensor_3 = Seesaw(i2c_bus, addr=0x38)
sensor_4 = Seesaw(i2c_bus, addr=0x39)

# Read moisture level through capacitive touch pad
touch_sensor_1 = sensor_1.moisture_read()
touch_sensor_2 = sensor_2.moisture_read()
touch_sensor_3 = sensor_3.moisture_read()
touch_sensor_4 = sensor_4.moisture_read()

# Read temperature from the sensors
temp_sensor_1 = sensor_1.get_temp()
temp_sensor_2 = sensor_2.get_temp()
temp_sensor_3 = sensor_3.get_temp()
temp_sensor_4 = sensor_4.get_temp()

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

            # Ensures the light is on
            GPIO.output(13, GPIO.LOW)
            GPIO.output(19, GPIO.LOW)

            # Current date & time variables for filenames used in photos/vids
            current_date = time.strftime("%m:%d:%Y")
            current_time = time.strftime("%H:%M:%S")

            # Convert Celsius to Farenheit, adjusted -2 for chip temp
            celsius_1 = float(temp_sensor_1)
            celsius_2 = float(temp_sensor_2)
            celsius_3 = float(temp_sensor_3)
            celsius_4 = float(temp_sensor_4)
            fahrenheit_1 = float((celsius_1 * 1.8) + 30  )
            fahrenheit_2 = float((celsius_2 * 1.8) + 30  )
            fahrenheit_3 = float((celsius_3 * 1.8) + 30  )
            fahrenheit_4 = float((celsius_4* 1.8) + 30  )
            format_farhenheit_1 = "{:.2f}".format(float(fahrenheit_1))
            format_farhenheit_2 = "{:.2f}".format(float(fahrenheit_2))
            format_farhenheit_3 = "{:.2f}".format(float(fahrenheit_3))
            format_farhenheit_4 = "{:.2f}".format(float(fahrenheit_4))

            # Printing and Bot saying temp and moisture level for sensor 1
            engine.say("Checking the sensor 1 for moisture level")
            engine.say("The moisture level is " + str(touch_sensor_1))
            print('The moisture level is for sensor 1 is: ' + str(touch_sensor_1))
            engine.say("The tempature is for sensor 1 is " + format_farhenheit_1 + " degrees farhenheit")
            print("Temperature: " + format_farhenheit_1 + " degrees farhenheit")
            engine.runAndWait()

            # Printing and Bot saying temp and moisture level for sensor 2
            engine.say("Checking sensor 2 for moisture level")
            engine.say("The moisture level for sensor 2 is " + str(touch_sensor_2))
            print('The moisture level is for sensor 2 is: ' + str(touch_sensor_2))
            engine.say("The tempature is for sensor 2 is " + format_farhenheit_2 + " degrees farhenheit")
            print("Temperature: " + format_farhenheit_2 + " degrees farhenheit")
            engine.runAndWait()

            # Setup for SendGrid API email
            message = Mail(
            from_email='dillan.craig@digitalspiffy.com',
            to_emails='dillan.k.craig@gmail.com',
            subject='Pump 1 has been activated @ ' + current_time,
            html_content='<strong>Photo taken on ' + current_date + ' at ' + current_time + '</strong>')
            time.sleep(60) # How often you check the moisture sensor (this needs to change to if else for prod)
            if touch_sensor_1 < 750:
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
                # Will add another sensor here
                # Turn on pump power supply & turn light off
                GPIO.output(13, GPIO.HIGH)
                # Turn on pump 2
                GPIO.output(6, GPIO.HIGH)
                print('Pump 2 ON')
                engine.say("The plants need water. Pump 2 is on")
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
            time_needed_until_light_on = 43200
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
            if touch < 750:
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
