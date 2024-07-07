from configparser import ConfigParser
from pathlib import Path

from rich.console import Console

console = Console()


def load_config() -> dict:
	config_file = Path('config.ini')
	
	if not config_file.exists():
		print('Configuration file not found, Card Generator will use the default configuration.')
		return None
	
	_config = ConfigParser()
	_config.optionxform = str
	_config.read('config.ini')
	
	_parsed_config = {}
	
	for section in _config.sections():
		_parsed_config[section] = {}
		for option in _config.options(section):
			_parsed_config[section][option] = eval(_config.get(section, option))
	
	# if 'highlight' in _parsed_config:
	# 	for key, value in _parsed_config['highlight'].items():
	# 		try:
	# 			color_tuple = ImageColor.getrgb(value)
	# 			_parsed_config['highlight'][key] = color_tuple
	# 		except ValueError:
	# 			print(f'{value} ({key}) is not a valid color. This term will be ignored.')
	
	return _parsed_config