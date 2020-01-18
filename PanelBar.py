from collections import deque

import cv2
import numpy as np

from Cell import Cell
from Circle import Circle
from Color import Color
from RoundedRect import RoundedRect


class PanelBar:
    # paddings in percentage
    TOP_BOTTOM_PADDING = 10
    OUT_PADDING = 3
    IN_PADDING = 0
    # that's about 0.3 sec when fps is 25
    ANIMATION_DURATION_IN_FRAMES = 9
    SCORE_TEXT_SCALE = 2
    SCORE_TEXT_THICKNESS = 3

    INFO_TEXT_SCALE = 1.6
    INFO_TEXT_THICKNESS = 2
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    PHOTO_WIDTH_PERCENTAGE = 40 / 100

    CIRCLE_COLORS = [Color.RED, Color.YELLOW, Color.BLUE, Color.AQUA]

    ICONS_DIR = 'icons/'
    ICONS_NAMES = ['image.png', 'money.png', 'lightning.png', 'heart.png']

    USER_INFO = 'YOU, 21'
    CHATTER_INFO = 'F, 23'

    USER_PHOTO = 'user.png'
    CHATTER_PHOTO = 'f_face.png'

    def __init__(self, top_rect: RoundedRect, bottom_rect: RoundedRect, is_left=False):
        self.top_rect = top_rect
        self.bottom_rect = bottom_rect
        self.is_left_panel = is_left

        self.background = self.generate_background((top_rect.height + bottom_rect.height * 2, top_rect.width, 3))
        self.background[:self.top_rect.height, :self.top_rect.width] = self.top_rect.figure
        if not is_left:
            self.background[self.top_rect.height:self.top_rect.height + self.bottom_rect.height,
            :self.bottom_rect.width] = self.bottom_rect.figure
        else:
            self.background[self.top_rect.height:self.top_rect.height + self.bottom_rect.height,
            self.background.shape[1] - self.bottom_rect.width: self.background.shape[1]] = self.bottom_rect.figure

        self.values_are_empty = True
        self.top_work_area = None
        self.circles = []
        self.circle_diameter = None
        self.cells = []
        self.icons = []
        self.photo_pos = None
        self.photo_size = None
        self.age_gender_pos = None
        self.age_gender_size = None
        self.emotion_pos = None
        self.emotion_size = None
        self.chatter_emotion = ''
        self.calc_cells()

    @staticmethod
    def generate_background(size):
        background = np.random.randint(0, 255, size, dtype='uint8')
        background[:] = Color.BACKGROUND_COLOR
        return background

    def draw_circles(self, background):
        for cell in self.cells:
            self.overlay_image_on_background(background, cell.circle.figure, cell.circle_pos)

    def draw_icons(self, background):
        for cell in self.cells:
            self.overlay_image_on_background(background, cell.pict, cell.pict_pos)

    def overlay_image_on_background(self, background, image, pos):
        background[pos[1]:pos[1] + image.shape[0], pos[0]:pos[0] + image.shape[1]] = image

    def calc_cells(self):
        width_padding = int(self.top_rect.width * (self.OUT_PADDING / 100))
        height_padding = int(self.top_rect.height * (self.TOP_BOTTOM_PADDING / 100))

        btw_padding = int(self.top_rect.width * (self.IN_PADDING / 100))

        cell_width, cell_height = (self.top_rect.width - width_padding * 2 - btw_padding * 7) // 4, \
                                  self.top_rect.height - height_padding * 2
        self.circle_diameter = cell_height

        icon_width, icons_height = cell_width - cell_height, cell_height

        self.generate_circles()
        self.load_icons((icon_width, int(icons_height * 0.4)))

        for i, circle in enumerate(self.circles):
            self.cells.append(
                Cell(circle, self.icons[i], (width_padding + (cell_width + btw_padding * 2) * i, height_padding),
                     (width_padding + (cell_width + btw_padding * 2) * i + self.circle_diameter + btw_padding,
                      height_padding), self.CIRCLE_COLORS[i]))

        info_panel_width = self.top_rect.width - self.bottom_rect.width
        photo_width = int(info_panel_width * self.PHOTO_WIDTH_PERCENTAGE)
        photo_height = self.bottom_rect.height * 2
        self.photo_size = photo_width, photo_height

        age_gender_width = info_panel_width - photo_width
        photo_pos_x = 0 if self.is_left_panel else self.top_rect.width - photo_width
        photo_pos_y = self.top_rect.height
        self.photo_pos = photo_pos_x, photo_pos_y

        age_gender_pos_x = photo_width if self.is_left_panel else self.bottom_rect.width
        age_gender_pos_y = self.top_rect.height
        self.age_gender_pos = age_gender_pos_x, age_gender_pos_y
        self.age_gender_size = age_gender_width, self.bottom_rect.height

        emotion_pos_x = photo_width
        emotion_pos_y = self.top_rect.height + self.bottom_rect.height
        emotion_width = photo_width + self.bottom_rect.width

        self.emotion_pos = emotion_pos_x, emotion_pos_y
        self.emotion_size = age_gender_width, self.bottom_rect.height

    def generate_circles(self):
        for color in self.CIRCLE_COLORS:
            self.circles.append(Circle(self.circle_diameter, 0, color))

    def load_icons(self, pict_size):
        for icon_name in self.ICONS_NAMES:
            icon = self.read_transparent_png(self.ICONS_DIR + icon_name)
            # icon = cv2.imread(self.ICONS_DIR + icon_name, cv2.IMREAD_UNCHANGED)
            icon = cv2.resize(icon, pict_size)

            self.icons.append(icon)

    def read_transparent_png(self, filename):
        image_4channel = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
        alpha_channel = image_4channel[:, :, 3]
        rgb_channels = image_4channel[:, :, :3]

        # White Background Image

        white_background_image = np.ones_like(rgb_channels, dtype=np.uint8) * 255
        white_background_image[:] = Color.PANEL_COLOR

        # Alpha factor
        alpha_factor = alpha_channel[:, :, np.newaxis].astype(np.float32) / 255.0
        alpha_factor = np.concatenate((alpha_factor, alpha_factor, alpha_factor), axis=2)

        # Transparent Image Rendered on White Background
        base = rgb_channels.astype(np.float32) * alpha_factor
        white = white_background_image.astype(np.float32) * (1 - alpha_factor)
        final_image = base + white
        return final_image.astype(np.uint8)

    def set_new_values(self, top_panel_values, emotion=''):
        assert len(top_panel_values) == 4

        self.values_are_empty = (top_panel_values[0] == -1)
        if self.values_are_empty:
            return

        self.chatter_emotion = emotion

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
        self.draw_emotion(background_copy)

        self.draw_circles(background_copy)
        self.draw_total_score(background_copy)
        self.draw_age_gender_info(background_copy)
        self.draw_photo(background_copy)
        return background_copy

    def is_chatter_not_detected(self):
        return self.is_left_panel and not (any([bool(cell.circle.percentage != 0) for cell in self.cells]))

    def draw_emotion(self, background):
        if not self.is_left_panel or self.is_chatter_not_detected() or not (
                self.is_left_panel and self.chatter_emotion):
            return

        text_size, base_line = cv2.getTextSize(self.chatter_emotion, self.FONT, self.SCORE_TEXT_SCALE,
                                               self.SCORE_TEXT_THICKNESS)
        text_point_x = self.emotion_pos[0] + (self.emotion_size[0] - text_size[0]) // 2
        text_point_y = self.emotion_pos[1] + (self.emotion_size[1] - text_size[1]) // 2 + text_size[1]

        cv2.putText(background, self.chatter_emotion, (text_point_x, text_point_y), self.FONT, self.SCORE_TEXT_SCALE,
                    Color.WHITE,
                    self.SCORE_TEXT_THICKNESS)

    def draw_photo(self, background):
        if self.is_chatter_not_detected():
            return

        photo_name = self.CHATTER_PHOTO if self.is_left_panel else self.USER_PHOTO
        photo = cv2.imread(photo_name)
        photo = cv2.resize(photo, self.photo_size)
        background[self.photo_pos[1]:self.photo_pos[1] + self.photo_size[1],
        self.photo_pos[0]:self.photo_pos[0] + self.photo_size[0]] = photo

    def draw_age_gender_info(self, background):
        if self.is_chatter_not_detected():
            return

        text = self.CHATTER_INFO if self.is_left_panel else self.USER_INFO
        text_size, base_line = cv2.getTextSize(text, self.FONT, self.INFO_TEXT_SCALE, self.INFO_TEXT_THICKNESS)

        text_point_x = self.age_gender_pos[0] + (self.age_gender_size[0] - text_size[0]) // 2
        text_point_y = self.age_gender_pos[1] + (self.age_gender_size[1] - text_size[1]) // 2 + text_size[1]

        cv2.putText(background, text, (text_point_x, text_point_y), self.FONT, self.INFO_TEXT_SCALE,
                    Color.WHITE,
                    self.INFO_TEXT_THICKNESS)

    def draw_total_score(self, background):
        total_score = int(sum([cell.circle.percentage for cell in self.cells]) / 4 * 10)
        text_size, base_line = cv2.getTextSize(str(total_score), self.FONT, self.SCORE_TEXT_SCALE,
                                               self.SCORE_TEXT_THICKNESS)
        text_point_x = (self.bottom_rect.width - text_size[0]) // 2
        text_point_x = text_point_x if not self.is_left_panel else self.background.shape[
                                                                       1] - self.bottom_rect.width + text_point_x
        text_point_y = (self.bottom_rect.height - text_size[1]) // 2 + \
                       self.top_rect.height + text_size[1]
        cv2.putText(background, str(total_score), (text_point_x, text_point_y), self.FONT, self.SCORE_TEXT_SCALE,
                    Color.WHITE,
                    self.SCORE_TEXT_THICKNESS)

    def is_panel_updating(self):
        return self.cells[0].remained_values
