import cv2
import numpy as np
from Color import Color


class RoundedRect:
    def __init__(self, size, color, round_top=True, round_bl=True, round_br=True):
        self.width, self.height = size
        self.figure = self.generate_rounded_rect(color, round_top, round_bl, round_br)

    def generate_rounded_rect(self, color, round_top=True, round_bl=True, round_br=True):
        image = np.ones((self.height, self.width, 3), dtype='uint8')
        image[:] = Color.BACKGROUND_COLOR

        circle_radius = (self.width if self.width <= self.height else self.height) // 4
        corner_circle_points = [(circle_radius, circle_radius), (self.width - circle_radius, circle_radius),
                                (self.width - circle_radius, self.height - circle_radius),
                                (circle_radius, self.height - circle_radius)]
        rects = [[(circle_radius, 0), (self.width - circle_radius, self.height)],
                 [(0, circle_radius), (self.width, self.height - circle_radius)]]

        for circle in corner_circle_points:
            cv2.circle(image, circle, circle_radius, color, -1)

        for lt_point, rb_point in rects:
            cv2.rectangle(image, lt_point, rb_point, color, -1)

        if not round_top:
            cv2.rectangle(image, (0, 0), (self.width, circle_radius), color, -1)

        if not round_bl:
            cv2.rectangle(image, (0, self.height - circle_radius), (circle_radius, self.height), color, -1)

        if not round_br:
            cv2.rectangle(image, (self.width - circle_radius, self.height - circle_radius), (self.width, self.height),
                          color, -1)

        return image
