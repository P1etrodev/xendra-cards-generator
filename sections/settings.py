import json
from configparser import ConfigParser
from math import ceil
from pathlib import Path

import dearpygui.dearpygui as dpg
import pandas as pd

from tools.load_config import load_config
from tools.theme import Colors
from tools.update_progress_bar import update_progress_bar

predefined_config = {
	'description': {
		'padding_top': 700,
		'padding_left': 80,
		'too_long_characters': 275,
		'long_max_characters_per_line': 58,
		'short_max_characters_per_line': 42
	},
	'default': {'final_result_height': 6000, 'final_result_width': 4180},
	'font': {
		'head_normal': 90,
		'head_medium': 70,
		'body_normal': 60,
		'body_medium': 46,
		'body_small': 40
	}
}

config = load_config()

changes_made = False

add_payload = {
	"raw_name": None,
	"name": None,
	"r": 255,
	"g": 0,
	"b": 0
}
preferences_file = Path('config.ini')
highlights_data = Path('highlights.xlsx')

if not highlights_data.exists():
	highlights_df = pd.DataFrame(columns=["raw_name", "name", "r", "g", "b"])
else:
	try:
		highlights_df = pd.read_excel(highlights_data)
	except:
		highlights_df = pd.DataFrame(columns=["raw_name", "name", "r", "g", "b"])


def refresh_highlight_list():
	search_terms = dpg.get_value("highlight_search_box")
	global highlights_df
	_filtered = highlights_df.loc[highlights_df["name"].str.contains(search_terms, case=False)]
	
	highlight_names = _filtered["name"].tolist() if not _filtered.empty else []
	
	dpg.configure_item(
		'selected_name',
		items=highlight_names
	)


def update_highlight(sender_id: str, _value, highlight_name: str):
	if _value is None:
		_value = dpg.get_value(sender_id)
	
	column = sender_id.replace('edit_', '').replace('_field', '')
	if column == "raw_name":
		_value = _value.lower()
		dpg.set_value(sender_id, _value)
	
	elif column == "color":
		r, g, b, _ = _value
		highlights_df.loc[highlight_name == highlights_df["name"], "r"] = ceil(r)
		highlights_df.loc[highlight_name == highlights_df["name"], "g"] = ceil(g)
		highlights_df.loc[highlight_name == highlights_df["name"], "b"] = ceil(b)
	
	else:
		highlights_df.loc[highlight_name == highlights_df["name"], column] = str(_value)


def update_add_payload(sender: str | int):
	_value = dpg.get_value(sender)
	
	global add_payload
	_key = sender.replace("add_", "").replace('_field', '')
	if _key == "raw_name":
		_value = _value.lower()
		dpg.set_value(sender, _value)
		add_payload[_key] = _value
	elif _key == "color":
		r, g, b, _ = _value
		add_payload["r"] = ceil(r)
		add_payload["g"] = ceil(g)
		add_payload["b"] = ceil(b)
	else:
		add_payload[_key] = _value


def add_new_highlight():
	global add_payload
	if any(_value is None for _value in add_payload.values()):
		update_progress_bar("All fields must be completed in order to add the highlight.")
	else:
		# noinspection PyTypedDict
		highlights_df.loc[len(highlights_df)] = add_payload
		
		refresh_highlight_list()
		render_edit_form()
		update_progress_bar(f'"{add_payload["name"]}" added to highlights.')


def delete_highlight():
	global highlights_df
	
	card_name = dpg.get_value("selected_name")
	highlights_df = highlights_df[highlights_df["name"] != card_name]
	
	refresh_highlight_list()
	
	if not highlights_df.empty:
		dpg.set_value("selected_name", highlights_df["name"][0])
	
	render_edit_form()


def save_highlights():
	if highlights_df.empty:
		update_progress_bar("You haven't added any highlights.")
	else:
		highlights_df.to_excel(highlights_data)
		update_progress_bar(f"Highlights saved.")
		refresh_highlight_list()


def update_preference(sender: str, _value):
	_section = sender.split('_')[0]
	_key = sender.replace(_section + "_", '').replace('_field', '')
	
	config[_section][_key] = _value
	
	dpg.set_value(sender, _value)


def reset_preferences():
	for _section, _config in predefined_config.items():
		for _key, _value in _config.items():
			update_preference(f"{_section}_{_key}_field", _value)


def save_preferences():
	_config_parser = ConfigParser()
	
	for section, options in config.items():
		_config_parser[section] = options
	
	with open(preferences_file, 'w', encoding='UTF-8') as configfile:
		_config_parser.write(configfile)


