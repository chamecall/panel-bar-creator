from Clock import Clock
from collections import deque
from Rect import Rect
from AnimationMover import AnimationMover

class FaceAnimationScheduler:
    def __init__(self, path_to_file):
        self.detections_queue = self.extract_lines_from_file(path_to_file)
        self.cur_data = []
        self.next_data = self.get_next_data()

    def get_info_by_time(self, cur_time):
        if not self.next_data or self.next_data[0].total_msecs > cur_time:
            return []

        self.cur_data = self.next_data
        self.next_data = self.get_next_data()

        return self.cur_data[1:]

    def get_next_data(self):
        if not self.detections_queue:
            return []

        return self.parse_line(self.detections_queue.popleft())



    @staticmethod
    def parse_line(line):
        line = line.split(',')

        time, *another = line
        clock = Clock(time)

        nums = list(map(int, another[:-1]))
        rect = Rect(*nums)
        side = another[-1]

        return clock, rect, side

    @staticmethod
    def extract_lines_from_file(path_to_file):
        with open(path_to_file, 'r') as file:
            lines = file.read()

        return deque(lines.strip().split('\n'))