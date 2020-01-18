import cv2
import numpy as np

from Circle import Circle
from Color import Color
from PanelBar import PanelBar
from RoundedRect import RoundedRect
from Clock import Clock
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('file_name', type=str, help='input file name')
parser.add_argument('-ad', type=int, help='animation duration in frames, def is 9')
parser.add_argument('-vp', type=int, help='vertical paddings in top panel, def is 10')
parser.add_argument('-cr', type=int, help='the thickness of radius of the circles, def is 9')
parser.add_argument('-cgt', type=int, help='the less the more shifted gradient to target color, [0:255], def is 220')
parser.add_argument('-cts', type=float, help='circle text scale, def is 1.5')
parser.add_argument('-ctt', type=int, help='circle text thickness, def is 3')
parser.add_argument('-tts', type=float, help='total text scale, def is 2.0')
parser.add_argument('-ttt', type=int, help='total text thickness, def is 3')
args = parser.parse_args()
if args.ad:
    PanelBar.ANIMATION_DURATION_IN_FRAMES = args.ad
if args.vp:
    PanelBar.TOP_BOTTOM_PADDING = args.vp
if args.cr:
    Circle.BORDER_THICKNESS = args.cr
if args.cgt:
    Circle.COLOR_GRADIENT_THRESH = args.cgt
if args.cts:
    Circle.TEXT_SCALE = args.cts
if args.ctt:
    Circle.TEXT_THICKNESS = args.ctt
if args.tts:
    PanelBar.TEXT_SCALE = args.tts
if args.ttt:
    PanelBar.TEXT_THICKNESS = args.ttt


class PanelGenerator:
    TOP_PANEL_SIZE = 625, 142
    BOTTOM_PANEL_SIZE = 243, 90
    VIDEO_FPS = 25
    VIDEO_RESOLUTION = 1920, 1080
    # in msec
    ONE_FRAME_DURATION = 1 / VIDEO_FPS * 1000

    def __init__(self):

        self.video_writer = cv2.VideoWriter('panel_animation.mkv', cv2.VideoWriter_fourcc(*"XVID"), self.VIDEO_FPS,
                                            self.VIDEO_RESOLUTION)

        self.r_panel = PanelBar(RoundedRect(self.TOP_PANEL_SIZE, Color.PANEL_COLOR, round_bl=False),
                                RoundedRect(self.BOTTOM_PANEL_SIZE, Color.PANEL_COLOR, round_top=False))
        self.l_panel = PanelBar(RoundedRect(self.TOP_PANEL_SIZE, Color.PANEL_COLOR, round_br=False),
                                RoundedRect(self.BOTTOM_PANEL_SIZE, Color.PANEL_COLOR, round_top=False),
                                reverse=True)

        self.background = np.ones((*self.VIDEO_RESOLUTION[::-1], 3), dtype='uint8')
        self.background[:] = Color.BACKGROUND_COLOR

        self.lp_x, self.y, self.rp_x = 0, 0, self.VIDEO_RESOLUTION[0] - self.TOP_PANEL_SIZE[0]

    def process_file(self, input_file_name):
        cur_time_in_msecs = 0

        def do_step():
            phone = np.copy(self.background)
            l_frame, r_frame = self.l_panel.updateUI(), self.r_panel.updateUI()
            phone[self.y:self.y + l_frame.shape[0], self.lp_x:self.lp_x + l_frame.shape[1]] = l_frame
            phone[self.y:self.y + r_frame.shape[0], self.rp_x:self.rp_x + r_frame.shape[1]] = r_frame
            self.video_writer.write(phone)

        with open(input_file_name, 'r') as input_file:
            line = input_file.readline().strip()

            while line:
                line = line.split(',')
                time, left_panel, right_panel = line[0], line[1:5], line[5:]
                left_panel, right_panel = list(map(int, left_panel)), list(map(int, right_panel))
                clock = Clock(time)
                while cur_time_in_msecs < clock.total_msecs:
                    do_step()
                    cur_time_in_msecs += self.ONE_FRAME_DURATION

                self.l_panel.set_new_values(left_panel)
                self.r_panel.set_new_values(right_panel)
                line = input_file.readline().strip()

        while self.l_panel.is_panel_updating() or self.r_panel.is_panel_updating():
            do_step()
            cur_time_in_msecs += self.ONE_FRAME_DURATION

        self.video_writer.release()


panel_generator = PanelGenerator()
panel_generator.process_file(args.file_name)
