# import mariadb
import mysql.connector as mariadb

conn = None
cur = None

def CreateConnection(user, password, database, server):
    global conn
    global cur
    conn = mariadb.connect(user=user, password=password, database=database, host=server)
    cur = conn.cursor()
    conn.autocommit = True

import db.student as student
import db.books as books
import db.transactions as transactions