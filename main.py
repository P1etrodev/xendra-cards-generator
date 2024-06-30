import sys
from os import mkdir
from pathlib import Path
from textwrap import wrap

import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from easygui import msgbox

data_path = Path("./cards_data.xlsx")

if not data_path.exists():
	msgbox("This app must be in the same folder as a file called 'cards_data.xlsx' containing the "
	       "cards information.")
	sys.exit()

df = pd.read_excel("./cards_data.xlsx")

cards = df.to_dict(orient='records')

font = ImageFont.truetype("./Zabdilus.ttf", 90)
font_md = ImageFont.truetype('./Zabdilus.ttf', 70)
font2 = ImageFont.truetype("./AGENCYB.ttf", 60)

for index, card in enumerate(cards):
	img = Image.new("RGBA", (1080, 1550), (255, 0, 0, 0))
	
	# img = Image.open("Template.jpg")
	draw = ImageDraw.Draw(img)
	
	# Title
	text = card.get('title').upper()
	text_length = draw.textlength(text, font=font_md if len(text) > 18 else font)
	position = ((img.width - text_length) / 2, 65 if len(text) <= 18 else 75)
	draw.text(position, text, (255, 255, 255), font=font_md if len(text) > 18 else font)
	
	# Range
	text = card.get('range').upper()
	position = (70, 35)
	draw.text(position, text, (255, 255, 255), font=font)
	
	# Type
	text = card.get('type').upper()
	text_length = draw.textlength(text, font=font)
	position = (img.width - text_length - 85, 35)
	draw.text(position, text, (255, 255, 255), font=font)
	
	# Description
	text = card.get('description')
	position = [60, img.height - 700]
	for line in wrap(text, width=48):
		draw.text(position, line, (0, 0, 0), font=font2)
		position = [position[0], position[1] + font2.size]
	
	# Worth
	text = card.get('worth')
	position = (150, img.height - 220)
	draw.text(position, text, (255, 255, 255), font=font2)
	
	# Delay
	text = card.get('delay')
	position = (150, img.height - 110)
	draw.text(position, text, (255, 255, 255), font=font2)
	
	# Effect
	text = card.get('effect')
	text_length = draw.textlength(text, font=font2)
	position = ((img.width - text_length - 140), img.height - 230)
	draw.text(position, text, (255, 255, 255), font=font2)
	
	# Effect type
	text = card.get('effect_type')
	text_length = draw.textlength(text, font=font2)
	position = ((img.width - text_length - 140), img.height - 110)
	draw.text(position, text, (255, 255, 255), font=font2)
	
	# Number
	i = str(index + 1)
	text_length = draw.textlength(i, font=font2)
	position = ((img.size[0] - text_length) / 2, img.height - 80)
	draw.text(position, i, (255, 255, 255), font=font2)
	
	path = Path("cards")
	
	if not path.exists():
		mkdir(path)
	
	filename = f"{i}_" + card.get("title").replace(' ', '_') + ".png"
	
	img.save(path.joinpath(filename), "png")
	# img.close()
	
msgbox(f"{len(cards)} cards generated successfully.")