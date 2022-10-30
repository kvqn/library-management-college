import logging
import db
import camera.test as test
import camera.utils as utils
import camera.interactables as interactables
import camera.states as states


STUDENT : db.student.Student = None
TEXT_LOGGED_IN_AS : utils.Text = None

CART_MENU = interactables.AR_Menu(utils.Point(400,200), scale=0.02)
CART_MENU.items = []

def func_confirm():
    logging.info("confirming borrow")
    for i in CART_MENU.items:
        print(i)
    CART_MENU.buttons.clear()
    CART_MENU.items.clear()
    test.set_state(states.WAITING_FOR_COMMAND, student = STUDENT)
    
BUTTON_CONFIRM = interactables.AR_Button.Create(400, 400, "Confirm", 0.02, utils.Color.GREEN, action=utils.Action(func_confirm), detection_thickness = 0.02)

def func_cancel():
    logging.info("cancel books")
    CART_MENU.buttons.clear()
    CART_MENU.items.clear()
    test.set_state(states.WAITING_FOR_COMMAND, student = STUDENT)

BUTTON_CANCEL = interactables.AR_Button.Create(500, 400, "Cancel", 0.02, utils.Color.RED, action=utils.Action(func_cancel), detection_thickness = 0.02)

def cart_add(book_id : int):
    CART_MENU.items.append(book_id)
    CART_MENU.add_button(str(book_id), utils.Action(cart_remove, (book_id,)))

def cart_remove(book_id : int):
    CART_MENU.items.remove(book_id)
    for i in range(len(CART_MENU.buttons)):
        if CART_MENU.buttons[i].text.text == str(book_id):
            CART_MENU.buttons.pop(i)
            return
    

def setup(student : db.student.Student):
    global STUDENT
    STUDENT = student
    global TEXT_LOGGED_IN_AS
    TEXT_LOGGED_IN_AS = interactables.Text(utils.Point(200,100), 0.04, f"Logged in as {student.name}", utils.Color.WHITE, 2)
    test.set_scan_hands(True)
    test.set_scan_qr(True)

def post_process_hook(ctx : test.Context):

    CART_MENU.process(ctx.hands)
    BUTTON_CONFIRM.process(ctx.hands)
    BUTTON_CANCEL.process(ctx.hands)
    
    CART_MENU.draw(ctx.frame)
    TEXT_LOGGED_IN_AS.draw(ctx.frame)
    BUTTON_CONFIRM.draw(ctx.frame)
    BUTTON_CANCEL.draw(ctx.frame)
    if ctx.qr_codes:
        for _code in ctx.qr_codes:
            code = int(_code.data.decode("utf-8"))
            if code not in CART_MENU.items:
                cart_add(code)

    
    