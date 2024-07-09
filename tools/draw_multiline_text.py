from textwrap import wrap

from PIL.ImageDraw import ImageDraw
from PIL.ImageFont import FreeTypeFont
from rich.console import Console

console: Console = Console()


def draw_multiline_text(
	config: dict,
	_draw: ImageDraw,
	_position: tuple[int] | list[int],
	_text: str,
	_font: FreeTypeFont,
	_fill: tuple[int] | list[int] | str,
	_max_width: int,
	highlights: bool = False
):
	symbols = '.,;:?!'
	if highlights:
		highlight_colors: dict = config.get('highlight')
		lines = wrap(_text, width=_max_width)
		y_offset = 0
		current_phrase: list[str] = []
		for line in lines:
			x = _position[0]
			y = _position[1] + y_offset
			words = line.split()
			x_offset = 0
			for word in words:
				word_width = _font.getlength(word.replace('_', ""))
				if any(word.endswith(symbol) for symbol in symbols):
					parts = []
					current_part = ""
					for char in word:
						if char in symbols:
							if current_part:
								parts.append(current_part)
								current_part = ""
							parts.append(char)
						else:
							current_part += char
					if current_part:
						parts.append(current_part)
					for part in parts:
						if (
							(lowered := part.lower()) in highlight_colors
						):
							_draw.text((x + x_offset, y), part, font=_font, fill=highlight_colors[lowered])
						else:
							_draw.text((x + x_offset, y), part, font=_font, fill=_fill)
						x_offset += _font.getlength(part) + (_font.getlength(' ') if part in symbols else 0)
				# width
				else:
					if (lowered := word.lower()) in highlight_colors:
						_draw.text((x + x_offset, y), word, font=_font, fill=highlight_colors[lowered])
					else:
						_draw.text((x + x_offset, y), word.replace('_', ""), font=_font, fill=_fill)
					
					current_phrase.append(word)
					
					x_offset += word_width + (_font.getlength(' '))
			y_offset += _font.size
	else:
		lines = wrap(_text, width=_max_width)
		y_offset = 0
		for line in lines:
			_draw.text((_position[0], _position[1] + y_offset), line, font=_font, fill=_fill)
			y_offset += _font.size

# def draw_multiline_text(
# 	config: dict,
# 	_draw: ImageDraw,
# 	_position: tuple[int, int],
# 	_text: str,
# 	_font: FreeTypeFont,
# 	_fill: tuple[int, int, int] | str,
# 	_max_width: int,
# 	highlights: bool = False
# ):
# 	symbols = '.,;:?!()'
#
# 	if highlights:
# 		highlight_colors = config.get('highlight', {})
# 		lines = wrap(_text, width=_max_width)
# 		y_offset = 0
# 		current_phrase = []
#
# 		for line in lines:
# 			x = _position[0]
# 			y = _position[1] + y_offset
# 			words = line.split()
# 			x_offset = 0
#
# 			for word in words:
# 				parts = filter(lambda item: item != "", re.split(f"([{symbols}])", word))
#
# 				for part in parts:
# 					space_length = _font.getlength(' ')
# 					if part in symbols:
# 						x_offset -= space_length
# 					if part.lower() in highlight_colors:
# 						_draw.text((x + x_offset, y), part, font=_font, fill=highlight_colors[part.lower()])
# 					else:
# 						_draw.text((x + x_offset, y), part, font=_font, fill=_fill)
# 					x_offset += _font.getlength(part) + space_length
#
# 				current_phrase.append(word)
#
# 			y_offset += _font.size
#
# 	else:
# 		lines = wrap(_text, width=_max_width)
# 		y_offset = 0
#
# 		for line in lines:
# 			_draw.text((_position[0], _position[1] + y_offset), line, font=_font, fill=_fill)
# 			y_offset += _font.size