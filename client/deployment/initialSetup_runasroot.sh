#!/bin/bash

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

#make sure dependencies are present
apt install chromium default-jre
apt install xvfb

#setup crontab to include virtual display. Must be used instead of headless chrome, as otherwise no webrtc-internals are generated
crontab -l > /mycron
echo "@reboot Xvfb :99 -screen 0 1920x1080x16 &" >> /mycron
crontab /mycron
rm /mycron

#make sure the correct display variable is set upon login. Must be used instead of headless chrome, as otherwise no webrtc-internals are generated
echo "export DISPLAY=:99" >> /etc/environment

#create folder structure
mkdir /home/webrtc/apprtc-logs
mkdir /home/webrtc/apprtc-media
wget https://media.xiph.org/video/derf/y4m/Johnny_1280x720_60.y4m -P /home/webrtc/apprtc-media/
chown -R webrtc:users /home/webrtc/*

