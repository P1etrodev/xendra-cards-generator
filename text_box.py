from textwrap import wrap

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


# def text_box(
# 	text: str, image_draw: ImageDraw, font: FreeTypeFont, max_characters: int,
# 	x: int, y: int, width: int, height: int,
# 	horizontal_allignment: Align = Align.LEFT,
# 	vertical_allignment: Align = Align.TOP,
# 	highlight_colors: dict[str, tuple[int, int, int]] = None,
# 	**kwargs
# ):
# 	fill = kwargs.get('fill', '#FFFFFF')
# 	lines = wrap(text, max_characters)
#
# 	# Ajustamos las alineaciones verticales
# 	x_offset = y_offset = 0
# 	lineheight = font.size * 1.2  # Margen de 0.2x la altura de la fuente
# 	if vertical_allignment == Align.CENTER:
# 		y = int(y + height / 2)
# 		y_offset = - (len(lines) * lineheight) / 2
# 	elif vertical_allignment == Align.BOTTOM:
# 		y = int(y + height)
# 		y_offset = - (len(lines) * lineheight)
#
# 	# Dibujamos cada línea de texto con el posible resaltado
# 	# full = False
# 	for line in lines:
# 		linewidth = font.getlength(line)
# 		if horizontal_allignment == Align.CENTER:
# 			x_offset = (width - linewidth) / 2
# 		elif horizontal_allignment == Align.RIGHT:
# 			x_offset = width - linewidth
#
# 		x_cursor = x + x_offset  # Posición inicial del cursor en x
#
# 		remaining_line = line
# 		while remaining_line:
# 			highlighted = False
# 			first_char = remaining_line[0]
# 			if first_char in '¿¡{[(':
# 				char_width = font.getlength(first_char)
# 				image_draw.text((x_cursor, y + y_offset), first_char, font=font, fill=fill)
# 				x_cursor += char_width
# 				remaining_line = remaining_line[1:].lstrip()
# 				continue
# 			for phrase, color in highlight_colors.items():
# 				if len(phrase_words := phrase.split()) > 1:
# 					# Highlights full phrases
# 					if remaining_line.startswith(phrase):
# 						phrase_width = font.getlength(phrase)
# 						image_draw.text((x_cursor, y + y_offset), phrase, font=font, fill=color)
# 						x_cursor += phrase_width + font.getlength(' ')
# 						remaining_line = remaining_line[len(phrase):].lstrip()
# 						highlighted = True
# 						break
# 					else:
# 						for word in phrase_words:
# 							if remaining_line == word:
# 								word_width = font.getlength(word)
# 								image_draw.text((x_cursor, y + y_offset), word, font=font, fill=color)
# 								x_cursor += word_width + font.getlength(' ')
# 								remaining_line = remaining_line[len(word):].lstrip()
# 								highlighted = True
# 								break
# 				else:
# 					# Highlights single words
# 					if remaining_line.startswith(phrase):
# 						word_width = font.getlength(phrase)
# 						image_draw.text((x_cursor, y + y_offset), phrase, font=font, fill=color)
# 						x_cursor += word_width + font.getlength(' ')
# 						remaining_line = remaining_line[len(phrase):].lstrip()
# 						highlighted = True
# 						break
# 			if not highlighted:
# 				space_index = remaining_line.find(' ')
# 				if space_index == -1:
# 					word = remaining_line
# 				else:
# 					word = remaining_line[:space_index]
# 				if any(word.startswith(symbol) for symbol in '.,:;¿?¡!()[]{}'):
# 					x_cursor -= font.getlength(' ')
# 				word_width = font.getlength(word)
# 				image_draw.text((x_cursor, y + y_offset), word, font=font, fill=fill)
# 				x_cursor += word_width + font.getlength(' ')
# 				remaining_line = remaining_line[len(word):].lstrip()
#
# 		y_offset += lineheight

def text_box(
	raw_text: str, image_draw: ImageDraw, font: FreeTypeFont, max_characters: int,
	x: int, y: int, width: int, height: int,
	horizontal_allignment: Align = Align.LEFT,
	vertical_allignment: Align = Align.TOP,
	highlight_colors: dict[str, dict[str, str]] = None,
	**kwargs
):
	text = raw_text
	for raw_effect_name, data in highlight_colors.items():
		text = text.replace("@" + raw_effect_name, data.get("name").replace(' ', '_'))
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
		for raw_effect_name, data in highlight_colors.items():
			raw_line = raw_line.replace(data.get("name").replace(' ', '_'), "@" + raw_effect_name)
			
		x_cursor = x + x_offset
		
		remaining_line = raw_line
		while remaining_line:
			highlighted = False
			first_char = remaining_line[0]
			if first_char in '¿¡{[(':
				char_width = font.getlength(first_char)
				image_draw.text((x_cursor, y + y_offset), first_char, font=font, fill=fill)
				x_cursor += char_width
				remaining_line = remaining_line[1:].lstrip()
				continue
			for raw_effect_name, data in highlight_colors.items():
				if remaining_line.startswith(raw_effect_name := "@" + raw_effect_name):
					effect_name, color = data.get("name"), data.get('color')
					phrase_width = font.getlength(effect_name)
					image_draw.text((x_cursor, y + y_offset), effect_name, font=font, fill=color)
					x_cursor += phrase_width + font.getlength(' ')
					remaining_line = remaining_line[len(raw_effect_name):].lstrip()
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