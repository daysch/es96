import time

# this part will try to import the necessary packages, depending on which ones were successfully installed
try:
    import usb.core as core
    import usb.util as util
except:
    import pyusb.core as core
    import pyusb.util as util


# use the function at the bottom of this script, accurate_reading(mode_weight_requested), which returns a stable value
# mode_weight_requested can take the values 'g' for grams or 'oz' for ounces, 'kg' for kilograms and 'lbs' for pounds
def readScale(mode_weight_requested):
    # these are conversion factors
    ounces_per_gram = 0.035274
    ounces_per_pound = 16

    # These values are specific to the Dymo scale. They can be found using the device filter, e.g. libusb_win32 in
    # windows
    VENDOR_ID = 0x0922
    PRODUCT_ID = 0x8003

    # find the USB device
    device = core.find(idVendor=VENDOR_ID,
                       idProduct=PRODUCT_ID)

    # use the default configuration
    device.set_configuration()

    # first endpoint, this is again specific to the Dymo scale
    endpoint = device[0][(0, 0)][0]

    # read a data packet, it will try so 10 times before throwing the error to the function calling, in this case
    # accurate_reading()
    attempts = 10
    data = None
    while data is None:
        try:
            data = device.read(endpoint.bEndpointAddress,
                               endpoint.wMaxPacketSize)

        except core.USBError as e:
            data = None
            if e.args == ('Operation timed out',):
                continue
            attempts -= 1
            if attempts < 0:
                print(e.args)
                print('Error in readscale')
                util.dispose_resources(device)
                return 'Error'

    # this releases the usb scale
    util.dispose_resources(device)

    # determine the weight units used by the scale, these can only be ounces or grams
    mode_weight = 'g'
    if data[2] == 11:
        mode_weight = 'oz'

    # determine the scaling factor, only relevant if the scale is set to ounces, 256 is scaling factor of 1,
    # 255 is 10^-1 etc
    scaling_factor = data[3]
    scaling_factor = scaling_factor - 256
    scaling_factor = 10 ** scaling_factor

    # determine the current reading and convert, using formulas from
    # http://steventsnyder.com/reading-a-dymo-usb-scale-using-python/
    if mode_weight == 'g':
        reading = (data[4] + (256 * data[5]))

        # convert if necessary to requested format
        if mode_weight_requested == 'oz':
            reading = reading * ounces_per_gram

        if mode_weight_requested == 'kg':
            reading = reading / 1000

        if mode_weight_requested == 'lbs':
            reading = reading * ounces_per_gram / ounces_per_pound

    # this means the scale is set to ounces
    else:
        reading = scaling_factor * (data[4] + (256 * data[5]))

        # convert if necessary
        if mode_weight_requested == 'g':
            reading = reading / ounces_per_gram

        if mode_weight_requested == 'kg':
            reading = reading / ounces_per_gram / 1000

        if mode_weight_requested == 'lbs':
            reading = reading / ounces_per_pound

    return reading


# this function makes sure that the scale has reached its full reading
# making the sleep time too short will make this crash
def accurate_reading(mode_requested):
    previous_reading = 0
    current_reading = -1

    # as long as the reading changes within an interval of reading_time, this function will continue to requery the
    # weight on the scale, otherwise it will return the current reading to check_weight() in application.py
    reading_time = 1
    while current_reading != previous_reading:
        previous_reading = current_reading
        current_reading = readScale(mode_requested)
        time.sleep(reading_time)
        if current_reading == 'Error':
            return 'Error'
    return previous_reading
