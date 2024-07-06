import sys
from configparser import ConfigParser
from os import mkdir, remove
from pathlib import Path
from textwrap import wrap

import pandas as pd
from PIL import Image, ImageColor, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont
from html2text import html2text
from markdown import markdown

is_app_frozen = hasattr(sys, "frozen")

data_path = Path("./cards_data.xlsx")
cards_folder = Path("cards")
max_length = 16

if not cards_folder.exists():
	mkdir(cards_folder)
else:
	print(f'Cards found, removing.')
	count = 0
	for file in cards_folder.glob('*'):
		remove(file)
		count += 1
	print(f'{count} cards removed.')

if not data_path.exists():
	print(
		"This app must be in the same folder as a file called 'cards_data.xlsx' containing the "
		"cards information."
	)
	sys.exit()


def load_config() -> dict:
	config_file = Path('config.ini')
	
	if not config_file.exists():
		print('Configuration file not found, Card Generator will use the default configuration.')
		return None
	
	_config = ConfigParser()
	_config.read('config.ini')
	
	_parsed_config = {}
	
	for section in _config.sections():
		_parsed_config[section] = {}
		for option in _config.options(section):
			_parsed_config[section][option] = eval(_config.get(section, option))
	
	if 'highlight' in _parsed_config:
		for key, value in _parsed_config['highlight'].items():
			try:
				color_tuple = ImageColor.getrgb(value)
				_parsed_config['highlight'][key.lower()] = color_tuple
			except ValueError:
				print(f'{value} ({key}) is not a valid color. This term will be ignored.')
	
	return _parsed_config


config = load_config()

df = pd.read_excel(data_path)

df.dropna(inplace=True)

cards = df.to_dict(orient='records')

font_config = config.get('font')
head_font = ImageFont.truetype(
	"./Zabdilus.ttf", (
		90 if font_config is None else font_config.get('head_normal')
	)
	)
head_font_md = ImageFont.truetype(
	"./Zabdilus.ttf", (
		70 if font_config is None else font_config.get('head_medium')
	)
	)
body_font = ImageFont.truetype(
	"./AGENCYB.ttf", (
		60 if font_config is None else font_config.get('body_normal')
	)
	)
body_font_md = ImageFont.truetype(
	"./AGENCYB.ttf", (
		46 if font_config is None else font_config.get('body_medium')
	)
	)
body_font_sm = ImageFont.truetype(
	"./AGENCYB.ttf", (
		40 if font_config is None else font_config.get('body_small')
	)
	)

print('Generating cards...')


def draw_multiline_text(
	_draw: ImageDraw.ImageDraw,
	_position: tuple[int] | list[int],
	_text: str,
	_font: ImageFont.FreeTypeFont,
	_fill: tuple[int] | list[int] | str,
	_max_width: int,
	highlights: bool = False
):
	if highlights:
		highlight_colors = config.get('highlight')
		lines = wrap(_text, width=_max_width)
		y_offset = 0
		for line in lines:
			x = _position[0]
			y = _position[1] + y_offset
			words = line.split()
			x_offset = 0
			for word in words:
				word_width = _font.getlength(word)
				symbols = '.,;:?!'
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
						if (lowered := part.lower()) in highlight_colors:
							_draw.text((x + x_offset, y), part, font=_font, fill=highlight_colors[lowered])
						else:
							_draw.text((x + x_offset, y), part, font=_font, fill=_fill)
						x_offset += _font.getlength(part) + (_font.getlength(' ') if part in symbols else 0)
					# width
				else:
					if (lowered := word.lower()) in highlight_colors:
						_draw.text((x + x_offset, y), word, font=_font, fill=highlight_colors[lowered])
					else:
						_draw.text((x + x_offset, y), word, font=_font, fill=_fill)
					x_offset += word_width + _font.getlength(' ')  # Add space width
			
			y_offset += _font.size  # Move to next line
	else:
		lines = wrap(_text, width=_max_width)
		y_offset = 0
		for line in lines:
			_draw.text((_position[0], _position[1] + y_offset), line, font=_font, fill=_fill)
			y_offset += _font.size

# Ejemplo de uso:
# draw_multiline_text(draw, position, text, font, fill, max_width, highlights=highlight_colors)


