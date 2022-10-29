from __future__ import annotations
from typing import List
from pyzbar import pyzbar
import cv2
from PIL import Image
import mediapipe
import time
import signal
from threading import Thread
import logging
import multiprocessing

mpHands = mediapipe.solutions.hands
mpDraw = mediapipe.solutions.drawing_utils
hands = mpHands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.1)

import camera.interactables as interactables
from camera.utils import Action, Color


class WebcamStream:
    
    objects = []    
    
    def __init__(self, video_capture):
        self.stream = video_capture
        self.stream.set(cv2.CAP_PROP_FPS, 30)
        self.ret , self.frame = self.stream.read()
        self.stopped = False
        WebcamStream.objects.append(self)
        # self.start()
        
    def start(self):
        Thread(target=self.update, args=()).start()
    
    def update(self):
        while True:
            # print("a")
            if self.stopped:
                return
            self.ret, self.frame = self.stream.read()
            cv2.flip(self.frame, 1, self.frame)
        
    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
    
    @staticmethod
    def StopAllStreams():
        for i in WebcamStream.objects:
            i.stop()

class Context:
    def __init__(self, frame, frame_no) :
        self.frame = frame
        self.frame_no = frame_no
        self.buttons = []
        self.menus = []
        self.qr_codes = []
        self.hands = []       
        self.process_id : int = 0

def process_context(putting_queue : multiprocessing.Queue, getting_queue : multiprocessing.Queue, process_id : int):
    
    while True:
        context = getting_queue.get()
        context.process_id = process_id

        # # Processing qr
        # context.qr_codes = pyzbar.decode(context.frame)
        
        # # Processing hands
        # context.hands = hands.process(context.frame).multi_hand_landmarks

        # if context.hands == None:
        #     context.hands = []

        # # Displaying hands landmarks
        # if context.hands:
        #     # print("hands")
        #     for hand in context.hands :
        #         # print(hand)
        #         mpDraw.draw_landmarks(context.frame, hand, mpHands.HAND_CONNECTIONS)
        
        
        # # Process buttons
        # for button in context.buttons:
        #     button.process()
        #     button.draw()
        
        # # Process menus
        # for menu in context.menus:
        #     menu.process()
        #     button.draw()

        putting_queue.put(context)



