def retrieve_order(scanner_id):
    # this function will only be called with a nonzero cursor
    try:
        getdata = 0
    except:
        # if there is a retrieval error
        return 'Retrieval Error'

    # if no orders are available
    # return 'No orders'
    # this function should retrieve from the WMS the current order for the scanner provided. It will return the MOVE
    # reference number, the product weight, weight unit and the target count
    return [100, 8, 'g', 2]