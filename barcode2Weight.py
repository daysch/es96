def barcode2Weight(barcode):

    """
    Takes in one int, the barcode.
    Queries the database es96 for the weight and unit associated with the barcode and returns these values.
    """

    import sqlite3
    conn = sqlite3.connect('es96.db')
    c = conn.cursor()

    # Query the database for the weight and unit associated with the scanned barcode
    c.execute("SELECT weight FROM products WHERE barcode = {}".format(barcode))
    weight = cursor.fetchall()[0][0]

    c.execute("SELECT unit FROM products WHERE barcode = {}".format(barcode))
    unit = cursor.fetchall()[0][0]

    return weight, unit
