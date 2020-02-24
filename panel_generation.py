import argparse

import cv2

from Circle import Circle
from Clock import Clock
from PanelBar import PanelBar
from Utils import overlay_transparent

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
    PanelBar.SCORE_TEXT_SCALE = args.tts
if args.ttt:
    PanelBar.SCORE_TEXT_THICKNESS = args.ttt


class PanelGenerator:
    VIDEO_FPS = 25
    VIDEO_RESOLUTION = 1920, 1080
    # in msec
    ONE_FRAME_DURATION = 1 / VIDEO_FPS * 1000
    LR_MARGIN = 170
    TOP_MARGIN = 70
    MALE_FRAME_FILE = 'frame/mobile.png'
    FEMALE_FRAME_FILE = 'frame/glasses.png'

    def __init__(self):

        self.video_writer = cv2.VideoWriter('panel_animation.mkv', cv2.VideoWriter_fourcc(*"XVID"), self.VIDEO_FPS,
                                            self.VIDEO_RESOLUTION)

        self.r_panel = PanelBar('avatars/male.png', 'M, 21')
        self.l_panel = PanelBar('avatars/female.png', 'F, 23')
        self.cap = cv2.VideoCapture('vozera_cut.mp4')
        self.male_frame = cv2.imread(self.MALE_FRAME_FILE, cv2.IMREAD_UNCHANGED)
        self.female_frame = cv2.imread(self.FEMALE_FRAME_FILE, cv2.IMREAD_UNCHANGED)
        self.lp_x, self.y, self.rp_x = self.LR_MARGIN, self.TOP_MARGIN, self.VIDEO_RESOLUTION[0] - \
                                       self.r_panel.background.shape[1] - self.LR_MARGIN

    def process_file(self, input_file_name):
        cur_time_in_msec = 0

        def update_frame(reverse, sex):
            captured, frame = self.cap.read()
            if not captured: return False

            l_panel_fragment = frame[self.y:self.y + self.l_panel.background.shape[0],
                               self.lp_x:self.lp_x + self.l_panel.background.shape[1]]
            r_panel_fragment = frame[self.y:self.y + self.r_panel.background.shape[0],
                               self.rp_x:self.rp_x + self.r_panel.background.shape[1]]

            if not reverse:
                l_frame = self.l_panel.update_UI(l_panel_fragment)
                r_frame = self.r_panel.update_UI(r_panel_fragment)
            else:
                r_frame = self.l_panel.update_UI(r_panel_fragment)
                l_frame = self.r_panel.update_UI(l_panel_fragment)

            overlay_transparent(frame, l_frame, (self.lp_x, self.y))
            overlay_transparent(frame, r_frame, (self.rp_x, self.y))

            if 'M' in sex:
                overlay_transparent(frame, self.male_frame, (0, 0))
            elif 'F' in sex:
                overlay_transparent(frame, self.female_frame, (0, 0))

            self.video_writer.write(frame)
            return captured

        with open(input_file_name, 'r') as input_file:
            line = input_file.readline().strip()
            prev_sex = ''
            while line:
                clock, left_panel, right_panel, sex, emotion = self.parse_line(line)
                reverse = True if 'F' in sex else False
                no_animation = True if prev_sex != sex else False

                while cur_time_in_msec < clock.total_msecs:
                    update_frame(reverse, prev_sex)
                    cur_time_in_msec += self.ONE_FRAME_DURATION

                if not reverse:
	                self.l_panel.set_new_values(left_panel, no_animation, emotion)
	                self.r_panel.set_new_values(right_panel, no_animation)
                else:
	                self.l_panel.set_new_values(left_panel, no_animation)
	                self.r_panel.set_new_values(right_panel, no_animation, emotion)
                prev_sex = sex
                line = input_file.readline().strip()

        while self.l_panel.is_panel_updating() or self.r_panel.is_panel_updating():
            update_frame(reverse, prev_sex)
            cur_time_in_msec += self.ONE_FRAME_DURATION

        captured = update_frame(reverse, prev_sex)
        while captured:
            captured = update_frame(reverse, prev_sex)

        self.video_writer.release()
        self.cap.release()

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


panel_generator = PanelGenerator()
panel_generator.process_file(args.file_name)
