# Access module for the student.db database

import sqlite3

conn = sqlite3.connect('databases/student.db')
cur = conn.cursor()

TABLE_NAME = "STUDENTS"

def CreateTableIfNotExist():
    cur.execute(
"""CREATE TABLE IF NOT EXISTS STUDENTS (
library_id integer primary key,
name text,
phone text,
branch text,
semester integer,
email text
)"""
    )
    conn.commit()
    
class Student:
    def __init__(self, library_id : int, name : str, phone : str, branch : str, semester : str, email : str):
        self.name = name
        self.library_id = library_id
        self.phone = phone
        self.branch = branch
        self.semester = semester
        self.email = email
    
    
def InsertIntoDatabase(student : Student):
    cur.execute(f"INSERT INTO {TABLE_NAME} VALUES ({student.library_id}, '{student.name}', '{student.phone}', '{student.branch}', {student.semester}, '{student.email}')")
    conn.commit()

def FetchFromDatabase(library_id : int):
    cur.execute(f"SELECT * FROM {TABLE_NAME} WHERE library_id = {library_id}")
    data = cur.fetchone()
    return Student(data[0], data[1], data[2], data[3], data[4], data[5])

def CheckIfInDatabase(library_id : int):
    cur.fetchall()
    cur.execute(f"SELECT * FROM {TABLE_NAME} WHERE library_id = {library_id}")
    return len(cur.fetchall()) != 0 