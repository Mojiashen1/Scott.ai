# Mojia & Harshita
# final project
# draft version
# Dec 3, 2017
# this file contains all the helper methods that app.py calls

import sys
import MySQLdb
import dbconn2
from flask import flash, json
import bcrypt

# Connects to the db
def getConn():
    DSN = dbconn2.read_cnf()
    DSN['db'] = 'scottai_db'
    return dbconn2.connect(DSN)

# Create a user profile if the user propile doesn't exist.
# if profile already exists, update user profile
# @ params: userId, birthdate, #years learning language, nationality, native language
def create_profile(userId, birthday, yearsLearned, nation, lang):
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
                return 'Profile successfully updated'

   # create profile if profile doesn't already exist
	else:
		sql = "insert into profile (userId, birthday, yearsLearned, nation, nativeLang) VALUES (%s, %s, %s, %s, %s)"
		data = (userId, birthday, yearsLearned, nation, lang)
		curs.execute(sql, data)
		conn.commit()
		curs.close()
		conn.close()
		return 'Profile successfully created'

# create an account for user if account doesn't exist
# if account exist, flash error message
# @ params: name, username, password
def create_account(name, username, password):
	conn = getConn()
	curs = conn.cursor(MySQLdb.cursors.DictCursor)

	if name and username and password:
		#check if user exists (log in)
		curs.execute("select * from account where username = %s", [username])
		other_account = curs.fetchone()

		if other_account:
            # we will update this later so it redirect to the login page
			return ('''User {username} already exists. Please log in.'''.format(username=username),0, '')
            #0 means login not successful

		else:
			#if user does not exist, insert into table (sign up)

			#encrypt password
			password = password.encode('utf-8')
			hashed = bcrypt.hashpw(password, bcrypt.gensalt())

			sql = "insert into account (name, username, password) VALUES (%s, %s, %s)"
			data = (name, username, hashed)
			curs.execute(sql, data)
			conn.commit()

			#pull user Id from account in order to start session
			curs.execute("select * from account where username = %s", [username])
			userId = curs.fetchone()['userId']
			curs.close()
			conn.close()
			return ('''User {username} created.'''.format(username=username),1, userId)
            # pass back userId to start session
            # 1 means log in successful
	else:
		return ("Form Incomplete. Please try again.", 0, '')

# helper function to check if password matches that in account database
# if password match, log user in, else, flash error
# @ params: username, password
def helper_login(username, password):
	conn = getConn()
	curs = conn.cursor(MySQLdb.cursors.DictCursor)

    # find user in the database
	curs.execute("select * from account where username = %s", [username])
	other_account = curs.fetchone()

    # if account exist, check if password is right
	if other_account:
		hashedPassword = other_account['password'].encode('utf-8')

		if bcrypt.hashpw(password.encode('utf-8'), hashedPassword) == hashedPassword:
			return ('''Success, {username} logged in.'''.format(username=username),1, other_account['userId'])
            # 1 means login sucessful
		else:
			return ("Password does not match. Please try again.", 0, '')
            # 0 means login failed
	else:
        # if user doesn't exist, create an account
		return ('''User {username} does not exist. Please create an account. '''.format(username=username),0, '')

# get user profile
# if profile already exists, return the profile to populate the form
# if profile doesn't exists, return None
# @ params: userId
def get_profile(userId):
    conn = getConn()
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from profile where userId = %s', [userId])
    existing_profile = curs.fetchone()
    conn.commit()
    curs.close()
    conn.close()
    return existing_profile

# !!! this is not implemented yet !!!
# get user infortion to give feedback. We are still deciding what to output from here
# @ params: userId
def get_feedback(id):
    conn = getConn()
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute("select * from profile where userId = %s", [id])
    existing_profile = curs.fetchone()
    #pull data from convos table
    #maybe, amount of time recorded on audio
    #append that data to results
    return existing_profile

# get a list of questions to ask the user based on the category of questions selected
# @ params: category type
def get_questions(type):
	conn = getConn()
	curs = conn.cursor(MySQLdb.cursors.DictCursor)

	curs.execute("select * from AI where categoryId = %s", [type])
	results = curs.fetchall()
	return results

# helper function to get all the options to display the form field years learned english
# this default to the option the user has selected in the past
# @ params: #years learned english
def get_options(data):
    all_options = ['1', '2', '3', '4', '5', 'more than 5, but less than 10', 'more than 10']
    index = 0
    if data != '':
        for i in range(len(all_options)):
            if all_options[i] == str(data):
                index = i
    return (all_options, index)

def increment_point_time(userId, time_spent):
    conn = getConn()
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute("select points, timeActive from profile where userId = %s", [userId])
    existing_data = curs.fetchone()
    print(existing_data)

    # update profile
    if existing_data:
        sql = '''update profile
        set points=%s, timeActive=%s
        where userId = %s'''
        points = int(existing_data[0] + time_spent*10)
        timeActive = int(existing_data[1] + time_spent)
        curs.execute(sql, (points, timeActive))
        conn.commit()
        curs.close()
        conn.close()
        return 1 #update successful
    return 0 #update failed
