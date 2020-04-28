@echo off
REM please enter the loaction of the folder containing the batch script and the folder application on your computer
set location_submit_to_sager_folder=C:\Users\Matthias Fischer\PycharmProjects\es96\submit_to_sager

REM start batch script to open up chrome after a delay
START CALL "%location_submit_to_sager_folder%\start_chrome_after_delay.bat"

REM Replace the path with whatever the path to you executable is
python "%location_submit_to_sager_folder%\application\application.py %*"

pause