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

#TODO: Run speed test in simple mode by getting run mode from argsv (init-script parameter)
#TODO: Method to sort the provided speed test server list based on distance from speed test device
#TODO: Loop through speed test server list if test fail
#TODO: Robustness if RabbitMQ fails?

#Load configuration file
with open('/opt/speedtest/config.yaml', 'r') as f:
    config = yaml.load(f)

#Global variables
##Device configuration
deviceId = config["device-info"]["deviceId"]
deviceType = config["device-info"]["deviceType"]
macAddress = config["device-info"]["mac-address"]

##Message receiver (Remote REST API)
URI = config["message-service"]["uri"]
postSvc = config["message-service"]["post-svc"]

##Request configuration service (Remote REST API)
configURI =  config["request-service"]["uri"]
getConfigSvc = config["request-service"]["get-config-svc"]
updateStatusSvc = config["request-service"]["update-status-svc"]


##Rabbit MQ related configuration
username = config["rabbit-mq"]["username"]
password = config["rabbit-mq"]["password"]
sendQueue = config["rabbit-mq"]["send-queue"]
syslogQueue = config["rabbit-mq"]["syslog-queue"]

##General configuration
pingTimeOut = config["general"]["ping-timeout"]
remoteLoggerTimeout = config["general"]["remote-timeout"]
requestConfigTimeout = config["general"]["request-config-timeout"]
updateRequestStatusTimeout = config["general"]["update-request-status-timeout"]
speedTestMiniEnabled = config["speed-test"]["mini-enabled"]
speedTestMiniServer = config["speed-test"]["mini-server"]
speedTestSimple = config["speed-test"]["simple-enabled"]
sessionId = ""

##Read commandline parameters if present (override config file)
#TODO - Add argument support to the /init.d/messagereceiver.sh start script
for arg in sys.argv: 
    if arg == 'simple':
        speedTestSimple = True
    if arg == 'mini':
        speedTestMiniEnabled = True


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
    rqid = 0
    tries = 0

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
       rabbitlog = kwargs.get('rabbitlog', None)

    if kwargs.has_key('rqid'):
       rqid = kwargs.get('rqid', None)

    if kwargs.has_key('tries'):
       tries = kwargs.get('tries', None)

    #Log to syslog?
    if syslog:
        syslogger(message, severity)

    #Log to rabbitMQ queue?
    if rabbitlog:
        logError = rabbitmqLog(message, queue=queue)

    #Send log to remote log server
    if remotelog:
        logError = remoteLogger(message, rqid=rqid, tries=tries)
    #logError = remoteLogger(message)

#Make sure that the speed test device can reach Internet
def waitForPing( ip, **kwargs):
    waiting =True
    counter =0
    rqId = 0

    if kwargs.has_key('rqid'):
       rqId = kwargs.get('rqid', None)

    logMsg = 'Testing Internet Connectivity.'
    processMessage(logMsg, rqid=rqId)
    while waiting:
	t = os.system('ping -c 1 -W 1 {}'.format(ip)+'> /dev/null 2>&1')
        if not t:
            waiting=False
	    logMsg = 'Ping reply from '+ip
            processMessage(logMsg, rqid=rqId)
            return True
        else:
            counter +=1
	    if (counter%30 == 0):
                logMsg = 'Trying to connect to Internet for '+str(counter)+' seconds'
 	        processMessage(logMsg, rqid=rqId)
            if counter == pingTimeOut: # this will prevent an never ending loop, set to the number of tries you think it will require
                waiting = False
		logMsg = 'Ping timeout after trying for '+str(counter)+' seconds!\nRestart the speed test by reconnecting the ethernet cable to the speed test device.'
                processMessage(logMsg, rqid=rqId)
                return False

