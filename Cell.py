from collections import deque


class Cell:



    def __init__(self, circle, pict, circle_pos, pict_pos, color):
        self.circle = circle
        self.pict = pict
        self.circle_pos = circle_pos
        self.pict_pos = pict_pos
        self.remained_values = None
        self.circle_color = color

    def set_new_values_deque(self, new_values):
        self.remained_values = new_values

    def set_new_circle(self, new_circle):
        self.circle = new_circle

