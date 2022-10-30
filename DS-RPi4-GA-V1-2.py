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
#Import for SendGrid Email that will be sent when pump is on
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName,
    FileType, Disposition, ContentId)
import base64 # Used for the file attachment
from send_grid_api import SENDGRID_API_KEY

# Current date & time variables for filenames used in photos/vids
current_date = time.strftime("%m: %d :%Y ,%H: %M: %S")
current_time = time.strftime("%H: %M: %S")
filename_photo = "Pump" + current_date + '.jpg'
filename_video = "Pump" + current_date + '.h264'

# Setup for SendGrid API email
message = Mail(
    from_email='dillan.craig@digitalspiffy.com',
    to_emails='dillan.k.craig@gmail.com',
    subject= 'Pump 1 has been activated 2 @ ' + current_time,
    html_content='<strong>and easy to do anywhere, even with Python</strong>')

# Email attachment (this will be moved to the photo that is taken)
file_path = 'example.pdf'
with open(file_path, 'rb') as f:
    data = f.read()
    f.close()

encoded = base64.b64encode(data).decode()
attachment = Attachment()
attachment.file_content = FileContent(encoded)
attachment.file_type = FileType('application/pdf')
attachment.file_name = FileName('example.pdf')
attachment.disposition = Disposition('attachment')
attachment.content_id = ContentId('Example Content ID')
message.attachment = attachment
try:
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)

camera = picamera.PiCamera()
camera.rotation = 180

GPIO.setmode(GPIO.BCM)

# Relay 1
GPIO.setup(21, GPIO.OUT)

# Relay 2
GPIO.setup(26, GPIO.OUT)

#try:
    #while True:
GPIO.output(21, GPIO.HIGH)
print('Relay 1 ON')
camera.capture(filename_photo)
camera.start_recording(filename_video)
time.sleep(5)
camera.stop_recording()
time.sleep(1)
GPIO.output(21, GPIO.LOW)
print('Relay 1 OFF')
sg = SendGridAPIClient(SENDGRID_API_KEY)
response = sg.send(message)
time.sleep(1)
GPIO.output(26, GPIO.HIGH)
print('Relay 2 ON') 
time.sleep(1)
GPIO.output(26, GPIO.LOW)
print('Relay 2 OFF')
time.sleep(1)
camera.close()
    
#finally:
