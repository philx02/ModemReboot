import serial
import time
import socket
import smtplib
from email.mime.text import MIMEText

REMOTE_SERVER = '1.1.1.1'
MAX_CONSECUTIVE_FAILURE = 15

def notify(subject):
    sender = 'root@spoluck.ca'
    rcpt = 'root@spoluck.ca'
    msg = MIMEText('')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = rcpt
    s = smtplib.SMTP('localhost')
    s.sendmail(sender, [rcpt], msg.as_string())
    s.quit()

def rebootmodem():
    notify('Modem reboot alert')
    openstring = b'\xA0\x01\x01\xA2'
    closestring = b'\xA0\x01\x00\xA1'
    ser = serial.Serial('/dev/ttyUSB0', 9600)
    ser.write(openstring)
    time.sleep(10)
    ser.write(closestring)

def checkconnection(hostname):
    try:
        host = socket.gethostbyname(hostname)
        s = socket.create_connection((host, 53), 2)
        s.close()
        return True
    except:
        pass
    return False

closestring = b'\xA0\x01\x00\xA1'
ser = serial.Serial('/dev/ttyUSB0', 9600)
ser.write(closestring)
failure = 0
while True:
    if checkconnection(REMOTE_SERVER):
        if failure != 0:
            if failure >= 5:
                notify('Network is back')
            failure = 0
    else:
        failure += 1
        if failure % 5 == 0:
            notify('Network consecutive failure(s): ' + str(failure))
        if failure > MAX_CONSECUTIVE_FAILURE:
            failure = MAX_CONSECUTIVE_FAILURE
    print('failure: ' + str(failure))
    if failure == MAX_CONSECUTIVE_FAILURE:
        rebootmodem()
        failure = 0
    time.sleep(60)
