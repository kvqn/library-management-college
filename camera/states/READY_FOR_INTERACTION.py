import camera.vision as vision
import camera.utils as utils
import db
import logging
import camera.states as states

TEXT_READY_FOR_INTERACTION = utils.Text(utils.Point(20,20), 0.02, "Ready for interaction", utils.Color.ORANGE, 2)

def setup():
    logging.info("Setting up stage READY_FOR_INTERACTION")
    vision.set_scan_qr(True)
    vision.set_scan_hands(False)

def post_process_hook(ctx : vision.Context):
    if ctx.qr_codes:
        code = ctx.qr_codes[0]
        logging.info(code)
        student_id = code.data.decode("utf-8")
        student = db.student.FetchFromDatabase(student_id)
        if student is not None:
            vision.set_state(states.WAITING_FOR_COMMAND, student = student)
        else:
            vision.set_state(states.INVALID_STUDENT)
    else:
        TEXT_READY_FOR_INTERACTION.draw(ctx.frame)

__all__ = ["setup", "post_process_hook"]