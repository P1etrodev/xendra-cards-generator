from PIL import ImageFont


class Fonts:
	
	def __init__(self, font_config: dict):
		self.head_font = ImageFont.truetype(
			"assets/fonts/Zabdilus.ttf", (
				90 if font_config is None else font_config.get('head_normal')
			)
		)
		self.head_font_md = ImageFont.truetype(
			"assets/fonts/Zabdilus.ttf", (
				70 if font_config is None else font_config.get('head_medium')
			)
		)
		self.body_font = ImageFont.truetype(
			"assets/fonts/AGENCYB.ttf", (
				60 if font_config is None else font_config.get('body_normal')
			)
		)
		self.body_font_md = ImageFont.truetype(
			"assets/fonts/AGENCYB.ttf", (
				46 if font_config is None else font_config.get('body_medium')
			)
		)
		self.body_font_sm = ImageFont.truetype(
			"assets/fonts/AGENCYB.ttf", (
				40 if font_config is None else font_config.get('body_small')
			)
		)