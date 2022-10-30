import mariadb
conn = mariadb.connect(user='root', password='root', database='library')
cur = conn.cursor()
conn.autocommit = True
import db.student as student
import db.books as books
import db.transactions as transactions