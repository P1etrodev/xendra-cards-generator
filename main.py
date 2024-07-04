import sys
from os import mkdir
from pathlib import Path
from textwrap import wrap

import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from easygui import msgbox

is_app_frozen = hasattr(sys, "frozen")

data_path = Path("./cards_data.xlsx")
cards_folder = Path("cards")
max_length = 16

if not cards_folder.exists():
	mkdir(cards_folder)

if not data_path.exists():
	msgbox(
		"This app must be in the same folder as a file called 'cards_data.xlsx' containing the "
		"cards information."
	)
	sys.exit()

df = pd.read_excel(data_path)

cards = df.to_dict(orient='records')

head_font = ImageFont.truetype("./Zabdilus.ttf", 90)
head_font_md = ImageFont.truetype('./Zabdilus.ttf', 70)
body_font = ImageFont.truetype("./AGENCYB.ttf", 60)
body_font_sm = ImageFont.truetype("./AGENCYB.ttf", 40)

print('Generating cards...', end="\r")

for index, card in enumerate(cards):
	print(f'Generating "{card.get("title")}"...', end="\r")
	
	if is_app_frozen:
		img = Image.new("RGBA", (1080, 1550), (255, 0, 0, 0))
	else:
		img = Image.open("Template.jpg")
	
	draw = ImageDraw.Draw(img)
	
	# Title
	text = card.get('title').upper()
	text_length = draw.textlength(text, font=head_font_md if len(text) > 18 else head_font)
	position = ((img.width - text_length) / 2, 65 if len(text) <= 18 else 75)
	draw.text(position, text, (255, 255, 255), font=head_font_md if len(text) > 18 else head_font)
	
	# Range
	text = card.get('range').upper()
	position = (70, 35)
	draw.text(position, text, (255, 255, 255), font=head_font)
	
	# Type
	text = card.get('type').upper()
	text_length = draw.textlength(text, font=head_font)
	position = (img.width - text_length - 85, 35)
	draw.text(position, text, (255, 255, 255), font=head_font)
	
	# Description
	text = card.get('description')
	position = [80, img.height - 700]
	for line in wrap(text, width=42):
		draw.text(position, line, (0, 0, 0), font=body_font)
		position = [position[0], position[1] + body_font.size]
	
	# Worth
	text = card.get('worth')
	if len(text) > max_length:
		position = [150, img.height - 235]
		for line in wrap(text, width=max_length):
			draw.text(position, line, (255, 255, 255), font=body_font_sm)
			position = [position[0], position[1] + body_font_sm.size]
	else:
		position = (150, img.height - 225)
		draw.text(position, text, (255, 255, 255), font=body_font)
	
	# Delay
	text = card.get('delay')
	if len(text) > max_length:
		position = [150, img.height - 125]
		for line in wrap(text, width=max_length):
			draw.text(position, line, (255, 255, 255), font=body_font_sm)
			position = [position[0], position[1] + body_font_sm.size]
	else:
		position = (150, img.height - 115)
		draw.text(position, text, (255, 255, 255), font=body_font)
	
	# Effect
	text = card.get('effect')
	if len(text) > max_length:
		position = [img.width / 2 + 100, img.height - 235]
		for line in wrap(text, width=max_length):
			draw.text(position, line, (255, 255, 255), font=body_font_sm)
			position = [position[0], position[1] + body_font_sm.size]
	else:
		text_length = draw.textlength(text, font=body_font)
		position = (img.width / 2 + 100, img.height - 225)
		draw.text(position, text, (255, 255, 255), font=body_font)
	
	# Effect type
	text = card.get('effect_type')
	if len(text) > max_length:
		position = [img.width / 2 + 100, img.height - 125]
		for line in wrap(text, width=max_length):
			draw.text(position, line, (255, 255, 255), font=body_font_sm)
			position = [position[0], position[1] + body_font_sm.size]
	else:
		text_length = draw.textlength(text, font=body_font)
		position = (img.width / 2 + 100, img.height - 115)
		draw.text(position, text, (255, 255, 255), font=body_font)
	
	# Number
	i = str(index + 1)
	text_length = draw.textlength(i, font=body_font)
	position = ((img.size[0] - text_length) / 2, img.height - 80)
	draw.text(position, i, (255, 255, 255), font=body_font)
	
	filename = f"{i}_" + card.get("title").replace(' ', '_') + ".png"
	
	location = cards_folder.joinpath(filename)
	
	resized = img.resize((4180, 6000))
	resized.save(location, "png")
	

print(f"{len(cards)} cards generated successfully.")
if is_app_frozen:
	input("Press ENTER to close this window...")