def render_preferences_modal():
	width = dpg.get_viewport_width() // 4
	_id = "preferences_modal"
	with dpg.window(
		tag=_id,
		width=width,
		height=700,
		no_move=True,
		no_resize=True,
		modal=True,
		on_close=lambda: dpg.delete_item(_id)
	) as parent:
		with dpg.theme() as _title_theme:
			with dpg.theme_component(dpg.mvText):
				dpg.add_theme_color(dpg.mvThemeCol_Text, Colors.orange)
		
		description_config = config.get("description")
		
		_description_title_id = dpg.add_text("Description")
		
		dpg.bind_item_theme(_description_title_id, _title_theme)
		
		padding_top_id = dpg.add_text(
			default_value="Padding top",
			parent=parent
		)
		
		with dpg.tooltip(padding_top_id):
			dpg.add_text(
				'Separation between the bottom side of the image and the top side of the '
				'description.'
			)
		
		dpg.add_input_int(
			tag="description_padding_top_field",
			default_value=description_config.get("padding_top"),
			parent=parent,
			width=width - 35,
			callback=update_preference
		)
		
		padding_left_id = dpg.add_text(
			default_value="Padding left",
			parent=parent
		)
		
		with dpg.tooltip(padding_left_id):
			dpg.add_text(
				'Separation between the left side of the image and the left side of the '
				'description.'
			)
		
		dpg.add_input_int(
			tag="description_padding_left_field",
			default_value=description_config.get("padding_left"),
			parent=parent,
			width=width - 35,
			callback=update_preference
		)
		
		too_long_characters_id = dpg.add_text(
			default_value="Too long characters",
			parent=parent
		)
		
		with dpg.tooltip(too_long_characters_id):
			dpg.add_text('Amount of characters for a description to be considered too long.')
		
		dpg.add_input_int(
			tag="description_too_long_characters_field",
			default_value=description_config.get("too_long_characters"),
			parent=parent,
			width=width - 35,
			callback=update_preference
		)
		
		long_max_characters_per_line_id = dpg.add_text(
			default_value="Too long characters",
			parent=parent
		)
		
		with dpg.tooltip(long_max_characters_per_line_id):
			dpg.add_text(
				'Max amount of characters per line when the description is considered too '
				'long.'
			)
		
		dpg.add_input_int(
			tag="description_long_max_characters_per_line_field",
			default_value=description_config.get("long_max_characters_per_line"),
			parent=parent,
			width=width - 35,
			callback=update_preference
		)
		
		short_max_characters_per_line_id = dpg.add_text(
			default_value="Too short characters",
			parent=parent
		)
		
		with dpg.tooltip(short_max_characters_per_line_id):
			dpg.add_text(
				'Max amount of characters per line when the description is not considered too '
				'long.'
			)
		
		dpg.add_input_int(
			tag="description_short_max_characters_per_line_field",
			default_value=description_config.get("short_max_characters_per_line"),
			parent=parent,
			width=width - 35,
			callback=update_preference
		)
		
		dpg.add_separator(parent=parent)
		
		_default_title_id = dpg.add_text("Default")
		
		dpg.bind_item_theme(_default_title_id, _title_theme)
		
		default_config = config.get('default')
		
		final_result_height_id = dpg.add_text(
			default_value="Final result height",
			parent=parent
		)
		
		with dpg.tooltip(final_result_height_id):
			dpg.add_text('Height of the final processed result.')
		
		dpg.add_input_int(
			tag="default_final_result_height_field",
			default_value=default_config.get("final_result_height"),
			parent=parent,
			width=width - 35,
			callback=update_preference
		)
		
		final_result_width_id = dpg.add_text(
			default_value="Final result width",
			parent=parent
		)
		
		with dpg.tooltip(final_result_width_id):
			dpg.add_text('Height of the final processed result.')
		
		dpg.add_input_int(
			tag="default_final_result_width_field",
			default_value=default_config.get("final_result_width"),
			parent=parent,
			width=width - 35,
			callback=update_preference
		)
		
		dpg.add_separator(parent=parent)
		
		_font_title_id = dpg.add_text("Font")
		
		dpg.bind_item_theme(_font_title_id, _title_theme)
		
		font_config = config.get('font')
		
		head_normal_id = dpg.add_text(
			default_value="Head normal font size",
			parent=parent
		)
		
		with dpg.tooltip(head_normal_id):
			dpg.add_text('Largest font size for the text at the top side of the image (in pixels).')
		
		dpg.add_input_int(
			tag="font_head_normal_field",
			default_value=font_config.get("head_normal"),
			parent=parent,
			width=width - 35,
			callback=update_preference
		)
		
		head_medium_id = dpg.add_text(
			default_value="Head medium font size",
			parent=parent
		)
		
		with dpg.tooltip(head_medium_id):
			dpg.add_text('Medium font size for the text at the top side of the image (in pixels).')
		
		dpg.add_input_int(
			tag="font_head_medium_field",
			default_value=font_config.get("head_medium"),
			parent=parent,
			width=width - 35,
			callback=update_preference
		)
		
		body_normal_id = dpg.add_text(
			default_value="Body normal font size",
			parent=parent
		)
		
		with dpg.tooltip(body_normal_id):
			dpg.add_text('Largest font size for the text at the bottom side of the image (in pixels).')
		
		dpg.add_input_int(
			tag="font_body_normal_field",
			default_value=font_config.get("body_normal"),
			parent=parent,
			width=width - 35,
			callback=update_preference
		)
		
		body_medium_id = dpg.add_text(
			default_value="Body medium font size",
			parent=parent
		)
		
		with dpg.tooltip(body_medium_id):
			dpg.add_text('Medium font size for the text at the bottom side of the image (in pixels).')
		
		dpg.add_input_int(
			tag="font_body_medium_field",
			default_value=font_config.get("body_medium"),
			parent=parent,
			width=width - 35,
			callback=update_preference
		)
		
		body_small_id = dpg.add_text(
			default_value="Body small font size",
			parent=parent
		)
		
		with dpg.tooltip(body_small_id):
			dpg.add_text('Smallest font size for the text at the bottom side of the image (in pixels).')
		
		dpg.add_input_int(
			tag="font_body_small_field",
			default_value=font_config.get("body_small"),
			parent=parent,
			width=width - 35,
			callback=update_preference
		)
		
		save_button_id = dpg.add_button(
			label="Save preferences",
			parent=parent,
			callback=save_preferences,
			width=width - 35
		)
		
		with dpg.theme() as _save_button_theme:
			with dpg.theme_component(dpg.mvAll):
				dpg.add_theme_color(
					dpg.mvThemeCol_Button,
					Colors.green,
					category=dpg.mvThemeCat_Core
				)
				dpg.add_theme_color(
					dpg.mvThemeCol_Text,
					Colors.dark,
					category=dpg.mvThemeCat_Core
				)
		
		dpg.bind_item_theme(save_button_id, _save_button_theme)
		
		reset_button_id = dpg.add_button(
			label="Reset preferences",
			parent=parent,
			callback=reset_preferences,
			width=width - 35
		)
		
		with dpg.theme() as _reset_button_theme:
			with dpg.theme_component(dpg.mvAll):
				dpg.add_theme_color(
					dpg.mvThemeCol_Button,
					Colors.orange,
					category=dpg.mvThemeCat_Core
				)
				dpg.add_theme_color(
					dpg.mvThemeCol_Text,
					Colors.dark,
					category=dpg.mvThemeCat_Core
				)
		
		dpg.bind_item_theme(reset_button_id, _reset_button_theme)


