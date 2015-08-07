#!/usr/bin/env python
<<<<<<< HEAD
<<<<<<< HEAD
import pika
import sys
=======
=======
>>>>>>> origin/raspberrypi

import pika
import sys
import datetime
from datetime import datetime
import logging
import logging.handlers
<<<<<<< HEAD
=======
import yaml

with open('/opt/speedtest/config.yaml', 'r') as f:
    config = yaml.load(f)

username = config["message_server"]["username"]
password = config["message_server"]["password"]
>>>>>>> origin/raspberrypi

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
<<<<<<< HEAD
>>>>>>> origin/release1.0
=======
>>>>>>> origin/raspberrypi


try:
    while 1:
	message = ""
        message = sys.stdin.readline().rstrip()

	if len(message) > 1:
<<<<<<< HEAD
<<<<<<< HEAD
	    connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
	    channel = connection.channel()

	    channel.queue_declare(queue='dhcpack')

	    channel.basic_publish(exchange='',
                      routing_key='dhcpack',
=======
            credentials = pika.PlainCredentials('speedtest', '1nfield')
=======
            credentials = pika.PlainCredentials(username, password)
>>>>>>> origin/raspberrypi
	    connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost', 5672, '/', credentials))
	    channel = connection.channel()

	    channel.queue_declare(queue='linkup')

	    channel.basic_publish(exchange='',
                      routing_key='linkup',
<<<<<<< HEAD
>>>>>>> origin/release1.0
=======
>>>>>>> origin/raspberrypi
                      body=message)

	    connection.close()
except Exception, e:
<<<<<<< HEAD
<<<<<<< HEAD
    f = open('/tmp/error.txt','ab')
    f.write(e)
    f.close()
=======
    syslogger('Speed test syslog receiver was terminated due to an unhandled exception:'+str(e),'err')
>>>>>>> origin/release1.0
=======
    syslogger('Speed test syslog receiver was terminated due to an unhandled exception:'+str(e),'err')
>>>>>>> origin/raspberrypi
    exit(0)
