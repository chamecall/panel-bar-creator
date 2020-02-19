
from PIL import ImageFont, ImageDraw, Image
from Rect import Rect
import numpy as np


def draw_text_in_center_with_shadow(image, text, font, rect:Rect, x_shift = 0, y_shift = 0, shadow_shift=2):
	img_pil = Image.fromarray(image)
	draw = ImageDraw.Draw(img_pil)
	text_size = draw.textsize(text, font=font)
	text_x = int((rect.width - text_size[0]) / 2) + rect.left + x_shift
	text_y = int((rect.height - text_size[1]) / 2) + rect.top + y_shift
	draw.text((text_x + 2, text_y + 2), text, font=font, fill=(0, 0, 0))
	draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))	
	return np.array(img_pil)

