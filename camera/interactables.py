from __future__ import annotations
from camera.utils import *
import camera.vision as vision
import logging

class AR_Button:
    
    def __init__(
        self, rect: Rectangle,
        loading_rect : LoadingRectangle,
        text: Text,
        frames_to_hold: int = 20,
        action : Action = None, 
        allowed_fingers : list = [vision.mpHands.HandLandmark.INDEX_FINGER_TIP],
        detection_thickness = 0.02
    ):
        self.rect = rect
        self.loading_rect = loading_rect
        self.text = text
        self.hovered = False
        self.frames_to_hold = frames_to_hold
        self.frames_held = 0
        self.action = action
        self.is_pressed = False
        self.is_hovering = False
        self.allowed_fingers = allowed_fingers
        self.detection_thickness = detection_thickness
    
    @staticmethod
    def Create(x, y, text, scale=0.04, color=Color.WHITE, **kwargs) -> AR_Button:
        rect = Rectangle(Point(x, y), scale, color, 2)
        # FIXME: the text is not alligned properly
        x2 = rect.point2.x * 1.01
        y2 = rect.point2.y
        text = Text(Point(x2, y2), scale, text, color, 2)
        loading_rect = LoadingRectangle(Point(x,y), scale, color)
        
        return AR_Button(rect, loading_rect, text,  **kwargs)
    
    def draw(self, frame):
        self.rect.draw(frame)
        self.loading_rect.draw(frame)
        self.text.draw(frame)
    
    def process(self, hands):
        
        # print("processing")
        
        inside = False
        if not hands:
            return 
    
        for hand in hands:
            for finger in self.allowed_fingers:
                pt = Point.fromLandmark(hand.landmark[finger])
                # print(pt)
                if self.rect.is_inside(pt, self.detection_thickness):
                    inside = True
                    break
            if inside:
                break
        
        # if inside:
        #     print("inside")
        
        if self.is_pressed:
            if not inside:
                self.is_pressed = False
                self.frames_held -= 1
                self.is_hovering = False
                self.loading_rect.setProgress(self.frames_held / self.frames_to_hold)
        
        else :
            
            if self.is_hovering:
                if inside: # TODO: loading circle
                    self.frames_held += 1
                    if (self.frames_held >= self.frames_to_hold):
                        # self.loading_rect.setProgress(0)
                        self.is_pressed = True
                        if self.action:
                            self.action()
                    else:
                        self.loading_rect.setProgress(self.frames_held / self.frames_to_hold)
                else:
                    self.frames_held -= 1
                    self.loading_rect.setProgress(self.frames_held / self.frames_to_hold)
                    self.is_hovering = False
            
            else:
                if inside:
                    self.is_hovering = True
            
        

class AR_Menu:
    
    def __init__(self, position : Point = Point(0, 0), scale : float = 0.1):
        self.buttons = []
        self.position = position
        self.scale = scale
    
    def get_next_position(self):
        return Point(self.position.x, self.position.y + self.scale*vision.SCREEN_HEIGHT*(len(self.buttons)))
    
    def add_button(self, text, action):
        next = self.get_next_position()
        button = AR_Button.Create(next.x, next.y, text, action=action)
        self.buttons.append(button)
        
    def draw(self, frame):
        for button in self.buttons:
            button.draw(frame)
    
    def process(self, hands):
        for button in self.buttons:
            button.process(hands)