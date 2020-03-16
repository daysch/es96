def barcode2weight(barcode):
    
    """
    Takes in one int, the barcode.
    Queries the database warehouse for the weight associated with the barcode and returns this float.
    """
    
    # Query the database for the weight associated with the scanned barcode
    weight = db.execute("SELECT weight FROM warehouse WHERE barcode = :barcode", barcode=barcode)
    
    return weight
