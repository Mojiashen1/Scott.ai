# Mojia & Harshita
# final project
# draft version
# Dec 3, 2017

from flask import Flask, render_template, request, flash, redirect, url_for, session
import os, sys
import MySQLdb
from helper import *
import dbconn2

# userId = 0

app = Flask(__name__)
app.secret_key = 'youcantguessthisout'
SESSION_TYPE = 'redis'
app.config.from_object(__name__)

# make all sessions persistent until logout
@app.before_request
def make_session_permanent():
    session.permanent = True

# landing page
@app.route('/', methods =['POST', 'GET'])
def home():
    return render_template('index.html')

# logout
@app.route('/logout/', methods =['POST', 'GET'])
def logout():
  if 'userId' in session:
    session.pop('userId', None)
  return redirect(url_for('home'))

# signup page
@app.route('/signup/', methods =['POST', 'GET'])
def signup():
  if (request.method == "GET"):
    return render_template('signup.html', script=(url_for("signup")))

  elif (request.method == "POST"):
    # get information from form
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']
    desc = create_account(name, username, password)

    flash(desc[0])

    # SUCCESFUL SIGN UP
    if desc[1] == 1: # if user added/logged-in, go to onboarding page
      userId = desc[2] # extract userId and store locally (will change)

      #create a new session
      session['userId'] = userId
      return redirect(url_for('survey'))

    else: #remain on sign up page if not successful
      return redirect(url_for('signup'))

# login page
@app.route('/login/', methods =['POST', 'GET'])
def login():
  if (request.method == "GET"):
    return render_template('login.html', script=(url_for("login")))

  elif (request.method == "POST"):
    # get information from form
    username = request.form['username']
    password = request.form['password']

    desc = helper_login(username, password)

    flash(desc[0])

    # SUCCESFUL LOGIN
    if desc[1] == 1: # if user added/logged-in, go to onboarding page
      userId = desc[2] # extract userId and store locally (will change)

      #create a new session
      session['userId'] = userId

      return redirect(url_for('topic'))

    else: #remain on sign up page if not successful
      return redirect(url_for('signup'))

# onboarding survey asking for user's basic information
@app.route('/survey/', methods =['POST', 'GET'])
def survey():
    if 'userId' in session:
        userId = session['userId']
        if request.method == 'GET':
            data = get_profile(userId)
            yearsLearned = data['yearsLearned'] if data else ''
            options = get_options(yearsLearned)
            print('option', options)
            return render_template('survey.html', script=url_for('survey'), data=data, options=options)
        elif request.method == 'POST':
            birthday = request.form['birthday']
            yearsLearned = request.form['yearsLearned']
            nation = request.form['nation']
            lang = request.form['lang']
            create_profile(userId, birthday, yearsLearned, nation, lang)
            return redirect(url_for('topic'))
    else:
        return redirect(url_for('home'))

# select topic
@app.route('/topic/', methods =['POST', 'GET'])
def topic():
    if 'userId' in session:
        if request.method == "POST":
            category_id = request.form['form-id']
            return redirect(url_for('convo', id=category_id))
        return render_template('topic.html')
    else:
        return redirect(url_for('home'))

#start a new convo
@app.route('/convo/<type>', methods =['POST', 'GET'])
def convo(type):
  if 'userId' in session:
      if request.method == 'GET':

        #convert type to ID
        categories = {"school": 1, "food":2, "hobby":3}
        typeId = categories[type]

        #pull questions from database by type
        all_questions = get_questions(typeId)
        print (all_questions);

        # store response in appropriate table
        # will do later with audio file
        # haven't set up convo id yet
        return render_template('convo.html', all_questions = all_questions, script=(url_for("feedback")))

      elif request.method == 'POST': #once they submit ?
        if request.form['submit']=='submit':
          return redirect(url_for('feedback')) #user id?
  else:
      return redirect(url_for('home'))

#NOT DONE
#feedback page
@app.route('/feedback/', methods =['POST', 'GET'])
def feedback():
    if 'userId' in session:
        userId = session['userId']
        if request.method == 'POST':
            result = get_feedback(userId)
            return render_template('feedback.html', feedback = result)
    else:
        return redirect(url_for('home'))

if __name__ == '__main__':
  ''' main method'''
  # port = os.getuid()
  port = 9000
  app.debug = True
  # Flask will print the port anyhow, but let's do so too
  print('Running on port '+str(port))
  app.run('0.0.0.0',port)
