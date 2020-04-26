@echo off
REM set url at typical localhost and start chrome
set url="http://127.0.0.1:5000"
start chrome "%url%"

REM Replace the path with whatever the path to you executable is
python "C:/Users/Matthias Fischer/PycharmProjects/es96/LP_to_orderid/application.py %*"

pause