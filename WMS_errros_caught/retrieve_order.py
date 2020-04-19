import jaydebeapi
import jpype

# need to clarify what is passed in here: ideally it would be the scanner id
# but it might need to be the dc_code and location and order by path sequence

def retrieve_order():

    try:
        # set up connection
        jvm_path = jpype.getDefaultJVMPath()
        jpype.startJVM(jvm_path, '-Djava.class.path=C:\ojdbc10.jar')
        con = jaydebeapi.connect("oracle.jdbc.driver.OracleDriver", "jdbc:oracle:thin:@wmsdbtst01.sager.com:1521:MV10TST",["TSTMOVE","TSTMOVE"])
        curs = con.cursor()

        # select order from the front of the path sequence
        curs.execute("SELECT A.product_id, A.allocated_qty FROM task_master A where A.task_type = 'PICKING' AND A.task_status = 'AVL' ORDER BY A.path_sequence")
        order = curs.fetchall()[0]

        if not order:
            return 'No Orders'

        product_id = order[0]
        target_quantity = order[1]

        # select weight with acquired product_id
        curs.execute("SELECT weight FROM product_uom WHERE product_id='{}'".format(product_id))
        weight = curs.fetchall()[0][0]

        # reference number, the product weight, weight unit and the target count
        output = [product_id,weight,'g',target_quantity]

        # close the connection
        con.close()
        #print(output)
        return output

    # if connection was unsuccessful, return None
    except:
        return 'Database Retrieval Error'

    #return [100, 8, 'g', 2]

retrieve_order()