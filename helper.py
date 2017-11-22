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