def get_max_text_length(_draw: ImageDraw, _text: str, _font: FreeTypeFont, max_width):
	lines = wrap(_text, width=max_width)
	_max_length = max(_draw.textlength(line, font=_font) for line in lines)
	return _max_length


for index, card in enumerate(cards):
	print(f'Generating "{card.get("title")}"...')
	
	if is_app_frozen:
		img = Image.new("RGBA", (1080, 1550), (255, 0, 0, 0))
	else:
		img = Image.open("Template.jpg")
	
	draw = ImageDraw.Draw(img)
	
	# Title
	text = html2text(markdown(card.get('title').upper())).strip()
	font = head_font_md if len(text) > 18 else head_font
	text_length = get_max_text_length(draw, text, font, max_width=30)
	position = ((img.width - text_length) / 2, 65 if len(text) <= 18 else 75)
	draw_multiline_text(draw, position, text, font, (255, 255, 255), 30)
	
	# Range
	text = html2text(markdown(card.get('range').upper())).strip()
	position = (70, 35)
	draw.text(position, text, (255, 255, 255), font=head_font)
	
	# Type
	text = html2text(markdown(card.get('type').upper())).strip()
	text_length = draw.textlength(text, font=head_font)
	position = (img.width - text_length - 85, 35)
	draw.text(position, text, (255, 255, 255), font=head_font)
	
	# Description
	text = html2text(markdown(card.get('description'))).strip()
	description_config = config.get('description')
	position = [
		80 if description_config is None else description_config.get('padding_left'),
		img.height - (700 if description_config is None else description_config.get('padding_top'))
	]
	is_too_long = len(text) > (
		275 if description_config is None else description_config.get('too_long_characters')
	)
	draw_multiline_text(
		draw, position, text, body_font_md if is_too_long else body_font, (0, 0, 0),
		(
			56 if description_config is None else description_config.get('long_max_characters_per_line')
		) if is_too_long else (
			42 if description_config is None else description_config.get('short_max_characters_per_line')
		), True
	)
	
	# Worth
	text = html2text(markdown(card.get('worth'))).strip()
	if len(text) > max_length:
		position = [150, img.height - 235]
		draw_multiline_text(draw, position, text, body_font_sm, (255, 255, 255), max_length)
	else:
		position = (150, img.height - 225)
		draw.text(position, text, (255, 255, 255), font=body_font)
	
	# Delay
	text = html2text(markdown(card.get('delay'))).strip()
	if len(text) > max_length:
		position = [150, img.height - 125]
		draw_multiline_text(draw, position, text, body_font_sm, (255, 255, 255), max_length)
	else:
		position = (150, img.height - 115)
		draw.text(position, text, (255, 255, 255), font=body_font)
	
	# Effect
	text = html2text(markdown(card.get('effect'))).strip()
	if len(text) > max_length:
		position = [img.width / 2 + 100, img.height - 235]
		draw_multiline_text(draw, position, text, body_font_sm, (255, 255, 255), max_length)
	else:
		text_length = draw.textlength(text, font=body_font)
		position = (img.width / 2 + 100, img.height - 225)
		draw.text(position, text, (255, 255, 255), font=body_font)
	
	# Effect type
	text = html2text(markdown(card.get('effect_type'))).strip()
	if len(text) > max_length:
		position = [img.width / 2 + 100, img.height - 125]
		draw_multiline_text(draw, position, text, body_font_sm, (255, 255, 255), max_length)
	else:
		text_length = draw.textlength(text, font=body_font)
		position = (img.width / 2 + 100, img.height - 115)
		draw.text(position, text, (255, 255, 255), font=body_font)
	
	# Number
	i = str(index + 1)
	text_length = draw.textlength(i, font=body_font)
	position = ((img.width - text_length) / 2, img.height - 80)
	draw.text(position, i, (255, 255, 255), font=body_font)
	
	filename = f"{i}_" + card.get("title").replace(' ', '_') + ".png"
	
	location = cards_folder.joinpath(filename)
	
	resized = img.resize((4180, 6000))
	resized.save(location, "png")

print(f"{len(cards)} cards generated successfully.")
if is_app_frozen:
	input("Press ENTER to close this window...")