# Mojia & Harshita
# final project

import sys
import MySQLdb
import dbconn2
from flask import flash

#Connects to the db
def getConn():
    DSN = dbconn2.read_cnf()
    DSN['db'] = 'hyerramr_db'
    return dbconn2.connect(DSN)

def feedback(id):
    pass

def new_convo(id):
    pass

def new_file(id):
    pass

def create_account(name, username, password):
	#establish connection 
	conn = getConn()
	curs = conn.cursor(MySQLdb.cursors.DictCursor)

	#check if user exists (log in) 

	curs.execute("select * from account where username = %s", [username])
	other_account = curs.fetchone()

	if other_account:
		return ('''User {username} already exists. Please try again.'''.format(username=username),0)

	else:
		#if user does not exist, insert into table (sign up)
		sql = "insert into account (name, username, password) VALUES (%s, %s, %s)"
		data = (name, username, password)
		curs.execute(sql, data)
		conn.commit()
		curs.close()
		conn.close()
		return ('''User {username} created.'''.format(username=username),1)

def login(username, password):
	print ("IN LOGIN")

	conn = getConn()
	curs = conn.cursor(MySQLdb.cursors.DictCursor)

	curs.execute("select * from account where username = %s", [username])
	other_account = curs.fetchone()

	if other_account:
		curs.execute("select * from account where password = %s", [password])

		if curs.fetchone['password']==password:
			#success
			return ('''Success, {username} logged in.'''.format(username=username),1)

		else:
			return ("Password does not match. Please try again.", 0)
	else: 
		return ('''User {username} does not exist. Please try again. '''.format(username=username),0)
