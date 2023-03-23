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

# Initialize time variable
initial = time.monotonic()

# Variables for light timer
light_on_time = datetime.datetime.utcnow()
needed_light_time = 43200

# Text to speech bot
engine = pyttsx3.init()
print("DigitalSpiffy.com GreenHouse timer test is beginning")
engine.say("DigitalSpiffy.com GreenHouse timer test is beginning")
engine.runAndWait()

time.sleep(120)

# Formatting light timer for print and bot speech
light_current_time = datetime.datetime.utcnow()
light_timer = ((light_current_time - light_on_time).total_seconds())
minutes_timer = (float(light_timer//60))
format_timer_1 = "{:.2f}".format(float(minutes_timer))

# Bot states how long the light has been on for
engine.say("The light has been on for " + format_timer_1 + "seconds")
engine.runAndWait()

# Print the timer value
print("The light has been on for " + format_timer_1 + " minutes")
print(format_timer_1)