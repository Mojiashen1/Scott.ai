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

def create_account(username, password):
	# check if user exists, and display error if account exists

	# otherwise, add username, password, name, etc to account table

def login(username, password):
	#check if user exists:
		# if so, check if passowrd matches
			#if true - return true (logs them in)

			#false - say incorrect password
		#say user does not exist -- link to create account
