#!/usr/bin/env python
import pika
import subprocess
import sys 
<<<<<<< HEAD
<<<<<<< HEAD

def speedtest():
    cmd = ['/usr/bin/python', '-u', '/home/netadmin/speedtest/speedtest_cli.py']
    print " [x] Executing speed test..."
   
    channel.queue_declare(queue='speedTestSendQueue', durable=True)
=======
=======
>>>>>>> origin/raspberrypi
import os
import time
import logging
import logging.handlers
import datetime
from datetime import datetime
import yaml
import uuid
import json
import requests

with open('/opt/speedtest/config.yaml', 'r') as f:
    config = yaml.load(f)

#Global variables
deviceId = config["device_info"]["deviceId"]
deviceType = config["device_info"]["deviceType"]
uri = config["message_server"]["uri"]
<<<<<<< HEAD
=======
username = config["message_server"]["username"]
password = config["message_server"]["password"]

>>>>>>> origin/raspberrypi
sessionId = ""

#Initialise syslogger
syslog = logging.getLogger('Syslog')
syslog.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
syslog.addHandler(handler)

#Initialise rabbitmq connection
<<<<<<< HEAD
credentials = pika.PlainCredentials('speedtest', '1nfield')
=======
credentials = pika.PlainCredentials(username, password)
>>>>>>> origin/raspberrypi
connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost', 5672, '/', credentials))
channel = connection.channel()
channel.queue_declare(queue='sendQueue')

def syslogger(message, severity):
    logtime = str(datetime.now())
    if severity == "info":
        syslog.info(logtime +': ' + message)
    elif severity == "critical":
        syslog.critical(logtime + ': ' + message)
    elif severity == "debug":
	syslog.debug(logtime + ': ' + message)    
    
def waitForPing( ip ):
    waiting =True
    counter =0
    logMsg = 'Testing Internet Connectivity.'
    syslogger(logMsg, 'info')
    remoteLogger(logMsg)
    channel.basic_publish(exchange='',routing_key="sendQueue",body=logMsg)
    while waiting:
	t = os.system('ping -c 1 -W 1 {}'.format(ip)+'> /dev/null 2>&1')
        if not t:
            waiting=False
	    logMsg = 'Ping reply from '+ip
            channel.basic_publish(exchange='',routing_key="sendQueue",body=logMsg)
	    syslogger(logMsg, 'info')
            remoteLogger(logMsg)
            return True
        else:
            counter +=1
	    if (counter%30 == 0):
                logMsg = 'Trying to connect to Internet for '+str(counter)+' seconds'
	        syslogger(logMsg, 'info')
                remoteLogger(logMsg)
	        channel.basic_publish(exchange='',routing_key="sendQueue",body=logMsg)
            if counter == 300: # this will prevent an never ending loop, set to the number of tries you think it will require
                waiting = False
		logMsg = 'Ping timeout after trying for '+str(counter)+' seconds!\nRestart the speed test by reconnecting the ethernet cable to the speed test device.'
		syslogger(logMsg, 'info')
                remoteLogger(logMsg)
		channel.basic_publish(exchange='',routing_key="sendQueue",body=logMsg)
                return False

def speedtest():
    cmd = ['/usr/bin/python', '-u', '/opt/speedtest/speedtest_cli.py']
    
    logMsg = 'Initiating Speed Test'
    syslogger(logMsg, 'info')
    remoteLogger(logMsg)
<<<<<<< HEAD
>>>>>>> origin/release1.0
=======
>>>>>>> origin/raspberrypi

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline,''):
        sys.stdout.flush()
<<<<<<< HEAD
<<<<<<< HEAD
        channel.basic_publish(exchange='',
                      routing_key="speedTestSendQueue",
                      body=line,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
    p.wait()
    return not p.returncode

def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)
    #Retry if unsuccessful
    if speedtest():
        print "[x] Successful"
	ch.basic_ack(delivery_tag = method.delivery_tag)
    else:
	print "[x] Unsuccessful"

connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
channel = connection.channel()

channel.queue_declare(queue='dhcpack')
    
channel.basic_consume(callback,
                      queue='dhcpack',
                      no_ack=False)

print ' [*] Waiting for messages. To exit press CTRL+C'
channel.start_consuming()


=======
=======
>>>>>>> origin/raspberrypi
        remoteLogger(line)
        channel.basic_publish(exchange='',
                      routing_key="sendQueue",
                      body=line)
    p.wait()
    return not p.returncode

def remoteLogger(msg):
    headers = {'Content-type': 'application/x-www-form-urlencoded ', 'Accept': 'text/plain'}
    json_data = json.dumps({'deviceId':deviceId, 'sessionId':str(sessionId), 'timeCreated':str(datetime.now()), 'msg':msg}) 
    payload = {'speedtest':json_data}
    r = requests.post(uri, data=payload, headers=headers)

def callback(ch, method, properties, body):
    global sessionId
    sessionId = uuid.uuid1()
    logMsg = 'Speed device has been plugged in. Initiating speed test process...'
    syslogger(logMsg, 'info')
    remoteLogger(logMsg)

    channel.basic_publish(exchange='',routing_key="sendQueue",body=logMsg)
    #print " [x] Received %r" % (body,)
    #Retry if unsuccessful
    if waitForPing("8.8.8.8") and speedtest():
	logMsg = 'Speed Test Completed!'
	channel.basic_publish(exchange='',routing_key="sendQueue",body=logMsg)
	syslogger(logMsg, 'info')
        remoteLogger(logMsg)
    else:
        logMsg = 'Speed Test Unsuccessful!'
        channel.basic_publish(exchange='',routing_key="sendQueue",body=logMsg)
	syslogger(logMsg, 'critical')
        remoteLogger(logMsg)

channel.queue_declare(queue='linkup')
    
channel.basic_consume(callback,
                      queue='linkup',
                      no_ack=True)

syslogger('Started speed test message receiver', 'info')
#print ' [*] Waiting for messages. To exit press CTRL+C'
channel.start_consuming()

<<<<<<< HEAD
>>>>>>> origin/release1.0
=======
>>>>>>> origin/raspberrypi
