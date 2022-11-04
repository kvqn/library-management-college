# Access module for the student.db database

import db

TABLE_NAME = "STUDENTS"

def CreateTableIfNotExist():
    db.cur.execute(
"""CREATE TABLE IF NOT EXISTS STUDENTS (
id integer primary key,
name text,
phone text,
branch text,
semester integer,
email text
)"""
    )

class Student:
    def __init__(self, id : int, name : str, phone : str, branch : str, semester : str, email : str):
        self.name = name
        self.id = id
        self.phone = phone
        self.branch = branch
        self.semester = semester
        self.email = email
    
    
def InsertIntoDatabase(student : Student):
    db.cur.execute(f"INSERT INTO {TABLE_NAME} VALUES ({student.id}, '{student.name}', '{student.phone}', '{student.branch}', {student.semester}, '{student.email}')")

def FetchFromDatabase(library_id : int):
    db.cur.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = {library_id}")
    data = db.cur.fetchone()
    if data is None:
        return None
    return Student(data[0], data[1], data[2], data[3], data[4], data[5])

def CheckIfInDatabase(id : int):
    db.cur.fetchall()
    db.cur.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = {id}")
    return len(db.cur.fetchall()) != 0 