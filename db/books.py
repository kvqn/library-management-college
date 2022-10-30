# Access module for the books.db database
from . import cur

def CreateTableIfNotExist():
    cur.execute(
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
    cur.execute(f"INSERT INTO BOOKS VALUES ({book.id}, '{book.name}', '{book.author}', {book.total_count}, {book.available_count})")

def FetchFromDatabase(id : int):
    cur.execute(f"SELECT * FROM BOOKS WHERE id = {id}")
    if cur.rowcount == 0:
        return None
    data = cur.fetchone()
    return Book(data[0], data[1], data[2], data[3], data[4])

def checkIfCanBeBorrowed(id : int):
    cur.execute(f"SELECT count(*) FROM BOOKS WHERE id = {id} and available_count > 0")
    return cur.fetchone()[0] == 1 

def reduceAvailableCount(id : int):
    cur.execute(f"UPDATE BOOKS SET available_count = available_count - 1 WHERE id = {id}")

def increaseAvailableCount(id : int):
    cur.execute(f"UPDATE BOOKS SET available_count = available_count + 1 WHERE id = {id}")