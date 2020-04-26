REM first try to uninstall, then reinstall all packages
echo y | pip uninstall flask
echo y | pip uninstall pandas
echo y | pip uninstall pyusb
echo y | pip uninstall usb
echo y | pip uninstall werkzeug==0.16.0
echo y | pip uninstall flask_session
echo y | pip uninstall Flask_wtf
echo y | pip uninstall jaydebeapi
echo y | pip uninstall Jpype1==0.6.3

pip install flask
pip install pyusb
pip install pandas
pip install usb
pip install werkzeug==0.16.0
pip install flask_session
pip install Flask_wtf
pip install jaydebeapi
pip install jaydebeapi
pip install Jpype1==0.6.3