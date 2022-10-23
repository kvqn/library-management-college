from __future__ import annotations
import cv2
import camera.vision2 as vision2

class Point:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
        
    def to_tuple(self):
        return (self.x, self.y)
    
    def __str__(self):
        return f"Point({self.x}, {self.y})"

    @staticmethod
    def fromLandmark(landmark, vision):
        return Point(landmark.x*vision.width, landmark.y*vision.height)

class Color:
    
    ORANGE = (0, 165, 255)
    RED = (0, 0, 255)
    BLUE = (255, 0, 0)
    GREEN = (0, 255, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
class Colour(Color):
    pass
        
class Rectangle :
    
    # def __init__(self, point1 : Point, point2 : Point, color : tuple, thickness, vision : vision2.Vision) :

    #     self.point1 = point1
    #     self.point2 = point2
    #     self.color = color
    #     self.thickness = thickness
    #     self.vision = vision
    
    
    def __init__(self, point : Point, scale : int, color : tuple, thickness : int, vision : vision2.Vision) :

        self.point1 = Point(
            point.x,
            point.y
        )
        self.point2 = Point(
            point.x + scale * min(vision.width, vision.height),
            point.y + scale * min(vision.width, vision.height)
        )
        self.color = color
        self.thickness = thickness
        self.vision = vision
        
    def draw(self):
        cv2.rectangle(
            img=self.vision.frame,
            pt1=self.point1.to_tuple(),
            pt2=self.point2.to_tuple(),
            color=self.color,
            thickness=self.thickness
        )
    
    def is_inside(self, point : Point):
        # print(self.point1, self.point2, point)
        return ((self.point1.x < point.x < self.point2.x) and (self.point1.y < point.y < self.point2.y))
        
            
        

class Text:
    
    def __init__(self, point, scale, text, color, thickness, vision) :
        self.point = point
        self.scale = scale
        self.text = text
        self.color = color
        self.thickness = thickness
        self.vision = vision
    
    def draw(self):
        cv2.putText(
            img=self.vision.frame,
            text=self.text,
            org=self.point.to_tuple(),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=self.scale*min(self.vision.width, self.vision.height)/16,
            # fontScale=12,
            color=self.color,
            thickness=self.thickness
        )
        
class Action:
    
    def __init__(self, func : callable, args : tuple = tuple()):
        self.func = func
        self.args = args
        
    def __call__(self):
        self.func(*self.args)