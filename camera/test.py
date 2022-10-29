import multiprocessing
import logging
import queue
import cv2
import time
import ctypes
import mediapipe
from enum import Enum
from pyzbar import pyzbar

mpHands = mediapipe.solutions.hands
mpDraw = mediapipe.solutions.drawing_utils
hands = mpHands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.1)

SCREEN_WIDTH = 0
SCREEN_HEIGHT = 0

class Context:
    def __init__(self, frame, frame_no, process_index):
        self.frame = frame
        self.frame_no = frame_no
        self.process_index = process_index
        self.qr_codes = []
        self.hands = []

class STATE(Enum):
    READY_FOR_INTERACTION = "READY_FOR_INTERACTION" # waiting to read barcode
    INVALID_STUDENT_ID = "INVALID_STUDENT_ID" # student id is not in database
    WAITING_COMMAND = "WAITING_COMMAND" # valid student id             
    BORROW_BOOK = "BORROW_BOOK"
    BOOK_CANT_BE_BORROWED = "BOOK_CANT_BE_BORROWED"
    BOOK_CAN_BE_BORROWED = "BOOK_CAN_BE_BORROWED"                         
    RETURN_BOOK = "BOOK_CANT_BE_RETURNED"                            
    BOOK_CANT_BE_RETURNED = "RETURN_BOOK"                          
    BOOK_CAN_BE_RETURNED = "BOOK_CAN_BE_RETURNED"


import camera.utils as utils
TEXT_READY_FOR_INTERACTION = utils.Text(utils.Point(200,100), 1, "Ready for interaction", utils.Color.ORANGE, 2)
TEXT_INVALID_STUDENT_ID = utils.Text(utils.Point(200,100), 1, "Invalid student id", utils.Color.RED, 2)
def process_frame(recv_queue, send_queue, stop_bool, SHOW_LANDMARKS, scan_qr, scan_hands):
    while True:
        with stop_bool.get_lock():
            if stop_bool.value:
                break
        ctx = recv_queue.get()

        # Mirror image
        ctx.frame = cv2.flip(ctx.frame, 1)

        with scan_qr.get_lock():
            _scan_qr = scan_qr.value
        
        with scan_hands.get_lock():
            _scan_hands = scan_hands.value
        
        if _scan_qr:
            ctx.qr_codes = pyzbar.decode(ctx.frame)
        
        if _scan_hands:
            ctx.hands = hands.process(cv2.cvtColor(ctx.frame, cv2.COLOR_BGR2RGB)).multi_hand_landmarks
            if SHOW_LANDMARKS and ctx.hands:
                for hand in ctx.hands:
                    mpDraw.draw_landmarks(ctx.frame, hand, mpHands.HAND_CONNECTIONS)

        send_queue.put(ctx)

def process_fps(frame):
    current_time = time.time()
    fps = 1/(current_time - process_fps.previous_times.get())
    process_fps.previous_times.put(current_time)
    frame = cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return frame




state = STATE.READY_FOR_INTERACTION 

