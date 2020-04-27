from SetupConn import *
import pandas
import requests # pip install requests
import csv
from datetime import datetime
from pytz import timezone

# set timezone
tz = timezone('US/Eastern')

def retrieve_all_tasks(dc_id):
    # this function should query for all orders assigned to DC001 and shelves
    # it returns the license plates, product ids, allocated quantities, weights and uoms per task id

    use_actual_database = True

    # try to download and update weight database, otherwise continue to use old database
    try:
        # link was generated like this:
        # https://stackoverflow.com/questions/33713084/download-link-for-google-spreadsheets-csv-export-with-multiple-sheets
        csv_url = \
            'https://docs.google.com/spreadsheets/d/18vBpk0YsZXi2ISwpICEjErgN4ec9Gd7A/gviz/tq?tqx=out:csv&sheet=Sheet1'

        # this code is based on: https://stackoverflow.com/questions/35371043/use-python-requests-to-download-csv
        with requests.Session() as s:
            download = s.get(csv_url)

            decoded_content = download.content.decode('utf-8')

            # read csv data
            onhand_items = csv.reader(decoded_content.splitlines(), delimiter=',')

            # rewrite csv file
            with open('DC001 On Hand Items.csv', 'w') as csvfile:
                writer_object = csv.writer(csvfile, delimiter=',')
                for row in onhand_items:
                    writer_object.writerow(row)

                # add a row to include a datestamp at position of MOVE part number in last row
                writer_object.writerow([0,0,0,datetime.now(tz),0,0,0,0,0,0,0,0])

            print('Updated onhand items')

    except Exception as e:
        print(e)
        print('Using local version, could not update')

    if use_actual_database:

        curs = setup_conn()

        # check the cursor object
        if not curs:
            return 'No connection'

        try:
            try:
                # select all tasks from given DC and order by task_id
                curs.execute(
                    "SELECT A.task_id, A.license_plate_no, A.allocated_qty, A.product_id, A.source_location_no FROM "
                    "task_master A where A.dc_code = '{}' AND A.task_type = 'PICKING' AND A.task_status = 'AVL' "
                    "ORDER BY A.task_id".format(dc_id))
                output = curs.fetchall()
            except Exception as e:
                print(e)
                return 'Retrieval error'

            # filter all picks for the shelves only
            filter_shelves = list(filter(lambda x: x[4][0] == 'S', output))

            # check if any orders
            if not filter_shelves:
                print('no orders in shelves')
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
                if not current_weight or not current_uom:
                    continue
                else:
                    order.append(current_weight)
                    order.append(current_uom)
                    valid_orders.append(order)

            # Check if no orders with weights in On Hand Items
            if not valid_orders:
                print('no orders with weight data on file')
                return 'No orders'

            # Output all tasks in dict
            all_tasks = []
            for order in valid_orders:
                entry = dict({'task_id': str(order[0]), 'license_plates_contained': [order[1]],
                              'quantity_requested': [order[2]], 'product_ids': [order[3]],
                              'product_weight': [order[5]],
                              'uom': [order[6]]})
                all_tasks.append(entry)

            return [all_tasks, data["MOVE Part Number"][len(data["MOVE Part Number"])-1]]

        except Exception as e:
            print(e)
            return 'General Error'
    else:
        # if an unspecified error occurs here, please print the error thrown and return "General Error"
        # if no orders in general, or no orders with weight data could be found, return "No orders"
        # if the connection didn't work, return 'No connection'
        # if there was some other error retrieving data return 'Retrieval error'
        fields = ["Weight", "Weight UOM", "MOVE Part Number"]
        data = pandas.read_csv('DC001 On Hand Items.csv', usecols=fields)
        return [{'task_id': 1111033, 'license_plates_contained': ['r1111233'], 'quantity_requested': [10],
                 'product_weight': [8], 'uom': ['g']},
                {'task_id': 1115610, 'license_plates_contained': ['l1432534'], 'quantity_requested': [10],
                 'product_weight': [5], 'uom': ['g']},
                {'task_id': 1341078, 'license_plates_contained': ['l1432534'],
                 'quantity_requested': [60], 'product_weight': [5], 'uom': ['g']}, data["MOVE Part Number"][len(data["MOVE Part Number"])-1]]

