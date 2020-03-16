def barcode2weight(barcode):
    
    """
    Takes in one int, the barcode.
    Queries the database warehouse for the weight associated with the barcode and returns this float.
    """
    
    # Query the database for the weight associated with the scanned barcode
    weight = db.execute("SELECT weight FROM warehouse WHERE barcode = :barcode", barcode=barcode)
    
    # the db needs to be something else, it needs to connect to the database 
    # conn = pyodbc.connect(driver, server, database, trustedconnection=yes)
    # db = conn.cursor()
    # source: https://youtu.be/aF552bMEcO4 
    
    return weight
