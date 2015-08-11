#!/usr/bin/env python

import pika
import subprocess
import sys 
import os
import signal
import time
import logging
import logging.handlers
import datetime
from datetime import datetime
import yaml
import uuid
from uuid import getnode as get_mac
import json
import requests
import pprint

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

##Configuration service (Remote REST API)
configuri =  config["configuration-service"]["uri"]

##Rabbit MQ related configuration
username = config["rabbit-mq"]["username"]
password = config["rabbit-mq"]["password"]
sendQueue = config["rabbit-mq"]["send-queue"]
syslogQueue = config["rabbit-mq"]["syslog-queue"]

##General configuration
pingTimeOut = config["general"]["ping-timeout"]
remoteLoggerRetry = config["general"]["remote-retry"]
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
    try:
        if severity == "info":
            syslog.info(logtime +': ' + message)
        elif severity == "critical":
            syslog.critical(logtime + ': ' + message)
        elif severity == "debug":
    	    syslog.debug(logtime + ': ' + message)    
        return True
    except Exception as e:
        processMessage("Unable to log message to syslog: "+str(e),severity='critical',syslog=False)
        raise 

def rabbitmqLog (message, queue, **kwargs):
    if kwargs.has_key('exchange'):
        exchange = kwargs.get('exchange', None)
    else:
        exchange = ''
    try:
        channel.basic_publish(exchange=exchange,routing_key=queue,body=message)
    except Exception as e:
        processMessage("Unable to push message to RabbitMQ queue: "+str(e),severity='critical', rabbitlog=False)
        raise
   
    

#Method for sending and logging messages
def processMessage(message, **kwargs):
    severity = 'info'
    exchange = ''
    remotelog = True
    syslog = True
    rabbitlog = True    
    logError = False

    if kwargs.has_key('severity'):
        severity = kwargs.get('severity', None)

    if not kwargs.has_key('queue'):
        queue = sendQueue #default queue
    else:
        queue = kwargs.get('queue', None)

    if kwargs.has_key('exchange'):
        exchange = kwargs.get('exchange', None)

    if kwargs.has_key('remotelog'):
        remotelog = kwargs.get('remotelog', None)

    if kwargs.has_key('syslog'):
       syslog = kwargs.get('syslog', None)
    
    if kwargs.has_key('rabbitlog'):
       rabbitlog = kwargs.get('rabbitlog')

    #Log to syslog?
    if syslog:
        syslogger(message, severity)

    #Log to rabbitMQ queue?
    if rabbitlog:
        logError = rabbitmqLog(message, queue=queue)

    #Send log to remote log server
    if remotelog:
        logError = remoteLogger(message)

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
    #Add possibility to select which servers to execute speed test against
    #Add parameters to the python script to execute simple mode etc.
    #TODO function to sort serverlist provided by configuration service
    #TODO loop through server list if one fails
    
    cmd = ['/usr/bin/python', '-u', '/opt/speedtest/speedtest_cli.py']

    try:
        logMsg = 'Initiating Speed Test'
        processMessage(logMsg)

        deviceMac = get_mac()
        deviceMac = ':'.join(("%012X" % deviceMac)[i:i+2] for i in range(0, 12, 2))

        request = getSpeedTestRequest(deviceMac)
        #TODO Validate result from getSpeedTestRequest
        srvList = request['request']['serverlist']

        rqId = request['request']['rqid']
        serviceOrderId = request['request']['serviceorderid']
        bwDown = request['request']['bandwidthdown']
        bwUp = request['request']['bandwidthup']

        logMsg = 'No Speed Test server related to the RSP of the service order. Selecting the closest one.'

        if len(srvList) > 0:
            #TODO sort list based on distance
            cmd = ['/usr/bin/python', '-u', '/opt/speedtest/speedtest_cli.py', '--server', srvList[0]]
            logMsg = 'Selecting Speed Test server ('+srvList[0]+') based on service order '+str(serviceOrderId)+' with bandwidth setting '+bwDown+'/'+bwUp+' Mb/s'

        processMessage(logMsg)
	pprint.pprint(cmd)

        #p = subprocess.Popen(cmd, stdout=subprocess.PIPE, preexec_fn=os.setsid)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        for line in iter(p.stdout.readline,''):
            sys.stdout.flush()
	    processMessage(line)

        p.wait()
        return not p.returncode
    except Exception as e:
        processMessage("Unable to complete Speed Test through external python script: "+str(cmd),remotelog=False, rabbitlog=False)
        raise

