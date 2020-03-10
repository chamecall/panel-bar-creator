import argparse
import cv2
from PIL import ImageFont

from Color import Color
from Circle import Circle
from PanelBar import PanelBar
from PanelInfoScheduler import PanelInfoScheduler
from Rect import Rect
from Utils import overlay_transparent
from ObjectDetectionAnimator import ObjectDetectionAnimator
from Utils import draw_text_in_pos
from FaceAnimationScheduler import FaceAnimationScheduler
from AnimationMover import AnimationMover
from Animator import Animator
from Clock import Clock
import moviepy.editor as mpe
import subprocess
import time
import pathlib
from os import path

parser = argparse.ArgumentParser()
parser.add_argument('input_video', type=str, help='input videofile name')
parser.add_argument('panel_info_file', type=str, help='input panel info file name')
parser.add_argument('object_detection_file', type=str, help='input object detection info file name')
parser.add_argument('face_animation_file', type=str, help='input face animation info file name')
parser.add_argument('-start', type=int, help='start time in msecs')
parser.add_argument('-ad', type=int, help='animation duration in frames, def is 9')
parser.add_argument('-vp', type=int, help='vertical paddings in top panel, def is 10')
parser.add_argument('-cr', type=int, help='the thickness of radius of the circles, def is 9')
parser.add_argument('-cgt', type=int, help='the less the more shifted gradient to target color, [0:255], def is 220')
parser.add_argument('-cts', type=float, help='circle text scale, def is 1.5')
parser.add_argument('-ctt', type=int, help='circle text thickness, def is 3')
parser.add_argument('-tts', type=float, help='total text scale, def is 2.0')
parser.add_argument('-ttt', type=int, help='total text thickness, def is 3')
args = parser.parse_args()

start_from = 0
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
if args.start:
	print(args.start)
	start_from = args.start


