import jaydebeapi
import jpype

# Sets up connection
jvm_path = jpype.getDefaultJVMPath()
jpype.startJVM(jvm_path, '-Djava.class.path=C:\ojdbc10.jar')
con = jaydebeapi.connect("oracle.jdbc.driver.OracleDriver", "jdbc:oracle:thin:@wmsdbtst01.sager.com:1521:MV10TST",
                         ["TSTMOVE", "TSTMOVE"])
curs = con.cursor()

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

# Retrieve dc code

# Retrieve product weight given product id
#product_id = 'ALPFIT2213/16CLR500' # valid id for testing, this will ultimately be extracted from the product order
#curs.execute("SELECT weight FROM product_uom WHERE product_id='{}'".format(product_id))

# Retrieve all current picks ordered by path_sequence
#curs.execute("SELECT A.dc_code, A.task_id, A.full_pick_ind, A.source_location_no, A.path_sequence, A.license_plate_no, A.product_id, A.allocated_qty, A.picked_qty FROM task_master A where A.task_type = 'PICKING' AND A.task_status = 'AVL' ORDER BY A.path_sequence")

list = curs.fetchall()

print(list)
