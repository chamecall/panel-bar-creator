import cv2
import imutils
import numpy as np
from PIL import Image, ImageSequence


class Animator:
    def __init__(self, path, dst_size, frames_limit=None, step_over=1):
        self.seq, self.size = self.decompose_gif(path)
        self.frame_n = 0
        self.len = len(self.seq)

        self.dst_size = dst_size
        self.resize_seq()
        self.elapsed_frames_num = 0
        self.frames_limit = self.len - 1 if frames_limit == -1 else frames_limit
        self.step_over = step_over

    def next(self):
        if self.is_over():
            return None

        self.elapsed_frames_num += self.step_over

        next_frame_num = self.frame_n + self.step_over
        if self.frames_limit is None:
            self.frame_n = next_frame_num % self.len
        elif next_frame_num <= self.frames_limit:
            self.frame_n = next_frame_num
        else:
            return None


        return self.seq[self.frame_n]

    def is_over(self):

        return self.frames_limit is not None and self.elapsed_frames_num + self.step_over >= self.frames_limit

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
