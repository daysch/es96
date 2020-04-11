#!/bin/bash
cd
# change the filepath appropriately
cd es96-master/
sudo python readScale.py
firefox -new-tab "127.0.0.1:5000"
sudo python application.py