def main(SHOW_FPS : bool, SHOW_LANDMARKS : bool, VIDEO_CAPTURE):

    process_fps.previous_times = queue.Queue()
    N_PROCESSES = 4
    for i in range(N_PROCESSES):
        process_fps.previous_times.put(time.time())
    
    global SCREEN_HEIGHT 
    global SCREEN_WIDTH
    global state

    logging.info("Starting camera")

    logging.debug("Creating video capture")
    # camera = cv2.VideoCapture(0)
    # camera = cv2.VideoCapture(1)
    # camera = cv2.VideoCapture("http://192.168.29.64:4747/video")
    camera = cv2.VideoCapture(VIDEO_CAPTURE)
    SCREEN_HEIGHT = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    SCREEN_WIDTH = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    logging.debug("created video capture")

    
    queues = []
    stop_bools = []
    processes = []

    frames_queue = multiprocessing.Queue()
    scan_qr = multiprocessing.Value(ctypes.c_bool, False)
    scan_hands = multiprocessing.Value(ctypes.c_bool, True)

    for i in range(N_PROCESSES):
        queues.append(multiprocessing.Queue())
        stop_bools.append(multiprocessing.Value(ctypes.c_bool, False))
        processes.append(multiprocessing.Process(target=process_frame, args=(queues[i], frames_queue, stop_bools[i], SHOW_LANDMARKS, scan_qr, scan_hands)))
        processes[i].start()

    logging.info("Launched Processes")

    for i in range(N_PROCESSES):
        queues[i].put(Context(camera.read()[1], i, i))
    
    processed_frames = {}
    next_frame = 0
    n_read_frames = 0
    window = "test"
    time_state_started = time.time()
    
    state = STATE.READY_FOR_INTERACTION

    import camera.interactables as interactables
    MENU_WAITING_FOR_COMMAND = interactables.AR_Menu(utils.Point(SCREEN_WIDTH/2, SCREEN_HEIGHT/2), 0.1)

    def ACTION_BORROW_BOOK_WAITING():
        # global state
        # state = STATE.BORROW_BOOK
        # with scan_qr.get_lock():
        #     scan_qr.value = True
        # with scan_hands.get_lock():
        #     scan_hands.value = False
        print("borrow")
        
    MENU_WAITING_FOR_COMMAND.add_button(
        text = "Borrow",
        action = utils.Action(ACTION_BORROW_BOOK_WAITING, ())
    )   

    def ACTION_RETURN_BOOK_WAITING():
        # global state
        # state = STATE.RETURN_BOOK
        # with scan_qr.get_lock():
        #     scan_qr.value = True
        # with scan_hands.get_lock():
        #     scan_hands.value = False
        print("return")
    
    MENU_WAITING_FOR_COMMAND.add_button(
        text = "Return",
        action = utils.Action(ACTION_RETURN_BOOK_WAITING, ())
    )

    state = STATE.WAITING_COMMAND
    
    while True:
        ctx = None

        if next_frame in processed_frames:
            ctx = processed_frames[next_frame]
            del processed_frames[next_frame]
            next_frame+=1
        else:
            ctx = frames_queue.get()
            queues[ctx.process_index].put(Context(camera.read()[1], n_read_frames, ctx.process_index))
            n_read_frames+=1
            processed_frames[ctx.frame_no] = ctx
        
        if ctx is not None:
            logging.debug(f"Frame {ctx.frame_no}")
            
            match state:
                case STATE.READY_FOR_INTERACTION:
                    if ctx.qr_codes:
                        code = ctx.qr_codes[0]
                        print(code)
                        student_id = code.data.decode("utf-8")
                        state = STATE.WAITING_COMMAND
                        with scan_qr.get_lock():
                            scan_qr.value = False
                        with scan_hands.get_lock():
                            scan_hands.value = True
                        # check if valid
                        time_state_started = time.time()
                    else:
                        TEXT_READY_FOR_INTERACTION.draw(ctx.frame)

                case STATE.INVALID_STUDENT_ID:
                    if time.time() - time_state_started > 5:
                        time_state_started = time.time()
                    else:
                        TEXT_INVALID_STUDENT_ID.draw(ctx.frame)
                    
                case STATE.WAITING_COMMAND:
                    MENU_WAITING_FOR_COMMAND.draw(ctx.frame)
                    MENU_WAITING_FOR_COMMAND.process(ctx.hands)
                    


            if SHOW_FPS:
                ctx.frame = process_fps(ctx.frame)
            cv2.imshow(window, ctx.frame)
            key = cv2.waitKey(1)
            if key == ord('q'):
                logging.info("Quitting")
                for i in range(N_PROCESSES):
                    with stop_bools[i].get_lock():
                        stop_bools[i].value = True
                
                for p in processes:
                    p.terminate()
                    # p.join()
                
                cv2.destroyAllWindows()
                logging.info("Exited")
                break
                
            

        
        




        