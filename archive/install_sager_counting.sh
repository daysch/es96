#!/bin/bash
cd
# change the filepath appropriately
echo y | sudo apt install python-pip
echo y |sudo -H pip uninstall flask
echo y |sudo -H pip uninstall pyusb
echo y |sudo -H pip uninstall werkzeug==0.16.0
echo y |sudo -H pip uninstall flask_session
echo y |sudo -H pip uninstall Flask_wtf
sudo -H pip install flask
sudo -H pip install pyusb
sudo -H pip install werkzeug==0.16.0
sudo -H pip install flask_session
sudo -H pip install Flask_wtf
pause
