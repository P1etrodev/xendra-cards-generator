import json
import sys
from os import mkdir, remove
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from html2text import html2text
from markdown import markdown
from rich.console import Console
from rich.pretty import install

from draw_multiline_text import draw_multiline_text
from get_max_text_length import get_max_text_length
from load_config import load_config
from text_box import Align, text_box

install()

is_app_frozen = hasattr(sys, "frozen")

console = Console()


def main():
	
	data_path = Path("./cards_data.xlsx")
	cards_folder = Path("cards")
	max_length = 16
	
	if not cards_folder.exists():
		mkdir(cards_folder)
	else:
		console.log(f'Cards found, removing.')
		count = 0
		for file in cards_folder.glob('*'):
			remove(file)
			count += 1
		console.log(f'{count} cards removed.')
	
	if not data_path.exists():
		console.log(
			"This app must be in the same folder as a file called 'cards_data.xlsx' containing the "
			"cards information."
		)
		sys.exit()
	
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
	
	console.log('Generating cards...')
	
	for index, card in enumerate(cards):
		console.log(f'Generating "{card.get("title")}"...')
		
		if is_app_frozen:
			img = Image.new("RGBA", (1080, 1550), (255, 0, 0, 0))
		else:
			img = Image.open("Template.jpg")
		
		draw = ImageDraw.Draw(img)
		
		# Title
		text = html2text(markdown(card.get('title').upper())).strip()
		font = head_font_md if len(text) > 18 else head_font
		text_length = get_max_text_length(draw, text, font, 30)
		position = ((img.width - text_length) / 2, 65 if len(text) <= 18 else 75)
		draw_multiline_text(config, draw, position, text, font, (255, 255, 255), 30)
		
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
		text_copy = text
		description_config = config.get('description')
		with open('highlights.json', 'rb') as highlights_file:
			highlight_colors = json.load(highlights_file)
		for raw_effect_name, data in highlight_colors.items():
			effect_name = data.get("name")
			text_copy = text_copy.replace("@"+raw_effect_name, effect_name)
		is_too_long = len(text_copy) > (
			275 if description_config is None else description_config.get('too_long_characters')
		)
		text_box(
			text,
			draw, body_font_md if is_too_long else body_font,
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
		text = html2text(markdown(card.get('worth'))).strip()
		if len(text) > max_length:
			position = [150, img.height - 235]
			draw_multiline_text(config, draw, position, text, body_font_sm, (255, 255, 255), max_length)
		else:
			position = (150, img.height - 225)
			draw.text(position, text, (255, 255, 255), font=body_font)
		
		# Delay
		text = html2text(markdown(card.get('delay'))).strip()
		if len(text) > max_length:
			position = [150, img.height - 125]
			draw_multiline_text(config, draw, position, text, body_font_sm, (255, 255, 255), max_length)
		else:
			position = (150, img.height - 115)
			draw.text(position, text, (255, 255, 255), font=body_font)
		
		# Effect
		text = html2text(markdown(card.get('effect'))).strip()
		if len(text) > max_length:
			position = [img.width / 2 + 100, img.height - 235]
			draw_multiline_text(config, draw, position, text, body_font_sm, (255, 255, 255), max_length)
		else:
			position = (img.width / 2 + 100, img.height - 225)
			draw.text(position, text, (255, 255, 255), font=body_font)
		
		# Effect type
		text = html2text(markdown(card.get('effect_type'))).strip()
		if len(text) > max_length:
			position = [img.width / 2 + 100, img.height - 125]
			draw_multiline_text(config, draw, position, text, body_font_sm, (255, 255, 255), max_length)
		else:
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
	
	console.log(f"{len(cards)} cards generated successfully.")


if __name__ == "__main__":
	try:
		main()
	except Exception:
		console.print_exception()
	if is_app_frozen:
		input("Press ENTER to close this window...")