def speedtest(request):
    #Add possibility to select which servers to execute speed test against
    #Add parameters to the python script to execute simple mode etc.
    #TODO function to sort serverlist provided by configuration service
    #TODO loop through server list if one fails
    
    cmd = ['/usr/bin/python', '-u', '/opt/speedtest/speedtest_cli.py']

    try:
        #TODO Validate result from getSpeedTestRequest
        srvList = request['request']['serverlist']
        rqId = request['request']['rqid']
        serviceOrderId = request['request']['serviceorderid']
        bwDown = request['request']['bandwidthdown']
        bwUp = request['request']['bandwidthup']
	rqStatus = request['request']['rqstatus']

        logMsg = 'Initiating Speed Test'
        processMessage(logMsg, rqid=rqId)


        logMsg = 'No Speed Test server related to the RSP of the service order. Selecting the closest one.'

        if len(srvList) > 0 and not speedTestMiniEnabled:
            #TODO sort list based on distance
            cmd = ['/usr/bin/python', '-u', '/opt/speedtest/speedtest_cli.py', '--server', srvList[0]]
            logMsg = 'Selecting Speed Test server ('+srvList[0]+') based on service order '+str(serviceOrderId)+' with bandwidth setting '+bwDown+'/'+bwUp+' Mb/s'
        elif speedTestMiniEnabled:
            cmd = ['/usr/bin/python', '-u', '/opt/speedtest/speedtest_cli.py', '--mini', speedTestMiniServer]
            logMsg = 'Selecting Speed Test Mini Server ('+speedTestMiniServer+') defined in config file.'

        if speedTestSimple:
            cmd.append('--simple')
 
        processMessage(logMsg, rqid=rqId)

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        for line in iter(p.stdout.readline,''):
            sys.stdout.flush()
	    processMessage(line, rqid=rqId)

        p.wait()
        return not p.returncode
    except Exception as e:
        processMessage("Unable to complete Speed Test through external python script: "+str(cmd),remotelog=False, rabbitlog=False)
        raise

#Implement function to validate that dns can be resolved

def remoteLogger(msg, **kwargs):
    uri = URI+postSvc
    rqid = 0
    sleep = 10
    noRetries = remoteLoggerTimeout/sleep
    tries = 0
    tryAgain = True

    if kwargs.has_key('rqid'):
        rqid = kwargs.get('rqid', None)

    if kwargs.has_key('tries'):
        tries = kwargs.get('tries', None)

    headers = {'Content-type': 'application/x-www-form-urlencoded ', 'Accept': 'text/plain'}
    json_data = json.dumps({'deviceId':deviceId, 'sessionId':str(sessionId), 'timeCreated':str(datetime.now()), 'msg':msg, 'rqid':rqid}) 
    payload = {'speedtest':json_data}
    #Try to send HTTP Request, retry 3 times
    while tryAgain:
        try:
            if tries >= noRetries:
                tryAgain = False
                raise
            else: 
                r = requests.post(uri, data=payload, headers=headers)
                tryAgain = False
        except requests.exceptions.Timeout:
            syslogger("Connection to server: "+uri+" timed out. Retried for  "+str(tries*sleep)+" seconds (timeout="+str(remoteLoggerTimeout)+"s)", 'critical')
        except requests.exceptions.TooManyRedirects:
            syslogger("Too many redirects when trying to connect to: "+uri+". Retried for "+str(tries*sleep)+" seconds (timeout="+str(remoteLoggerTimeout)+"s)", 'critical')
        except requests.exceptions.RequestException as e:
            syslogger("HTTP Request Exception. Trying to connect to "+uri+". Retried for "+str(tries*sleep)+" seconds (timeout="+str(remoteLoggerTimeout)+"s)", 'critical')
        
        if tryAgain: time.sleep(sleep)
        tries += 1

