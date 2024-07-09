import dearpygui.dearpygui as dpg


class Colors:
	dark = (20, 20, 20)
	medium = (60, 60, 60)
	light = (165, 165, 165)
	white = (245, 245, 245)
	green = (48, 248, 134)
	orange = (248, 148, 48)
	red = (220, 20, 60)
	purple = (148, 48, 248)


def load_theme():
	with dpg.theme() as main_theme:
		with dpg.theme_component(dpg.mvAll):
			dpg.add_theme_color(
				dpg.mvThemeCol_ScrollbarGrab,
				Colors.light
			)
			dpg.add_theme_color(
				dpg.mvThemeCol_ScrollbarBg,
				Colors.medium
			)
		
		with dpg.theme_component(dpg.mvWindowAppItem):
			dpg.add_theme_color(
				dpg.mvThemeCol_WindowBg,
				Colors.dark
			)
		
		with dpg.theme_component(dpg.mvButton, enabled_state=False):
			dpg.add_theme_color(
				dpg.mvThemeCol_Text,
				Colors.dark
			)
			dpg.add_theme_color(
				dpg.mvThemeCol_Button,
				Colors.medium
			)
			dpg.add_theme_color(
				dpg.mvThemeCol_ButtonHovered,
				Colors.medium
			)
		
		with dpg.theme_component(dpg.mvButton):
			dpg.add_theme_color(
				dpg.mvThemeCol_Button,
				Colors.medium
			)
			dpg.add_theme_color(
				dpg.mvThemeCol_Text,
				Colors.white
			)
		
		with dpg.theme_component(dpg.mvInputText):
			dpg.add_theme_color(
				dpg.mvThemeCol_FrameBg,
				Colors.medium
			)
		
		with dpg.theme_component(dpg.mvCombo):
			dpg.add_theme_color(
				dpg.mvThemeCol_Header,
				Colors.light
			)
			dpg.add_theme_color(
				dpg.mvThemeCol_HeaderHovered,
				Colors.light
			)
			dpg.add_theme_color(
				dpg.mvThemeCol_FrameBg,
				Colors.medium
			)
			dpg.add_theme_color(
				dpg.mvThemeCol_Text,
				Colors.white
			)
			dpg.add_theme_color(
				dpg.mvThemeCol_PopupBg,
				Colors.medium
			)
		
		with dpg.theme_component(dpg.mvCheckbox):
			dpg.add_theme_color(
				dpg.mvThemeCol_FrameBg,
				Colors.medium
			)
			dpg.add_theme_color(
				dpg.mvThemeCol_CheckMark,
				Colors.white
			)
		
		with dpg.theme_component(dpg.mvListbox):
			dpg.add_theme_color(
				dpg.mvThemeCol_FrameBg,
				Colors.medium
			)
			dpg.add_theme_color(
				dpg.mvThemeCol_Text,
				Colors.white
			)
		
		with dpg.theme_component(dpg.mvProgressBar):
			dpg.add_theme_color(
				dpg.mvThemeCol_FrameBg,
				Colors.medium
			)
	
	dpg.bind_theme(main_theme)