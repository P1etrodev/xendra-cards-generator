import json
import sys
from os import mkdir
from pathlib import Path

from PIL import Image, ImageDraw
from html2text import html2text
from markdown import markdown
from pandas import Series

from tools.fonts import Fonts
from tools.text_box import Align, text_box
from tools.draw_multiline_text import draw_multiline_text
from tools.get_max_text_length import get_max_text_length

is_app_frozen = hasattr(sys, "frozen")

max_length = 16

cards_folder = Path("cards")
if not cards_folder.exists():
	mkdir(cards_folder)
assets_folder = Path("assets")
if not assets_folder.exists():
	raise Exception(f"{assets_folder} not found.")
ranges_folder = assets_folder.joinpath("ranges")
if not ranges_folder.exists():
	raise Exception(f"{ranges_folder} not found.")
areas_folder = assets_folder.joinpath("areas")
if not areas_folder.exists():
	raise Exception(f"{areas_folder} not found.")


def create_card(
	config: dict,
	fonts: Fonts,
	index: int,
	card: Series,
	**kwargs
):
	is_preview = kwargs.get('is_preview')
	
	if is_preview:
		img = Image.open("assets/Template.jpg")
	else:
		img = Image.new("RGBA", (1080, 1550), (255, 0, 0, 0))
	
	draw = ImageDraw.Draw(img)
	
	# Title
	text = card['name'].upper()
	parsed_text = html2text(markdown(text)).strip()
	font = fonts.head_font_md if len(parsed_text) > 18 else fonts.head_font
	text_length = get_max_text_length(draw, parsed_text, font, 30)
	position = ((img.width - text_length) / 2, 65 if len(parsed_text) <= 18 else 75)
	draw_multiline_text(config, draw, position, parsed_text, font, (255, 255, 255), 30)
	#
	# text = "RANGO"
	# parsed_text = html2text(markdown(text)).strip()
	# position = (80, 35)
	# draw.text(position, parsed_text, (255, 255, 255), font=fonts.head_font)
	
	# Range
	_range = str(card['range'])
	if _range != 'N/A':
		file_path = ranges_folder.joinpath(f'{_range}.png')
		if file_path.exists():
			with Image.open(file_path) as range_img:
				position = (75, 130)
				range_img.thumbnail((150, 150))
				img.paste(range_img, position, range_img)
	#
	# text = "ÁREA"
	# parsed_text = html2text(markdown(text)).strip()
	# text_length = draw.textlength(parsed_text, font=fonts.head_font)
	# position = (img.width - text_length - 90, 35)
	# draw.text(position, parsed_text, (255, 255, 255), font=fonts.head_font)
	
	# Area
	if (area := card['area']) and area != "N/A":
		area = str(area)
		file_path = areas_folder.joinpath(f'{area}.png')
		if file_path.exists():
			with Image.open(file_path) as area_img:
				area_img.thumbnail((150, 150))
				position = (img.width - 75 - area_img.width, 130)
				img.paste(area_img, position, area_img)
	
	# Description
	highlights_json_file = Path("highlights.json")
	text = str(card['description'])
	if text != "N/A":
		parsed_text = html2text(markdown(text)).strip()
		text_copy = parsed_text
		description_config = config.get('description')
		if highlights_json_file.exists():
			with highlights_json_file.open('rb') as highlights_file:
				highlight_colors = json.load(highlights_file)
		else:
			highlight_colors = {}
		for raw_effect_name, data in highlight_colors.items():
			effect_name = data.get("name")
			text_copy = text_copy.replace("@" + raw_effect_name, effect_name)
		is_too_long = len(text_copy) > (
			275 if description_config is None else description_config.get('too_long_characters')
		)
		text_box(
			parsed_text,
			draw, fonts.body_font_md if is_too_long else fonts.body_font,
			(
				56 if description_config is None else description_config.get(
					'long_max_characters_per_line'
				)
			) if is_too_long else (
				42 if description_config is None else description_config.get(
					'short_max_characters_per_line'
				)
			),
			80 if description_config is None else description_config.get('padding_left'),
			img.height - (700 if description_config is None else description_config.get('padding_top')),
			img.width - 160, 400,
			Align.LEFT, Align.CENTER,
			highlight_colors, fill='#000000', show_frame=True
		)
	
	# Worth
	text = str(card['worth'])
	parsed_text = html2text(markdown(text)).strip()
	if len(parsed_text) > max_length:
		position = [150, img.height - 235]
		draw_multiline_text(
			config, draw, position, parsed_text, fonts.body_font_sm, (255, 255, 255),
			max_length
		)
	else:
		position = (150, img.height - 225)
		draw.text(position, parsed_text, (255, 255, 255), font=fonts.body_font)
	
	# Delay
	text = str(card['delay'])
	parsed_text = html2text(markdown(text)).strip()
	if len(parsed_text) > max_length:
		position = [150, img.height - 125]
		draw_multiline_text(
			config, draw, position, parsed_text, fonts.body_font_sm, (255, 255, 255),
			max_length
		)
	else:
		position = (150, img.height - 115)
		draw.text(position, parsed_text, (255, 255, 255), font=fonts.body_font)
	
	# Effect
	text = str(card['effect'])
	parsed_text = html2text(markdown(text)).strip()
	if len(parsed_text) > max_length:
		position = [img.width / 2 + 100, img.height - 235]
		draw_multiline_text(
			config, draw, position, parsed_text, fonts.body_font_sm, (255, 255, 255),
			max_length
		)
	else:
		position = (img.width / 2 + 100, img.height - 225)
		draw.text(position, parsed_text, (255, 255, 255), font=fonts.body_font)
	
	# Effect type
	text = str(card['effect_type'])
	parsed_text = html2text(markdown(text)).strip()
	if len(parsed_text) > max_length:
		position = [img.width / 2 + 100, img.height - 125]
		draw_multiline_text(
			config, draw, position, parsed_text, fonts.body_font_sm, (255, 255, 255),
			max_length
		)
	else:
		position = (img.width / 2 + 100, img.height - 115)
		draw.text(position, parsed_text, (255, 255, 255), font=fonts.body_font)
	
	# Number
	i = str(index + 1)
	text_length = draw.textlength(i, font=fonts.body_font)
	position = ((img.width - text_length) / 2, img.height - 80)
	draw.text(position, i, (255, 255, 255), font=fonts.body_font)
	
	if not is_preview:
		filename = f"{i}_" + card["name"].replace(' ', '_') + ".png"
		
		location = cards_folder.joinpath(filename)
		resized = img.resize((4180, 6000))
		resized.save(location, "png")
	else:
		location = Path('preview.png')
		img.save(location, "png")