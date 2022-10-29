from __future__ import annotations
import cv2
import camera.test as test

class Point:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
        
    def to_tuple(self):
        return (self.x, self.y)
    
    def __str__(self):
        return f"Point({self.x}, {self.y})"

    @staticmethod
    def fromLandmark(landmark):
        return Point(landmark.x*test.SCREEN_WIDTH, landmark.y*test.SCREEN_HEIGHT)

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
    
    def __init__(self, point : Point, scale : int, color : tuple, thickness : int):

        self.point1 = Point(
            point.x,
            point.y
        )
        self.point2 = Point(
            point.x + scale * min(test.SCREEN_WIDTH, test.SCREEN_HEIGHT),
            point.y + scale * min(test.SCREEN_WIDTH, test.SCREEN_HEIGHT)
        )
        self.color = color
        self.thickness = thickness
        
    def draw(self, frame):
        cv2.rectangle(
            img=frame,
            pt1=self.point1.to_tuple(),
            pt2=self.point2.to_tuple(),
            color=self.color,
            thickness=self.thickness
        )
    
    def is_inside(self, point : Point):
        # print(self.point1, self.point2, point)
        return ((self.point1.x < point.x < self.point2.x) and (self.point1.y < point.y < self.point2.y))
        
            
class LoadingRectangle(Rectangle):
    
    def __init__(self, point : Point, scale : int, color : tuple):
        self.point1 = Point(
            point.x,
            point.y
        )
        self.point2 = Point(
            point.x,
            point.y + scale * min(test.SCREEN_WIDTH, test.SCREEN_HEIGHT)
        )
        self.scale = scale
        self.color = color
    
    def setProgress(self, progress):
        self.point2.x = int(self.point1.x + self.scale * min(test.SCREEN_WIDTH, test.SCREEN_HEIGHT) * progress)
    
    def draw(self, frame):
        cv2.rectangle(
            img = frame,
            pt1 = self.point1.to_tuple(),
            pt2 = self.point2.to_tuple(),
            color=self.color,
            thickness=-1
        )
        

class Text:
    
    def __init__(self, point, scale, text, color, thickness) :
        self.point = point
        self.scale = scale
        self.text = text
        self.color = color
        self.thickness = thickness
    
    def draw(self, frame):
        cv2.putText(
            img=frame,
            text=self.text,
            org=self.point.to_tuple(),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=self.scale*min(test.SCREEN_HEIGHT, test.SCREEN_WIDTH)/16,
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