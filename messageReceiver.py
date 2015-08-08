#!/usr/bin/env python

import pika
import subprocess
import sys 
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

#Load configuration file
with open('/opt/speedtest/config.yaml', 'r') as f:
    config = yaml.load(f)

#Global variables
##Device configuration
deviceId = config["device-info"]["deviceId"]
deviceType = config["device-info"]["deviceType"]
macAddress = config["device-info"]["mac-address"]

##Message receiver (Remote REST API)
uri = config["message-receiver"]["uri"]

##Rabbit MQ related configuration
username = config["rabbit-mq"]["username"]
password = config["rabbit-mq"]["password"]
sendQueue = config["rabbit-mq"]["send-queue"]
syslogQueue = config["rabbit-mq"]["syslog-queue"]

##General configuration
pingTimeOut = config["general"]["ping-timeout"]

sessionId = ""

#Initialise syslogger
syslog = logging.getLogger('Syslog')
syslog.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
syslog.addHandler(handler)

#Initialise rabbitmq connection
credentials = pika.PlainCredentials(username, password)
connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost', 5672, '/', credentials))
channel = connection.channel()
channel.queue_declare(queue=sendQueue)

#Log to syslog
def syslogger(message, severity):
    logtime = str(datetime.now())
    if severity == "info":
        syslog.info(logtime +': ' + message)
    elif severity == "critical":
        syslog.critical(logtime + ': ' + message)
    elif severity == "debug":
	syslog.debug(logtime + ': ' + message)    

def rabbitmqLog (message, queue, **kwargs):
    if kwargs.has_key('exchange'):
        exchange = kwargs.get('exchange', None)
    else:
        exchange = ''

    channel.basic_publish(exchange=exchange,routing_key=queue,body=message)

#Method for sending and logging messages
def processMessage(message, **kwargs):
#def processMessage(message, severity='info', queue=None, exchange='', remotelog=True, syslog=True, rabbitlog=True):
    severity = 'info'
    exchange = ''
    remotelog = True
    syslog = True
    rabbitlog = True    

    if kwargs.has_key('severity'):
        severity = kwargs.get('severity', None)

    if not kwargs.has_key('queue'):
        queue = sendQueue #default queue
    else:
        queue = kwargs.get('queue', None)

    if kwargs.has_key('exchange'):
        exchange = kwargs.get('exchange', None)

    if kwargs.has_key('syslog'):
       syslog = kwargs.get('syslog', None)
    
    if kwargs.has_key('rabbitlog'):
       rabbitlog = kwargs.get('rabbitlog')

    #Log to syslog?
    if syslog:
        syslogger(message, severity)

    #Log to rabbitMQ queue?
    if rabbitlog:
        rabbitmqLog(message, queue=queue)

    #Send log to remote log server
    if remotelog:
        remoteLogger(message)
    
#Make sure that the speed test device can reach Internet
def waitForPing( ip ):
    waiting =True
    counter =0
    logMsg = 'Testing Internet Connectivity.'
    processMessage(logMsg)
    while waiting:
	t = os.system('ping -c 1 -W 1 {}'.format(ip)+'> /dev/null 2>&1')
        if not t:
            waiting=False
	    logMsg = 'Ping reply from '+ip
            processMessage(logMsg)
            return True
        else:
            counter +=1
	    if (counter%30 == 0):
                logMsg = 'Trying to connect to Internet for '+str(counter)+' seconds'
	        processMessage(logMsg)
            if counter == pingTimeOut: # this will prevent an never ending loop, set to the number of tries you think it will require
                waiting = False
		logMsg = 'Ping timeout after trying for '+str(counter)+' seconds!\nRestart the speed test by reconnecting the ethernet cable to the speed test device.'
                processMessage(logMsg)
                return False

def speedtest():
    cmd = ['/usr/bin/python', '-u', '/opt/speedtest/speedtest_cli.py']
    
    logMsg = 'Initiating Speed Test'
    processMessage(logMsg)

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline,''):
        sys.stdout.flush()
	processMessage(line)
    p.wait()
    return not p.returncode

#Implement function to validate that dns can be resolved

def remoteLogger(msg):
    #TODO: error handling
    headers = {'Content-type': 'application/x-www-form-urlencoded ', 'Accept': 'text/plain'}
    json_data = json.dumps({'deviceId':deviceId, 'sessionId':str(sessionId), 'timeCreated':str(datetime.now()), 'msg':msg}) 
    payload = {'speedtest':json_data}
    r = requests.post(uri, data=payload, headers=headers)
    #If http error log this to syslog and rabbitmq retry?
    print r

def callback(ch, method, properties, body):
    global sessionId
    sessionId = uuid.uuid1()
    logMsg = 'Speed device has been plugged in. Initiating speed test process...' #Start tag to identify session start
    processMessage(logMsg)
    #Retry if unsuccessful
    if waitForPing("8.8.8.8") and speedtest():
	logMsg = 'Speed Test Completed!'
        processMessage(logMsg)
    else:
        logMsg = 'Speed Test Unsuccessful!'
        processMessage(logMsg, severity='critical')

channel.queue_declare(queue=syslogQueue)
    
channel.basic_consume(callback,
                      queue=syslogQueue,
                      no_ack=True)

syslogger('Started speed test message receiver', 'info')
#print ' [*] Waiting for messages. To exit press CTRL+C'
channel.start_consuming()

