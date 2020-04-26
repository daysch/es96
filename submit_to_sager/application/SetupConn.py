def setup_conn():
    try:
        import jaydebeapi
        import jpype

        if jpype.isJVMStarted() and not jpype.isThreadAttachedToJVM():
            jpype.attachThreadToJVM()
            jpype.java.lang.Thread.currentThread().setContextClassLoader(
                jpype.java.lang.ClassLoader.getSystemClassLoader())

            con = jaydebeapi.connect("oracle.jdbc.driver.OracleDriver",
                                     "jdbc:oracle:thin:@wmsdbtst01.sager.com:1521:MV10TST", ["TSTMOVE", "TSTMOVE"])
            return con.cursor()
        else:
            jvm_path = jpype.getDefaultJVMPath()
            jpype.startJVM(jvm_path, '-Djava.class.path=C:\ojdbc10.jar')
            con = jaydebeapi.connect("oracle.jdbc.driver.OracleDriver",
                                     "jdbc:oracle:thin:@wmsdbtst01.sager.com:1521:MV10TST", ["TSTMOVE", "TSTMOVE"])
            return con.cursor()

    except Exception as e:
        print(e)
        print('no connection')
        return None
