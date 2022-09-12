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

mpHands = mediapipe.solutions.hands
mpDraw = mediapipe.solutions.drawing_utils
hands = mpHands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.1)

import library.interactables as interactables
from library.utils import Action, Color


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
        

class Vision:
    """
    Processes:
        self.process_fps()
        self.process_hands()
    
    """
    objects = []
    
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
        Vision.objects.append(self)
        
        self.window_name = "preview"+str(len(Vision.objects))
        
        self.buttons = []
        self.menus = []
        self.is_scanning_for_qr = False
        self.action_queue : List[Action]= []
        self.codes : List[pyzbar.Decoded]= []
    
    def start(self):    
        self.ReadVideoCapture()
    
    def stop(self):
        self.stopped=True
        # self.barrier.abort()
        self.webcam.stop()
        cv2.destroyWindow(self.window_name)
    
    @staticmethod
    def StopAllVision():
        for i in Vision.objects:
            i.stop()
    
     
    @staticmethod
    def process_fps(vision) -> int:
        vision.ctime = time.time()
        fps = 1/(vision.ctime-vision.ptime)
        vision.ptime = vision.ctime
        cv2.putText(vision.frame, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
    
    @staticmethod
    def process_hands(vision):
        # Processing hands using some library
        vision.hands = hands.process(vision.frame).multi_hand_landmarks
        if vision.hands == None:
            vision.hands = []
    
        # Displaying hands landmarks
        if vision.hands:
            # print("hands")
            for hand in vision.hands :
                # print(hand)
                mpDraw.draw_landmarks(vision.frame, hand, mpHands.HAND_CONNECTIONS)
    
    @staticmethod
    def process_qr(vision):
        vision.codes = pyzbar.decode(vision.frame)
    
    
    def do_actions(self):
        for action in self.action_queue:
            action()
    
    def add_action(self, action : Action):
        self.action_queue.append(action)

    
    # Process input from a webcam as per requirement
    def ReadVideoCapture(self):
        
        
        logging.debug("Starting webcam thread")
        self.webcam.start()    
        logging.debug("Started webcam thread")
        
        
        logging.debug("Creating window")
        cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
        logging.debug("Created window")
               
        logging.info("Starting main loop")
        
        while True :
            
            self.frame = self.webcam.read()
            
            self.do_actions()
            self.process_buttons()
            self.process_menus()
            
            self.draw()
            
            
            cv2.imshow(self.window_name, self.frame)
            key = cv2.waitKey(1)
            if key == ord('q') :
                break
           
        
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
    


def InteruptHandler(signum, frame):
    print("Interupt")
    Vision.StopAllVision()
    # WebcamStream.StopAllStreams() 


def func():
    print("Button pressed !")

    
def main():
    
    logging.basicConfig(level=logging.DEBUG)
    
    # cv2.dnn.Net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    # cv2.dnn.Net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
    
    video_capture = cv2.VideoCapture(0)
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
    vision.add_button(button)
    vision.add_action(Action(Vision.process_fps, (vision,)))
    vision.add_action(Action(Vision.process_hands, (vision,)))
    
    signal.signal(signal.SIGINT, InteruptHandler)
    vision.start()

if __name__ == "__main__":
    main()