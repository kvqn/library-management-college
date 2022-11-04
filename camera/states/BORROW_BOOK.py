import logging
import db
import camera.vision as vision
import camera.utils as utils
import camera.interactables as interactables
import camera.states as states
import time


STUDENT : db.student.Student = None
TEXT_LOGGED_IN_AS : utils.Text = None
TEXT_ERROR : utils.Text = None
time_text_error_start = 0

# CART_MENU = interactables.AR_Menu(utils.Point(vision.SCREEN_WIDTH-300,100), scale=0.004)
CART_MENU = interactables.AR_Menu(utils.Point(vision.SCREEN_WIDTH-300,100))
CART_MENU.items = []

def func_confirm():
    logging.info("confirming borrow")
    for i in CART_MENU.items:
        db.transactions.BorrowBook(i.id, STUDENT.id)
    CART_MENU.buttons.clear()
    vision.set_state(states.BORROW_INVOICE, books = CART_MENU.items.copy(), student = STUDENT)
    CART_MENU.items.clear()
    
BUTTON_CONFIRM = interactables.AR_Button.Create(vision.SCREEN_WIDTH - 350, vision.SCREEN_HEIGHT - 80, "Confirm", 0.03, utils.Color.GREEN, action=utils.Action(func_confirm), detection_thickness = 0.02)

def func_cancel():
    logging.info("cancel borrow")
    CART_MENU.buttons.clear()
    CART_MENU.items.clear()
    vision.set_state(states.WAITING_FOR_COMMAND, student = STUDENT)

BUTTON_CANCEL = interactables.AR_Button.Create(vision.SCREEN_WIDTH - 150, vision.SCREEN_HEIGHT - 80, "Cancel", 0.03, utils.Color.RED, action=utils.Action(func_cancel), detection_thickness = 0.02)

def cart_add(book_id : int):
    global TEXT_ERROR
    global time_text_error_start
    if db.books.checkIfCanBeBorrowed(book_id):
        if db.transactions.checkIfAlreadyBorrowed(book_id, STUDENT.id):
            TEXT_ERROR = interactables.Text(utils.Point(20,vision.SCREEN_HEIGHT-20), 0.02, f"Book {book_id} is already borrowed", utils.Color.ORANGE, 2)
            time_text_error_start = time.time()
        else:
            book = db.books.FetchFromDatabase(book_id)
            CART_MENU.items.append(book)
            CART_MENU.add_button(book.name, utils.Action(cart_remove, (book,)))
    else:
        TEXT_ERROR = interactables.Text(utils.Point(20,vision.SCREEN_HEIGHT-20), 0.02, f"Book {book_id} is not available", utils.Color.RED, 2)
        time_text_error_start = time.time()

def cart_remove(book : db.books.Book):
    CART_MENU.items.remove(book)
    for i in range(len(CART_MENU.buttons)):
        if CART_MENU.buttons[i].text.text == book.name:
            CART_MENU.buttons.pop(i)
            return
    

def setup(student : db.student.Student):
    logging.info("Setting state to BORROW_BOOK")
    global STUDENT
    STUDENT = student
    global TEXT_LOGGED_IN_AS
    TEXT_LOGGED_IN_AS = interactables.Text(utils.Point(20,20), 0.02, f"Logged in as {student.name}", utils.Color.BLUE, 2)
    vision.set_scan_hands(True)
    vision.set_scan_qr(True)

codes_on_screen = []

def post_process_hook(ctx : vision.Context):

    global TEXT_ERROR
    global time_text_error_start

    CART_MENU.process(ctx.hands)
    BUTTON_CONFIRM.process(ctx.hands)
    BUTTON_CANCEL.process(ctx.hands)
    
    CART_MENU.draw(ctx.frame)
    TEXT_LOGGED_IN_AS.draw(ctx.frame)
    BUTTON_CONFIRM.draw(ctx.frame)
    BUTTON_CANCEL.draw(ctx.frame)

    global codes_on_screen

    if TEXT_ERROR is not None:
        if time.time() - time_text_error_start > 2:
            TEXT_ERROR = None
        else:
            TEXT_ERROR.draw(ctx.frame)
    
    _codes_on_screen = []
    for _code in ctx.qr_codes:
        code = _code.data.decode("utf-8")
        for item in CART_MENU.items:
            if item.id == code:
                if code not in codes_on_screen:
                    TEXT_ERROR = interactables.Text(utils.Point(20,vision.SCREEN_HEIGHT-20), 0.02, f"Book {code} is already in cart", utils.Color.ORANGE, 2)
                    time_text_error_start = time.time()
                break
        else:
            cart_add(code)
        _codes_on_screen.append(code)
    codes_on_screen = _codes_on_screen.copy()

    
    