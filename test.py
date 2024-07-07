from PIL import Image, ImageDraw, ImageFont

from text_box import text_box, Align

symbols = '.,:;?!'

text = (
	"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus lacinia odio vitae.	Vestibulum "
	"ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae.	Sed nisi. Nulla "
	"quis sem at nibh elementum imperdiet. Duis sagittis ipsum. Praesent	mauris. Xendra.")

with Image.open('Template.jpg') as img:
	
	draw = ImageDraw.Draw(img)
	
	head_font_md = ImageFont.truetype("./AGENCYB.ttf", 46)
	
	highlight_colors = {
		"Xendra": "#04444e",
		"Vestibulum ante": "#04444e",
	}
	
	text_box(
		text,
		draw, head_font_md, 56,
		80, img.height - 700, img.width - 160, 400,
		Align.LEFT, Align.CENTER,
		highlight_colors, fill='#000000'
	)
	
	img.show()