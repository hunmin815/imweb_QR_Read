#-*- coding:utf-8 -*-
from flask import Flask, render_template, request, url_for, flash, session
from datetime import datetime
from time import sleep
from pymysql import NUMBER, STRING
from werkzeug.utils import escape, redirect
import db_insertQR
import hashlib
import db_conn

application = Flask(__name__)
application.secret_key = 'ABCDEFGHIJKL_Malden'

@application.route("/")
def Login():
  if ('userid' in session) and ('user_key' in session):
    session_user_id = '%s' % escape(session['userid'])
    # session_user_key = '%s' % escape(session['user_key'])
    db_conn.conn3
    db_conn.curs3

    table = "user_account"
    SELECT_sql = "select user_num, admin from " + table + " where id = '"+session_user_id+"';"
    try:
      db_conn.curs3.execute(SELECT_sql)
      user_num_rows = db_conn.curs3.fetchall()
      sleep(0.1)
      db_user_num = user_num_rows[0]['user_num']
      # db_admin = str(user_num_rows[0]['admin'])
      # user_num = db_user_num  
    except:
      return render_template("Login.html")
  else:
    return render_template("Login.html")
  
  if str(db_user_num) != '0':
    return render_template("home.html", user_id = session_user_id)
  else:
    flash("허가되지 않은 사용자입니다.\\n지속적인 로그인 시도 시 차단될 수 있습니다.")
    return redirect('/logout')
    

# 로그인 체크 START
@application.route("/login" , methods=['POST', 'GET'])
def login():
  if request.method == 'POST':
    str = ""
    salt = "malden"
    user_id = request.form['user_id']
    user_pw = request.form['user_pw']
    str = user_pw
    user_crypt = hashlib.sha512((str+salt).encode('utf8')).hexdigest()
    user_crypt2 = hashlib.sha512((user_crypt).encode('utf8')).hexdigest()

    db_conn.conn3
    db_conn.curs3

    table = "user_account"
    SELECT_sql = "select * from " + table + " where id = '"+user_id+"';"
    try:
      if db_conn.curs3.execute(SELECT_sql) != "0":
        user_account_rows = db_conn.curs3.fetchall()
        db_user_pw = user_account_rows[0]['password']
        # print("user_crypt2 : "+user_crypt2)
        # print("db_user_pw : "+db_user_pw)
        if user_crypt2 == db_user_pw:
          session['userid'] = user_id
          session['user_key'] = user_crypt2
          return redirect('/home')
          # return render_template("qr_gen_box.html")
          # return '%s' % escape(session['username'])
        else:
          flash("아이디가 존재하지 않거나 비밀번호가 잘못되었습니다")
          return redirect('/logout')
      else:
        flash("아이디가 존재하지 않거나 비밀번호가 잘못되었습니다")
        return redirect('/logout')
    except:
      flash("아이디가 존재하지 않거나 비밀번호가 잘못되었습니다")
      return redirect('/logout')
  else:
    flash("잘못된 접근입니다.")
    return redirect('/logout')
# 로그인 체크 END

# 로그아웃 START
@application.route("/logout")
def logout():
  try:
    session.pop('userid', None)
    session.pop('user_key', None)
    return redirect('/')
  except:
    session.pop('userid', None)
    session.pop('user_key', None)
    return redirect('/')
# 로그아웃 END


@application.route("/home")
def home():
  if ('userid' in session):
    session_user_id = '%s' % escape(session['userid'])
    db_conn.conn3
    db_conn.curs3

    table = "user_account"
    SELECT_sql = "select user_num from " + table + " where id = '"+session_user_id+"';"
    try:
      db_conn.curs3.execute(SELECT_sql)
      user_num_rows = db_conn.curs3.fetchall()
      db_user_num = user_num_rows[0]['user_num']
      user_num = db_user_num  
    except:
      flash("아이디가 존재하지 않거나 비밀번호가 잘못되었습니다.")
      return redirect('/logout')
    else:
      return render_template("home.html", user_id = session_user_id)
  else:
    flash("로그인 후 이용가능합니다.")
    return redirect('/logout')