class PanelGenerator:
	VIDEO_FPS = 29.97002997002997

	VIDEO_RESOLUTION = 1920, 1080
	# in msec
	ONE_FRAME_DURATION = 1 / VIDEO_FPS * 1000
	LR_MARGIN = 139
	TOP_MARGIN = 155
	MALE_FRAME_FILE = 'frame/mobile.png'
	FEMALE_FRAME_FILE = 'frame/glasses.png'
	OBJ_DETECT_GIF = 'raw/object_detection.gif'
	OBJ_DETECT_DUR_IN_FRAMES = 30
	FONT = ImageFont.truetype('LatoBlack.ttf', 25)
	FACE_DETECT_ANIMATION = 'raw/face_detect.gif'

	OUTPUT_FILE_NAME = 'completed_result.mp4'
	SPLITTED_AUDIO_FILE_NAME = 'splitted_audio.wav'
	TEMP_FILE_NAME = 'temp.mkv'

	
	def __init__(self, path_to_video, path_to_panel_file, path_to_obj_detect_file, path_to_face_animation_file):
		
		self.video_writer = cv2.VideoWriter(self.TEMP_FILE_NAME, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
		                                    self.VIDEO_FPS,
		                                    self.VIDEO_RESOLUTION)
		self.panel_info_scheduler = PanelInfoScheduler(path_to_panel_file)
		self.obj_detect_animator = ObjectDetectionAnimator(path_to_obj_detect_file, self.OBJ_DETECT_GIF)
		self.face_animation_scheduler = FaceAnimationScheduler(path_to_face_animation_file)
		self.r_panel = PanelBar('M', 23)
		self.l_panel = PanelBar('F', 21)
		scanned_male_avatar = cv2.imread('avatars/scanned_male.png', cv2.IMREAD_UNCHANGED)
		male_avatar = cv2.imread('avatars/male.png', cv2.IMREAD_UNCHANGED)
		self.scanned_female_avatar = None
		female_avatar = cv2.imread('avatars/female.png', cv2.IMREAD_UNCHANGED)
		
		avatar_size = self.l_panel.photo_cell.width, self.l_panel.photo_cell.height
		
		self.scanned_male_avatar = cv2.resize(scanned_male_avatar, avatar_size)
		self.male_avatar = cv2.resize(male_avatar, avatar_size)
		self.female_avatar = cv2.resize(female_avatar, avatar_size)
		
		self.cap = cv2.VideoCapture(path_to_video)
		mpe.AudioFileClip(path_to_video).write_audiofile(self.SPLITTED_AUDIO_FILE_NAME)



		self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_from / self.ONE_FRAME_DURATION)
		
		self.male_frame = cv2.imread(self.MALE_FRAME_FILE, cv2.IMREAD_UNCHANGED)
		self.female_frame = cv2.imread(self.FEMALE_FRAME_FILE, cv2.IMREAD_UNCHANGED)
		self.lp_x, self.y, self.rp_x = self.LR_MARGIN, self.TOP_MARGIN, self.VIDEO_RESOLUTION[0] - \
		                               self.r_panel.background.shape[1] - self.LR_MARGIN
		self.prev_sex = self.sex = ''
		self.reverse = False
		self.animation_data = None
		self.face_detection_bound_animator = None
		self.cur_side = None
		self.face_position = None
	
	def process_file(self):
		
		cur_time_in_msec = -2580 + start_from
		self.reverse = False
		
		while True:
			captured, frame = self.cap.read()
			if not captured:
				break
			
			cur_time_in_msec += self.ONE_FRAME_DURATION
			
			if cur_time_in_msec >= Clock('0:30:000').total_msecs and not self.face_detection_bound_animator:
				self.face_position = (743, 65)
				self.face_detection_bound_animator = Animator('raw/face_detect.gif',
				                                              (440, 440), 70)
			
			print(cur_time_in_msec / 1000)
			changed, panel_info = self.panel_info_scheduler.get_info_by_time(cur_time_in_msec)
			animation_frame = self.obj_detect_animator.next_frame(cur_time_in_msec)
			face_animation_info = self.face_animation_scheduler.get_info_by_time(cur_time_in_msec)
			self.check_next_face(frame, face_animation_info)
			
			frame = self.overlay_face_animation(frame)
			self.update_panels(panel_info, changed)
			
			frame = self.overlay_object_detection_animation(frame, animation_frame)
			frame = self.overlay_panels(frame, self.reverse, self.sex)
			frame = self.overlay_face_detection_bound(frame)
			
			cv2.imshow('frame', frame)
			cv2.waitKey(1)

			self.video_writer.write(frame)
		
		self.video_writer.release()
		self.cap.release()
		cur_dir = str(pathlib.Path().absolute())
		subprocess.call(['ffmpeg', '-i', path.join(cur_dir, self.TEMP_FILE_NAME), '-i', path.join(cur_dir, self.SPLITTED_AUDIO_FILE_NAME),
		 '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', path.join(cur_dir, self.OUTPUT_FILE_NAME)])
	
	def overlay_face_detection_bound(self, frame):
		if self.face_detection_bound_animator and not self.face_detection_bound_animator.is_over():
			face_detection_bound_frame = self.face_detection_bound_animator.next()
			
			overlay_transparent(frame, face_detection_bound_frame, self.face_position)
		return frame
	
	def check_next_face(self, frame, face_animation_info):
		if face_animation_info:
			start_rect, side = face_animation_info
			print('start', start_rect.__dict__)
			self.cur_side = side
			end_rect = Rect(318, 181, 66, 67)
			bitmap = frame[start_rect.top:start_rect.top + start_rect.height,
			         start_rect.left:start_rect.left + start_rect.width]
			
			self.animation_data = AnimationMover(bitmap.copy(), start_rect, end_rect, 15)
	
	def overlay_face_animation(self, frame):
		
		if not self.animation_data:
			return frame
		
		scaled_bitmap, new_pos = self.animation_data.get_new_located_bitmap()
		overlay_transparent(frame, scaled_bitmap, (new_pos.x, new_pos.y))
		
		if not self.animation_data.steps_left():
			self.scanned_female_avatar = scaled_bitmap
			self.l_panel.photo = self.scanned_female_avatar
			self.animation_data = None
		
		return frame
	
	def update_panels(self, panel_info, changed):
		if panel_info:
			clock, left_values, right_values, self.sex, emotion = panel_info
			self.reverse = True if 'F' in self.sex else False
			view_changed = True if self.prev_sex != self.sex else False
			
			if changed:
				if not self.reverse:
					self.r_panel.photo = self.male_avatar
					self.l_panel.photo = self.scanned_female_avatar
				else:
					self.l_panel.photo = self.female_avatar
					self.r_panel.photo = self.scanned_male_avatar
			
			if changed:
				if not self.reverse:
					self.l_panel.set_new_values(left_values, view_changed, emotion)
					self.r_panel.set_new_values(right_values, view_changed)
				else:
					self.l_panel.set_new_values(left_values, view_changed)
					self.r_panel.set_new_values(right_values, view_changed, emotion)
				self.prev_sex = self.sex
	
	def overlay_panels(self, frame, reverse, sex):
		l_panel_fragment = frame[self.y:self.y + self.l_panel.background.shape[0],
		                   self.lp_x:self.lp_x + self.l_panel.background.shape[1]]
		r_panel_fragment = frame[self.y:self.y + self.r_panel.background.shape[0],
		                   self.rp_x:self.rp_x + self.r_panel.background.shape[1]]
		
		if not reverse:
			l_frame = self.l_panel.update_UI(l_panel_fragment, side='L')
			r_frame = self.r_panel.update_UI(r_panel_fragment, side='R')
		else:
			r_frame = self.l_panel.update_UI(r_panel_fragment, side='R')
			l_frame = self.r_panel.update_UI(l_panel_fragment, side='L')
		
		overlay_transparent(frame, l_frame, (self.lp_x, self.y))
		overlay_transparent(frame, r_frame, (self.rp_x, self.y))

		# if 'M' in sex:
		#     overlay_transparent(frame, self.male_frame, (0, 0))
		# elif 'F' in sex:
		#     overlay_transparent(frame, self.female_frame, (0, 0))
		
		return frame
	
	def extract_rect_image_from_background(self, background, rect: Rect):
		return background[rect.top:rect.top + rect.height, rect.left:rect.left + rect.width]
	
	def overlay_object_detection_animation(self, frame, animation_frame):
		if animation_frame is not None:
			pos = self.obj_detect_animator.animation_rect.get_pos()
			overlay_transparent(frame, animation_frame, pos)
			frame = draw_text_in_pos(frame, self.obj_detect_animator.label, self.FONT, (pos[0], pos[1] - 30))
		return frame


panel_generator = PanelGenerator(args.input_video, args.panel_info_file, args.object_detection_file, args.face_animation_file)
panel_generator.process_file()
