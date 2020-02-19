from collections import deque
from PIL import Image, ImageSequence
import cv2
import numpy as np
import imutils
from Cell import Cell
from Circle import Circle
from Color import Color
from RoundedRect import RoundedRect
from Utils import draw_text_in_center_with_shadow
from PIL import ImageFont, ImageDraw, Image
from Rect import Rect

def overlay_transparent(background, overlay, pos):
	x, y = pos

	background_width = background.shape[1]
	background_height = background.shape[0]

	if x >= background_width or y >= background_height:
		return background

	h, w = overlay.shape[0], overlay.shape[1]

	if x + w > background_width:
		w = background_width - x
		overlay = overlay[:, :w]

	if y + h > background_height:
		h = background_height - y
		overlay = overlay[:h]

	if overlay.shape[2] < 4:
		overlay = np.concatenate(
			[
				overlay,
				np.ones((overlay.shape[0], overlay.shape[1], 1), dtype = overlay.dtype) * 255
			],
			axis = 2,
		)

	overlay_image = overlay[..., :3]
	mask = overlay[..., 3:] / 255.0

	background[y:y+h, x:x+w] = (1.0 - mask) * background[y:y+h, x:x+w] + mask * overlay_image

	return background





class BrainAnimation:
	def __init__(self, path, dst_size):
		self.seq, self.size = self.decompose_gif(path)
		self.frame_n = 0
		self.len = len(self.seq)
		self.dst_size = dst_size
		self.resize_seq()

	def next(self):
		self.frame_n = (self.frame_n + 1) % self.len
		return self.seq[self.frame_n]

	def decompose_gif(self, path):
		imgs = []
		gif = Image.open(path)
		for frame in ImageSequence.Iterator(gif):
			bgra_im = cv2.cvtColor(np.array(frame.convert('RGBA')), cv2.COLOR_RGBA2BGRA)

			imgs.append(bgra_im)

		return imgs, gif.size

	def resize_seq(self):
		frame = self.seq[0]
		if frame.shape[1] >= frame.shape[0]:
			self.seq = [imutils.resize(frame, width=self.dst_size[0]) for frame in self.seq]
		else:
			self.seq = [imutils.resize(frame, height=self.dst_size[1]) for frame in self.seq]



