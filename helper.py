# Mojia & Harshita
# final project

import sys
import MySQLdb
import dbconn2
from flask import flash

#Connects to the db
def getConn():
    DSN = dbconn2.read_cnf()
    DSN['db'] = 'scottai_db'
    return dbconn2.connect(DSN)

#this should come from session
userId = 1

def create_profile(birthday, yearsLearned, nation, lang):
    #establish connection
	conn = getConn()
	curs = conn.cursor(MySQLdb.cursors.DictCursor)

	#check if profile exists
	curs.execute("select * from profile where userId = %s", [userId])
        existing_profile = curs.fetchone()

    # update profile
	if existing_profile:
                sql = '''update profile
                 set birthday=%s, yearsLearned=%s, nation=%s, nativeLang=%s
                 where userId = %s'''
                data = (birthday, yearsLearned, nation, lang, str(userId))
                curs.execute(sql, data)
                conn.commit()
                curs.close()
                conn.close()
                return 'Profile update'
    # create profile
	else:
		sql = "insert into profile (userId, birthday, yearsLearned, nation, nativeLang) VALUES (%s, %s, %s, %s, %s)"
		data = (userId, birthday, yearsLearned, nation, lang)
		curs.execute(sql, data)
		conn.commit()
		curs.close()
		conn.close()
		return 'Profile created'

def get_profile():

	conn = getConn()
	curs = conn.cursor(MySQLdb.cursors.DictCursor)

	#check if profile exists

	curs.execute('select * from profile where userId = %s', [userId])
        existing_profile = curs.fetchone()
        print (existing_profile)
        conn.commit()
        curs.close()
        conn.close()
        return existing_profile

def feedback(id):
	curs.execute("select * from profile where userId = %s", [userId])
        existing_profile = curs.fetchone()
        print existing_profile

	#pull data from convos table
	#maybe, amount of time recorded on audio
	#append that data to results

	return existing_profile

def get_questions(type):
	#establish connection
	conn = getConn()
	curs = conn.cursor(MySQLdb.cursors.DictCursor)

	curs.execute("select * from AI where categoryId = %s", [type])
	results = curs.fetchall()
	print (results)
	return results

def new_convo(id):
    pass

def new_file(id):
    pass

def create_account(name, username, password):
	#establish connection
	conn = getConn()
	curs = conn.cursor(MySQLdb.cursors.DictCursor)

	if name and username and password:
		#check if user exists (log in)

		curs.execute("select * from account where username = %s", [username])
		other_account = curs.fetchone()

		if other_account:
			return ('''User {username} already exists. Please try again.'''.format(username=username),0)

		else:
			#if user does not exist, insert into table (sign up)

			#encrypt password
			password = password.encode('ascii')

			sql = "insert into account (name, username, password) VALUES (%s, %s, %s)"
			data = (name, username, password)
			curs.execute(sql, data)
			conn.commit()

			#pull user Id

			curs.execute("select * from account where username = %s", [username])
			userId = curs.fetchone()['userId']

			curs.close()
			conn.close()
			return ('''User {username} created.'''.format(username=username),1, userId)
	else:
		return ("Form Incomplete. Please try again.")

def login(username, password):
	conn = getConn()
	curs = conn.cursor(MySQLdb.cursors.DictCursor)

	#encode password
	password = password.encode('ascii')

	curs.execute("select * from account where username = %s", [username])
	other_account = curs.fetchone()

	if other_account:
		curs.execute("select * from account where password = %s", [password])

		found_account = curs.fetchone()

		if found_account:
			if found_account['password']==password:
				#success
				return ('''Success, {username} logged in.'''.format(username=username),1, found_account['userId'])
			else:
				return ("Password does not match. Please try again.", 0)
		else:
			return ("Password does not match. Please try again.", 0)
	else:
		return ('''User {username} does not exist. Please try again. '''.format(username=username),0)
