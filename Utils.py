import numpy as np
from PIL import ImageDraw, Image

from Rect import Rect


def draw_text_in_center(image, text, font, rect: Rect, x_shift=0, y_shift=0, shadow_shift=2):
	img_pil = Image.fromarray(image)
	draw = ImageDraw.Draw(img_pil)
	text_size = draw.textsize(text, font=font)
	text_x = int((rect.width - text_size[0]) / 2) + rect.left + x_shift
	text_y = int((rect.height - text_size[1]) / 2) + rect.top + y_shift
	draw.text((text_x + shadow_shift, text_y + shadow_shift), text, font=font, fill=(0, 0, 0))
	draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))
	return np.array(img_pil)


def draw_text_in_pos(image, text, font, pos, shadow_shift=2):
	img_pil = Image.fromarray(image)
	draw = ImageDraw.Draw(img_pil)
	draw.text((pos[0] + shadow_shift, pos[1] + shadow_shift), text, font=font, fill=(0, 0, 0))
	draw.text(pos, text, font=font, fill=(255, 255, 0))
	return np.array(img_pil)


def overlay_transparent(background, overlay, pos):
	x, y = pos
	
	background_width = background.shape[1]
	background_height = background.shape[0]
	
	if x >= background_width or y >= background_height:
		return background
	
	h, w = overlay.shape[0], overlay.shape[1]
	
	if x + w > background_width:
		w = background_width - x
		overlay = overlay[:, :w]
	
	if y + h > background_height:
		h = background_height - y
		overlay = overlay[:h]
	
	if overlay.shape[2] < 4:
		overlay = np.concatenate(
			[
				overlay,
				np.ones((overlay.shape[0], overlay.shape[1], 1), dtype=overlay.dtype) * 255
			],
			axis=2,
		)
	
	overlay_image = overlay[..., :3]
	mask = overlay[..., 3:] / 255.0
	
	background[y:y + h, x:x + w] = (1.0 - mask) * background[y:y + h, x:x + w] + mask * overlay_image
	
	return background
