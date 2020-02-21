import cv2
import imutils
import numpy as np
from PIL import Image, ImageSequence


class Animator:
    def __init__(self, path, dst_size):
        self.seq, self.size = self.decompose_gif(path)
        self.frame_n = 0
        self.len = len(self.seq)
        self.dst_size = dst_size
        self.resize_seq()

    def next(self):
        self.frame_n = (self.frame_n + 1) % self.len
        return self.seq[self.frame_n]

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
