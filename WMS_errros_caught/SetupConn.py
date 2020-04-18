import jaydebeapi
import jpype

def setup_conn():
    # try to make connection with the database
    try:
        jvm_path = jpype.getDefaultJVMPath()
        jpype.startJVM(jvm_path, '-Djava.class.path=C:\ojdbc10.jar')
        con = jaydebeapi.connect("oracle.jdbc.driver.OracleDriver", "jdbc:oracle:thin:@wmsdbtst01.sager.com:1521:MV10TST",["TSTMOVE","TSTMOVE"])
        curs = con.cursor()
        return curs
    # if connection was unsuccessful, return None
    except:
        return None