def render_add_form():
	parent = "highlight_info_group"
	
	dpg.delete_item(parent, children_only=True)
	
	raw_name_id = dpg.add_text(
		default_value="Raw name",
		parent=parent
	)
	
	with dpg.tooltip(raw_name_id):
		dpg.add_text('Placeholder for your highlighted term. It will be replaced with "Name" after.')
		dpg.add_text('It cannot contain spaces, they must be replaced with underscores.')
	
	dpg.add_input_text(
		tag="add_raw_name_field",
		hint="raw_name",
		parent=parent,
		no_spaces=True,
		callback=update_add_payload
	)
	
	name_id = dpg.add_text(
		default_value="Name",
		parent=parent
	)
	
	with dpg.tooltip(name_id):
		dpg.add_text("The term that will replace the placeholder.")
	
	dpg.add_input_text(
		tag="add_name_field",
		hint="Name",
		parent=parent,
		callback=update_add_payload
	)
	
	color_id = dpg.add_text(
		default_value="Color",
		parent=parent
	)
	
	with dpg.tooltip(color_id):
		dpg.add_text("The color for your highlighted term.")
	
	dpg.add_color_picker(
		tag="add_color_field",
		default_value=(add_payload["r"], add_payload["g"], add_payload["b"]),
		parent=parent,
		no_small_preview=True,
		no_alpha=True,
		callback=update_add_payload
	)
	
	save_button_id = dpg.add_button(
		label="Save highlight",
		parent=parent,
		callback=add_new_highlight
	)
	
	with dpg.theme() as _save_button_theme:
		with dpg.theme_component(dpg.mvAll):
			dpg.add_theme_color(
				dpg.mvThemeCol_Button,
				Colors.green,
				category=dpg.mvThemeCat_Core
			)
			dpg.add_theme_color(
				dpg.mvThemeCol_Text,
				Colors.dark,
				category=dpg.mvThemeCat_Core
			)
	
	dpg.bind_item_theme(save_button_id, _save_button_theme)


