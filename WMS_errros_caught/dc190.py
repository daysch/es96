import serial
import time
import os

def readScale():
  # for dc190
  # I think SPEC 10 needs to be updated to first bit = 1
  # I think SPEC 12 should be set to 11 or 01, and somehow set scale
  # 'when counting' condition to true.
  # please include link to documentation

  scale_serial_port = "COM1" # dependent on serial port number
  path = os.path.dirname(os.path.abspath(__file__)) # relative directory path

  # Create an instance of serial object, set serial parameters for scale
  ser=serial.Serial()
  ser.port=scale_serial_port
  ser.bytesize=serial.EIGHTBITS
  ser.baudrate=9600
  ser.parity=serial.PARITY_NONE
  ser.stopbits=1
  ser.timeout=5
  ser.xonxoff=0

  # get scale transmission
  ser.open()
  transmission = rec_response(ser)
  ser.close()
  if transmission == "":
    return None

  # parse response
  transmission = transmission.split('\r')
  for data in transmission:
    if data[0] = '0':
      return float(data[1:-1]);
  return None


# receives response from serial port until reaches carriage \r\n or no more input
def rec_response(ser):
  response = ser.read(1)
  if len(response) == 0:
    return response
  while response[-1] != '\r\n':
    old = response
    response = response + ser.read(1)
    if response == old:
      break
  return response
