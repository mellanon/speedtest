#!/usr/bin/env python

from __future__ import print_function
from datetime import date, datetime, timedelta
import mysql.connector
import re
import subprocess
import os
import sys
import MySQLdb

cnx = mysql.connector.connect(user='root', password='bitnami',
                              host='127.0.0.1',
                              database='speedtest')
cursor = cnx.cursor()

add_server = ("INSERT INTO serverlist "
               "(srvid, srvname, srvcity, srvcountry, srvdistance) "
               "VALUES (%s, %s, %s, %s, %s)")

cmd = ['/usr/bin/python', '-u', '/opt/speedtest/speedtest_cli.py', '--list']

p = subprocess.Popen(cmd, stdout=subprocess.PIPE, preexec_fn=os.setsid)

for line in iter(p.stdout.readline,''):
    sys.stdout.flush()
    reg = re.compile('\s*(\d+)\).(.*).\((.*)\,.(.*)\).\[(.*).km\].*')
    match = reg.match(line)
    if match:
        #print(match.groups())
        data_server = match.groups()
        #srv = match.group(1)
        #srvname = match.group(2)
        #srvcountry = match.group(3)
        #srvcity = match.group(4)
        #srvdistance = match.group(5)
        cursor.execute(add_server, data_server) #Insert server
    else:
        print("'"+line+"'")
p.wait()

# Make sure data is committed to the database
cnx.commit()

cursor.close()
cnx.close()
