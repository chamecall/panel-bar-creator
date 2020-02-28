from Animator import Animator
from ObjectDetectionScheduler import ObjectDetectionScheduler


class ObjectDetectionAnimator:
	def __init__(self, path_to_file, path_to_gif, duration_in_frames=-1):
		self.gif_file = path_to_gif
		self.duration_in_frames = duration_in_frames
		self.animation_scheduler = ObjectDetectionScheduler(path_to_file)
		self.animator = None
		self.animation_rect = None
		self.label = ''
	
	def update_animator(self, cur_time):
		detection_data = self.animation_scheduler.get_data_by_time(cur_time)
		if detection_data:
			self.animation_rect, self.label = detection_data
			self.animator = Animator(self.gif_file, (self.animation_rect.width, self.animation_rect.height), -1)
			
	def next_frame(self, cur_time):
		self.update_animator(cur_time)
		
		if self.animator:
			return self.animator.next()
		return None
	