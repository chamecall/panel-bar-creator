class Rect:
	def __init__(self, x_left, y_top, width, height):
		self.left = x_left
		self.top = y_top

		self.width = int(width)
		self.height = int(height)

		self.right = self.left + self.width
		self.bottom = self.top + self.height
		
	def get_pos(self):
		return self.left, self.top
	
	def get_size(self):
		return self.width, self.height
	
	