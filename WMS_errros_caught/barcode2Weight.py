def barcode2Weight(barcode, cursor):
    # this function is currently unused, retrieve_order() is used instead
    """
    Takes in one int, the barcode.
    Queries the database es96 for the weight and unit associated with the barcode and returns these values.
    """

    import sqlite3

    # Make a connection to the database
    conn = sqlite3.connect('es96.db')
    c = conn.cursor()

    # Query the database for the weight and unit associated with the scanned barcode
    c.execute("SELECT weight FROM products WHERE barcode = {}".format(barcode))
    weight = c.fetchall()[0][0]

    c.execute("SELECT unit FROM products WHERE barcode = {}".format(barcode))
    unit = c.fetchall()[0][0]

    return weight, unit
