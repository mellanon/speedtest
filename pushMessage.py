#!/usr/bin/env python

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


try:
    while 1:
	message = ""
        message = sys.stdin.readline().rstrip()

	if len(message) > 1:
            credentials = pika.PlainCredentials('speedtest', '1nfield')
	    connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost', 5672, '/', credentials))
	    channel = connection.channel()

	    channel.queue_declare(queue='linkup')

	    channel.basic_publish(exchange='',
                      routing_key='linkup',
                      body=message)

	    connection.close()
except Exception, e:
    syslogger('Speed test syslog receiver was terminated due to an unhandled exception:'+str(e),'err')
    exit(0)