class PanelBar:
	# paddings in percentage

	# that's about 0.3 sec when fps is 25
	ANIMATION_DURATION_IN_FRAMES = 9
	SCORE_TEXT_SCALE = 2
	SCORE_TEXT_THICKNESS = 3

	INFO_TEXT_SCALE = 1.6
	INFO_TEXT_THICKNESS = 2
	FONT = cv2.FONT_HERSHEY_SIMPLEX

	CIRCLE_COLORS = [Color.RED, Color.YELLOW, Color.BLUE, Color.AQUA]

	ICONS_DIR = 'raw/'
	ICONS_NAMES = ['lips.png', 'coin.png', 'lightning.png', 'heart.png']

	BRAIN_BACK_IMG = 'raw/brain_back.png'

	BTW_PANELS_VERTICAL_MARGIN = 10
	cells_sizes = (0.33, 0.33, 0.34)
	AVATAR_SIZE_TO_PHOTO_CELL_SIZE = 0.7
	FONT = ImageFont.truetype('LatoBlack.ttf', 50)


	def __init__(self, photo, info):
		scale_coeff = 2.1
		self.top_panel = cv2.imread('raw/top_panel.png', cv2.IMREAD_UNCHANGED)
		self.top_panel = cv2.resize(self.top_panel, (int(self.top_panel.shape[1] * scale_coeff), int(self.top_panel.shape[0] * scale_coeff)))
		self.bottom_panel = cv2.imread('raw/bottom_panel.png', cv2.IMREAD_UNCHANGED)
		self.bottom_panel = cv2.resize(self.bottom_panel, (int(self.bottom_panel.shape[1] * scale_coeff), int(self.bottom_panel.shape[0] * scale_coeff)))

		self.background = self.generate_background((self.top_panel.shape[0] + self.BTW_PANELS_VERTICAL_MARGIN + self.bottom_panel.shape[0], self.top_panel.shape[1], 3))

		self.background = overlay_transparent(self.background, self.top_panel, (0, 0))
		self.background = overlay_transparent(self.background, self.bottom_panel, (0, self.top_panel.shape[0] + self.BTW_PANELS_VERTICAL_MARGIN))

		self.values_are_empty = True
		self.top_work_area = None
		self.circles = []
		self.circle_diameter = None
		self.cells = []
		self.icons = []
		self.photo_cell = None
		self.age_gender_cell = None
		self.emotion_cell = None
		self.score_cell = None
		self.emotion = ''
		self.info = info
		self.calc_cells()
		self.brain_animation = BrainAnimation('new_brain.gif', (self.score_cell.width, self.score_cell.height))
		self.load_images(photo)
		self.overlay_brain_back()



	def load_images(self, photo):
		photo = cv2.imread(photo)
		self.photo = cv2.resize(photo, (self.photo_cell.width, self.photo_cell.height))

	def overlay_brain_back(self):
		brain_back = cv2.imread(self.BRAIN_BACK_IMG, cv2.IMREAD_UNCHANGED)
		resized_brain_back = None
		if brain_back.shape[1] >= brain_back.shape[0]:
			resized_brain_back = imutils.resize(brain_back, width=self.score_cell.width) 
		else:
			resized_brain_back = imutils.resize(brain_back, height=self.score_cell.height)
		x = (self.score_cell.width - resized_brain_back.shape[1]) // 2 + self.score_cell.left
		y = (self.score_cell.height - resized_brain_back.shape[0]) // 2 + self.score_cell.top
		self.background = overlay_transparent(self.background, resized_brain_back, (x, y))



	@staticmethod
	def generate_background(size):
		background = np.random.randint(0, 255, size, dtype='uint8')
		background[:] = Color.BACKGROUND_COLOR
		return background

	def draw_circles(self, background):
		for cell in self.cells:
			background = overlay_transparent(background, cell.circle.figure, cell.circle_pos)

	def draw_icons(self, background):
		for cell in self.cells:
			background = overlay_transparent(background, cell.pict, cell.pict_pos)

	def overlay_image_on_background(self, background, image, pos):
		background[pos[1]:pos[1] + image.shape[0], pos[0]:pos[0] + image.shape[1]] = image

	def calc_cells(self):


		cell_width, cell_height = self.top_panel.shape[1] // 4, self.top_panel.shape[0]
		self.circle_diameter = int(cell_width * 0.6)

		icon_width, icons_height = cell_width - self.circle_diameter, cell_height

		self.generate_circles()
		self.load_icons(icon_width)


		for i, circle in enumerate(self.circles):
			self.cells.append(
				Cell(circle, self.icons[i], (cell_width * i, (self.top_panel.shape[0] - self.circle_diameter) // 2),
					 (cell_width * i + self.circle_diameter, 0), self.CIRCLE_COLORS[i]))

		photo_cell_width = int(self.bottom_panel.shape[1] * self.cells_sizes[0])
		photo_cell_height = self.bottom_panel.shape[0]

		photo_cell_top = self.top_panel.shape[0] + self.BTW_PANELS_VERTICAL_MARGIN

		avatar_width, avatar_height = int(photo_cell_width * self.AVATAR_SIZE_TO_PHOTO_CELL_SIZE), int(photo_cell_height * self.AVATAR_SIZE_TO_PHOTO_CELL_SIZE)
		avatar_left = (photo_cell_width - avatar_width) // 2
		avatar_top = (photo_cell_height - avatar_height) // 2
		self.photo_cell = Rect(avatar_left, self.top_panel.shape[0] + self.BTW_PANELS_VERTICAL_MARGIN + avatar_top, avatar_width, avatar_height)
			 

		self.age_gender_cell = Rect(photo_cell_width,
			photo_cell_top,
			int(self.bottom_panel.shape[1] * self.cells_sizes[1]),
			self.bottom_panel.shape[0] / 2)

		self.emotion_cell = Rect(self.age_gender_cell.left, self.age_gender_cell.top + self.age_gender_cell.height,
			self.age_gender_cell.width, self.age_gender_cell.height)


		self.score_cell = Rect(self.emotion_cell.right, self.age_gender_cell.top,
			int(self.bottom_panel.shape[1] * self.cells_sizes[2]),
			photo_cell_height)

	def generate_circles(self):
		for color in self.CIRCLE_COLORS:
			self.circles.append(Circle(self.circle_diameter, 0, color))

	def load_icons(self, max_width):
		for icon_name in self.ICONS_NAMES:
			icon = cv2.imread(self.ICONS_DIR + icon_name, cv2.IMREAD_UNCHANGED)
			icon = imutils.resize(icon, width=max_width)

			self.icons.append(icon)






	def set_new_values(self, top_panel_values, emotion=''):
		assert len(top_panel_values) == 4

		self.values_are_empty = (top_panel_values[0] == -1)
		if self.values_are_empty:
			return

		self.emotion = emotion

		for i, new_value in enumerate(top_panel_values):
			step = (new_value - self.cells[i].circle.percentage) // (self.ANIMATION_DURATION_IN_FRAMES - 1)

			values = [new_value - step * i for i in range(self.ANIMATION_DURATION_IN_FRAMES)][::-1]
			self.cells[i].set_new_values_deque(deque(values))

	def updateUI(self):
		if self.values_are_empty:
			return self.generate_background(self.background.shape)

		for i, cell in enumerate(self.cells):
			if cell.remained_values:
				cell.set_new_circle(Circle(self.circle_diameter, cell.remained_values.popleft(), cell.circle_color))

		background_copy = np.copy(self.background)
		self.draw_icons(background_copy)
		background_copy = self.draw_emotion(background_copy)

		self.draw_circles(background_copy)
		self.draw_brain_frame(background_copy)
		background_copy = self.draw_total_score(background_copy)
		background_copy = self.draw_age_gender_info(background_copy)
		self.draw_photo(background_copy)
		return background_copy

	def is_chatter_not_detected(self):
		return not (any([bool(cell.circle.percentage != 0) for cell in self.cells]))

	def draw_emotion(self, background):
		if self.is_chatter_not_detected():
			return

		return draw_text_in_center_with_shadow(background, self.emotion, self.FONT, self.emotion_cell)

	def draw_brain_frame(self, background):
		brain = self.brain_animation.next()
		x = (self.score_cell.width - brain.shape[1]) // 2 + self.score_cell.left
		y = (self.score_cell.height - brain.shape[0]) // 2 + self.score_cell.top

		background = overlay_transparent(background, brain, (x, y))



	def draw_photo(self, background):
		if self.is_chatter_not_detected():
			return

		background[self.photo_cell.top:self.photo_cell.top + self.photo_cell.height,
		self.photo_cell.left:self.photo_cell.left + self.photo_cell.width] = self.photo

	def draw_age_gender_info(self, background):
		if self.is_chatter_not_detected():
			return

		return draw_text_in_center_with_shadow(background, self.info, self.FONT, self.age_gender_cell)


	def draw_total_score(self, background):
		total_score = int(sum([cell.circle.percentage for cell in self.cells]) / 4 * 10)
		score = str(total_score)

		return draw_text_in_center_with_shadow(background, score, self.FONT, self.score_cell, y_shift=-20)


	def is_panel_updating(self):
		return self.cells[0].remained_values



