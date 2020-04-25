from SetupConn import *


# this function should return all orders assigned to the same location, as well as the license
# plates contained, and the quantity requested. it should only return those that have product weights associated
def retrieve_all_tasks(scanner_id, cursor):
    # this function should query for all orders assigned to DC001, and shelves
    # it returns the license plates and allocated quantities per task id
    # it only returns those that have product weights associated in DC On Hand Items

    use_actual_database = False

    if use_actual_database:
        # check if the connection has been made previously
        if not jpype.isJVMStarted():
            curs = setup_conn()

        if not curs:
            return 'No connection'

        try:
            # select all tasks from DC001 in shelves and order by task_id
            curs.execute(
                "SELECT A.task_id, A.license_plate_no, A.allocated_qty, A.product_id, A.source_location_no FROM task_master A where A.dc_code = 'DC001' AND A.task_type = 'PICKING' AND A.task_status = 'AVL' ORDER BY A.task_id")
            output = curs.fetchall()
            filter_shelves = list(filter(lambda x: x[4][0] == 'S', output))

            # Check if any orders
            if not filter_shelves:
                print('no orders in DC001 shelves')
                return 'No orders'

            # Filter for orders that have weight data in DC001 On Hand Items
            fields = ["Weight", "Weight UOM", "MOVE Part Number"]
            data = pandas.read_csv('DC001 On Hand Items.csv', usecols=fields)
            valid_orders = []

            for i in range(len(filter_shelves)):
                record = data.loc[data["MOVE Part Number"] == filter_shelves[i][2]]
                if not pandas.Index.tolist(record["Weight"]) and pandas.Index.tolist(record["Weight UOM"]):
                    continue
                else:
                    valid_orders.append(filter_shelves[i])

            # Check if no orders with weights in On Hand Items
            if not valid_orders:
                print('no orders with weight data')
                return 'No orders'

            # Output orders in correct format
            all_tasks = []
            for i in range(len(filter_shelves)):
                entry = dict({'task_id': filter_shelves[i][0], 'license_plates_contained': [filter_shelves[i][1]],
                              'quantity_requested': [filter_shelves[i][2]], 'product_ids': [filter_shelves[i][3]]})
                all_tasks.append(entry)
            print(all_tasks)

            return all_tasks

        except:
            print('likely to be cursor error')  # need to print relevant error messages
            return 'General Error'
    else:
        # if an unspecified error occurs here, please print the error thrown and return "General Error"
        # if no orders in general, or no orders with weight data could be found, return "No orders"
        # if the connection didnt work, return 'No connection'
        # if there was some other error retrieving data return 'Retrieval error'
        return [{'task_id': 1111033, 'license_plates_contained': ['r1111233'], 'quantity_requested': [10],
                 'product_weight': [8], 'uom': ['g']},
                {'task_id': 1115610, 'license_plates_contained': ['l1432534'], 'quantity_requested': [10],
                 'product_weight': [5], 'uom': ['g']},
                {'task_id': 1341078, 'license_plates_contained': ['l1432534'],
                 'quantity_requested': [60], 'product_weight': [5], 'uom': ['g']}]
