
#!/usr/bin/env python
import pika
import subprocess

cmd = ['/usr/bin/python', '-u', '/home/netadmin/speedtest/speedtest_cli.py']

#connection = pika.BlockingConnection(pika.ConnectionParameters(
#               'localhost'))
#channel = connection.channel()
#
#channel.queue_declare(queue='hello')

#def callback(ch, method, properties, body):
#    print " [x] Received %r" % (body,)
#p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
p = subprocess.Popen(cmd, shell=True)
for line in p.stdout:
    print line
p.wait()
print p.returncode
#    print subprocess.check_output(speedtest, shell=True)

#channel.basic_consume(callback,
#                      queue='hello',
#                      no_ack=True)

#print ' [*] Waiting for messages. To exit press CTRL+C'
#channel.start_consuming()

