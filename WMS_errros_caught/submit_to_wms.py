def submit_to_wms(MOVE_number):
    # this funcion will only be called with a nonzero cursor
    if MOVE_number != 0:
        # do stuff here

        pass
        # if cursor is None:
        # print('Database connection unsuccessful')
        # if other error, ideally clarify possible error scenarios
        # print('WMS submit error')
        # return False

    # if no reference number for the WMS is supplied, it was a manual order, and thus should not be submitted to the WMS
    return True