import jaydebeapi
import jpype
import pandas
from SetupConn import *

# Sets up connection
# jvm_path = jpype.getDefaultJVMPath()
# jpype.startJVM(jvm_path, '-Djava.class.path=C:\ojdbc10.jar')
# con = jaydebeapi.connect("oracle.jdbc.driver.OracleDriver", "jdbc:oracle:thin:@wmsdbtst01.sager.com:1521:MV10TST",
#                          ["TSTMOVE", "TSTMOVE"])
# curs = con.cursor()

# Retrieves table names
#curs.execute("SELECT table_name FROM all_tables ORDER BY table_name")

# Retrieves column names from a given table
#curs.execute("SELECT column_name FROM user_tab_columns WHERE table_name='EQUIPMENT'")

# Retrieves all data from a given table
#curs.execute("SELECT * FROM user_mast")

# Retrieves a percentage of random records from a table
#curs.execute("SELECT * FROM location SAMPLE(0.1)")

# Retrieve employee id
#curs.execute("SELECT A.user_id, A.employee_no, B.dc_code FROM user_mast A, user_dc_access B WHERE A.active_flag='Y' SAMPLE(0.01)") #error with this one
#employee_id = 16208 # valid id for testing
#curs.execute("SELECT * FROM user_mast WHERE employee_no='{}'".format(employee_id))

# Retrieve rf scanner id
#curs.execute("SELECT * FROM location A WHERE A.zone_code = 'EQUIPMENT-Z' AND A.location_status = 'AVL'") #no output
#curs.execute("SELECT * FROM equipment") #no scanners here

# Retrieve product weight given product id
#product_id = 'ALPFIT2213/16CLR500' # valid id for testing, this will ultimately be extracted from the product order
#curs.execute("SELECT weight FROM product_uom WHERE product_id='{}'".format(product_id))

# Retrieve all current picks ordered by path_sequence
#curs.execute("SELECT A.dc_code, A.task_id, A.full_pick_ind, A.source_location_no, A.path_sequence, A.license_plate_no, A.product_id, A.allocated_qty, A.picked_qty FROM task_master A where A.task_type = 'PICKING' AND A.task_status = 'AVL' ORDER BY A.path_sequence")
#curs.execute("SELECT A.product_id, A.allocated_qty, A.source_location_no, A.license_plate_no, A.order_id, A.task_id FROM task_master A where A.task_type = 'PICKING' AND A.task_status = 'AVL' AND A.dc_code = 'DC004' ORDER BY A.task_id")

# Retrieve product id, qty and order id given license_plate_no
#license_plate_no = 'R001409288'
#curs.execute("SELECT A.product_id, A.allocated_qty, A.order_id FROM task_master A where A.license_plate_no = '{}' AND A.task_type = 'PICKING' AND A.task_status = 'AVL' ORDER BY A.path_sequence".format(license_plate_no))

#curs.execute("SELECT A.source_location_no FROM task_master A where A.task_type = 'PICKING' AND A.task_status = 'AVL' ORDER BY A.path_sequence")

#filter_shelves = list(filter(lambda x : x[4][0] == 'S', output))

# Retrieve weight from on-hand items
# fields = ["Weight","Weight_UOM","MOVE_Part_Number"]
# data = pandas.read_csv('DC001 On Hand Items.csv', usecols=fields)
# record = data.loc[data["MOVE_Part_Number"] == 'TXM200-112']
# weight_unit = record["Weight_UOM"]
# weight = record["Weight"]
# print(weight, weight_unit)