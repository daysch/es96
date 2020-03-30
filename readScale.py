import time

try:
    import usb.core as core
    import usb.util as util
except:
    import pyusb.core as core
    import pyusb.util as util

# use the function at the bottom of this script, accurate_reading(mode_weight_requested), which returns a stable value

# mode_weight_requested can take the values 'g' for grams or 'oz' for ounces, 'kg' for kilograms and 'lbs' for pounds
def readScale(mode_weight_requested):
    ounces_per_gram = 0.035274
    ounces_per_pound = 16

    VENDOR_ID = 0x0922
    PRODUCT_ID = 0x8003

    # find the USB device
    device = core.find(idVendor=VENDOR_ID,
                           idProduct=PRODUCT_ID)

# include this when you get an error like 'resource busy'
    """
    for cfg in device:
        for intf in cfg:
            if device.is_kernel_driver_active(intf.bInterfaceNumber):
                try:
                    device.detach_kernel_driver(intf.bInterfaceNumber)
                except core.USBError as e:
                    sys.exit("Could not detatch kernel driver from interface({0}): {1}".format(intf.bInterfaceNumber, str(e)))
                    """


    # use the first/default configuration
    device.set_configuration()

    # first endpoint
    endpoint = device[0][(0,0)][0]

    # read a data packet
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

    util.dispose_resources(device)

    # determine the weight units used by the scale
    mode_weight = 'g'
    if data[2] == 11:
        mode_weight = 'oz'

    # determine the scaling factor
    scaling_factor = data[3]
    if scaling_factor > 128:
        scaling_factor = scaling_factor - 256
    scaling_factor = 10 ** (scaling_factor)

    # determine the current reading and convert
    reading = 0
    if mode_weight == 'g':
        reading = data[4] + (256 * data[5])

        # convert if necessary
        if mode_weight_requested == 'oz':
            reading = reading * ounces_per_gram

        if mode_weight_requested == 'kg':
            reading = reading / 1000

        if mode_weight_requested == 'lbs':
            reading = reading * ounces_per_gram / ounces_per_pound

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
    while current_reading != previous_reading:
        previous_reading = current_reading
        current_reading = readScale(mode_requested)
        time.sleep(1)
        if current_reading == 'Error':
            return 'Error'
    return previous_reading

