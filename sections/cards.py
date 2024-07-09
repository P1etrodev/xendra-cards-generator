from math import ceil
from os import startfile
from pathlib import Path
from textwrap import wrap

import dearpygui.dearpygui as dpg
import pandas as pd

from tools.create_card import create_card
from tools.fonts import Fonts
from tools.load_config import load_config
from tools.theme import Colors
from tools.thread_function import thread_function
from tools.update_progress_bar import update_progress_bar


class Data:
	ranges = [str(x) for x in range(0, 7)] + ["Global"]
	areas = [
		        "Aliados", "Entre casilleros", "Global", "Linea recta de casilleros", "Objetivo",
		        "Oponentes", "Trampa", "Un casillero", "Zona de Colisión", "0"
	        ] + [f"R{x}" for x in range(2, 7)]
	worth = [
		"Una acción",
		"Acción gratuita",
		"Acción gratuita (requiere prueba)"
	]
	effects = [
		"Veneno",
		"Quemaduras",
		"Sangrado",
		"Electrificar",
		"Ralentizado",
		"Aturdido",
		"Encandilar",
		"Derribo",
		"Energizar",
		"Aumento",
		"Pasoextra",
		"Precisión",
		"Daño extra",
		"Perforante",
		"Escudo mágico",
		"Combo",
		"No requiere prueba"
	]


add_payload = {
	"id": 0,
	"name": None,
	"range": None,
	"area": None,
	"description": None,
	"worth": None,
	"delay": "Normal",
	"effect": None,
	"effect_type": None
}

template_width, template_height, template_channels, template_data = dpg.load_image(
	"assets/Template.jpg"
)

cards_data = Path('cards_data.xlsx')

if not cards_data.exists():
	cards_df = pd.DataFrame(
		columns=[
			"id",
			"name",
			"range",
			"area",
			"description",
			"worth",
			"delay",
			"effect",
			"effect_type"
		]
	)
else:
	try:
		cards_df = pd.read_excel(cards_data)
	except:
		highlights = pd.DataFrame(
			columns=[
				"id",
				"name",
				"range",
				"area",
				"description",
				"worth",
				"delay",
				"effect",
				"effect_type"
			]
		)

config = load_config()

fonts = Fonts(config.get('font'))


def generate_single_card(card_name: str):
	card = cards_df[cards_df["name"] == card_name].iloc[0]
	update_progress_bar(f'Generating "{card_name}"...')
	create_card(config, fonts, card)
	update_progress_bar(f'"{card_name}" generated.')


def refresh_card_list():
	search_terms = dpg.get_value("card_search_box")
	global cards_df
	_filtered = cards_df.loc[cards_df["name"].str.contains(search_terms, case=False)]
	
	card_names = _filtered.sort_values(by="id")["name"].tolist() if not _filtered.empty else []
	
	dpg.configure_item(
		'selected_card',
		items=card_names
	)


def update_card(sender_id: str, value, card_name: str):
	if value is None:
		value = dpg.get_value(sender_id)
	
	column = sender_id.replace('edit_', '').replace('_field', '')
	
	if column == "description":
		clean_value = value.replace('\n', " ")
		cards_df.loc[card_name == cards_df["name"], column] = clean_value
		wrapped = wrap(clean_value, 55)
		dpg.set_value(sender_id, "\n".join(wrapped))
	elif column == "delay":
		cards_df.loc[card_name == cards_df["name"], column] = "Instantáneo" if value else "Normal"
	else:
		cards_df.loc[card_name == cards_df["name"], column] = value
	
	filtered = cards_df.loc[card_name == cards_df["name"]]
	if not filtered.empty:
		card = filtered.iloc[0]
		thread_function(refresh_card_preview, card)


def save_cards():
	if cards_df.empty:
		update_progress_bar("You haven't added any cards.")
	else:
		cards_df.to_excel(cards_data, index=False)
		update_progress_bar("Cards saved.")
		refresh_card_list()


def generate_cards():
	if cards_df.empty:
		update_progress_bar("You can't generate cards because you haven't added any")
	else:
		rows, _ = cards_df.shape
		
		generate_cards_button_id = "generate_cards_button"
		
		dpg.disable_item(generate_cards_button_id)
		
		for index, card in cards_df.iterrows():
			new_status = ceil((index / rows) * 100)
			update_progress_bar(
				f'Generating "{card['name']}"...',
				new_status / 100,
				True
			)
			create_card(config, fonts, card)
		
		# noinspection PyUnboundLocalVariable
		update_progress_bar(f"{rows} cards generated.")
		
		dpg.enable_item(generate_cards_button_id)


def refresh_card_preview(card: pd.Series = None):
	
	dpg.delete_item("card_preview", children_only=True)
	
	dpg.add_image(
		"card_preview_texture",
		width=template_width * .45,
		height=template_height * .45,
		parent="card_preview"
	)
	
	if card is None:
		value = dpg.get_value("selected_card")
		filtered: pd.DataFrame = cards_df.loc[cards_df["name"] == value]
		if filtered.empty:
			raise Exception("Error obtaining card.")
		filtered = filtered.fillna('N/A')
		card = filtered.iloc[0]
	
	create_card(config, fonts, card, is_preview=True)
	
	new_width, new_height, new_channels, new_data = dpg.load_image("preview.png")
	dpg.set_value("card_preview_texture", new_data)


