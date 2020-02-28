import imageio
import urllib.request
import cv2
import numpy as np
from PIL import Image
from PIL import Image, ImageSequence


def decompose_gif(path):
	imgs = []
	gif = Image.open(path)
	for frame in ImageSequence.Iterator(gif):
		bgra_im = cv2.cvtColor(np.array(frame.convert('RGBA')), cv2.COLOR_RGBA2BGRA)
		imgs.append(bgra_im)

	return imgs, gif.size



brain_seq, size = decompose_gif('new_brain.gif')
nums = len(brain_seq)
print(brain_seq[0].shape)
print((*size, 3))
back = np.ones((3, *size))
print(back.shape)
back = (0, 0, 255)

i = 0

while True:
    cv2.imshow("gif", back)
    if cv2.waitKey(1) & 0xFF == 27:
        break
    i = (i+1)%nums
cv2.destroyAllWindows()