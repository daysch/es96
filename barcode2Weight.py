def barcode2weight(barcode):
    
    """
    Takes in one int, the barcode.
    Queries the database warehouse for the weight associated with the barcode and returns this float.
    """
    
    import pyodbc
    
    # Establish connection to the database - my ODBC driver is not working, it is installed but not in odbcinst.ini?
    conn = pyodbc.connect(
    'DRIVER=MySQL ODBC 8.0 ANSI Driver;'
    'SERVER=localhost;'
    'DATABASE=es96;'
    'UID=root;'
    'PWD=ES96database;'
    'charset=utf8;')
    
    # Create a cursor
    cursor = conn.cursor()
    
    # Query the database for the weight associated with the scanned barcode
    weight = cursor.execute("SELECT weight FROM products WHERE barcode = :barcode", barcode=barcode)
    
    conn.commit()
    conn.close()
    
    return weight