# speedtest

Enable SSH
$ sudo mv /etc/init/ssh.conf.back /etc/init/ssh.conf
$ sudo start ssh


Extra sources

#------------------------------------------------------------------------------#
#                            OFFICIAL UBUNTU REPOS                             #
#------------------------------------------------------------------------------#


###### Ubuntu Main Repos
deb http://nz.archive.ubuntu.com/ubuntu/ trusty main restricted universe multiverse 
deb-src http://nz.archive.ubuntu.com/ubuntu/ trusty main restricted universe multiverse 

###### Ubuntu Update Repos
deb http://nz.archive.ubuntu.com/ubuntu/ trusty-security main restricted universe multiverse 
deb http://nz.archive.ubuntu.com/ubuntu/ trusty-updates main restricted universe multiverse 
deb http://nz.archive.ubuntu.com/ubuntu/ trusty-proposed main restricted universe multiverse 
deb http://nz.archive.ubuntu.com/ubuntu/ trusty-backports main restricted universe multiverse 
deb-src http://nz.archive.ubuntu.com/ubuntu/ trusty-security main restricted universe multiverse 
deb-src http://nz.archive.ubuntu.com/ubuntu/ trusty-updates main restricted universe multiverse 
deb-src http://nz.archive.ubuntu.com/ubuntu/ trusty-proposed main restricted universe multiverse 
deb-src http://nz.archive.ubuntu.com/ubuntu/ trusty-backports main restricted universe multiverse 

###### Ubuntu Partner Repo
deb http://archive.canonical.com/ubuntu trusty partner
deb-src http://archive.canonical.com/ubuntu trusty partner

###### Ubuntu Extras Repo
deb http://extras.ubuntu.com/ubuntu trusty main
deb-src http://extras.ubuntu.com/ubuntu trusty main

##### RabbitMQ Repo
deb http://www.rabbitmq.com/debian/ stable main

Install syslog / syslog ng
apt-get install syslog-ng syslog-ng-core

Install erlang
sudo apt-get install libncurses5-dev

wget http://www.erlang.org/download/otp_src_18.0.tar.gz
tar -xzvf otp_src_18.0.tar.gz
cd otp_src_18.0
./configure
sudo make && sudo make install

Install rabbitmq
sudo echo "deb http://www.rabbitmq.com/debian/ stable main" >> /etc/apt/sources.list
cd
wget https://www.rabbitmq.com/rabbitmq-signing-key-public.asc
sudo apt-key add rabbitmq-signing-key-public.asc
apt-get update
sudo apt-get install rabbitmq-server

Create speedtest directory
sudo mkdir /opt/speedtest
cp pushMessage.py
cp receiveSpeedTest.py
cp speedtest_cli.py

Get pika for rabbitmq
sudo apt-get install python-pip git-core
sudo pip install pika==0.9.8

Configure syslog-ng
filter dhcp_ack { match("DHCPACK" value("MESSAGE")); };
destination rabbitmq { program("/usr/bin/python -u /opt/speedtest/pushMessage.py" template("${DATE} ${MSG}\n") flush_lines(1) flags(no_multi_line) flush_timeout(1000)); };
log { source(s_src); filter(dhcp_ack); destination(rabbitmq); };

init scripts for the python scripts

timezone + ntp time synch
sudo dpkg-reconfigure tzdata
sudo apt-get install ntp
https://help.ubuntu.com/lts/serverguide/NTP.html

syslog in pushMessage.py

configuration file with device ID

JSON messages to msg queue

Commit to github

Error message on ping timeout: "Restart test by reconnecting the ethernet cable to the speed test device."

Python yaml
sudo pip instal pyyaml

enable port 15674 
sudo ufw allow

Enable federated exchange on both servers