@application.route("/scanner", methods=['POST', 'GET'])
def choice_main():
  if request.method == 'GET':
    if ('userid' in session):
      session_user_id = '%s' % escape(session['userid'])
      db_conn.conn3
      db_conn.curs3

      table = "user_account"
      SELECT_sql = "select user_num from " + table + " where id = '"+session_user_id+"';"
      try:
        db_conn.curs3.execute(SELECT_sql)
        user_num_rows = db_conn.curs3.fetchall()
        db_user_num = user_num_rows[0]['user_num']
        user_num = db_user_num  
      except:
        flash("아이디가 존재하지 않거나 비밀번호가 잘못되었습니다.")
        return redirect('/logout')
      else:
        if request.args.get('in_OR_out') == 'in' :
          return render_template("scanner.html",in_OR_out = "in", title="입고", scan_data0='undefined',scan_data1='undefined',scan_data2='undefined',scan_data3='undefined',scan_data4='undefined',scan_data5='A',dup='no')
        elif request.args.get('in_OR_out') == 'out' :
          return render_template("scanner.html",in_OR_out = "out", title="출고", scan_data0='undefined',scan_data1='undefined',scan_data2='undefined',scan_data3='undefined',scan_data4='undefined',scan_data5='A',dup='no')
    else:
      flash("로그인 후 이용가능합니다.")
      return redirect('/logout')

  

@application.route("/insertQR", methods=['POST', 'GET'])
def api():
  if request.method == 'GET':
    scan_in_OR_out = request.args.get('in_OR_out')                                              # in OR out
    # scan_stock_sku = request.args.get('scan_data1')+'-'+request.args.get('scan_data2')        # scan_data1(custom_prod_code), scan_data2(size)
    scan_current_time_uk = request.args.get('scan_data0')+'_'+request.args.get('scan_data3')    # scan_data0(create_time), scan_data3(unique_key)
    scan_custom_prod_code = request.args.get('scan_data1')
    scan_size = request.args.get('scan_data2')
    # scan_user_num = request.args.get('scan_data4')
    scan_A_OR_B = request.args.get('scan_data5')

    if request.args.get('scan_data1') != 'undefined' or request.args.get('scan_data2') != 'undefined' or request.args.get('scan_data3') != 'undefined':
      try:
        db_insertQR.insertQR_fn(str(scan_in_OR_out), str(scan_current_time_uk), str(scan_custom_prod_code), str(scan_size), str(scan_A_OR_B)) # try Insert
        
      except ValueError as e:
        print("!!No Insert History QR!!",e)
        flash("입고 이력이 없습니다.")
        if str(scan_in_OR_out) == 'in' :
          title1 = "입고"
        else:
          title1 = "출고"
        return render_template("scanner.html",in_OR_out = scan_in_OR_out, title=title1, scan_data0='undefined',scan_data1='undefined',scan_data2='undefined',scan_data3='undefined',scan_data4='undefined',scan_data5='A',dup='no')
      
      except NameError as e:
        print("!!OUT OK History QR !!",e)
        flash("출고 처리된 상품입니다.")
        if str(scan_in_OR_out) == 'in' :
          title1 = "입고"
        else:
          title1 = "출고"
        return render_template("scanner.html",in_OR_out = scan_in_OR_out, title=title1, scan_data0='undefined',scan_data1='undefined',scan_data2='undefined',scan_data3='undefined',scan_data4='undefined',scan_data5='A',dup='no')
      
      except Exception as e:
        print("!!Duplication QR!!",e)                                                                                       # Fail Insert
        if str(scan_in_OR_out) == 'in' :
          title1 = "입고"
        else:
          title1 = "출고"
        return render_template("scanner.html",in_OR_out = scan_in_OR_out, title=title1, scan_data0='undefined',scan_data1='undefined',scan_data2='undefined',scan_data3='undefined',scan_data4='undefined',scan_data5='A',dup='duplicate')
    
    if str(scan_in_OR_out) == 'in' :
      return render_template("scanner.html",in_OR_out = "in", title="입고", scan_data0='undefined',scan_data1='undefined',scan_data2='undefined',scan_data3='undefined',scan_data4='undefined',scan_data5='A',dup='no')
    elif str(scan_in_OR_out) == 'out' :
      return render_template("scanner.html",in_OR_out = "out", title="출고", scan_data0='undefined',scan_data1='undefined',scan_data2='undefined',scan_data3='undefined',scan_data4='undefined',scan_data5='A',dup='no')


if __name__ == "__main__":
    application.run(host='0.0.0.0')
    # application.run(debug=True)
    
