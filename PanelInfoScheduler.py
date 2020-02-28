from Clock import Clock
from collections import deque

class PanelInfoScheduler:
	def __init__(self, path_to_file):
		self.lines_queue = self.extract_lines_from_file(path_to_file)
		self.cur_data = []
		self.next_data = self.get_next_data()



	def get_info_by_time(self, cur_time):
		if not self.next_data or self.next_data[0].total_msecs > cur_time:
			return False, self.cur_data

		self.cur_data = self.next_data
		self.next_data = self.get_next_data()
		return True, self.cur_data

	@staticmethod
	def parse_line(line):
		line = line.split(',')
		emotion = ''
		sex = ''
		time, *another = line
		clock = Clock(time)

		if int(another[0]) == -1:
			left_panel = another[0:1]
			another = another[1:]
		else:
			left_panel = another[:4]
			another = another[4:]

		if int(another[0]) == -1:
			right_panel = another[0:1]
			another = another[1:]
		else:
			right_panel = another[:4]
			another = another[4:]

		left_panel, right_panel = list(map(int, left_panel)), list(map(int, right_panel))

		if left_panel[0] != -1 or right_panel[0] != -1:
			sex = another[0]
			another = another[1:]

			if another:
				emotion = another[0]

		return clock, left_panel, right_panel, sex, emotion

	@staticmethod
	def extract_lines_from_file(path_to_file):
		with open(path_to_file, 'r') as file:
			lines = file.read()

		return deque(lines.strip().split('\n'))

	def get_next_data(self):
		if not self.lines_queue:
			return []

		return self.parse_line(self.lines_queue.popleft())


