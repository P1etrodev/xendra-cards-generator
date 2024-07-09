import asyncio
from math import ceil

import dearpygui.dearpygui as dpg


def update_progress_bar(
	overlay: str = None,
	new_status: float = 0,
	with_percentage: bool = False
):
	progress_bar_id = "generate_card_progress_bar"
	dpg.set_value(progress_bar_id, new_status)
	if overlay is not None:
		if with_percentage:
			percentage = ceil(new_status * 100)
			overlay = f"{overlay} ({percentage}%)"
		dpg.configure_item(
			progress_bar_id,
			overlay=overlay
		)
		