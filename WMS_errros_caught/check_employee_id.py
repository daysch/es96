import jaydebeapi
import jpype

# need to clarify what is passed in here, whether or not it is possible to connect these 3 ids in the database

def check_employee_id(employee_id, scanner_id, dc_id):

    try:
        # set up connection
        jvm_path = jpype.getDefaultJVMPath()
        jpype.startJVM(jvm_path, '-Djava.class.path=C:\ojdbc10.jar')
        con = jaydebeapi.connect("oracle.jdbc.driver.OracleDriver", "jdbc:oracle:thin:@wmsdbtst01.sager.com:1521:MV10TST",["TSTMOVE","TSTMOVE"])
        curs = con.cursor()

        # check if employee id exists
        curs.execute("SELECT * FROM user_mast WHERE employee_no='{}'".format(employee_id))
        employee_check = curs.fetchall()[0]
        print(employee_check)

        if not employee_check:
            return 'Employee not found'
        else:
            return 'successful'

        # close the connection
        con.close()

    # if connection was unsuccessful, return None
    except:
        return 'Database Retrieval Error'

check_employee_id(16208,0,0)
