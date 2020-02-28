import cv2
from Rect import Rect

class Size:
    def __init__(self, width, height):
        self.width = width
        self.height = height


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class AnimationMover:
    def __init__(self, bitmap, start_rect: Rect, end_rect: Rect, steps_num):
        self.bitmap = bitmap

        self.start_rect = start_rect
        self.end_rect = end_rect

        self.steps_num = steps_num
        self.cur_step_num = 0

        self.size_diff = Size(end_rect.width - start_rect.width, end_rect.height - start_rect.height)
        self.axis_diff = Point(end_rect.left - start_rect.left, end_rect.top - start_rect.top)

    def steps_left(self):
        return self.cur_step_num <= self.steps_num

    def inc_step(self):
        self.cur_step_num += 1

    def get_new_size(self):
        return Size(int(self.start_rect.width + self.size_diff.width * self.cur_step_num / self.steps_num),
                    int(self.start_rect.height + self.size_diff.height * self.cur_step_num / self.steps_num))

    def get_new_pos(self):
        return Point(int(self.start_rect.left + self.axis_diff.x * self.cur_step_num / self.steps_num),
                     int(self.start_rect.top + self.axis_diff.y * self.cur_step_num / self.steps_num))

    def get_new_located_bitmap(self):
        new_size = self.get_new_size()
        new_pos = self.get_new_pos()
        scaled_bitmap = cv2.resize(self.bitmap, (new_size.width, new_size.height), interpolation=cv2.INTER_AREA)

        self.inc_step()
        return scaled_bitmap, new_pos
