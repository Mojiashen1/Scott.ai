# Mojia & Harshita
# final project

from flask import Flask, render_template, request, flash, redirect, url_for, session
# from flask.ext.session import Session
import os, sys
import MySQLdb
from helper import *
import dbconn2

# userId = 0

app = Flask(__name__)
app.secret_key = 'youcantguessthisout'
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
# Session(app)

# make all sessions persistent until logout
@app.before_request
def make_session_permanent():
    session.permanent = True

# landing page
@app.route('/', methods =['POST', 'GET'])
def home():
    return render_template('index.html')

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
    desc = ""

    if request.form['submit']=='signup':
      desc = create_account(name, username, password)

    elif request.form['submit']=='login':
      desc = login(username, password)

    print desc

    flash(desc[0])

    # SUCCESFUL LOGIN/SIGN UP
    if desc[1] == 1: # if user added/logged-in, go to onboarding page
      userId = desc[2] # extract userId and store locally (will change)
      
      #create a new session 
      session['userId'] = userId

      if request.form['submit']=='login':
        return redirect(url_for('topic'))

      else: 
        return redirect(url_for('survey'))

    else: #remain on sign up page if not successful
      return redirect(url_for('signup'))

# onboarding survey asking for user's basic information
@app.route('/survey', methods =['POST', 'GET'])
def survey():
    if 'userId' in session: 
        userId = session['userId']
        if request.method == 'GET':
            data = get_profile(userId)
            return render_template('survey.html', script=url_for('survey'), data=data)
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
    if request.method == "POST":
        category_id = request.form['form-id']
        return redirect(url_for('convo', id=category_id)) #user id?
    return render_template('topic.html')

#start a new convo
@app.route('/convo/<type>', methods =['POST', 'GET'])
def convo(type):
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
      return render_template('convo.html', all_questions = all_questions, script=(url_for("feedback", id=userId)))

    elif request.method == 'POST': #once they submit ?
      if request.form['submit']=='submit':
        return redirect(url_for('feedback', id=userId)) #user id?

#NOT DONE
#feedback page
@app.route('/feedback/<id>', methods =['POST', 'GET'])
def feedback(id):

  if request.method == 'POST':
    if 'userId' in session: 
        userId = session['userId']
        result = get_feedback(userId)
        return render_template('feedback.html', feedback = result, id=userId)

if __name__ == '__main__':
  ''' main method'''
  # port = os.getuid()
  port = 9000
  app.debug = True
  # Flask will print the port anyhow, but let's do so too
  print('Running on port '+str(port))
  app.run('0.0.0.0',port)
