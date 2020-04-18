import time

# Define interval (s)
interval = 2

# Define confidence interval
conf_int = 0.5


def main():
    """
    Check continually until the desired order weight has been reached, printing out part count each check.
    """

    # Get barcode number
    barcode = readScanner()

    # Get product weight (per unit) and unit
    unit, weight = barcode2Weight(barcode)

    # Get order quantity
    quantity = barcode2OrderQuantity(barcode)

    # Get initial scale readout
    reading = readScale(quantity)

    # Define desired weight interval
    goal_weight_lb = (quantity * weight) - (conf_int * weight)
    goal_weight_ub = (quantity * weight) + (conf_int * weight)

    # Find initial parts
    parts = round(reading / weight)

    # Check every interval seconds if desired order weight has been reached
    while not goal_weight_lb <= reading <= goal_weight_ub:
        print("Total not reached: {} / {} pieces".format(parts, quantity))
        time.sleep(interval)
        reading = readScale(quantity)
        reading = accurate_reading(unit)
        # avg_weight = reading/quantity
        parts = round(reading / weight)

    print("Total reached: {} / {} pieces".format(parts, quantity))
    return


if __name__ == "__main__":
    main()