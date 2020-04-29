def retrieve_specific_order_info(scanner_id, license_plate):
    try:
        getdata = 0
    except:
        # if there is a retrieval error
        return 'Retrieval Error'
    # return 'No connection' if no connetion could be established

    # if no orders are available
    # return 'No orders'
    # this function should retrieve from the WMS the current order for the scanner provided. It will return the MOVE
    # reference number, the product weight, weight unit and the target count
    return [100, 8, 'g', 2]


# this function should return all order IDs assigned to the same location as the employee scanned
def retrieve_all_license_plates(scanner_id):
    try:
        getdata = 0
    except:
        return "General Error"
    # if any error occurs here, please print relevant error messages and return "General Error"
    return [11110, 1112, 1113, 1114, 11132]
