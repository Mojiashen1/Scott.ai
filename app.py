# Mojia & Harshita
# final project

from flask import Flask, render_template, request, flash, redirect, url_for
import os, sys
import MySQLdb
import movie as movie
import dbconn2

app = Flask(__name__)

@app.route('/', methods =['POST', 'GET'])
def home():
    return render_template('index.html')

@app.route('/login/', methods =['POST', 'GET'])
def login():
    pass

app.secret_key = 'youcantguessthisout'

if __name__ == '__main__':
  app.debug == True
  port = os.getuid()
  app.run('0.0.0.0', port)
