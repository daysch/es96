import jaydebeapi
import jpype
import pandas


def retrieve_specific_order_info(scanner_id, license_plate):

    # if not jpype.isJVMStarted():
    try:
        # set up connection
        jvm_path = jpype.getDefaultJVMPath()
        jpype.startJVM(jvm_path, '-Djava.class.path=C:\ojdbc10.jar')
        con = jaydebeapi.connect("oracle.jdbc.driver.OracleDriver",
                                 "jdbc:oracle:thin:@wmsdbtst01.sager.com:1521:MV10TST", ["TSTMOVE", "TSTMOVE"])
        curs = con.cursor()
    except:
        # in the case the connection could not be made
        print('no connection')
        return 'No connection'

    try:
        # select orders with supplied license_plate (filter to where DC = 1 and first letter = S?)
        curs.execute(
            "SELECT A.product_id, A.allocated_qty, A.order_id, A.task_id FROM task_master A where A.license_plate_no = '{}' AND A.task_type = 'PICKING' AND A.task_status = 'AVL' ORDER BY A.path_sequence".format(
                license_plate))
        output = curs.fetchall()

        # check if retrieval is empty
        if not output:
            print('no order for given license plate')
            return 'No orders'

        # select weight with acquired product_id from product_uom
        product_id = output[0][0] # this returns first in the list if more than one
        quantity = output[0][1]
        order_id = output[0][2] # might want to add these to the count pages at the end
        task_id = output[0][3]

        # select weight and weight unit using acquired product_id from DC On Hand Items
        fields = ["Weight", "Weight UOM", "MOVE Part Number"]
        data = pandas.read_csv('DC001 On Hand Items.csv', usecols=fields)
        record = data.loc[data["MOVE Part Number"] == product_id]
        weight = pandas.Index.tolist(record["Weight"])
        weight_unit = pandas.Index.tolist(record["Weight UOM"])

        if not weight or not weight_unit:
            print('no weight data on file')
            return 'No weight data on file'

        order = [product_id, float(weight[0]), weight_unit[0], quantity]

        # close the connection
        # curs.close()
        # con.close()
        # jpype.shutdownJVM()

        return order

    except:
        # if there is a retrieval error
        print('could not retrieve')
        return 'Retrieval Error'

# retrieve_specific_order_info(0,'R001476007')


# this function should return all order IDs assigned to the same location as the employee scanned
def retrieve_all_license_plates(scanner_id):
    try:
        getdata = 0
    except:
        return "General Error"
    # if any error occurs here, please print relevant error messages and return "General Error"
    return [11110, 1112, 1113, 1114, 11132]
