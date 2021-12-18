#-*- coding:utf-8 -*-

def insertQR_fn(scan_in_OR_out, scan_current_time_uk, scan_custom_prod_code, scan_size, scan_A_OR_B):
  import pymysql
  from datetime import datetime
  from time import sleep
  from dateutil.relativedelta import relativedelta
  import configparser

  config = configparser.ConfigParser()
  config.read('config.ini')

  current_FullYear = datetime.today().strftime("%Y")                      # 현재 년(2021)
  current_Month = datetime.today().strftime("%m")                         # 현재 월(08)
  ago_Month = (datetime.today() - relativedelta(months=1)).strftime("%m") # 이전 월(07)

  # 상품 입출고 (Product_IN, Product_OUT)
  class db_con:
    host = config['DBSET']['HOST']
    port = config['DBSET']['PORT']
    user = config['DBSET']['USER']
    passwd = config['DBSET']['PASSWD']
    db = 'MALDEN_'+current_FullYear+'_'+current_Month
    db2 = 'MALDEN_'+current_FullYear+'_'+ago_Month
    char = config['DBSET']['CHAR']
    
  conn = pymysql.connect(host=db_con.host, port=db_con.port, user=db_con.user, password=db_con.passwd, db=db_con.db, charset=db_con.char, autocommit=True)
  curs = conn.cursor(pymysql.cursors.DictCursor)
  sleep(0.3)
  # 입고 #
  if scan_in_OR_out == 'in':
    table = 'Product_IN_'+datetime.today().strftime("%d")

    # A 타입의 QR 입고 시 출고 내역 검토 START #
    if scan_A_OR_B == 'A':
      sql = "SELECT TABLE_NAME FROM information_schema. tables WHERE table_schema = '"+db_con.db+"' AND TABLE_NAME LIKE 'Product_OUT%' ORDER BY table_name;"   # 현재 달 Product_IN 테이블 전체 조회
      curs.execute(sql)
      db_table = curs.fetchall()
      for table_name in db_table:                                                                             # 각 테이블에 QR값 중복 조회
        ck_record = 0
        DB_table_name = str(table_name['TABLE_NAME'])
        sql = "SELECT * FROM "+DB_table_name+" WHERE current_time_uk LIKE '"+str(scan_current_time_uk)+"%';"
        ck_record = curs.execute(sql)
        if ck_record != 0:
          raise NameError # 이미 출고된 QR

      sql2 = "SELECT TABLE_NAME FROM information_schema. tables WHERE table_schema = '"+db_con.db2+"' AND TABLE_NAME LIKE 'Product_OUT%' ORDER BY table_name;" # 이전 달 Product_IN 테이블 전체 조회
      curs.execute(sql2)
      db_table2 = curs.fetchall()
      for table_name in db_table2:                                                                            # 이전 달 각 테이블에 QR값 중복 조회
        ck_record = 0
        DB_table_name = str(table_name['TABLE_NAME'])
        sql = "SELECT * FROM "+db_con.db2+"."+DB_table_name+" WHERE current_time_uk LIKE '"+str(scan_current_time_uk)+"%';"
        ck_record = curs.execute(sql)
        if ck_record != 0:
          raise NameError # 이미 출고된 QR
    # A 타입의 QR 입고 시 출고 내역 검토 END #

    
    # 2개월 내 테이블 QR 중복 조회 START #
    sql = "SELECT TABLE_NAME FROM information_schema. tables WHERE table_schema = '"+db_con.db+"' AND TABLE_NAME LIKE 'Product_IN%' ORDER BY table_name;"   # 현재 달 Product_IN 테이블 전체 조회
    curs.execute(sql)
    db_table = curs.fetchall()
    for table_name in db_table:                                                                               # 각 테이블에 QR값 중복 조회
      ck_record = 0
      DB_table_name = str(table_name['TABLE_NAME'])
      sql = "SELECT * FROM "+DB_table_name+" WHERE current_time_uk LIKE '"+str(scan_current_time_uk)+"%';"
      ck_record = curs.execute(sql)
      if ck_record != 0:
        print("Dup : "+db_con.db+"."+DB_table_name)
        raise Exception # 이미 처리된 QR

    sql2 = "SELECT TABLE_NAME FROM information_schema. tables WHERE table_schema = '"+db_con.db2+"' AND TABLE_NAME LIKE 'Product_IN%' ORDER BY table_name;" # 이전 달 Product_IN 테이블 전체 조회
    curs.execute(sql2)
    db_table2 = curs.fetchall()
    for table_name in db_table2:                                                                              # 이전 달 각 테이블에 QR값 중복 조회
      ck_record = 0
      DB_table_name = str(table_name['TABLE_NAME'])
      sql = "SELECT * FROM "+db_con.db2+"."+DB_table_name+" WHERE current_time_uk LIKE '"+str(scan_current_time_uk)+"%';"
      ck_record = curs.execute(sql)
      if ck_record != 0:
        print("Dup : "+db_con.db2+"."+DB_table_name)
        raise Exception 
    # 2개월 내 테이블 QR 중복 조회 END #

    if scan_A_OR_B == 'A':
      sql = "INSERT INTO "+table+" VALUES ('"+scan_current_time_uk+"','"+scan_custom_prod_code+"','"+scan_size+"',"+" 1, NOW(),'NO');"
      curs.execute(sql)
      print("IN_insert OK")

    elif scan_A_OR_B == 'B':
      Size_and_Quantity = str(scan_size).split(',')
      BoxQR_uk = 1                                                                                            # BoxQR 중복 방지 값
      for i in Size_and_Quantity:
        if i != '':
          Size = i.split(':')[0]
          Quantity = i.split(':')[1]
          sql = "INSERT INTO "+table+" VALUES ('"+scan_current_time_uk+"-"+str(BoxQR_uk)+"','"+scan_custom_prod_code+"','"+Size+"','"+Quantity+"', NOW(),'NO');"
          curs.execute(sql)
          BoxQR_uk += 1
          print("IN_insert OK")
        else:
          break

    

  # 출고 #
  elif scan_in_OR_out == 'out':
    table = 'Product_OUT_'+datetime.today().strftime("%d")
    
    # 전체 데이터베이스내 입고 이력 검사 START (BOX QR만 실시) #
    sql = "show databases LIKE 'MALDEN_2%';"
    curs.execute(sql)
    database_name = curs.fetchall()
    In_History = 0                                              # 입고된 적이 있으면 '1'
      
    if scan_A_OR_B == 'B':
      for Database in database_name:
        DB_Database_name = str(Database['Database (MALDEN_2%)'])
        sql2 = "SELECT TABLE_NAME FROM information_schema. tables WHERE table_schema = '"+DB_Database_name+"' AND TABLE_NAME LIKE 'Product_IN%' ORDER BY table_name;"
        curs.execute(sql2)
        db_table2 = curs.fetchall()

        for table_name in db_table2:
          ck_record = 0
          DB_table_name = str(table_name['TABLE_NAME'])
          sql = "SELECT * FROM "+DB_Database_name+"."+DB_table_name+" WHERE current_time_uk LIKE '"+str(scan_current_time_uk)+"%';"
          ck_record = curs.execute(sql)
          if ck_record != 0:
            In_History = 1
    # 전체 데이터베이스내 입고 이력 검사 END #

    # 전체 데이터베이스내 출고 중복 검사 START #
    if (In_History == 1) or (scan_A_OR_B == 'A'):
      for Database in database_name:
        DB_Database_name = str(Database['Database (MALDEN_2%)'])
        sql2 = "SELECT TABLE_NAME FROM information_schema. tables WHERE table_schema = '"+DB_Database_name+"' AND TABLE_NAME LIKE 'Product_OUT%' ORDER BY table_name;"
        curs.execute(sql2)
        db_table2 = curs.fetchall()

        for table_name in db_table2:
          ck_record = 0
          DB_table_name = str(table_name['TABLE_NAME'])
          sql = "SELECT * FROM "+DB_Database_name+"."+DB_table_name+" WHERE current_time_uk LIKE '"+str(scan_current_time_uk)+"%';"
          ck_record = curs.execute(sql)
          if ck_record != 0:
            print("Dup : "+DB_Database_name+"."+DB_table_name)
            raise Exception # 이미 처리된 QR
    else:
      raise ValueError    # 입고 이력 없음
    # 전체 데이터베이스내 출고 중복 검사 END #

    if scan_A_OR_B == 'A':
      sql = "INSERT INTO "+table+" VALUES ('"+scan_current_time_uk+"','"+scan_custom_prod_code+"','"+scan_size+"',"+" 1, NOW(),'NO');"
      curs.execute(sql)
      print("OUT_insert OK")

    elif scan_A_OR_B == 'B':
      Size_and_Quantity = str(scan_size).split(',')
      BoxQR_uk = 1                                                                                          # BoxQR 중복 방지 값
      for i in Size_and_Quantity:
        if i != '':
          Size = i.split(':')[0]
          Quantity = i.split(':')[1]
          sql = "INSERT INTO "+table+" VALUES ('"+scan_current_time_uk+"-"+str(BoxQR_uk)+"','"+scan_custom_prod_code+"','"+Size+"','"+Quantity+"', NOW(),'NO');"
          curs.execute(sql)
          BoxQR_uk += 1
          print("OUT_insert OK")
        else:
          break

  else:
    print("!!insert ERROR!!")
  