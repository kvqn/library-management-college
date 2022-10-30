# Access module for the transactions.db database

import sqlite3
from datetime import datetime

conn = sqlite3.connect('databases/transactions.db')
cur = conn.cursor()

def CreateTableIfNotExist():
    cur.execute(
"""CREATE TABLE IF NOT EXISTS TRANSACTIONS (
transaction_id integer primary key,
library_id integer,
book_id integer,
issue_datetime datetime,
return_datetime datetime,
FOREIGN KEY (library_id) REFERENCES STUDENTS(library_id),
FOREIGN KEY (book_id) REFERENCES BOOKS(book_id)
)"""
    )


class Transaction:
    def __init__(self, transaction_id : int, library_id : int, book_id : int, issue_datetime : datetime, return_datetime : datetime):
        self.transaction_id = transaction_id
        self.library_id = library_id
        self.book_id = book_id
        self.issue_datetime = issue_datetime
        self.return_datetime = return_datetime
    
    @staticmethod
    def FetchFromDatabase(transaction_id : int):
        cur.execute(f"SELECT * FROM TRANSACTIONS WHERE transaction_id = {transaction_id}")
        if cur.rowcount == 0:
            return None
        data = cur.fetchone()
        return Transaction(data[0], data[1], data[2], datetime.strptime(data[3]), datetime.strptime(data[4]))