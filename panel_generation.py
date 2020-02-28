import argparse
import cv2
from PIL import ImageFont
from Circle import Circle
from PanelBar import PanelBar
from PanelInfoScheduler import PanelInfoScheduler
from Rect import Rect
from Utils import overlay_transparent
from ObjectDetectionAnimator import ObjectDetectionAnimator
from Utils import draw_text_in_pos
from FaceAnimationScheduler import FaceAnimationScheduler
from AnimationData import AnimationData

parser = argparse.ArgumentParser()

parser.add_argument('panel_info_file', type=str, help='input panel info file name')
parser.add_argument('object_detection_file', type=str, help='input object detection info file name')
parser.add_argument('face_animation_file', type=str, help='input face animation info file name')

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
    OBJ_DETECT_GIF = 'raw/object_detection.gif'
    OBJ_DETECT_DUR_IN_FRAMES = 30
    FONT = ImageFont.truetype('LatoBlack.ttf', 25)

    def __init__(self, path_to_panel_file, path_to_obj_detect_file, path_to_face_animation_file):

        self.video_writer = cv2.VideoWriter('panel_animation.mp4', cv2.VideoWriter_fourcc(*"mp4v"), self.VIDEO_FPS,
                                            self.VIDEO_RESOLUTION)
        self.panel_info_scheduler = PanelInfoScheduler(path_to_panel_file)
        self.obj_detect_animator = ObjectDetectionAnimator(path_to_obj_detect_file, self.OBJ_DETECT_GIF)
        self.face_animation_scheduler = FaceAnimationScheduler(path_to_face_animation_file)
        self.r_panel = PanelBar('avatars/male.png', 'M', 21)
        self.l_panel = PanelBar('avatars/female.png', 'F', '23')
        self.cap = cv2.VideoCapture('vozera_cut.mp4')
        self.male_frame = cv2.imread(self.MALE_FRAME_FILE, cv2.IMREAD_UNCHANGED)
        self.female_frame = cv2.imread(self.FEMALE_FRAME_FILE, cv2.IMREAD_UNCHANGED)
        self.lp_x, self.y, self.rp_x = self.LR_MARGIN, self.TOP_MARGIN, self.VIDEO_RESOLUTION[0] - \
                                       self.r_panel.background.shape[1] - self.LR_MARGIN
        self.prev_sex = self.sex = ''
        self.reverse = False
        self.animation_data = None

    def process_file(self):

        cur_time_in_msec = 0
        self.reverse = False

        while True:
            captured, frame = self.cap.read()
            if not captured:
                break

            cur_time_in_msec += self.ONE_FRAME_DURATION
            changed, panel_info = self.panel_info_scheduler.get_info_by_time(cur_time_in_msec)
            animation_frame = self.obj_detect_animator.next_frame(cur_time_in_msec)
            face_animation_info = self.face_animation_scheduler.get_info_by_time(cur_time_in_msec)
            if face_animation_info:
                start_rect, side = face_animation_info
                self.cur_size = side
                if side == 'L':
                    end_rect = self.l_panel.photo_cell
                    end_rect = Rect(self.lp_x + end_rect.left, self.TOP_MARGIN + end_rect.top, end_rect.width,
                                    end_rect.height)
                else:
                    end_rect = self.r_panel.photo_cell
                    end_rect = Rect(self.rp_x + end_rect.left, self.y + end_rect.top, end_rect.width,
                                    end_rect.height)
                bitmap = frame[start_rect.top:start_rect.top+start_rect.height, start_rect.left:start_rect.left+start_rect.width]
                self.animation_data = AnimationData(bitmap, start_rect, end_rect, 10)

            self.update_panels(panel_info, changed)

            frame = self.overlay_object_detection_animation(frame, animation_frame)
            frame = self.overlay_panels(frame, self.reverse, self.sex)
            frame = self.overlay_face_animation(frame)

            self.video_writer.write(frame)

        self.video_writer.release()
        self.cap.release()

    def overlay_face_animation(self, frame):

        if not self.animation_data:
            return frame


        scaled_bitmap, new_pos = self.animation_data.get_new_located_bitmap()
        overlay_transparent(frame, scaled_bitmap, (new_pos.x, new_pos.y))

        if not self.animation_data.steps_left():
            if self.cur_size == 'L':
                self.l_panel.photo = scaled_bitmap
            else:
                self.r_panel.photo = scaled_bitmap
            self.animation_data = None

        return frame

    def update_panels(self, panel_info, changed):
        if panel_info:
            clock, left_values, right_values, self.sex, emotion = panel_info
            self.reverse = True if 'F' in self.sex else False
            no_animation = True if self.prev_sex != self.sex else False

            if changed:
                if not self.reverse:
                    self.l_panel.set_new_values(left_values, no_animation, emotion)
                    self.r_panel.set_new_values(right_values, no_animation)
                else:
                    self.l_panel.set_new_values(left_values, no_animation)
                    self.r_panel.set_new_values(right_values, no_animation, emotion)
                self.prev_sex = self.sex

    def overlay_panels(self, frame, reverse, sex):
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

        return frame

    def extract_rect_image_from_background(self, background, rect: Rect):
        return background[rect.top:rect.top + rect.height, rect.left:rect.left + rect.width]

    def overlay_object_detection_animation(self, frame, animation_frame):
        if animation_frame is not None:
            pos = self.obj_detect_animator.animation_rect.get_pos()
            overlay_transparent(frame, animation_frame, pos)
            frame = draw_text_in_pos(frame, self.obj_detect_animator.label, self.FONT, (pos[0] + 10, pos[1] - 12))
        return frame


panel_generator = PanelGenerator(args.panel_info_file, args.object_detection_file, args.face_animation_file)
panel_generator.process_file()
