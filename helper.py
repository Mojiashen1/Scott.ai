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
	# check if user exists, and display error if account exists

	# otherwise, add username, password, name, etc to account table

def login(username, password):
	pass
	#check if user exists:
		# if so, check if passowrd matches
			#if true - return true (logs them in)

			#false - say incorrect password
		#say user does not exist -- link to create account
