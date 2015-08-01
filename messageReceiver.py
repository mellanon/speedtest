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

syslog = logging.getLogger('Syslog')
syslog.setLevel(logging.DEBUG)

handler = logging.handlers.SysLogHandler(address = '/dev/log')

syslog.addHandler(handler)

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
    while waiting:
        counter =0
	t = os.system('ping -c 1 {}'.format(ip)+'> /dev/null 2>&1')
        if not t:
            waiting=False
	    syslogger('Ping reply from '+ip, 'info')
            return True
        else:
            counter +=1
            if counter == 10000: # this will prevent an never ending loop, set to the number of tries you think it will require
                waiting = False
		syslog.info(str(datetime.now())+': Ping timeout '+ip)
                return False
        time.sleep(1)

def speedtest():
    cmd = ['/usr/bin/python', '-u', '/opt/speedtest/speedtest_cli.py']
    syslog.info(str(datetime.now())+': Initiating speed test')
    channel.queue_declare(queue='sendQueue')

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline,''):
        sys.stdout.flush()
        channel.basic_publish(exchange='',
                      routing_key="sendQueue",
                      body=line)
    p.wait()
    return not p.returncode

def callback(ch, method, properties, body):
    syslog.info(str(datetime.now())+': Speed device has been connected via ethernet. Initiating speed test process...')
    print " [x] Received %r" % (body,)
    #Retry if unsuccessful
    if waitForPing("8.8.8.8") and speedtest():
	syslog.info(str(datetime.now())+': Speed test successful')
    else:
	syslogger('Speed test unsuccessful!', 'err')

connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
channel = connection.channel()

channel.queue_declare(queue='dhcpack')
    
channel.basic_consume(callback,
                      queue='dhcpack',
                      no_ack=True)

syslogger('Started speed test message receiver', 'info')
print ' [*] Waiting for messages. To exit press CTRL+C'
channel.start_consuming()

