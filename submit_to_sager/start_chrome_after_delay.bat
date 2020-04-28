@echo off
REM set url at typical localhost and start chrome

REM start chrome after a delay

echo please wait while we start up the server

set url="http://127.0.0.1:5000"
timeout 6 > NUL
start chrome "%url%"
exit