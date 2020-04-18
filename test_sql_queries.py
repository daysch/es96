import jaydebeapi
import jpype

jvm_path = jpype.getDefaultJVMPath()
jpype.startJVM(jvm_path, '-Djava.class.path=C:\ojdbc10.jar')
con = jaydebeapi.connect("oracle.jdbc.driver.OracleDriver", "jdbc:oracle:thin:@wmsdbtst01.sager.com:1521:MV10TST",
                         ["TSTMOVE", "TSTMOVE"])
curs = con.cursor()

# Retrieves table names
#curs.execute("SELECT table_name FROM all_tables ORDER BY table_name")

# Retrieves column names from a given table
#curs.execute("SELECT column_name FROM user_tab_columns WHERE table_name='USER_MAST'")

# Retrieves all data from a table
#curs.execute("SELECT * FROM user_mast")

# Retrieves 5 random records from a table
#curs.execute("SELECT weight FROM product_uom SAMPLE(0.001)")

# Retrieve employee id
#curs.execute("SELECT A.user_id, A.employee_no, B.dc_code FROM user_mast A, user_dc_access B WHERE A.active_flag='Y' SAMPLE(0.01)")
#employee_id = 16208
#curs.execute("SELECT * FROM user_mast WHERE employee_no='{}'".format(employee_id))

# Retrieve rf scanner id

# Retrieve dc code'

# Retrieve product weight given product id
#product_id = 'ALPFIT2213/16CLR500' # this will ultimately be extracted from the product order
#curs.execute("SELECT weight FROM product_uom WHERE product_id='{}'".format(product_id))

#list = curs.fetchall()[0]
#list = curs.fetchall()

#print(list)