def update_add_payload(sender: str | int):
	
	value = dpg.get_value(sender)
	
	global add_payload
	key = sender.replace("add_", "").replace('_field', '')
	if key == "delay":
		# noinspection PyTypedDict
		add_payload["delay"] = "Normal" if not value else "Instantáneo"
	else:
		add_payload[key] = value
	
	card = pd.Series(add_payload).fillna('N/A')
	thread_function(refresh_card_preview, card)


def add_new_card():
	global add_payload
	if any(not _value for _value in add_payload.values()):
		update_progress_bar("All fields must be completed in order to add the card.")
	else:
		cards_df.loc[len(cards_df)] = add_payload
		
		refresh_card_list()
		render_edit_form()
		
		update_progress_bar(f'"{add_payload["name"]}" added to cards.')


def delete_card():
	global cards_df
	
	card_name = dpg.get_value("selected_card")
	cards_df = cards_df[cards_df["name"] != card_name]
	
	refresh_card_list()
	
	if not cards_df.empty:
		dpg.set_value("selected_card", cards_df["name"][0])
	
	render_edit_form()


def render_delete_card():
	card_info_group_id = "card_info_group"
	
	dpg.delete_item(card_info_group_id, children_only=True)
	
	card_name = dpg.get_value("selected_card")
	
	dpg.add_text(
		default_value=f"¿Are you sure that you want to delete {card_name}?",
		parent=card_info_group_id
	)
	
	_delete_button_id = dpg.add_button(
		parent=card_info_group_id,
		label=f"YES, I WANT TO DELETE THIS CARD",
		callback=delete_card
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
			dpg.add_theme_style(
				dpg.mvThemeCol_Text,
			)
	
	dpg.bind_item_theme(_delete_button_id, delete_button_theme)
	
	dpg.add_button(
		parent=card_info_group_id,
		label="Cancel",
		callback=render_edit_form
	)


def render_add_form():
	parent = "card_info_group"
	
	dpg.delete_item(parent, children_only=True)
	
	global add_payload
	
	_title_id = dpg.add_text(
		default_value="Add new card",
		parent=parent
	)
	
	with dpg.theme() as _title_theme:
		with dpg.theme_component(dpg.mvText):
			dpg.add_theme_color(dpg.mvThemeCol_Text, Colors.green)
		
		dpg.bind_item_theme(_title_id, _title_theme)
	dpg.bind_item_font(_title_id, "main_bold_font")
	
	dpg.add_input_text(
		tag="add_name_field",
		hint="Card name",
		parent=parent,
		callback=update_add_payload
	)
	
	dpg.add_text(
		default_value="Card ID",
		parent=parent
	)
	
	dpg.add_input_int(
		tag="add_id_field",
		parent=parent,
		callback=update_add_payload
	)
	
	dpg.add_checkbox(
		label="Instantaneous",
		tag="add_delay_field",
		parent=parent,
		callback=update_add_payload
	)
	
	dpg.add_input_text(
		tag="add_description_field",
		hint="Card description",
		parent=parent,
		multiline=True,
		height=200,
		width=300,
		callback=update_add_payload
	)
	
	dpg.add_text(
		default_value='Range',
		parent=parent
	)
	dpg.add_combo(
		tag="add_range_field",
		items=Data.ranges,
		parent=parent,
		callback=update_add_payload,
		width=200
	)
	
	dpg.add_text(
		default_value='Area',
		parent=parent
	)
	dpg.add_combo(
		tag="add_area_field",
		items=Data.areas,
		parent=parent,
		callback=update_add_payload
	)
	
	dpg.add_text(
		default_value='Worth',
		parent=parent
	)
	dpg.add_combo(
		tag="add_worth_field",
		items=Data.worth,
		parent=parent,
		callback=update_add_payload
	)
	
	dpg.add_text(
		default_value="Effect",
		parent=parent
	)
	dpg.add_combo(
		tag="add_effect_field",
		items=Data.effects,
		parent=parent,
		width=300,
		callback=update_add_payload
	)
	
	dpg.add_text(
		default_value='Effect type',
		parent=parent
	)
	dpg.add_input_text(
		tag="add_effect_type_field",
		hint="Effect type",
		parent=parent,
		callback=update_add_payload
	)
	
	_save_button_id = dpg.add_button(
		label="Save card",
		callback=add_new_card,
		parent=parent
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
		
		dpg.bind_item_theme(_save_button_id, _save_button_theme)
	
	card = pd.Series(add_payload).fillna('N/A')
	
	thread_function(refresh_card_preview, card)


def render_edit_form():
	parent = "card_info_group"
	
	dpg.delete_item(parent, children_only=True)
	dpg.delete_item("card_preview", children_only=True)
	
	if cards_df.empty:
		dpg.add_text("Please select a card or add a new one.", parent=parent)
	else:
		card_name = dpg.get_value("selected_card")
		
		filtered: pd.DataFrame = cards_df.loc[cards_df["name"] == card_name]
		
		if not filtered.empty:
			filtered = filtered.fillna("N/A")
			first_result: pd.Series = filtered.iloc[0]
			
			_title_id = dpg.add_text(
				default_value=first_result["name"],
				parent=parent
			)
			
			with dpg.theme() as _title_theme:
				with dpg.theme_component(dpg.mvText):
					dpg.add_theme_color(dpg.mvThemeCol_Text, Colors.orange)
				
				dpg.bind_item_theme(_title_id, _title_theme)
			dpg.bind_item_font(_title_id, "main_bold_font")
			
			dpg.add_text(
				default_value="Card ID",
				parent=parent
			)
			
			dpg.add_input_int(
				tag="edit_id_field",
				default_value=int(first_result["id"]),
				parent=parent,
				callback=update_card,
				user_data=card_name
			)
			
			dpg.add_checkbox(
				label="Instantaneous",
				tag="edit_is_insta_field",
				default_value=first_result["delay"] != "Normal",
				parent=parent,
				user_data=card_name,
				callback=update_card
			)
			lines = wrap(first_result["description"], 55)
			
			dpg.add_input_text(
				tag="edit_description_field",
				default_value="\n".join(lines),
				parent=parent,
				multiline=True,
				height=200,
				width=300,
				callback=update_card,
				user_data=card_name
			)
			
			dpg.add_text('Range:', parent=parent)
			dpg.add_combo(
				tag="edit_range_field",
				items=Data.ranges,
				default_value=first_result["range"],
				parent=parent,
				width=80,
				user_data=card_name,
				callback=update_card
			)
			dpg.add_text('Area:', parent=parent)
			dpg.add_combo(
				tag="edit_area_field",
				items=Data.areas,
				default_value=first_result["range"],
				parent=parent,
				width=80,
				user_data=card_name,
				callback=update_card
			)
			dpg.add_text('Worth:', parent=parent)
			dpg.add_combo(
				tag="edit_worth_field",
				items=Data.worth,
				default_value=first_result["worth"],
				parent=parent,
				width=80,
				user_data=card_name,
				callback=update_card
			)
			
			dpg.add_text("Effect:", parent=parent)
			dpg.add_combo(
				tag="edit_effect_field",
				items=Data.effects,
				default_value=first_result["effect"],
				parent=parent,
				width=300,
				user_data=card_name,
				callback=update_card
			)
			dpg.add_text('Effect type:', parent=parent)
			dpg.add_input_text(
				tag="edit_effect_type_field",
				hint="Effect type",
				parent=parent,
				default_value=first_result["effect_type"],
				user_data=card_name,
				callback=update_card
			)
			
			_delete_button_id = dpg.add_button(
				label="Generate this card (only)",
				parent=parent,
				callback=lambda: thread_function(generate_single_card, card_name=card_name)
			)
			
			_delete_button_id = dpg.add_button(
				label="Delete card",
				parent=parent,
				callback=render_delete_card
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
			
			dpg.bind_item_theme(_delete_button_id, delete_button_theme)
		
		thread_function(refresh_card_preview)


def render_cards_section():
	with dpg.texture_registry():
		dpg.add_dynamic_texture(
			width=template_width,
			height=template_height,
			default_value=template_data,
			tag="card_preview_texture"
		)
	
	with dpg.group(tag="cards_group", horizontal=True):
		with dpg.group(
			width=dpg.get_viewport_width() // 4
		):
			dpg.add_input_text(
				hint="Search",
				tag="card_search_box",
				callback=refresh_card_list
			)
			card_names = cards_df.sort_values(by="id")["name"].tolist()
			dpg.add_listbox(
				items=card_names,
				callback=render_edit_form,
				num_items=20,
				tracked=True,
				tag="selected_card",
			)
			generate_button_id = dpg.add_button(
				label="Generate cards",
				tag="generate_cards_button",
				callback=lambda: thread_function(generate_cards)
			)
			
			with dpg.theme() as generate_button_theme:
				with dpg.theme_component(dpg.mvAll):
					dpg.add_theme_color(
						dpg.mvThemeCol_Button,
						Colors.purple,
						category=dpg.mvThemeCat_Core
					)
					dpg.add_theme_color(
						dpg.mvThemeCol_Text,
						Colors.white,
						category=dpg.mvThemeCat_Core
					)
				
				dpg.bind_item_theme(generate_button_id, generate_button_theme)
			
			dpg.add_button(label="Save cards", callback=lambda: thread_function(save_cards))
			dpg.add_button(label="Add card", callback=render_add_form)
			dpg.add_button(label="Open cards folder", callback=lambda: startfile(Path("cards")))
		with dpg.group(horizontal=True):
			with dpg.group(
				tag="card_info_group", horizontal=False,
				width=(dpg.get_viewport_width() // 3)
			):
				dpg.add_text("Please select a card or add a new one.")
			with dpg.group(
				tag="card_preview", horizontal=False
			):
				pass