@echo off
REM Replace the path with whatever the path to you executable is
set url="http://127.0.0.1:5000"
start chrome "%url%"

REM Replace the path with whatever the path to you executable is
python "C:\Users\Matthias Fischer\Documents\GitHub\es96-master\es96-master\application.py %*"

pause
