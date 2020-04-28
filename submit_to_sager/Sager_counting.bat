@echo off
REM set url at typical localhost and start chrome

REM start batch script to open up chrome after a delay
START CALL "{path_to_submit_to_sager}\start_chrome_after_delay.bat"

REM Replace the path with whatever the path to you executable is
python "{path_to_submit_to_sager}\application\application.py %*"

pause