from collections import deque
import cv2
import imutils
import numpy as np
from PIL import ImageFont
from Animator import Animator
from Cell import Cell
from Circle import Circle
from Color import Color
from Rect import Rect
from Utils import draw_text_in_center_with_shadow
from Utils import overlay_transparent


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
    FONT = ImageFont.truetype('LatoBlack.ttf', 30)

    def __init__(self, photo, info):
        scale_coeff = 1.5
        self.top_panel = cv2.imread('raw/top_panel.png', cv2.IMREAD_UNCHANGED)
        self.top_panel = cv2.resize(self.top_panel, (
            int(self.top_panel.shape[1] * scale_coeff), int(self.top_panel.shape[0] * scale_coeff)))
        self.bottom_panel = cv2.imread('raw/bottom_panel.png', cv2.IMREAD_UNCHANGED)
        self.bottom_panel = cv2.resize(self.bottom_panel, (
            int(self.bottom_panel.shape[1] * scale_coeff), int(self.bottom_panel.shape[0] * scale_coeff)))

        self.background = self.generate_background((self.top_panel.shape[0] + self.BTW_PANELS_VERTICAL_MARGIN +
                                                    self.bottom_panel.shape[0], self.top_panel.shape[1], 4))

        self.blend_images(self.background, self.top_panel, (0, 0))
        self.blend_images(self.background, self.bottom_panel,
                          (0, self.top_panel.shape[0] + self.BTW_PANELS_VERTICAL_MARGIN))
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
        self.brain_back = None
        self.photo = None
        self.calc_cells()
        self.brain_animation = Animator('raw/new_brain.gif', (self.score_cell.width, self.score_cell.height))
        self.load_images(photo)

    def blend_images(self, back_image, fore_image, pos):
        back_image[pos[1]:pos[1] + fore_image.shape[0],
        pos[0]:pos[0] + fore_image.shape[1]] = fore_image

    def load_images(self, photo):
        photo = cv2.imread(photo, cv2.IMREAD_UNCHANGED)
        self.photo = cv2.resize(photo, (self.photo_cell.width, self.photo_cell.height))

        brain_back = cv2.imread(self.BRAIN_BACK_IMG, cv2.IMREAD_UNCHANGED)
        resized_brain_back = None
        if brain_back.shape[1] >= brain_back.shape[0]:
            resized_brain_back = imutils.resize(brain_back, width=self.score_cell.width)
        else:
            resized_brain_back = imutils.resize(brain_back, height=self.score_cell.height)
        self.brain_back = resized_brain_back

    def overlay_brain_back(self, background):

        x = (self.score_cell.width - self.brain_back.shape[1]) // 2 + self.score_cell.left
        y = (self.score_cell.height - self.brain_back.shape[0]) // 2 + self.score_cell.top
        overlay_transparent(background, self.brain_back, (x, y))

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

        avatar_width, avatar_height = int(photo_cell_width * self.AVATAR_SIZE_TO_PHOTO_CELL_SIZE), int(
            photo_cell_height * self.AVATAR_SIZE_TO_PHOTO_CELL_SIZE)
        avatar_left = (photo_cell_width - avatar_width) // 2
        avatar_top = (photo_cell_height - avatar_height) // 2
        self.photo_cell = Rect(avatar_left, self.top_panel.shape[0] + self.BTW_PANELS_VERTICAL_MARGIN + avatar_top,
                               avatar_width, avatar_height)

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

    def set_new_values(self, top_panel_values, no_animation, emotion=''):
        self.values_are_empty = (top_panel_values[0] == -1)
        if self.values_are_empty:
            return

        self.emotion = emotion

        for i, new_value in enumerate(top_panel_values):
            step = (new_value - self.cells[i].circle.percentage) // (self.ANIMATION_DURATION_IN_FRAMES - 1)

            values = [new_value - step * i for i in range(self.ANIMATION_DURATION_IN_FRAMES)][::-1]
            if no_animation:
                values = values[-1:]
            self.cells[i].set_new_values_deque(deque(values))

    def update_UI(self, frame):
        if self.values_are_empty:
            return frame

        for i, cell in enumerate(self.cells):
            if cell.remained_values:
                cell.set_new_circle(Circle(self.circle_diameter, cell.remained_values.popleft(), cell.circle_color))

        frame = overlay_transparent(frame, self.background, (0, 0))
        self.overlay_brain_back(frame)
        self.draw_icons(frame)
        frame = self.draw_emotion(frame)

        self.draw_circles(frame)
        self.draw_brain_frame(frame)
        frame = self.draw_total_score(frame)
        frame = self.draw_age_gender_info(frame)
        self.draw_photo(frame)
        return frame

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

        overlay_transparent(background, self.photo, (self.photo_cell.left, self.photo_cell.top))

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
