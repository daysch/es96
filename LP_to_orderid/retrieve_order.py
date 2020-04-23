def retrieve_specific_order_info(scanner_id, order_id):
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


# this function should return given a scanner_id all orders assigned to the same location, as well as the license
# plates contained, and the quantity requested
def retrieve_all_license_plates(scanner_id):
    try:
        getdata = 0
    except:
        return "General Error"
    # if any error occurs here, please print relevant error messages and return "General Error"

    return [{'order_id': 1111033, 'license_plates_contained':['e11122', 'r1111233'], 'quantity_requested':[10, 20]},
            {'order_id': 1115610, 'license_plates_contained':['l1432534'], 'quantity_requested':[10]},
            {'order_id': 1341078, 'license_plates_contained':['k1112', 'o1113324', '4443', 'l1432534'], 'quantity_requested':[10, 20, 30, 60]}]
