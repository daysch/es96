def barcode2OrderQuantity(barcode):
    
    """
    Takes in one int, the barcode.
    Queries the database es96 for the order quantity associated with the order and barcode and returns these values.
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
    cursor.execute("SELECT quantity FROM orders WHERE barcode = {}".format(barcode))
    quantity = cursor.fetchall()[0][0]

    return quantity
