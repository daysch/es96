# Introduction
The goal of this project will be to scan a barcode with an RF scanner, reference that against a database of parts, read in the weight from a scale, and use the weight in the database to determine the number of parts on the scale.

We will be using Python 3. 
Each function shall be in its own file with the same name as the function (e.g., readScale will be defined in a file called readScale.py), except main, which shall be contained in scales.py.

Useful links:
https://learn.adafruit.com/barcode-scanner/usb-interfacing
http://steventsnyder.com/reading-a-dymo-usb-scale-using-python/


# readScale.py

The function readScale shall not take in any parameters. It shall return a float containing the current reading from the scale attached to the USB port.


# readScanner.py

The function readScanner shall not take in any parameters. It shall return an int, the barcode currently being read by the RF scanner, or alternatively, the most recently read bar code. If that is too difficult, the read scanner can instead prompt the user to use the RF scanner in keyboard mode and return that entered number.


# Database warehouse

The SQL database warehouse shall contain one table, called products. This table shall have the fields barcode (int) (primary key), weight (float), and name (VARCHAR(MAX)). Barcode shall not be set to autoincrement.


# barcode2Weight.py

The function barcode2Weight shall take in one int, the barcode. It shall query the database warehouse for the weight associated with the barcode and return this float.


# scales.py

The function main shall use the other functions to print out the number of parts on the scale every time the number changes. It shall use a loop to do this and shall recheck the number at intervals of INTERVAL milliseconds, where INTERVAL is an integer defined above the main loop.
