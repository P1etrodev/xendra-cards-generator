import os
from pathlib import Path

import dearpygui.dearpygui as dpg

from tools.theme import Colors, load_theme
from sections.cards import render_cards_section
from sections.settings import render_preferences_modal, render_highlights_modal

width, height = 1240, 776

title_bar_drag = False

dpg.create_context()
dpg.setup_dearpygui()

# noinspection PyNoneFunctionAssignment
viewport_id = dpg.create_viewport(
	title='Card Generator v2.0',
	small_icon='assets/icon.ico',
	large_icon='assets/icon.ico',
	resizable=False,
	decorated=False,
	width=width,
	height=height
)


def cal_dow(_, data):
	global title_bar_drag
	threshold = 80
	if dpg.is_mouse_button_down(0):
		y = data[1]
		if -threshold <= y <= threshold:
			title_bar_drag = True
		else:
			title_bar_drag = False


def cal(_, data):
	global title_bar_drag
	if title_bar_drag:
		pos = dpg.get_viewport_pos()
		x = data[1]
		y = data[2]
		final_x = pos[0] + x
		final_y = pos[1] + y
		dpg.configure_viewport(viewport_id, x_pos=final_x, y_pos=final_y)


def _exit():
	dpg.destroy_context()


with dpg.window(
	tag="main",
	no_collapse=True,
	no_move=True,
	no_resize=True,
	no_title_bar=True,
	on_close=_exit,
	width=width,
	height=height,
	pos=[0, 0]
):
	close_button_id = dpg.add_button(label="X", width=50, callback=_exit, pos=[width - 50, 5])
	
	with dpg.theme() as close_button_theme:
		with dpg.theme_component(dpg.mvAll):
			dpg.add_theme_color(
				dpg.mvThemeCol_Button,
				Colors.red,
				category=dpg.mvThemeCat_Core
			)
			dpg.add_theme_color(
				dpg.mvThemeCol_Text,
				Colors.white,
				category=dpg.mvThemeCat_Core
			)
		dpg.bind_item_theme(close_button_id, close_button_theme)
	
	with dpg.tab_bar(tag="tab_bar"):
		dpg.add_tab_button(label="Highlights", callback=render_highlights_modal)
		dpg.add_tab_button(label="Preferences", callback=render_preferences_modal)
		
	render_cards_section()
	
	dpg.add_progress_bar(
		tag="generate_card_progress_bar",
		pos=[5, dpg.get_viewport_client_height() - 57.1],
		width=dpg.get_viewport_width()
	)

with dpg.handler_registry():
	dpg.add_mouse_drag_handler(0, callback=cal)
	dpg.add_mouse_move_handler(callback=cal_dow)

with dpg.font_registry():
	dpg.add_font("assets/fonts/Poppins-Regular.ttf", size=20, tag="main_font")
	dpg.add_font("assets/fonts/Poppins-Bold.ttf", size=25, tag="main_bold_font")

dpg.bind_font("main_font")

load_theme()

dpg.show_viewport(maximized=True)
dpg.start_dearpygui()
dpg.destroy_context()

if (last_preview := Path('preview.png')).exists():
	os.remove(last_preview)