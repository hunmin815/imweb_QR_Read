#-*- coding:utf-8 -*-
# MariaDB Connection Option

import pymysql
from datetime import datetime
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


# 상품 리스트 (Product_List, Prod_od_List)
class db_con2:
  host = config['DBSET']['HOST']
  port = config['DBSET']['PORT']
  user = config['DBSET']['USER']
  passwd = config['DBSET']['PASSWD']
  db = config['DBSET']['DB_Product']
  char = config['DBSET']['CHAR']
  
conn2 = pymysql.connect(host=db_con2.host, port=db_con2.port, user=db_con2.user, password=db_con2.passwd, db=db_con2.db, charset=db_con2.char, autocommit=True)
curs2 = conn2.cursor(pymysql.cursors.DictCursor)


# 로그인 사용자 리스트
class db_con3:
  host = config['DBSET']['HOST']
  port = config['DBSET']['PORT']
  user = config['DBSET']['USER']
  passwd = config['DBSET']['PASSWD']
  db = config['DBSET']['DB_user']
  char = config['DBSET']['CHAR']
  
conn3 = pymysql.connect(host=db_con3.host, port=db_con3.port, user=db_con3.user, password=db_con3.passwd, db=db_con3.db, charset=db_con3.char, autocommit=True)
curs3 = conn3.cursor(pymysql.cursors.DictCursor)