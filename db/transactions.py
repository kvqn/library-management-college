# Access module for the transactions.db database

from . import cur
from datetime import datetime
import db.books as books
import logging

def CreateTableIfNotExist():
    cur.execute(
"""CREATE TABLE IF NOT EXISTS TRANSACTIONS (
transaction_id integer primary key auto_increment,
student_id integer,
book_id integer,
issue_datetime datetime,
return_datetime datetime,
FOREIGN KEY (student_id) REFERENCES STUDENTS(id),
FOREIGN KEY (book_id) REFERENCES BOOKS(id)
)"""
    )


class Transaction:
    def __init__(self, transaction_id : int, student_id : int, book_id : int, issue_datetime : datetime, return_datetime : datetime):
        self.transaction_id = transaction_id
        self.student_id = student_id
        self.book_id = book_id
        self.issue_datetime = issue_datetime
        self.return_datetime = return_datetime
    
    @staticmethod
    def FetchFromDatabase(transaction_id : int):
        cur.execute(f"SELECT * FROM TRANSACTIONS WHERE transaction_id = {transaction_id}")
        data = cur.fetchone()
        if data is None:
            return None
        return Transaction(data[0], data[1], data[2], datetime.strptime(data[3]), datetime.strptime(data[4]))

def BorrowBook(book_id : int, student_id : int):
    logging.info(f"Student {student_id} borrowed book {book_id}")
    cur.execute(f"insert into TRANSACTIONS(book_id, student_id, issue_datetime) values ({book_id}, {student_id}, '{datetime.now()}')")
    books.reduceAvailableCount(book_id)

def ReturnBook(book_id : int, student_id : int):
    logging.info(f"Student {student_id} returned book {book_id}")
    cur.execute(f"update TRANSACTIONS set return_datetime = '{datetime.now()}' where book_id = {book_id} and student_id = {student_id} and return_datetime is null order by issue_datetime asc limit 1")
    books.increaseAvailableCount(book_id)

def checkIfAlreadyBorrowed(book_id : int, student_id : int):
    cur.execute(f"select count(*) from TRANSACTIONS where book_id = {book_id} and student_id = {student_id} and return_datetime is null")
    return cur.fetchone()[0] == 1

def checkIfCanBeReturned(book_id : int, student_id : int):
    return checkIfAlreadyBorrowed(book_id, student_id)