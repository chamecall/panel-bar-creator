import numpy as np
import cv2
from Utils import draw_text_in_center_with_shadow
from Color import Color
from Rect import Rect
from PIL import ImageFont

MAX_PERCENT_VALUE = 99
ONE_PERCENT_IN_DEGREES = 360 / MAX_PERCENT_VALUE


class Circle:
    BORDER_THICKNESS = 10
    TEXT_THICKNESS = 2
    TEXT_SCALE = 1

    # the less the more saturated
    COLOR_GRADIENT_THRESH = 220

    FONT = ImageFont.truetype('LatoBlack.ttf', 35)

    def __init__(self, diameter, percentage, front_color):
        self.diameter = diameter
        self.figure = self.generate_gradient_circle(diameter, percentage, front_color)
        self.percentage = percentage

    def update_progress(self, percentage):
        pass

    @staticmethod
    def generate_gradient_circle(diameter, percentage, front_color, back_color=Color.WHITE):

        # implied white color as start of gradient and circle background
        b, g, r = front_color
        b_step, g_step, r_step = (255 - b) / MAX_PERCENT_VALUE, (255 - g) / MAX_PERCENT_VALUE, (
                    255 - r) / MAX_PERCENT_VALUE

        radius = diameter // 2
        circle = np.ones((diameter, diameter, 4), dtype='uint8')
        radius = radius - Circle.BORDER_THICKNESS
        circle[:, :, 3] = 255

        for i in range(1, percentage + 1):
            prev_degree = int((i - 1) * ONE_PERCENT_IN_DEGREES)
            degree = int(i * ONE_PERCENT_IN_DEGREES)

            cur_color = (Circle.COLOR_GRADIENT_THRESH - int(i * b_step),
                         Circle.COLOR_GRADIENT_THRESH - int(i * g_step),
                         Circle.COLOR_GRADIENT_THRESH - int(i * r_step))
            cv2.ellipse(circle, (diameter // 2, diameter // 2), (radius, radius), -90, prev_degree, degree, cur_color,
                        Circle.BORDER_THICKNESS)

        degrees = int(percentage * ONE_PERCENT_IN_DEGREES)
        if degrees != 360:
            cv2.ellipse(circle, (diameter // 2, diameter // 2), (radius, radius), -90, degrees, 360, back_color,
                        Circle.BORDER_THICKNESS)

        # text_size, base_line = cv2.getTextSize(str(percentage), Circle.FONT, Circle.TEXT_SCALE, Circle.TEXT_THICKNESS)
        # text_point = ((diameter - text_size[0]) // 2), (diameter - text_size[1]) // 2 + text_size[1]
        # cv2.putText(circle, str(percentage), text_point, Circle.FONT, Circle.TEXT_SCALE, Color.WHITE,
        #             Circle.TEXT_THICKNESS)


        circle[:, :, 3] = 255 - circle[:, :, 3]
        circle = draw_text_in_center_with_shadow(circle, str(percentage), Circle.FONT, Rect(0, 0, circle.shape[1], circle.shape[0]), shadow_shift=1, y_shift=-5)


        return circle
