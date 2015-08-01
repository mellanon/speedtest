#!/usr/bin/env python
import pika
import subprocess
import sys 

def speedtest():
    cmd = ['/usr/bin/python', '-u', '/opt/speedtest/speedtest_cli.py']
    print " [x] Executing speed test..."
   
    channel.queue_declare(queue='speedTestSendQueue', durable=True)

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline,''):
        sys.stdout.flush()
        channel.basic_publish(exchange='',
                      routing_key="speedTestSendQueue",
                      body=line,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
    p.wait()
    return not p.returncode

def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)
    #Retry if unsuccessful
    if speedtest():
        print "[x] Successful"
	ch.basic_ack(delivery_tag = method.delivery_tag)
    else:
	print "[x] Unsuccessful"

connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
channel = connection.channel()

channel.queue_declare(queue='dhcpack')
    
channel.basic_consume(callback,
                      queue='dhcpack',
                      no_ack=False)

print ' [*] Waiting for messages. To exit press CTRL+C'
channel.start_consuming()

