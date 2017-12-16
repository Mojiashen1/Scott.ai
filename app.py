'''
This file contains the flask app which must be run in terminal
(using python app.py) to start the application in the broswer.
It contains methods that add functionality to all pages in the
web program, including the home page, sign-up, log-in, onboarding
survey, choose topics page, conversation with AI, and feedbacks page.
Helper functions from helper.py are used to pull necessary data from
the database. Sessions are used to remember users that login, and
log them out when they press log-out, to make this program easier to use.

Filename: app.py
Authors: Mojia & Harshita
Modified Date: 12/14/2017
Scott.ai final project alpha version
'''

from flask import Flask, render_template, request, flash, redirect, url_for, session
import os, sys
import MySQLdb
import dbconn2
from scott import *

app = Flask(__name__)
app.secret_key = 'youcantguessthisout'
SESSION_TYPE = 'redis'
app.config.from_object(__name__)


''' Make all sessions persistent until logout '''
@app.before_request
def make_session_permanent():
    session.permanent = True


''' Scott.ai landing page. Has places to sign in or sign up for the service. '''
@app.route('/', methods =['POST', 'GET'])
def home():
    return render_template('index.html')


'''  Logout page can be accessed from any page on the site after logging in.
If a session exists, this will quit the session. Then, the user will be
redirected to the home page, where they can sign in as a different user.'''
@app.route('/logout/', methods =['POST', 'GET'])
def logout():
  if 'userId' in session: #if a session exists, exit it
    session.pop('userId', None)
  return redirect(url_for('home')) #redirect to home once complete


''' Signup page has fields for user's name, username, and password.
All fields are required, and an account will be created if the username
does not already exist in the account table in the database.
If the input is not valid, remain on signup page and flash
a message telling user to try again.'''
@app.route('/signup/', methods =['POST', 'GET'])
def signup():

  # display form
  if (request.method == "GET"):
    return render_template('signup.html', script=(url_for("signup")))

  # once user adds information to create account
  elif (request.method == "POST"):

    # get information from form
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']

    # call helper function to create account by checking
    # if the input is valid and writing to the database
    message, success_message, userId = create_account(name, username, password)
    flash(message) #flash whether sign up is successful

    # if sign-up is successful
    if success_message == 1:
      # create a new session
      session['userId'] = userId
      # redirect user to onboarding page, since they are a new user
      return redirect(url_for('survey'))

    else: #remain on sign up page if not successful
      #we will also implement a check to see if the user entered an
      #existing username, to go to the login page instead of signup page
      return redirect(url_for('signup'))


''' Login page has fields for user's username and password.
All fields are required, and if the username exists in the databse and
has a matching password, the user will be logged in.
If the inputs are not valid (username does not exist or password does
not match), remain on login page and flash a message telling user to try again.'''
@app.route('/login/', methods =['POST', 'GET'])
def login():

  # display form
  if (request.method == "GET"):
    return render_template('login.html', script=(url_for("login")))

  # fetch information from the form
  elif (request.method == "POST"):
    # get information from form
    username = request.form['username']
    password = request.form['password'] #password is encrpyted in helper.py
    # call helper function to check if valid login
    message, success_message, userId = helper_login(username, password)

    flash(message) #flash return message

    # if login is successful
    if success_message == 1:
      #create a new session
      session['userId'] = userId
      # since user has alreday created account before, go directly to topics page
      return redirect(url_for('topic'))

    else: #remain on sign up page if not successful
      return redirect(url_for('signup'))


''' Onboarding survey to get user's basic information. This page
will be accessed following whenever a user creates a new account,
but can also be accessed later on whenever the user clicks the 'profile'
button on the navigation bar at any point in their use of the app.
Will only allow user to access this page if there is a session, otherwise
(if the user goes to the /survey/ webpage directly, not after signing in),
redirect to the home page. User's profile data is pulled from the databse
if it already exists, and is otherwise blank when account is first created.'''
@app.route('/survey/', methods =['POST', 'GET'])
def survey():
    # check if session already created (user logged in)
    if 'userId' in session:
        userId = session['userId'] # extract userId

        # generate survey form
        if request.method == 'GET':

            data = get_profile(userId)# get profile data, if any
            yearsLearned = data['yearsLearned'] if data else ''
            # return all the options and the index of the choice selected by the user
            options, index = get_options(yearsLearned)
            return render_template('survey.html', script=url_for('survey'), data=data, options=options, index=index)

        # submit changes to form
        elif request.method == 'POST':

            # pull data from fields
            birthday = request.form['birthday']
            yearsLearned = request.form['yearsLearned']
            nation = request.form['nation']
            lang = request.form['lang']

            # call helper function to update or insert profile data into table
            message = create_profile(userId, birthday, yearsLearned, nation, lang)
            flash(message)
            # once profile created/updated, redirect to topic page to start convo
            return redirect(url_for('topic'))

    # if no session created, redirect to home page
    else:
        return redirect(url_for('home'))


''' Topic page displays all possible topics that the user can
have a conversation with AI in. As of now, these topics are hard-coded,
but in the future, the topics can be generated by an intelligent AI,
where they are related to the user's interests as found in the
onboarding survey. Once a user selects a topic, they will be
redirected to a 'conversation' page with the AI based on the
topic selected. This page can only be accessed if there is a session
in progress, and otherwise the user is redirected to homepage.'''
@app.route('/topic/', methods =['POST', 'GET'])
def topic():
    if 'userId' in session:
        userId = session['userId'] # extract userId
        if request.method == "POST":
            category_id = request.form['categoryId']
            return redirect(url_for('convo', categoryId = category_id))
        elif request.method == "GET":
            return render_template('topic.html', script=(url_for('topic')))
    else:
        return redirect(url_for('home'))


