import time

# Define interval (s)
interval = 0.01

# Define confidence interval (the percentage of the weight within which you want the desired scale reading)
conf_int = 0.01 # can also define this as an absolute value if that works better

def main():

    """ 
    Check continually until the desired order weight has been reached, printing out part count each check.
    """
    
    # Get barcode number
    barcode = readScanner()
    
    # Get product weight (per unit) in common unit - kg or g?
    weight = barcode2Weight(barcode)
    
    # Get order quantity - from database? Set as 1 temporarily
    quantity = barcode2OrderQuantity(barcode)
    
    # Get initial scale readout - how to incorporate mode_weight_requested as input? Define another function to return it?
    reading = readScale()
    
    # Define desired weight interval
    goal_weight_lb = (quantity * weight) - (conf_int * weight)
    goal_weight_ub = (quantity * weight) + (conf_int * weight)
    
    # Find initial parts
    parts = round(reading/weight)
    
    # Check every interval seconds if desired order weight has been reached
    while not goal_weight_lb <= reading <= goal_weight_ub:
        print("Total not reached: {} / {} pieces".format(parts,quantity))
        time.sleep(interval)
        reading = readScale()
        parts = round(reading/weight)
        
    print("Total reached: {} / {} pieces".format(parts,quantity))    
    return
    
    # Note: parts should == quantity if reading is within interval (these 2 conditions should be synonomous) 
    # However, they will only be so if we choose a correct confidence interval...
    # Shall we return parts or print parts?
    
    
    
if __name__ == "__main__":
    main()

