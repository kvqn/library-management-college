import logging
import camera.vision as vision
import camera.utils as utils
import db
from typing import List
import datetime
import time
import camera.states as states

BOOKS : List[db.books.Book] = None
STUDENT : db.student.Student = None
TEXT_LOGGED_IN_AS : utils.Text = None

TEXT_BORROW_INVOICE = utils.Text(utils.Point(vision.SCREEN_WIDTH*0.15,vision.SCREEN_HEIGHT*0.3), 0.05, "Borrow Invoice", utils.Color.ORANGE, 4)
TEXT_BOOKS = []
TEXT_RETURN_DATE : utils.Text = None

def setup(books : List[db.books.Book], student : db.student.Student):
    logging.info("Setting up stage BORROW_INVOICE")
    global BOOKS
    global STUDENT
    global TEXT_LOGGED_IN_AS
    BOOKS = books
    STUDENT = student
    TEXT_LOGGED_IN_AS = utils.Text(utils.Point(20,20), 0.02, f"Logged in as {student.name}", utils.Color.WHITE, 2)
    vision.set_scan_hands(False)
    vision.set_scan_qr(False)

    global TEXT_BOOKS
    TEXT_BOOKS = []
    for i in range(len(BOOKS)):
        TEXT_BOOKS.append(utils.Text(utils.Point(vision.SCREEN_WIDTH*0.20,vision.SCREEN_HEIGHT*0.40 + i * vision.SCREEN_HEIGHT*0.05), 0.02, BOOKS[i].name, utils.Color.WHITE, 2))
    
    global TEXT_RETURN_DATE
    TEXT_RETURN_DATE = utils.Text(utils.Point(150,vision.SCREEN_HEIGHT-100), 0.02, f"Return date: {(datetime.datetime.now() + datetime.timedelta(days=14)).date()}", utils.Color.WHITE, 2)

def post_process_hook(ctx : vision.Context):
    
    TEXT_LOGGED_IN_AS.draw(ctx.frame)
    TEXT_BORROW_INVOICE.draw(ctx.frame)
    TEXT_RETURN_DATE.draw(ctx.frame)
    for i in TEXT_BOOKS:
        i.draw(ctx.frame)
    
    if time.time() - vision.time_state_started > 5:
        vision.set_state(states.WAITING_FOR_COMMAND, student = STUDENT)
    
    