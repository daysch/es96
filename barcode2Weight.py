def barcode2weight(barcode):
    
    """
    Takes in one int, the barcode.
    Queries the database es96 for the weight and unit associated with the barcode and returns these values.
    """
    
    import mysql.connector

    # Establish connection to the database
    conn = mysql.connector.connect(
          host="localhost",
          user="root",
          password="ES96database",
          database="es96")

    # Create a cursor
    cursor = conn.cursor()

    # Query the database for the weight and unit associated with the scanned barcode
    cursor.execute("SELECT weight FROM products WHERE barcode = {}".format(barcode))
    weight = cursor.fetchall()[0][0]

    cursor.execute("SELECT unit FROM products WHERE barcode = {}".format(barcode))
    unit = cursor.fetchall()[0][0]
    
    return weight, unit