#Implement function to validate that dns can be resolved

def remoteLogger(msg):
    tries = 0
    tryAgain = True

    headers = {'Content-type': 'application/x-www-form-urlencoded ', 'Accept': 'text/plain'}
    json_data = json.dumps({'deviceId':deviceId, 'sessionId':str(sessionId), 'timeCreated':str(datetime.now()), 'msg':msg}) 
    payload = {'speedtest':json_data}

    #Try to send HTTP Request, retry 3 times
    while tryAgain:
        try:
            tries += 1
            r = requests.post(uri, data=payload, headers=headers)
            tryAgain = False
        except requests.exceptions.Timeout:
            processMessage("Connection to server: "+uri+" timed out. Tried "+str(tries)+" times.", remotelog=False)
            if tries > remoteLoggerRetry:
                tryAgain = False
        except requests.exceptions.TooManyRedirects:
            processMessage("Too many redirects when trying to connect to: "+uri+". Tried "+str(tries)+" times.", remotelog=False)
            if tries > remoteLoggerRetry:
                tryAgain = False
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            processMessage("HTTP Request Exception. Trying to connect to "+uri+". Tried "+str(tries)+" times.", remotelog=False, severity='critical')
            if tries > remoteLoggerRetry:
               tryAgain = False
               raise
        #wait 10 seconds
        time.sleep(10)

def getSpeedTestRequest(deviceMac, **kwargs):
    tries = 0
    tryAgain = True

    if kwargs.has_key('deviceid'):
        deviceId = kwargs.get('deviceid', None)
    else:
   	deviceId = 0

    headers = {'Content-type': 'application/x-www-form-urlencoded ', 'Accept': 'text/plain'}
    json_data = json.dumps({'deviceId':deviceId, 'deviceMac':deviceMac})
    payload = {'getconfiguration':json_data}
    
    #Try to send HTTP Request, retry 3 times
    while tryAgain:
        try:
            tries += 1
            r = requests.post(configuri, data=payload, headers=headers)
            response = json.loads(r.text)
            request = json.loads(response['data'])
            tryAgain = False
        except requests.exceptions.Timeout:
            processMessage("Connection to server: "+configuri+" timed out. Tried "+str(tries)+" times.", remotelog=False)
            if tries > remoteLoggerRetry:
                tryAgain = False
        except requests.exceptions.TooManyRedirects:
            processMessage("Too many redirects when trying to connect to: "+configuri+". Tried "+str(tries)+" times.", remotelog=False)
            if tries > remoteLoggerRetry:
                tryAgain = False
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            processMessage("HTTP Request Exception. Trying to connect to "+configuri+". Tried "+str(tries)+" times.", remotelog=False, severity='critical')
            if tries > remoteLoggerRetry:
               tryAgain = False
               raise
        #wait 10 seconds
        time.sleep(10)
    return request


def callback(ch, method, properties, body):
    global sessionId
    try:
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
    except Exception as e:
        processMessage(str(e), severity='critical', remotelog=False, rabbitlog=False)
        raise

while True: 
    try:
        channel.queue_declare(queue=syslogQueue)
    
        channel.basic_consume(callback,
                      queue=syslogQueue,
                      no_ack=True)
        syslogger('Started speed test message receiver', 'info')

        #print ' [*] Waiting for messages. To exit press CTRL+C'
        channel.start_consuming()

    except Exception as e:
        print "Unable to perform speed test due to: "+str(e)+"\n"


