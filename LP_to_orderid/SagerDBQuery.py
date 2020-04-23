# query is a string of SQL commands to query the Sager Database for the product order details: ID, quantity, weight
# curs is a cursor object from calling SetupConn
def SagerDBQuery(curs, query):

    curs.execute(query)
    order = curs.fetchall()

    # curs.close()
    # conn.close()

    return order