class Vision:
    """
    Processes:
        self.process_fps()
        self.process_hands()
    
    """
    # objects = []
    
    def __init__(self, video_capture):
        self.video_capture = video_capture
        self.height = self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.width = self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        
        self.webcam = WebcamStream(video_capture)
        self.ptime = 0
        self.ctime = 1
        self.stopped = False
        self.frame = None
        self.threads = []
        self.hands = None
        # Vision.objects.append(self)
        
        # self.window_name = "preview"+str(len(Vision.objects))
        
        self.buttons = []
        self.menus = []
        self.is_scanning_for_qr = False
        self.action_queue : List[Action]= []
        self.codes : List[pyzbar.Decoded]= []
        self.processes = []
        self.N_PROCESSES = 4
        self.processed_frames = dict()
        self.process_queues = []
        self.frames_queue = multiprocessing.Queue()
    
    def start(self):    
        self.ReadVideoCapture()
    
    def stop(self):
        self.stopped=True
        # self.barrier.abort()
        self.webcam.stop()
        cv2.destroyWindow(self.window_name)
    
    # @staticmethod
    # def StopAllVision():
    #     for i in Vision.objects:
    #         i.stop()
    
     
    # @staticmethod
    def process_fps(self) -> int:
        self.ctime = time.time()
        fps = 1/(self.ctime-self.ptime)
        self.ptime = self.ctime
        cv2.putText(self.frame, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
    
    # @staticmethod
    def process_hands(self):
        # Processing hands using some library
        self.hands = hands.process(self.frame).multi_hand_landmarks
        if self.hands == None:
            self.hands = []
    
        # Displaying hands landmarks
        if self.hands:
            # print("hands")
            for hand in self.hands :
                # print(hand)
                mpDraw.draw_landmarks(self.frame, hand, mpHands.HAND_CONNECTIONS)
    
    # @staticmethod
    def process_qr(self):
        self.codes = pyzbar.decode(self.frame)
    
    
    # Process input from a webcam as per requirement
    def ReadVideoCapture(self):
        
        
        logging.debug("Starting webcam thread")
        self.webcam.start()    
        logging.debug("Started webcam thread")
        
        
        logging.debug("Creating window")
        cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
        logging.debug("Created window")
               
        logging.info("Starting main loop")

        n_frame = 0
        next_frame = 0

        for i in range(self.N_PROCESSES):
            queue = multiprocessing.Queue()
            self.process_queues.append(queue)
            multiprocessing.Process(target=process_context, args=(self.frames_queue, queue, i)).start()
        
        for i in range(self.N_PROCESSES):
            self.process_queues[i].put(Context(self.webcam.read(), n_frame))
            n_frame += 1

        
        while True :

            context = None
            if next_frame in self.processed_frames:
                context = self.processed_frames[next_frame]
                del self.processed_frames[next_frame]
                
            else:
                logging.debug("getting frame from queue")
                context : Context = self.frames_queue.get()
                logging.debug(f"got {context.frame_no}")

                self.process_queues[context.process_id].put(Context(self.webcam.read(), n_frame))
                n_frame+=1

                if (context.frame_no != next_frame):
                    self.processed_frames[context.frame_no] = context
                    context = None
                else:
                    next_frame+=1
            
            if context:
                cv2.imshow(self.window_name, context.frame)
                key = cv2.waitKey(1)
                if key == ord('q') :
                    break

            
            # self.frame = self.webcam.read()
            # # print(ret)
            
            # # self.do_actions()
            # self.process_fps()
            # self.process_buttons()
            # self.process_menus()

            # self.process_qr()
            # if self.codes:
            #     print(self.codes)
            # self.process_hands()
            
            # self.draw()
            
            
            # cv2.imshow(self.window_name, self.frame)
            # key = cv2.waitKey(1)
            # if key == ord('q') :
            #     break
           
        
        self.stop()
        logging.info("Stopped main loop")
    
    def add_button(self, button : interactables.AR_Button):
        self.buttons.append(button)
        
    def add_menu(self, menu : interactables.AR_Menu):
        self.menus.append(menu)

    def process_buttons(self):
        for button in self.buttons:
            button.process()
    
    def process_menus(self):
        for menu in self.menus:
            menu.process()
    
        
    def draw(self):
        for button in self.buttons:
            button.draw()
        
        for menu in self.menus:
            menu.draw()
            
    def start_scanning_for_qr(self):
        self.is_scanning_for_qr = True
        
    def stop_scanning_for_qr(self):
        self.is_scanning_for_qr = False
    
    
    def InteruptHandler(self, signum, frame):
        print("Interupt")
        self.stop()
        # WebcamStream.StopAllStreams() 
        




        



def func():
    print("Button pressed !")

    
def main():
    
    logging.basicConfig(level=logging.DEBUG)
    
    # cv2.dnn.Net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    # cv2.dnn.Net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
    
    # video_capture = cv2.VideoCapture("http://192.168.29.64:4747/video")
    video_capture = cv2.VideoCapture(0)
    if video_capture is None:
        logging.error("Could not open video capture")
        return
    global vision
    vision = Vision(video_capture)  
    button = interactables.AR_Button.Create(
        x=100,
        y=100,
        scale=0.1,
        text="hello",
        vision=vision,
        color=Color.GREEN,
        action=Action(func),
    )
    # vision.add_button(button)
    # vision.add_action(vision.process_fps)
    # vision.add_action(vision.process_hand)
    # vision.add_action(Action(Vision.process_fps, (vision,)))
    # vision.add_action(Action(Vision.process_hands, (vision,)))
    vision.window_name = "abc"
    
    signal.signal(signal.SIGINT, vision.InteruptHandler)
    vision.start()

if __name__ == "__main__":
    main()