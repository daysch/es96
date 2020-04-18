def check_employee_id(employee_id, scanner_id, dc_id, cursor):
    # this function will only be called with a nonzero cursor
    # if there is a database retrieval error, return 'Retrieval Error'
    # if the employee could not be found return 'employee not found'
    # otherwise return successful
    # insert code here that checks whether the entered id exists in the database

    # check if the employee exists in the system
    cursor.execute("SELECT * FROM user_mast WHERE employee_no='{}'".format(employee_id))
    employee_check = cursor.fetchall()

    # if the employee could not be found return 'employee not found'
    if not employee_check:
        print('not found')
        return 'Employee not found'
    print('found')
    return 'successful'



