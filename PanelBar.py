from collections import deque

import cv2
import numpy as np

from Cell import Cell
from Circle import Circle
from Color import Color
from RoundedRect import RoundedRect


class PanelBar:
    # paddings in percentage
    OUT_PADDING = 2
    IN_PADDING = 1
    # that's about 0.3 sec when fps is 25
    ANIMATION_DURATION_IN_FRAMES = 9
    TEXT_SCALE = 5
    TEXT_THICKNESS = 8
    FONT = cv2.FONT_HERSHEY_SIMPLEX

    CIRCLE_COLORS = [Color.RED, Color.YELLOW, Color.BLUE, Color.AQUA]

    ICONS_DIR = 'icons/'
    ICONS_NAMES = ['image.png', 'money.png', 'lightning.png', 'heart.png']

    def __init__(self, top_rect: RoundedRect, bottom_rect: RoundedRect, reverse=False):
        self.top_rect = top_rect
        self.bottom_rect = bottom_rect
        self.reverse = reverse
        self.background = np.random.randint(0, 255, (top_rect.height + bottom_rect.height, top_rect.width, 3),
                                            dtype='uint8')
        self.background[:] = Color.BACKGROUND_COLOR
        self.background[:self.top_rect.height, :self.top_rect.width] = self.top_rect.figure
        if not reverse:
            self.background[self.bottom_rect.height:, :self.bottom_rect.width] = self.bottom_rect.figure
        else:
            self.background[self.bottom_rect.height:, self.background.shape[1] - self.bottom_rect.width:
                                                      self.background.shape[1]] = self.bottom_rect.figure

        self.top_work_area = None
        self.circles = []
        self.circle_diameter = None
        self.cells = []
        self.icons = []
        self.calc_cells()

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
        height_padding = int(self.top_rect.height * (self.OUT_PADDING / 100))

        btw_padding = int(self.top_rect.width * (self.IN_PADDING / 100))

        cell_width, cell_height = (self.top_rect.width - width_padding * 2 - btw_padding * 7) // 4, \
                                  self.top_rect.height - height_padding * 2
        self.circle_diameter = cell_height

        icon_width, icons_height = cell_width - cell_height, cell_height

        self.generate_circles()
        self.load_icons((icon_width, icons_height // 2))

        for i, circle in enumerate(self.circles):
            self.cells.append(
                Cell(circle, self.icons[i], (width_padding + (cell_width + btw_padding * 2) * i, height_padding),
                     (width_padding + (cell_width + btw_padding * 2) * i + self.circle_diameter + btw_padding,
                      height_padding), self.CIRCLE_COLORS[i]))

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

    def set_new_values(self, top_panel_values):
        assert len(top_panel_values) == 4

        for i, new_value in enumerate(top_panel_values):
            step = new_value // (self.ANIMATION_DURATION_IN_FRAMES - 1)
            values = [new_value - step * i for i in range(self.ANIMATION_DURATION_IN_FRAMES)][::-1]
            self.cells[i].set_new_values_deque(deque(values))

    def updateUI(self):
        for i, cell in enumerate(self.cells):
            if cell.remained_values:
                cell.set_new_circle(Circle(self.circle_diameter, cell.remained_values.popleft(), cell.circle_color))

        background_copy = np.copy(self.background)
        self.draw_icons(background_copy)
        self.draw_circles(background_copy)
        self.draw_total_score(background_copy)

        return background_copy

    def draw_total_score(self, background):
        total_score = int(sum([cell.circle.percentage for cell in self.cells]) / 4 * 10)
        text_size, base_line = cv2.getTextSize(str(total_score), self.FONT, self.TEXT_SCALE, self.TEXT_THICKNESS)
        text_point_x = (self.bottom_rect.width - text_size[0]) // 2
        text_point_x = text_point_x if not self.reverse else self.background.shape[1] - self.bottom_rect.width + text_point_x
        text_point_y = (self.bottom_rect.height - text_size[1]) // 2 + \
                     self.top_rect.height + text_size[1]
        cv2.putText(background, str(str(total_score)), (text_point_x, text_point_y), self.FONT, self.TEXT_SCALE, Color.WHITE,
                    self.TEXT_THICKNESS)

    def is_panel_updating(self):
        return self.cells[0].remained_values
