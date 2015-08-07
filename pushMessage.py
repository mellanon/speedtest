#!/usr/bin/env python
<<<<<<< HEAD
import pika
import sys
=======

import pika
import sys
import datetime
from datetime import datetime
import logging
import logging.handlers

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
>>>>>>> origin/release1.0


try:
    while 1:
	message = ""
        message = sys.stdin.readline().rstrip()

	if len(message) > 1:
<<<<<<< HEAD
	    connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
	    channel = connection.channel()

	    channel.queue_declare(queue='dhcpack')

	    channel.basic_publish(exchange='',
                      routing_key='dhcpack',
=======
            credentials = pika.PlainCredentials('speedtest', '1nfield')
	    connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost', 5672, '/', credentials))
	    channel = connection.channel()

	    channel.queue_declare(queue='linkup')

	    channel.basic_publish(exchange='',
                      routing_key='linkup',
>>>>>>> origin/release1.0
                      body=message)

	    connection.close()
except Exception, e:
<<<<<<< HEAD
    f = open('/tmp/error.txt','ab')
    f.write(e)
    f.close()
=======
    syslogger('Speed test syslog receiver was terminated due to an unhandled exception:'+str(e),'err')
>>>>>>> origin/release1.0
    exit(0)
