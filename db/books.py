# Access module for the books.db database
import db

def CreateTableIfNotExist():
    db.cur.execute(
"""CREATE TABLE IF NOT EXISTS BOOKS (
id integer primary key,
name text,
author text,
total_count integer,
available_count integer
)"""
    )


class Book:
    def __init__(self, id : int, name : str, author : str, total_count : int, available_count : int):
        self.id = id
        self.name = name
        self.author = author
        self.total_count = total_count
        self.available_count = available_count

def InsertIntoDatabase(book : Book):
    db.cur.execute(f"INSERT INTO BOOKS VALUES ({book.id}, '{book.name}', '{book.author}', {book.total_count}, {book.available_count})")

def FetchFromDatabase(id : int):
    db.cur.execute(f"SELECT * FROM BOOKS WHERE id = {id}")
    if db.cur.rowcount == 0:
        return None
    data = db.cur.fetchone()
    return Book(data[0], data[1], data[2], data[3], data[4])

def checkIfCanBeBorrowed(id : int):
    db.cur.execute(f"SELECT count(*) FROM BOOKS WHERE id = {id} and available_count > 0")
    return db.cur.fetchone()[0] == 1 

def reduceAvailableCount(id : int):
    db.cur.execute(f"UPDATE BOOKS SET available_count = available_count - 1 WHERE id = {id}")

def increaseAvailableCount(id : int):
    db.cur.execute(f"UPDATE BOOKS SET available_count = available_count + 1 WHERE id = {id}")