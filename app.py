# Mojia & Harshita
# final project

from flask import Flask, render_template, request, flash, redirect, url_for
import os, sys
import MySQLdb
from helper import *
import dbconn2

app = Flask(__name__)
app.secret_key = 'youcantguessthisout'

@app.route('/', methods =['POST', 'GET'])
def home():
    return render_template('index.html')

#harshita
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
      print ("IN SUBMIT")
      desc = create_account(name, username, password)

    elif request.form['submit']=='login':
      print ("IN ELIF")
      desc = login(username, password)

    print (desc[0])

    if desc[1] == 1: #if user added/logged-in, go to onboarding page
      return redirect(url_for('signup')) #CHANGE TO GO TO ONBOARDING PAGE

    else: #remain on sign up page if not successful
      return redirect(url_for('signup'))

# onboarding survey asking for user's basic information
@app.route('/survey/', methods =['POST', 'GET'])
def survey():
    pass

# select topic
@app.route('/topic/', methods =['POST', 'GET'])
def topic():
    if request.methods == "POST":
        category_id = request.form['form-id']
        return redirect(url_for('convo', id=category_id)) #user id?
    return render_template('topic.html')

#start a new convo
@app.route('/convo/<id>', methods =['POST', 'GET'])
def convo(id):
    if request.methods == 'POST':
        #sessionid?
        answer = new_file(id) # start a new audio file, return a file path
        new_convo(id, answer) #create a new convo with the selected topic, and audio file
        return redirect(url_for('feedback', id = session_id)) #maybe not session_id, we need to retrieve the most recent convo to a user
    return render_template('convo.html')

#feedback page
@app.route('/feedback/<id>', methods =['POST', 'GET'])
def feedback(id):
    if request.methods == 'POST':
        return redirect(url_for('topic'))
    result = feedback(id)
    return render_template('feedback.html', feedback = result)

if __name__ == '__main__':
  ''' main method'''
  # port = os.getuid()
  port = 8000
  app.debug = True
  # Flask will print the port anyhow, but let's do so too
  print('Running on port '+str(port))
  app.run('0.0.0.0',port)
