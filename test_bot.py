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


# Text to speech bot
engine = pyttsx3.init()
engine.say("How's it going my ginger")
engine.runAndWait()