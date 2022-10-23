# Access module for the books.db database
import sqlite3

conn = sqlite3.connect('books.db')
cur = conn.cursor()

def CreateTableIfNotExist():
    cur.execute(
"""CREATE TABLE IF NOT EXISTS BOOKS (
book_id integer primary key,
name text,
author text,
total_count integer,
available_count integer
)"""
    )


class Book:
    def __init__(self, book_id : int, name : str, author : str, total_count : int, available_count : int):
        self.book_id = book_id
        self.name = name
        self.author = author
        self.total_count = total_count
        self.available_count = available_count

    @staticmethod
    def FetchFromDatabase(book_id : int):
        cur.execute(f"SELECT * FROM BOOKS WHERE book_id = {book_id}")
        if cur.rowcount == 0:
            return None
        data = cur.fetchone()
        return Book(data[0], data[1], data[2], data[3], data[4])
    
def InsertIntoDatabase(book : Book):
    cur.execute(f"INSERT INTO BOOKS VALUES ({book.book_id}, '{book.name}', '{book.author}', {book.total_count}, {book.available_count})")
    conn.commit()