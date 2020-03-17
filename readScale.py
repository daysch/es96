def readScale(mode_weight_requested):
    ounces_per_gram = 0.035274
    ounces_per_pound = 16

    import usb.core
    import usb.util

    VENDOR_ID = 0x0922
    PRODUCT_ID = 0x8003

    # find the USB device
    device = usb.core.find(idVendor=VENDOR_ID,
                           idProduct=PRODUCT_ID)

    # include this when you get an error like 'resource busy'
    """
        for cfg in device:
      for intf in cfg:
        if device.is_kernel_driver_active(intf.bInterfaceNumber):
          try:
            device.detach_kernel_driver(intf.bInterfaceNumber)
          except usb.core.USBError as e:
            sys.exit("Could not detatch kernel driver from interface({0}): {1}".format(intf.bInterfaceNumber, str(e)))
    """


    # use the first/default configuration
    device.set_configuration()

    # first endpoint
    endpoint = device[0][(0,0)][0]

    # read a data packet
    attempts = 10
    data = None
    while data is None and attempts > 0:
        try:
            data = device.read(endpoint.bEndpointAddress,
                               endpoint.wMaxPacketSize)
        except usb.core.USBError as e:
            data = None
            if e.args == ('Operation timed out',):
                attempts -= 1
                continue

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

    print(reading)
    return reading