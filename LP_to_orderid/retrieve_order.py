from LP_to_orderid.SetupConn import setup_conn
import pandas
import jpype


def retrieve_all_tasks(scanner_id, curs):
    # this function should query for all orders assigned to DC001 and shelves
    # it returns the license plates, product ids, allocated quantities, weights and uoms per task id

    use_actual_database = False

    if use_actual_database:

        # check if the JVM has started
        if not jpype.isJVMStarted():
            curs = setup_conn()

        # check the cursor object
        if not curs:
            print('issue with cursor object, but JVM already started')
            return 'No connection'

        try:
            try:
                # select all tasks from DC001 and order by task_id
                curs.execute(
                    "SELECT A.task_id, A.license_plate_no, A.allocated_qty, A.product_id, A.source_location_no FROM "
                    "task_master A where A.dc_code = 'DC001' AND A.task_type = 'PICKING' AND A.task_status = 'AVL' "
                    "ORDER BY A.task_id")
                output = curs.fetchall()
            except Exception as e:
                print(e)
                return 'Retrieval error'

            # filter all picks for the shelves only
            filter_shelves = list(filter(lambda x: x[4][0] == 'S', output))
            print(filter_shelves)
            # check if any orders
            if not filter_shelves:
                print('no orders in DC001 shelves')
                return 'No orders'

            # filter for orders that have weight data in DC001 On Hand Items
            fields = ["Weight", "Weight UOM", "MOVE Part Number"]
            data = pandas.read_csv('DC001 On Hand Items.csv', usecols=fields)
            valid_orders = []

            for order in filter_shelves:
                order = list(order)
                record = data.loc[data["MOVE Part Number"] == order[3]]
                current_weight = pandas.Index.tolist(record["Weight"])[0]
                current_uom = pandas.Index.tolist(record["Weight UOM"])[0]
                if not current_weight and not current_uom:
                    continue
                else:
                    order.append(current_weight)
                    order.append(current_uom)
                    valid_orders.append(order)
            print(valid_orders)

            # Check if no orders with weights in On Hand Items
            if not valid_orders:
                print('no orders with weight data on file')
                return 'No orders'

            # Output all tasks in dict
            all_tasks = []
            for order in valid_orders:
                entry = dict({'task_id': order[0], 'license_plates_contained': [order[1]],
                              'quantity_requested': [order[2]], 'product_ids': [order[3]], 'product_weight': [order[5]],
                              'uom': [order[6]]})
                all_tasks.append(entry)
            print(all_tasks)

            return all_tasks

        except Exception as e:
            print(e)
            return 'General Error'
    else:
        # if an unspecified error occurs here, please print the error thrown and return "General Error"
        # if no orders in general, or no orders with weight data could be found, return "No orders"
        # if the connection didn't work, return 'No connection'
        # if there was some other error retrieving data return 'Retrieval error'
        return [{'task_id': 1111033, 'license_plates_contained': ['r1111233'], 'quantity_requested': [10],
                 'product_weight': [8], 'uom': ['g']},
                {'task_id': 1115610, 'license_plates_contained': ['l1432534'], 'quantity_requested': [10],
                 'product_weight': [5], 'uom': ['g']},
                {'task_id': 1341078, 'license_plates_contained': ['l1432534'],
                 'quantity_requested': [60], 'product_weight': [5], 'uom': ['g']}]
