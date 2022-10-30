import camera.vision as vision
import logging
import db
import camera.utils as utils
import camera.interactables as interactables
import camera.states as states

STUDENT : db.student.Student = None
TEXT_WELCOME_STUDENT : utils.Text = None
MENU = interactables.AR_Menu(utils.Point(100,200))

def func_borrow_book():
    logging.info("borrow book")
    vision.set_state(states.BORROW_BOOK, student = STUDENT)
    
def func_return_book():
    logging.info("return book")
    vision.set_state(states.RETURN_BOOK, student = STUDENT)
   
def func_exit():
    vision.set_state(states.READY_FOR_INTERACTION)

MENU.add_button("Borrow Book", utils.Action(func_borrow_book))
MENU.add_button("Return Book", utils.Action(func_return_book))
MENU.add_button("Exit", utils.Action(func_exit))

def setup(student : db.student.Student):
    logging.info("Setting up stage WAITING_FOR_COMMAND")
    global STUDENT 
    global TEXT_WELCOME_STUDENT 
    STUDENT = student
    vision.set_scan_hands(True)
    vision.set_scan_qr(False)
    TEXT_WELCOME_STUDENT = interactables.Text(utils.Point(20,80), 0.04, f"Welcome {student.name}", utils.Color.BLUE, 4)
    
def post_process_hook(ctx : vision.Context):
    MENU.draw(ctx.frame)
    MENU.process(ctx.hands)
    TEXT_WELCOME_STUDENT.draw(ctx.frame)


__all__ = ["setup", "post_process_hook"]