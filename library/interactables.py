from __future__ import annotations
import library.vision2 as vision2
from library.utils import *

class AR_Button:
    
    def __init__(
        self, rect: Rectangle,
        text: Text,
        vision: vision2.Vision,
        frames_to_hold: int = 10,
        action : Action = None, 
        allowed_fingers : list = [vision2.mpHands.HandLandmark.INDEX_FINGER_TIP]
    ):
        self.rect = rect
        self.text = text
        self.vision = vision
        self.hovered = False
        self.frames_to_hold = frames_to_hold
        self.frames_held = 0
        self.action = action
        self.is_pressed = False
        self.is_hovering = False
        self.allowed_fingers = allowed_fingers
    
    @staticmethod
    def Create(x, y, text, vision, scale=0.04, color=Color.WHITE, **kwargs) -> AR_Button:
        rect = Rectangle(Point(x, y), scale, color, 2, vision)
        # FIXME: the text is not alligned properly
        x2 = rect.point2.x * 1.01
        y2 = rect.point2.y
        text = Text(Point(x2, y2), scale, text, color, 2, vision)
        return AR_Button(rect, text, vision, **kwargs)
    
    def draw(self):
        self.rect.draw()
        self.text.draw()
    
    def process(self):
        
        # print("processing")
        
        inside = False
        if not self.vision.hands:
            return 
    
        for hand in self.vision.hands:
            for finger in self.allowed_fingers:
                pt = Point.fromLandmark(hand.landmark[finger], self.vision)
                # print(pt)
                if self.rect.is_inside(pt):
                    inside = True
                    break
            if inside:
                break
        
        # if inside:
        #     print("inside")
        
        if self.is_pressed:
            if not inside:
                self.is_pressed = False
                self.frames_held = 0
                self.is_hovering = False
        
        else :
            
            if self.is_hovering:
                if inside: # TODO: loading circle
                    self.frames_held += 1
                    if (self.frames_held >= self.frames_to_hold):
                        self.is_pressed = True
                        if self.action:
                            self.action()
                else:
                    self.frames_held = 0
                    self.is_hovering = False
            
            else:
                if inside:
                    self.is_hovering = True
            
        

class AR_Menu:
    
    def __init__(self, vision : vision2.Vision, position : Point = Point(0, 0), scale : float = 0.1):
        self.vision = vision
        self.buttons = []
        self.position = position
        self.scale = scale
    
    def add_button(self, button : AR_Button):
        self.buttons.append(button)
    
    def get_next_position(self):
        return Point(self.position.x, self.position.y + self.scale*self.vision.height*(len(self.buttons)))
    
    def add_button(self, text, action):
        next = self.get_next_position()
        button = AR_Button(next.x, next.y, text, self.vision, action=action)
        self.add_button(button)
        
    def draw(self):
        for button in self.buttons:
            button.draw()
    
    def process(self):
        for button in self.buttons:
            button.process()