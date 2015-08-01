#!/usr/bin/env python

import pika
import sys


try:
    while 1:
	message = ""
        message = sys.stdin.readline().rstrip()

	if len(message) > 1:
	    connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
	    channel = connection.channel()

	    channel.queue_declare(queue='dhcpack')

	    channel.basic_publish(exchange='',
                      routing_key='dhcpack',
                      body=message)

	    connection.close()
except Exception, e:
    f = open('/tmp/error.txt','ab')
    f.write(e)
    f.close()
    exit(0)
