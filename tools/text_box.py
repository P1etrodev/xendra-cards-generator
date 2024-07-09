from textwrap import wrap

import pandas as pd
from PIL import ImageDraw
from PIL.ImageFont import FreeTypeFont
from rich.console import Console

console = Console()


class Align:
	LEFT = 0
	CENTER = 1
	RIGHT = 2
	TOP = 3
	BOTTOM = 4


def text_box(
	raw_text: str, image_draw: ImageDraw.Draw, font: FreeTypeFont, max_characters: int,
	x: int, y: int, width: int, height: int,
	horizontal_allignment: Align = Align.LEFT,
	vertical_allignment: Align = Align.TOP,
	highlight_colors: pd.DataFrame = None,
	**kwargs
):
	text = raw_text
	if highlight_colors is not None:
		for _, highlight in highlight_colors.iterrows():
			text = text.replace("@" + highlight["raw_name"], highlight["name"].replace(' ', '_'))
	fill = kwargs.get('fill', '#FFFFFF')
	lines = wrap(text, max_characters)
	
	x_offset = y_offset = 0
	lineheight = font.size * 1.2
	if vertical_allignment == Align.CENTER:
		y = int(y + height / 2)
		y_offset = - (len(lines) * lineheight) / 2
	elif vertical_allignment == Align.BOTTOM:
		y = int(y + height)
		y_offset = - (len(lines) * lineheight)
	
	for line in lines:
		linewidth = font.getlength(line)
		if horizontal_allignment == Align.CENTER:
			x_offset = (width - linewidth) / 2
		elif horizontal_allignment == Align.RIGHT:
			x_offset = width - linewidth
		
		raw_line = line
		if highlight_colors is not None:
			for _, highlight in highlight_colors.iterrows():
				raw_line = raw_line.replace(highlight["name"].replace(' ', '_'), "@" + highlight["raw_name"])
		
		x_cursor = x + x_offset
		
		remaining_line = raw_line
		while remaining_line:
			highlighted = False
			first_char = remaining_line[0]
			if highlight_colors is not None:
				if first_char in '¿¡{[(':
					char_width = font.getlength(first_char)
					image_draw.text((x_cursor, y + y_offset), first_char, font=font, fill=fill)
					x_cursor += char_width
					remaining_line = remaining_line[1:].lstrip()
					continue
				for _, highlight in highlight_colors.iterrows():
					if remaining_line.startswith(placeholder := "@" + highlight["raw_name"]):
						effect_name = highlight["name"]
						color = highlight['r'], highlight["g"], highlight["b"]
						phrase_width = font.getlength(effect_name)
						image_draw.text(
							(x_cursor, y + y_offset), effect_name, font=font,
							fill=color
							)
						x_cursor += phrase_width + font.getlength(' ')
						remaining_line = remaining_line[len(placeholder):].lstrip()
						highlighted = True
						break
			if not highlighted:
				space_index = remaining_line.find(' ')
				if space_index == -1:
					word = remaining_line
				else:
					word = remaining_line[:space_index]
				if any(word.startswith(symbol) for symbol in '.,:;¿?¡!()[]{}'):
					x_cursor -= font.getlength(' ')
				word_width = font.getlength(word)
				image_draw.text((x_cursor, y + y_offset), word, font=font, fill=fill)
				x_cursor += word_width + font.getlength(' ')
				remaining_line = remaining_line[len(word):].lstrip()
		
		y_offset += lineheight