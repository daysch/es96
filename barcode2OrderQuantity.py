def barcode2OrderQuantity(barcode):
    """
    Takes in one int, the barcode.
    Queries the database es96 for the order quantity associated with the order and barcode and returns these values.
    """

    import sqlite3

    # Make a connection to the database
    conn = sqlite3.connect('es96.db')
    c = conn.cursor()

    # Query the database for the weight and unit associated with the scanned barcode
    c.execute("SELECT quantity FROM orders WHERE barcode = {}".format(barcode))
    quantity = c.fetchall()[0][0]

    # test
    
    return quantity