def render_edit_form():
	parent = "highlight_info_group"
	
	dpg.delete_item(parent, children_only=True)
	
	if highlights_df.empty:
		dpg.add_text("Please select a highlight or add a new one.", parent=parent)
		return
	
	highlight_name = dpg.get_value("selected_name")
	
	filtered: pd.DataFrame = highlights_df.loc[highlights_df["name"] == highlight_name]
	
	if not filtered.empty:
		highlight: pd.Series = filtered.iloc[0]
		
		raw_name_id = dpg.add_text(
			default_value="Raw name",
			parent=parent
		)
		
		with dpg.tooltip(raw_name_id):
			dpg.add_text('Placeholder for your highlighted term. It will be replaced with "Name" after.')
			dpg.add_text('It cannot contain spaces, they must be replaced with underscores.')
		
		dpg.add_input_text(
			tag="edit_raw_name_field",
			default_value=highlight["raw_name"],
			hint="raw_name",
			parent=parent,
			no_spaces=True,
			callback=update_highlight,
			user_data=highlight_name
		)
		
		name_id = dpg.add_text(
			default_value="Name",
			parent=parent
		)
		
		with dpg.tooltip(name_id):
			dpg.add_text("The term that will replace the placeholder.")
		
		dpg.add_input_text(
			tag="edit_name_field",
			default_value=highlight["name"],
			hint="Name",
			parent=parent,
			callback=update_highlight,
			user_data=highlight_name
		)
		
		color_id = dpg.add_text(
			default_value="Color",
			parent=parent
		)
		
		with dpg.tooltip(color_id):
			dpg.add_text("The color for your highlighted term.")
		
		dpg.add_color_picker(
			tag="edit_color_field",
			default_value=(highlight["r"], highlight["g"], highlight["b"]),
			parent=parent,
			no_small_preview=True,
			no_alpha=True,
			callback=update_highlight,
			user_data=highlight_name
		)
		
		delete_button_id = dpg.add_button(
			label="Delete highlight",
			parent=parent,
			callback=render_delete_form
		)
		
		with dpg.theme() as delete_button_theme:
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
		
		dpg.bind_item_theme(delete_button_id, delete_button_theme)


def render_delete_form():
	card_info_group_id = "highlight_info_group"
	
	dpg.delete_item(card_info_group_id, children_only=True)
	
	highlight_name = dpg.get_value("selected_name")
	
	dpg.add_text(
		default_value=f"¿Are you sure that you want to delete {highlight_name}?",
		parent=card_info_group_id
	)
	
	_delete_button_id = dpg.add_button(
		parent=card_info_group_id,
		label=f"YES, I WANT TO DELETE THIS HIGHLIGHT",
		callback=delete_highlight
	)
	
	with dpg.theme() as delete_button_theme:
		with dpg.theme_component(dpg.mvAll):
			dpg.add_theme_color(
				dpg.mvThemeCol_Button,
				(220, 20, 60),
				category=dpg.mvThemeCat_Core
			)
			dpg.add_theme_color(
				dpg.mvThemeCol_Text,
				(33, 33, 33),
				category=dpg.mvThemeCat_Core
			)
			dpg.add_theme_style(
				dpg.mvThemeCol_Text,
			)
	
	dpg.bind_item_theme(_delete_button_id, delete_button_theme)
	
	dpg.add_button(
		parent=card_info_group_id,
		label="Cancel",
		callback=render_edit_form
	)


def render_highlights_modal():
	width = dpg.get_viewport_width() // 5 * 4
	_id = "highlights_modal"
	with dpg.window(
		tag=_id,
		width=width,
		height=700,
		no_move=True,
		no_resize=True,
		modal=True,
		on_close=lambda: dpg.delete_item(_id)
	):
		with dpg.group(
			horizontal=True
		):
			with dpg.group(
				width=(width // 4) + 50
			):
				dpg.add_input_text(
					hint="Search",
					tag="highlight_search_box",
					callback=refresh_highlight_list
				)
				names = highlights_df["name"].tolist()
				dpg.add_listbox(
					tag="selected_name",
					items=names,
					default_value=names[0] if len(names) > 0 else None,
					num_items=20,
					callback=render_edit_form
				)
				dpg.add_button(
					label="Save changes",
					callback=save_highlights
				)
				dpg.add_button(
					label="Add highlight",
					callback=render_add_form
				)
			with dpg.group(
				tag="highlight_info_group",
				horizontal=False,
				width=(width // 3) * 2
			):
				render_edit_form()