# Mojia & Harshita
# final project

import sys
import MySQLdb
import dbconn2
from flask import flash

#Connects to the db
def getConn():
    DSN = dbconn2.read_cnf()
    DSN['db'] = 'mshen2_db'
    return dbconn2.connect(DSN)

#this should come from session
username = 'mshen2'

def create_profile(name, birthday, yearsLearned, nation, lang):
    #establish connection
	conn = getConn()
	curs = conn.cursor(MySQLdb.cursors.DictCursor)

	#check if profile exists
	curs.execute("select * from profile where useId = %s", [username])
    existing_profile = curs.fetchone()

    # update profile
	if existing_profile:
        sql = '''update profile
                 set birthday=%s, yearsLearned=%s, nation=%s, nativeLang=%s
                 where userId = %s'''
        data = (birthday, yearsLearned, nation, lang, str(username))
        curs.execute(sql, data)
        conn.commit()
		curs.close()
		conn.close()
        return ('Profile {username} updated'.format(username=username),1)
    # create profile
	else:
		sql = "insert into profile (birthday, yearsLearned, nation, nativeLang) VALUES (%s, %s, %s, %s)"
		data = (birthday, yearsLearned, nation, lang)
		curs.execute(sql, data)
		conn.commit()
		curs.close()
		conn.close()
		return ('''Profile {username} created.'''.format(username=username),1)

def feedback(id):
    pass

def new_convo(id):
    pass

def new_file(id):
    pass

def create_account(username, password):
	pass
	# check if user exists, and display error if account exists

	# otherwise, add username, password, name, etc to account table

def login(username, password):
	pass
	#check if user exists:
		# if so, check if passowrd matches
			#if true - return true (logs them in)

			#false - say incorrect password
		#say user does not exist -- link to create account
