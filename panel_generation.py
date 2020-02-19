import cv2
import numpy as np

from Circle import Circle
from Color import Color
from PanelBar import PanelBar
from RoundedRect import RoundedRect
from Clock import Clock
import argparse
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
	LR_MARGIN = 200
	TOP_MARGIN = 70


	def __init__(self):

		self.video_writer = cv2.VideoWriter('panel_animation.mkv', cv2.VideoWriter_fourcc(*"XVID"), self.VIDEO_FPS,
											self.VIDEO_RESOLUTION)

		self.r_panel = PanelBar('user.png', 'YOU, 21')
		self.l_panel = PanelBar('f_face.png', 'F, 23')
		self.cap = cv2.VideoCapture('vozera.mp4')


		self.lp_x, self.y, self.rp_x = self.LR_MARGIN, self.TOP_MARGIN, self.VIDEO_RESOLUTION[0] - self.r_panel.background.shape[1] - self.LR_MARGIN

	def process_file(self, input_file_name):
		cur_time_in_msecs = 0

		def do_step():
			_, phone = self.cap.read()
			l_panel_fragment = phone[self.y:self.y + self.l_panel.background.shape[0], self.lp_x:self.lp_x + self.l_panel.background.shape[1]]
			r_panel_fragment = phone[self.y:self.y + self.r_panel.background.shape[0], self.rp_x:self.rp_x + self.r_panel.background.shape[1]]

			l_frame  = self.l_panel.updateUI(l_panel_fragment)
			r_frame = self.r_panel.updateUI(r_panel_fragment)
			overlay_transparent(phone, l_frame, (self.lp_x, self.y))
			overlay_transparent(phone, r_frame, (self.rp_x, self.y))


			self.video_writer.write(phone)

		with open(input_file_name, 'r') as input_file:
			line = input_file.readline().strip()

			while line:
				line = line.split(',')
				time, left_panel, right_panel = line[0], line[1:5], line[5:]
				emotion = ''
				if len(right_panel) == 5:
					emotion = right_panel[-1]
					right_panel = right_panel[:-1]

				left_panel, right_panel = list(map(int, left_panel)), list(map(int, right_panel))
				clock = Clock(time)
				while cur_time_in_msecs < clock.total_msecs:
					do_step()
					cur_time_in_msecs += self.ONE_FRAME_DURATION

				self.l_panel.set_new_values(left_panel, emotion)
				self.r_panel.set_new_values(right_panel)
				line = input_file.readline().strip()

		while self.l_panel.is_panel_updating() or self.r_panel.is_panel_updating():
			do_step()
			cur_time_in_msecs += self.ONE_FRAME_DURATION

		self.video_writer.release()
		self.cap.release()


panel_generator = PanelGenerator()
panel_generator.process_file(args.file_name)
