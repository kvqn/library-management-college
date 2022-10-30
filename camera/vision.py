import multiprocessing
import logging
import queue
from tkinter import W
import cv2
import time
import ctypes
import mediapipe
from pyzbar import pyzbar
import threading
import db

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


class SmartVideoCapture(cv2.VideoCapture):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frame = None
        self.is_stopped = False
        self.thread = threading.Thread(target=self.refreshFrameLoop, args=())
        self.thread.start()

    def refreshFrameLoop(self):
        while True:
            if self.is_stopped:
                break
            self.frame = super().read()
    
    def read(self):
        while True:
            if self.frame is not None:
                return self.frame
    
    def stop(self):
        self.is_stopped = True
        self.thread.join()
    

state = None
time_state_started = time.time()
scan_qr = multiprocessing.Value(ctypes.c_bool, True)
scan_hands = multiprocessing.Value(ctypes.c_bool, False)

def set_state(new_state, **setup_args):
    global state
    global time_state_started
    state = new_state
    state.setup(**setup_args)
    time_state_started = time.time()

def set_scan_qr(value : bool):
    with scan_qr.get_lock():
        scan_qr.value = value

def set_scan_hands(value : bool):
    with scan_hands.get_lock():
        scan_hands.value = value

def main(SHOW_FPS : bool, SHOW_LANDMARKS : bool, VIDEO_CAPTURE):

    db.student.CreateTableIfNotExist()
    db.books.CreateTableIfNotExist()
    db.transactions.CreateTableIfNotExist()

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
    # camera = SmartVideoCapture("http://192.168.29.64:4747/video")
    # camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    camera = SmartVideoCapture(VIDEO_CAPTURE)
    SCREEN_HEIGHT = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    SCREEN_WIDTH = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    logging.debug("created video capture")
    logging.info(f"Screen Height = {SCREEN_HEIGHT}")
    logging.info(f"Screen Width = {SCREEN_WIDTH}")

    
    queues = []
    stop_bools = []
    processes = []

    frames_queue = multiprocessing.Queue()
    

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
    global time_state_started
    time_state_started = time.time()
    import camera.states.READY_FOR_INTERACTION as READY_FOR_INTERACTION
    state = READY_FOR_INTERACTION
    state.setup()
    
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
            
            state.post_process_hook(ctx)
                
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

    camera.stop()
                
            

        
        




        