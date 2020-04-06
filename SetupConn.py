import jaydebeapi

# Takes no inputs and returns a cursor object once setting up a JDBC connection with the Oracle Database
def SetupConn():
    conn = jaydebeapi.connect('oracle.jdbc.driver.OracleDriver','[MYUSER]/[MYPASS]@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=[MYHOST])(PORT=1521))(CONNECT_DATA=(SERVER=dedicated) (SERVICE_NAME=[MYSERVICENAME])))')
    curs = conn.cursor()
    return curs
