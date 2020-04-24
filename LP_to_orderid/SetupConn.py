def setup_conn():
    # if not cursor:
    #     try:
    #         import jaydebeapi
    #         import jpype
    #
    #         jvm_path = jpype.getDefaultJVMPath()
    #         jpype.startJVM(jvm_path, '-Djava.class.path=C:\ojdbc10.jar')
    #         con = jaydebeapi.connect("oracle.jdbc.driver.OracleDriver", "jdbc:oracle:thin:@wmsdbtst01.sager.com:1521:MV10TST",["TSTMOVE","TSTMOVE"])
    #         curs = con.cursor()
    #         return curs
    #     except:
    #         return None
    # else:
    #     cursor = cursor
    #     # first close the connection then reopen
    #     return cursor

    try:
        import jaydebeapi
        import jpype

        jvm_path = jpype.getDefaultJVMPath()
        jpype.startJVM(jvm_path, '-Djava.class.path=C:\ojdbc10.jar')
        con = jaydebeapi.connect("oracle.jdbc.driver.OracleDriver", "jdbc:oracle:thin:@wmsdbtst01.sager.com:1521:MV10TST",["TSTMOVE","TSTMOVE"])
        curs = con.cursor()

        return curs

    except:
        print('no connection')
        return None
