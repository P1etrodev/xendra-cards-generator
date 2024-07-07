from textwrap import wrap

from PIL.ImageDraw import ImageDraw
from PIL.ImageFont import FreeTypeFont


def get_max_text_length(_draw: ImageDraw, _text: str, _font: FreeTypeFont, _max_width: int):
	lines = wrap(_text, width=_max_width)
	_max_length = max(_draw.textlength(line, font=_font) for line in lines)
	return _max_length