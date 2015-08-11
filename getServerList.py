#!/usr/bin/env python

from __future__ import print_function
from datetime import date, datetime, timedelta
import mysql.connector
import re
import subprocess
import os
import sys
import json

#cnx = mysql.connector.connect(user='root', password='bitnami',
#                              host='127.0.0.1',
#                              database='speedtest')
#cursor = cnx.cursor()

#add_server = ("INSERT INTO serverlist "
#               "(srvid, srvname, srvcountry, srvcity, srvdistance) "
#               "VALUES (%s, %s, %s, %s, %s)")

cmd = ['/usr/bin/python', '-u', '/opt/speedtest/speedtest_cli.py', '--list']

p = subprocess.Popen(cmd, stdout=subprocess.PIPE, preexec_fn=os.setsid)

#(\d+)\).(.*).\((.*)\,.(\w+)\).\[(.*).km\]

f = open('myfile','w')

for line in iter(p.stdout.readline,''):
    sys.stdout.flush()
    reg = re.compile('(\d+)\).(.*).\((.*)\,.(\w+)\).\[(.*).km\].*')
    match = reg.match(line)
    if match:
        print(match.groups())
        f.write(json.dumps(str(match.groups()))+'\n') # python will convert \n to os.linesep
        
    #data_server = match.group(0)#str(match.groups())
    #print(data_server)
    #print(line)
    #srv = match.group(1)
    #srvname = match.group(2)
    #srvcountry = match.group(3)
    #srvcity = match.group(4)
    #srvdistance = match.group(5)
p.wait()

f.close
#data_server = ('Geert', 'Vanderkelen', tomorrow, 'M', date(1977, 6, 14))

# Insert new employee
#cursor.execute(add_employee, data_employee)
#emp_no = cursor.lastrowid

# Insert salary information
#data_salary = {
#  'emp_no': emp_no,
#  'salary': 50000,
#  'from_date': tomorrow,
#  'to_date': date(9999, 1, 1),
#}
#cursor.execute(add_salary, data_salary)

# Make sure data is committed to the database
#cnx.commit()

#cursor.close()
#cnx.close()

