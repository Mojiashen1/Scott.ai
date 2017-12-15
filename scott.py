# Mojia & Harshita
# final project
# draft version
# Dec 14, 2017

# this file contains all the helper methods that app.py calls, and contains
# most of the code that will be communicating with the SQL servers to add or
# modify user data as necessary. 

import sys
import MySQLdb
import dbconn2
from flask import flash, json
import bcrypt, random

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

# get user infortion to give feedback. We are still deciding what to output from here
# @ params: userId
def get_user_data(userId):
    conn = getConn()
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute("select timeActive, points from profile where userId = %s", [userId])
    existing_profile = curs.fetchone()
    return existing_profile

# when a new conversation is started, a new convo is added to the convos
# table using the userId, audio filepath, categoryID, and user feedback. 
# the convoId auto-increments, and thus all other parameters are insered 
# into the table. 
def create_convo(categoryId, userId, audio_path, feedback):
    conn = getConn()
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    sql = "insert into convos (categoryId, userId, audio, feedback) VALUES (%s, %s, %s, %s)"
    data = (categoryId, userId, audio_path, feedback)
    curs.execute(sql, data)
    curs.execute('select convoId from convos where categoryId=%s and userId=%s', (categoryId, userId))
    return curs.fetchone()

# A random feedback message is generated in this helper method. The idea is that 
# in an actual implementation of the AI, the feedback will be 'smart', and will
# critique the user's grammar or pronounciation. For this use case, the feedback
# is just hard coded.  
def create_feedback(userId, audio_path):
    scores = ['GREAT WORK! You can start to challenge yourself more on the diversity of your vocabulary.',
    'GOOD IMPROVEMENT ON THE ACCENT, WAY TO GO',
    'GREAT! Try to pay more attention to your past tenses.',
    'THANKS FOR CHATTING WITH ME! I love chatting with you.',
    'You are sounding like a native now!']
    return scores[random.randint(0,len(scores)-1)]

# pulls the feedback message for a particular user using the convoId and userId, 
# and returns the message.
def get_feedback(convoId, userId):
    conn = getConn()
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute("select feedback from convos where convoId = %s and userId = %s", (convoId, userId))
    return curs.fetchone()

# get a list of questions to ask the user based on the category of questions selected
# @ params: category type
def get_questions(type):
    conn = getConn()
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute("select questionText from AI where categoryId = %s", [type])
    results = curs.fetchall()

    all_questions = []
    #take out the questionText from objects into an array to return
    for question in results:
        all_questions.append(question['questionText'])
    return all_questions

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

# In order to implement the gamification element of this application,
# a point system is used to show users how much time they've spent on the
# app, and thereby also how many points they've earned. This increments
# the total points of a user depdending on the amount of time they had spent
# in a single conversation. 
def increment_point_time(userId, time_spent):
    conn = getConn()
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute("select points, timeActive from profile where userId = %s", [userId])
    existing_data = curs.fetchone()

    # update profile
    if existing_data:
        sql = '''update profile
        set points=%s, timeActive=%s
        where userId = %s'''
        points = int(int(existing_data['points']) + time_spent*10)
        timeActive = int(int(existing_data['timeActive']) + time_spent)
        curs.execute(sql, (int(points), int(timeActive), userId))

        curs.execute("select points, timeActive from profile where userId = %s", [userId])
        existing_data = curs.fetchone()
        conn.commit()
        curs.close()
        conn.close()
        return 1 #update successful
    return 0 #update failed

# This helper method returns all conversations a user has had, which is useful for the 
# progress page in our application, where all data for one user is shown. 
def get_convos(userId):
    conn = getConn()
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from convos inner join category using
    (categoryId) where userId = %s''', [userId])
    result = curs.fetchall()
    return result

# tihs is yet to be imlemented, but will take an audio input, and add it to the SQL database
# according to the userId and convoID, such that the audio can be retrieved later.
def get_audio():
    return None

# this helper function deletes an entry from the convos table givecn some convoID, and
# is meant to be used when the user is not happy with the audio recording for a 
# particular question.
def delete_audio(userId, convoId):
    conn = getConn()
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute("delete from convos where convoId = %s and userId = %s", (convoId, userId))
    result = curs.fetchone()
    if result:
        return 1 #delete successful
    return 0 #delete failed
