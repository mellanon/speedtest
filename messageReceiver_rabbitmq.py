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

with open('config.yaml', 'r') as f:
    config = yaml.load(f)

deviceId = config["speedtest"]["deviceId"]
print deviceId


syslog = logging.getLogger('Syslog')
syslog.setLevel(logging.DEBUG)

handler = logging.handlers.SysLogHandler(address = '/dev/log')

syslog.addHandler(handler)

connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
channel = connection.channel()
channel.queue_declare(queue='sendQueue')

def syslogger(message, severity):
    logtime = str(datetime.now())
    if severity == "info":
        syslog.info(logtime +': ' + message)
    elif severity == "err":
        syslog.err(logtime + ': ' + message)
    elif severity == "debug":
	syslog.debug(logtime + ': ' + message)    
    
def waitForPing( ip ):
    waiting =True
    counter =0
    logMsg = 'Testing Internet Connectivity.'
    syslogger(logMsg, 'info')
    channel.basic_publish(exchange='',routing_key="sendQueue",body=logMsg)
    while waiting:
	t = os.system('ping -c 1 -W 1 {}'.format(ip)+'> /dev/null 2>&1')
        if not t:
            waiting=False
	    logMsg = 'Ping reply from '+ip
            channel.basic_publish(exchange='',routing_key="sendQueue",body=logMsg)
	    syslogger(logMsg, 'info')
            return True
        else:
            counter +=1
	    if (counter%30 == 0):
                logMsg = 'Trying to connect to Internet for '+str(counter)+' seconds'
	        syslogger(logMsg, 'info')
	        channel.basic_publish(exchange='',routing_key="sendQueue",body=logMsg)
            if counter == 300: # this will prevent an never ending loop, set to the number of tries you think it will require
                waiting = False
		logMsg = 'Ping timeout after trying for '+str(counter)+' seconds!\nRestart the speed test by reconnecting the ethernet cable to the speed test device.'
		syslogger(logMsg, 'info')
		channel.basic_publish(exchange='',routing_key="sendQueue",body=logMsg)
                return False

def speedtest():
    cmd = ['/usr/bin/python', '-u', '/opt/speedtest/speedtest_cli.py']
    
    logMsg = 'Initiating Speed Test'
    syslogger(logMsg, 'info')

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline,''):
        sys.stdout.flush()
        channel.basic_publish(exchange='',
                      routing_key="sendQueue",
                      body=line)
    p.wait()
    return not p.returncode

def callback(ch, method, properties, body):
    logMsg = 'Speed device has been plugged in. Initiating speed test process...'
    syslogger(logMsg, 'info')
    channel.basic_publish(exchange='',routing_key="sendQueue",body=logMsg)
    print " [x] Received %r" % (body,)
    #Retry if unsuccessful
    if waitForPing("8.8.8.8") and speedtest():
	logMsg = 'Speed Test Completed!'
	channel.basic_publish(exchange='',routing_key="sendQueue",body=logMsg)
	syslogger(logMsg, 'info')
    else:
        logMsg = 'Speed Test Unsuccessful!'
        channel.basic_publish(exchange='',routing_key="sendQueue",body=logMsg)
	syslogger(logMsg, 'err')


channel.queue_declare(queue='dhcpack')
    
channel.basic_consume(callback,
                      queue='dhcpack',
                      no_ack=True)

syslogger('Started speed test message receiver', 'info')
print ' [*] Waiting for messages. To exit press CTRL+C'
channel.start_consuming()

