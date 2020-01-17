import cv2

from Clock import Clock
from Color import Color
from PanelBar import PanelBar
from RoundedRect import RoundedRect

PANEL_SIZE = 1366, 400
BOTTOM_BLOCK_WIDTH = int(PANEL_SIZE[0] * 0.4)
VIDEO_FPS = 25

# in msec
ONE_FRAME_DURATION = 1 / VIDEO_FPS * 1000

l_panel_vr = cv2.VideoWriter('left_panel.mkv', cv2.VideoWriter_fourcc(*"XVID"), VIDEO_FPS, PANEL_SIZE)
r_panel_vr = cv2.VideoWriter('right_panel.mkv', cv2.VideoWriter_fourcc(*"XVID"), VIDEO_FPS, PANEL_SIZE)

window_name = 'Image'

r_panel = PanelBar(RoundedRect(PANEL_SIZE[0], PANEL_SIZE[1] // 2, Color.PANEL_COLOR, round_bl=False),
                   RoundedRect(BOTTOM_BLOCK_WIDTH, PANEL_SIZE[1] // 2, Color.PANEL_COLOR, round_top=False))
l_panel = PanelBar(RoundedRect(PANEL_SIZE[0], PANEL_SIZE[1] // 2, Color.PANEL_COLOR, round_br=False),
                   RoundedRect(BOTTOM_BLOCK_WIDTH, PANEL_SIZE[1] // 2, Color.PANEL_COLOR, round_top=False),
                   reverse=True)

# panel.set_new_values([69, 99, 73, 48])

# in msec
cur_time_in_msecs = 0
input_file_name = 'input.txt'

with open(input_file_name, 'r') as input_file:
    line = input_file.readline().strip()

    while line:
        line = line.split(',')
        time, left_panel, right_panel = line[0], line[1:5], line[5:]
        left_panel, right_panel = list(map(int, left_panel)), list(map(int, right_panel))
        clock = Clock(time)
        while cur_time_in_msecs < clock.total_msecs:
            l_frame, r_frame = l_panel.updateUI(), r_panel.updateUI()
            #cv2.imshow(window_name, frame)
            l_panel_vr.write(l_frame), r_panel_vr.write(r_frame)
            cur_time_in_msecs += ONE_FRAME_DURATION
            key = cv2.waitKey(100)

        l_panel.set_new_values(left_panel)
        r_panel.set_new_values(right_panel)
        line = input_file.readline().strip()

while l_panel.is_panel_updating() or r_panel.is_panel_updating():
    l_frame, r_frame = l_panel.updateUI(), r_panel.updateUI()

    #cv2.imshow(window_name, frame)
    l_panel_vr.write(l_frame), r_panel_vr.write(r_frame)
    cur_time_in_msecs += ONE_FRAME_DURATION
    key = cv2.waitKey(1)

l_panel_vr.release()
r_panel_vr.release()
