import logging
import camera.test as test
import camera.utils as utils
import time
import camera.states as states

TEXT_INVALID_STUDENT_ID = utils.Text(utils.Point(200,100), 0.05, "Invalid student id", utils.Color.RED, 2)

def setup():
    logging.info(f"Setting state to INVALID_STUDENT")
    test.set_scan_qr(False)
    test.set_scan_hands(False)

def post_process_hook(ctx : test.Context):
    if time.time() - test.time_state_started > 5:
        test.set_state(states.READY_FOR_INTERACTION)
    else:
        TEXT_INVALID_STUDENT_ID.draw(ctx.frame)

__all__ = ["setup", "post_process_hook"]