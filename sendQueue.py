#!/usr/bin/env python

import pika
import yaml

with open('/opt/speedtest/config.yaml', 'r') as f:
    config = yaml.load(f)

username = config["message_server"]["username"]
password = config["message_server"]["password"]

credentials = pika.PlainCredentials(username, password)
connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost', 5672, '/', credentials))
channel = connection.channel()
channel.queue_declare(queue='sendQueue')

print ' [*] Waiting for messages. To exit press CTRL+C'

def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)

channel.basic_consume(callback,
                      queue='sendQueue',
                      no_ack=True)

channel.start_consuming()

