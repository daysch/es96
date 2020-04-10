echo y | pip uninstall flask 
echo y | pip uninstall pyusb 
echo y | pip uninstall usb 
echo y | pip uninstall werkzeug==0.16.0 
echo y | pip uninstall flask_session 
echo y | pip uninstall Flask_wtf 

pip install flask
pip install pyusb
pip install usb
pip install werkzeug==0.16.0
pip install flask_session
pip install Flask_wtf

pause