def getSpeedTestRequest(deviceMac, **kwargs):
    uri = configURI+getConfigSvc
    tries = 0
    tryAgain = True
    valueError = False
    sleep= 10
    noRetriesConfig = requestConfigTimeout/sleep

    if kwargs.has_key('deviceid'):
        deviceId = kwargs.get('deviceid', None)
    else:
   	deviceId = 0

    headers = {'Content-type': 'application/x-www-form-urlencoded ', 'Accept': 'text/plain'}
    json_data = json.dumps({'deviceId':deviceId, 'deviceMac':deviceMac})
    payload = {'getconfiguration':json_data}

    while tryAgain:
        try:
            if tries >= noRetriesConfig and not valueError:
                tryAgain = False
                raise
            elif tries >= noRetriesConfig+1 and valueError:
  	        raise ValueError("Unable to get device ("+deviceMac+") configuration.")
            else:
                r = requests.post(uri, data=payload, headers=headers)
                if r.status_code == 404:
                    logMsg = "Unable to get device ("+deviceMac+") configuration. Retried for "+str(tries*sleep)+" seconds (timeout="+str(requestConfigTimeout)+"s)"
                    processMessage(logMsg)
                    if tries >= noRetriesConfig-1: valueError = True 
                    tryAgain = True
                else:
                    response = json.loads(r.text)
                    request = json.loads(response['data'])
                    processMessage("Found request configuration for device ("+deviceMac+").")
                    tryAgain = False
                    return request
        except requests.exceptions.Timeout:
            syslogger("Connection to server: "+uri+" timed out.  "+str(tries*sleep)+" seconds.", 'critical')
        except requests.exceptions.TooManyRedirects:
            syslogger("Too many redirects when trying to connect to: "+uri+". Retried for  "+str(tries*sleep)+" seconds (timeout="+str(requestConfigTimeout)+"s)", 'critical')
        except requests.exceptions.RequestException as e:
            syslogger("HTTP Request Exception. Trying to connect to "+uri+". Retried for "+str(tries*sleep)+" seconds (timeout="+str(requestConfigTimeout)+"s)", 'critical')

        tries += 1
        if tryAgain: time.sleep(sleep)

def updateRequestStatus(rqId, rqStatus):
    uri = configURI+updateStatusSvc
    sleep = 10
    noRetries = updateRequestStatusTimeout/sleep
    tries = 0
    tryAgain = True
    headers = {'Content-type': 'application/x-www-form-urlencoded ', 'Accept': 'text/plain'}
    json_data = json.dumps({'rqId':rqId, 'rqStatus':rqStatus}) 
    payload = {'updaterequeststatus':json_data}
    while tryAgain:
        try:
	    if tries >= noRetries:
                tryAgain = False
                raise
            else:
                r = requests.post(uri, data=payload, headers=headers)
                if r.status_code == 404:
                    logMsg = 'Unable to update Speed Test Request Configuration Status (rqId:'+str(rqId)+' rqStatus:'+str(rqStatus)+')'
                else:
                    logMsg = 'Updated Speed Test Request Configuration Status (rqId:'+str(rqId)+' rqStatus:'+str(rqStatus)+')'
                processMessage(logMsg, rqid=rqId)
                tryAgain = False
        except requests.exceptions.Timeout:
            syslogger("Connection to server: "+uri+" timed out. Retried for  "+str(tries*sleep)+" seconds (timeout="+str(updateRequestStatusTimeout)+"s)", 'critical')
        except requests.exceptions.TooManyRedirects:
            syslogger("Too many redirects when trying to connect to: "+uri+". Retried for "+str(tries*sleep)+" seconds (timeout="+str(updateRequestStatusTimeout)+"s)", 'critical')
        except requests.exceptions.RequestException as e:
            syslogger("HTTP Request Exception. Trying to connect to "+uri+". Retried for  "+str(tries*sleep)+" seconds (timeout="+str(updateRequestStatusTimeout)+"s)", 'critical')

        #wait 10 seconds
        tries += 1
        if tryAgain: time.sleep(10)

def callback(ch, method, properties, body):
    global sessionId
    try:
        sessionId = uuid.uuid1()

        deviceMac = get_mac()
        deviceMac = ':'.join(("%012X" % deviceMac)[i:i+2] for i in range(0, 12, 2))

        logMsg = 'Fetching Speed Test request configuratin for device '+deviceMac
        processMessage(logMsg, remotelog=False)

        request = getSpeedTestRequest(deviceMac)
        
        if request == None:
            raise ValueError('Unable to get speed test request configuration!')
	else:
            rqId = request['request']['rqid']
	
        logMsg = 'Speed device has been plugged in. Initiating speed test process...'
        processMessage(logMsg, rqid=rqId)
        #Retry if unsuccessful
        if waitForPing("8.8.8.8", rqid=rqId) and speedtest(request):
            updateRequestStatus(rqId, 3)
	    logMsg = 'Speed Test Completed!'
            processMessage(logMsg, rqid=rqId)
        else:
            logMsg = 'Speed Test Unsuccessful!'
            processMessage(logMsg, severity='critical', rqid=rqId)
    except Exception as e:
        syslogger(str(e), 'critical')
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


