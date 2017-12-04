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
Modified Date: 12/3/2017
Scott.ai final project draft version
'''

from flask import Flask, render_template, request, flash, redirect, url_for, session
import os, sys
import MySQLdb
from helper import *
import dbconn2

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
    # note that right now, this does not check for a 'good' password
    # (with minimum # of characters, for example), but will be implemented
    password = request.form['password']

    # call helper function to create account by checking
    # if the input is valid and writing to the database
    desc = create_account(name, username, password)

    flash(desc[0]) #flash the return message

    # if sign-up is successful
    if desc[1] == 1:

      # extract userId and store locally, to be used as session
      userId = desc[2]

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
    desc = helper_login(username, password)

    flash(desc[0]) #flash return message

    # if login is successful
    if desc[1] == 1:

      # extract userId and store locally, to be used as session
      userId = desc[2]

      #create a new session
      session['userId'] = userId

      # since user has alreday created account before, go directly to topics page
      return redirect(url_for('topic'))

    else: #remain on sign up page if not successful
      return redirect(url_for('signup'))


''' Onboarding survey to get user's basic information. This page
will be accessed following whenever a user creates a new account,
but can also be existed later on whenever the user clicks the 'profile'
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

            data = get_profile(userId) #get profile data, if any
            options = get_options(data['yearsLearned'])
            # render template and fill in user's profile data
            return render_template('survey.html', script=url_for('survey'), data=data, options = options)

        # submit changes to form
        elif request.method == 'POST':

            # pull data from fields
            birthday = request.form['birthday']
            yearsLearned = request.form['yearsLearned']
            nation = request.form['nation']
            lang = request.form['lang']

            # note that more questions will be added related to the
            # user's personal interests (favorite sports teams, hobbies, etc.)

            # call helper function to update or insert profile data into table
            create_profile(userId, birthday, yearsLearned, nation, lang)

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
        if request.method == "POST":
            category_id = request.form['form-id']
            return redirect(url_for('convo', id=category_id))
        return render_template('topic.html')
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
@app.route('/convo/<type>', methods =['POST', 'GET'])
def convo(type):

  # check if session in progress (user logged in)
  if 'userId' in session:

      if request.method == 'GET':

        #convert type to ID
        categories = {"school": 1, "food":2, "hobby":3}
        typeId = categories[type]

        #pull questions from database by type
        all_questions = get_questions(typeId)

        # TO DO:
        # start recording audio file once conversation is entered
        # show a timer for the duration of each conversation question
        # store audio filepath and timestamps in appropriate table (convos)
        # increment a user's points and time spent as appropriate

        # render template and fill with questions pulled from database
        return render_template('convo.html', all_questions = all_questions, script=(url_for("feedback")))

      # go to feedback page once user submits
      elif request.method == 'POST':
        if request.form['submit']=='submit':
          return redirect(url_for('feedback'))

  # redirect to home page if user not logged in
  else:
      return redirect(url_for('home'))


''' Feedback page shows user's progress thus far. This will render the
feedback page, whih displays their total time spent thus far and
number of points earned. From this page, the user can log out, or return
to the homepage, or (in the future) go back to the topics page. Again,
this page can only be accessed if a session is in progress.'''
@app.route('/feedback/', methods =['POST', 'GET'])
def feedback():

    # if a session is in progress
    if 'userId' in session:

        # extract userId
        userId = session['userId']

        if request.method == 'POST':

            # pull user profile (progress)
            result = get_feedback(userId)

            # render template with user's progress
            return render_template('feedback.html', feedback = result)

    # if no session in progress, redirect to home
    else:
        return redirect(url_for('home'))

if __name__ == '__main__':
  ''' main method'''
  # port = os.getuid()
  port = 9000 # hardcode port for now
  app.debug = True
  # Flask will print the port anyhow, but let's do so too
  print('Running on port '+str(port))
  app.run('0.0.0.0',port)