''' Convo page allows user to have a conversation with the AI
such that they can practice their English skills. This takes
in as a parameter the conversation type, which is passed in by
the topic method above. This conversation type maps to
different topics (school, hobbies, food). In the final iteration,
the app will begin to record an audio file that stores all of the
user's answers, with a list of timestamps corresponding to the
time at which the user finishes answering each question (when
they click next). This file will be then uploaded to the database.
Here, the list of questions are pulled from the database using the
conversation type ID, and are passed into the template, where each
question is shown. Again, this only happens if a session is created --
otherwise, redirects to homepage'''
@app.route('/convo/<categoryId>', methods =['POST', 'GET'])
def convo(categoryId):

  # check if session in progress (user logged in)
  if 'userId' in session:
      userId = session['userId']
      if request.method == 'GET':
        #pull questions from database by type
        all_questions = get_questions(categoryId)
        #change the list of questions json format to send to the front end
        questions = json.dumps(all_questions)

        # convoId = create_convo(categoryId, userId)
        return render_template('convo.html', questions = questions, categoryId = categoryId,
                              script=(url_for('convo', categoryId = categoryId)))

      # go to feedback page once user finishes the conversation
    #   elif request.method == 'POST':
      else:
            print('inside convos post')
            audio_length = 1 # minutes of the new audio
            file = request.files['blob']
            # convoId = request.form['convoId']
            feedback = create_feedback(userId, file)
            print('this is feedbakc', feedback)
            #build url path for audiofile
            url_path = request.base_url
            convoId = create_convo(categoryId, userId, url_path, feedback)
            print('convoId', convoId)
            increment_point_time(userId, audio_length)
            print('done with everything, gonna redirect to feedbakc')
            # save_audio(convoId, userId, audio_url)
            # update_feedback(feedback, audio_path, convoId, userId)
            return redirect(url_for('feedback', convoId=convoId))
  # redirect to home page if user not logged in
  else:
      return redirect(url_for('home'))


''' Feedback page shows user's progress thus far. This will render the
feedback page, whih displays their total time spent thus far and
number of points earned. From this page, the user can log out, or return
to the homepage, or (in the future) go back to the topics page. Again,
this page can only be accessed if a session is in progress.'''
@app.route('/feedback/<convoId>', methods =['POST', 'GET'])
def feedback(convoId):
    # if a session is in progress
    if 'userId' in session:
        userId = session['userId']
        # pull user timeActive and points from profile using userId
        data = get_user_time_point(userId)
        # full feedback from database based on convoId
        feedback = get_feedback(convoId, userId)
        return render_template('feedback.html', data = data, feedback=feedback)

    # if no session in progress, redirect to home
    else:
        return redirect(url_for('home'))

''' This route gets any audio files that are posted to it
by the AJAX script after audio recording, and will call a
helper function in scott.py to take the file, and save it to the server
using the user ID and convoID. Not yet implemented.'''
# @app.route('/audiofile/<userId>/<convoId>/', methods = ['POST', 'GET'])
# def audiofile(userId, convoId):
#     if 'userId' in session:
#         print request.base_url
#         print "in audiofile"
#
#         # it actaully reaches this when end convo is clicked
#
#         # request.files is empty!!
#         print (request.files['blob'])
#
#         # not working yet
#         file = request.files['blob']
#
#         # file.save(secure_filename(f.filename))
#
#         save_audio(convoId, userId, file)
#
#         return ''
#     else:
#         print ("not in session!!")
#     return ''


''' The progress page shows the user's progress thus far when
using the app. It displays all conversations that the user has had in
chonrological order (most recent last), as well as the audio file (not
yet implmented), feedback message,  and an option to delete the entry
if the user finds something wrong with the audio file or their performance.
The userId is pulled from the session, and thus there are no other parameters
to this method. This is not fully implemented! (delete audio)'''
@app.route('/progress/', methods =['POST', 'GET'])
def progress():
    if 'userId' in session:
        userId = session['userId']
        # data is a dictionary of user's timeActive and points
        data = get_user_time_point(userId)
        points = data['points']
        # data is a list of a user's conversations
        convos = get_convos(userId)

        # when a user views the progress page: display information
        if request.method == 'GET':
            return render_template('progress.html',
            points=points,
            data=convos, script=url_for('progress'))

        # post request listens for delte button click
        elif request.method == 'POST':
            # extract matching convoId from form
            convoId = request.form['convoId']

            #delete using convo primary key
            delete_audio(convoId)
            print('it is deleted')

            # retrieve updated data
            data = get_convos(userId)

		    # re-render page with new data
            # since the convoId is guarenteed to be
            # in the database, there is no need to catch
            # user errors, as a matching data entry to the
            # table can always be found
            return render_template('progress.html',
                  points=points,
                  data=convos, script=url_for('progress'))

    # if no session in progress, redirect to home
    else:
        return redirect(url_for('home'))


if __name__ == '__main__':
  port = os.getuid()
  app.debug = True
  # Flask will print the port anyhow, but let's do so too
  print('Running on port ' + str(port))
  app.run('0.0.0.0',port, ssl_context='adhoc')
