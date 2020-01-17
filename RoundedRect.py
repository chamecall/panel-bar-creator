
import cv2
import numpy as np
from Color import Color


class RoundedRect:
    def __init__(self, width, height, color, round_top=True, round_bl=True, round_br=True):
        self.width = width
        self.height = height
        self.figure = self.generateRoundedRect(width, height, color, round_top, round_bl, round_br)

    @staticmethod
    def generateRoundedRect(width, height, color, round_top=True, round_bl=True, round_br=True):
        image = np.ones((height, width, 3), dtype='uint8')
        image[:] = Color.BACKGROUND_COLOR

        circle_radius = (width if width <= height else height) // 4
        corner_circle_points = [(circle_radius, circle_radius), (width - circle_radius, circle_radius),
                                (width - circle_radius, height - circle_radius),
                                (circle_radius, height - circle_radius)]
        rects = [[(circle_radius, 0), (width - circle_radius, height)],
                 [(0, circle_radius), (width, height - circle_radius)]]

        for circle in corner_circle_points:
            cv2.circle(image, circle, circle_radius, color, -1)

        for lt_point, rb_point in rects:
            cv2.rectangle(image, lt_point, rb_point, color, -1)

        if not round_top:
            cv2.rectangle(image, (0, 0), (width, circle_radius), color, -1)

        if not round_bl:
            cv2.rectangle(image, (0, height - circle_radius), (circle_radius, height), color, -1)

        if not round_br:
            cv2.rectangle(image, (width - circle_radius, height - circle_radius), (width, height), color, -1)

        return image