import camera.test as test
import camera.utils as utils
import db
import logging
import camera.states as states

TEXT_READY_FOR_INTERACTION = utils.Text(utils.Point(200,100), 0.05, "Ready for interaction", utils.Color.ORANGE, 2)

def setup():
    logging.info("Setting up stage READY_FOR_INTERACTION")
    test.set_scan_qr(True)
    test.set_scan_hands(False)

def post_process_hook(ctx : test.Context):
    if ctx.qr_codes:
        code = ctx.qr_codes[0]
        logging.info(code)
        student_id = code.data.decode("utf-8")
        student = db.student.FetchFromDatabase(student_id)
        if student is not None:
            test.set_state(states.WAITING_FOR_COMMAND, student = student)
        else:
            test.set_state(states.INVALID_STUDENT)
    else:
        TEXT_READY_FOR_INTERACTION.draw(ctx.frame)

__all__ = ["setup", "post_process_hook"]